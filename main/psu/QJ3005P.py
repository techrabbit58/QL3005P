"""
Copyright (c) 2021 Karl-Dieter Zimmer-Bentin

This provides a remote control class for bench power supplies that have some
remote control capabilities, like QuatPower LN-3005P, QJE QJ-3005P, TEK3005P
etc. There are a lot of likewise devices available from chinese manufacturers,
all sharing the same look and feel, and remote control capabilities.

The xy3005P provides one adjustable PSU channel and can be controlled via
USB serial emulation, at 9600 bps.

The remote control capabilities are limited and have some special properties
that must be taken in account when using the interface class:

- During remote control, the front panel knob and buttons are disabled.
- Remote control mode can only be left by power-cycling the device.
- OCP, memory recall and store settings is not possible with remote control.
  Works only by using the front panel. Preset OCP can not be influenced
  by remote control.
- Voltage and current set points can not be read back without setting it
  first.
- Awkward command delimiter: it is not CD LF or LF, but literally backslash+r
  backslash+n, or backslash+n alone.
- Switching the output on or off needs some time to let the meter settle.
  Some wait time between switching the output and reading back the actual
  voltage and current seems to be recommendable.
- Settings from remote can not be stored permanently on the PSU and do not
  survive a power cycle of the PSU.
- The baud rate of the PSU serial channel is 9600 bps, as the user manual
  specifies. This is actually the default for new `pyserial` Serial objects,
  and this setting is implicit. The `pyserial` user manual does recommend
  setting a timeout for the PSU communication.
  Refer to the `__init__` for details.
- There is no clear error feedback from the PSU. Errors must be derived from
  status/ID feedbacks and voltage/current readings.

This code is tested with python 3.8. May also run with earlier or subsequent
versions of python.
"""
import time
from typing import List, NamedTuple

import serial


class Readings(NamedTuple):
    volt: float
    amps: float
    enabled: bool
    mode: str


class PSU:

    def __init__(self, port: str):
        """
        The PSU objects delegate all communication to the Serial class from the pyserial
        library, which must be installed in your python runtime if you want to work with
        the PSU class. The pyserial lib is the only requirement. All other stuff comes
        from the python standard library.
        :param port:
        """
        self.com = serial.Serial(timeout=0.5)
        self.com.port = port

    def __enter__(self) -> "PSU":
        """
        The PSU object can be used as a context manager, so that open/close
        of the serial channel are handled automagically, in a 'with' statement.
        Please read https://docs.python.org/3.8/reference/datamodel.html#object.__enter__
        for reference about context managers.
        :return: the current PSU object.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        The PSU object can be used as a context manager, so that open/close
        of the serial channel are handled automagically, in a 'with' statement.
        Please read https://docs.python.org/3.8/reference/datamodel.html#object.__exit__
        for reference about context managers.
        :param exc_type: The exception that may have occurred during __enter__.
        :param exc_val: The exception value, if any.
        :param exc_tb: The caller traceback, if any.
        :return: always True (which means: exception suppression).
        """
        self.close()
        return True

    def _write(self, text: str):
        """
        Write a line of text to the PSU. The text must be limited by the literal "slash+backslash".
        The procedure adds the required delimiter automatically, and flushes the buffer after
        the serial write.
        :param text: the text to be written.
        :return: nothing.
        """
        if self.is_open():
            self.com.reset_output_buffer()
            self.com.reset_input_buffer()
            self.com.write(f'{text}\\n'.encode())
            self.com.flush()

    def _read(self) -> str:
        """
        Read a response from the PSU (a line of text, delimited by the newline character).
        :return: the response from the PSU, as a string.
        """
        return self.com.readline().decode().strip()

    def open(self) -> bool:
        """
        Open the serial channel to the PSU.
        :return: True (success) or False (an error occurred).
        """
        rc = True
        if not self.is_open():
            try:
                self.com.open()
            except serial.SerialException:
                rc = False
        return rc

    def close(self):
        """
        Close the serial channel to the PSU.
        :return: nothing.
        """
        if self.is_open():
            self.com.close()

    def set(self, *, volt: float, amps: float):
        """
        Set voltage and current at the same time.
        As Github user MarkuBu has reported, some machines may need a
        short delay between the VSET and ISET. He recmmended 100 ms.
        :param volt: the new voltage set point (in Volt).
        :param amps: the new current set point (in Ampere).
        :return: nothing.
        """
        if self.is_open():
            self._write(f'VSET1:{min(30., max(0., volt)):5.2f}')
            time.sleep(0.1)
            self._write(f'ISET1:{min(30., max(0., amps)):5.3f}')

    def get(self) -> Readings:
        return Readings(volt=self.volt, amps=self.amps, enabled=self.is_enabled, mode=self.mode)

    @property
    def volt(self) -> float:
        """
        Read the currently supplied voltage from the PSU, if OUTPUT enabled.
        Otherwise, read the current voltage set point.
        :return: the voltage (in Volt) as a floating point number.
        """
        if self.is_open() and self.is_enabled:
            self._write('VOUT1?')
            result = float(self._read())
        elif self.is_open():
            self._write('VSET1?')
            time.sleep(0.1)
            result = float(self._read())
        else:
            result = 0.
        return result

    @volt.setter
    def volt(self, value: float):
        """
        Define a new output voltage for CV mode.
        :param value: the new voltage setting.
        :return: nothing.
        """
        if self.is_open():
            self._write(f'VSET1:{min(30., max(0., value)):5.2f}')

    @property
    def amps(self) -> float:
        """
        Read the currently supplied current from the PSU, if OUTPUT enabled.
        Otherwise, read the current set point.
        :return: the current (in Ampere) as a floating point number.
        """
        if self.is_open() and self.is_enabled:
            self._write('IOUT1?')
            result = float(self._read())
        elif self.is_open():
            self._write('ISET1?')
            result = float(self._read())
        else:
            result = 0.
        return result

    @amps.setter
    def amps(self, value: float):
        """
        Define a new maximum output current, at which the PSU switches from CV to CC.
        :param value: the new current setting.
        :return: nothing.
        """
        if self.is_open():
            self._write(f'ISET1:{min(30., max(0., value)):5.3f}')

    def enable(self) -> bool:
        """
        Switch PSU output on.
        :return: the resulting output status.
        """
        if self.is_open():
            self._write('OUTPUT1')
            time.sleep(0.5)
        return 'OUTPUT' in self.status

    def disable(self) -> bool:
        """
        Switch PSU output off.
        :return: the resulting output status.
        """
        if self.is_open():
            self._write('OUTPUT0')
            time.sleep(0.5)
        return 'OUTPUT_OFF' in self.status

    @property
    def status(self) -> List[str]:
        """
        Request status information about the PSU.
        Status information is available for the supply mode
        (constant current vs. constant voltage),
        and if the output is switched on or off.
        The third status flag seems to be meaningless. It does not
        change, regardless if OCP is enabled or not.
        :return: a list of CV/CC (= index 0) and OUTPUT/OUTPUT_OFF (= index 1)
        """
        results = []
        if self.is_open():
            self._write('STATUS?')
            rc = self._read()
            results.append('CV' if rc[0] == '1' else 'CC')
            results.append('OUTPUT' if rc[1] == '1' else 'NO_OUTPUT')
        else:
            results = [""] * 3
        return results

    @property
    def name(self) -> str:
        """
        Asks the PSU for its type number.
        The library was written for, and tested with a thing that
        answered "QJE3005PV1.0" on this request.
        :return: the brand and type of the PSU.
        """
        name = None
        if self.is_open():
            self._write('*IDN?')
            name = self._read()
        return name or ""

    def is_available(self) -> bool:
        """
        Checks if the PSU can be reached, and if dialog is possible.
        Internally this asks for the PSU name (via *IDN? request) and
        answers false, if, after the *IDN? request, the name could not
        be read from the PSU.
        :return: True if connectivity exists, or False, if not.
        """
        return self.name is not None

    def is_open(self) -> bool:
        """
        Report if the serial communication channel could be opened or not.
        :return: True/False, according to the openness of the serial channel.
        """
        return self.com.is_open

    @property
    def is_enabled(self) -> bool:
        """
        Read the output status from the PSU and return it as a boolean.
        :return: True/False, according to the momentary PSU output status.
        """
        result = False
        if self.is_open():
            if 'OUTPUT' in self.status:
                result = True
        return result

    @property
    def mode(self) -> str:
        """
        Read the C.C./C.V. mode the PSU is currently in. Returns the string 'CC'
        if the PSU is in constant current mode, and 'CV' if it is in constant
        voltage mode.
        :return: 'CC' or 'CV' according to the mode of operation of the PSUs
            power outlet.
        """
        if self.is_open():
            result = self.status[0]
        else:
            result = ""
        return result
