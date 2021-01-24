# A Remote Control Class For QJE3005P Like PSUs #

## Summary ##

QJ3005P is a remote control interface class for bench power
supplies that have a couple of
remote control capabilities, like QuatPower LN-3005P, QJE QJ-3005P, TEK3005P
etc. There are a lot of very similar devices available from chinese manufacturers,
all sharing the same look and feel, and more or less the same
remote control capabilities.

The xy3005P provides one adjustable PSU channel and can be controlled via
USB serial emulation, at 9600 bps.

The remote control capabilities are limited and have some special properties
that must be taken in account when using the interface class.

## Supported PSU Commands ##

Command | Usage
--- | ---
*IDN? | Query for the PSU model name and product version
STATUS? | Query PSU mode of operation (C.V./C.C.) and output status (on/off)
VOUT1? | Query current output voltage reading
IOUT1? | Query current output current reading
VSET1:vv.vv | Set new output voltage to 0.0 ... 30.00 volt in 10 milli volt steps
VSET1? | Read the last maximum output voltage set point
ISET1:c.ccc | Set new output voltage to 0.0 ... 5.000 ampere in 1 milli amp steps
ISET1? | Read the last maximum output current set point
OUTPUT1 | Load switch set to on (i.e. output enabled)
OUTPUT0 | Load switch set to off (i.e. output disabled)

## The QJ3005P API ##

- Create a new instance of the PSU interface.
```python
from psu.QJ3005P import PSU

qj3005p = PSU('/dev/yourtty')
````
- Recommended: Use a `with` clause to interact with the PSU.
```python
import time

with qj3005p as psu:
    psu.set(volt=5, amps=.5)
    psu.enable()
    psu.read()
```
- The API consists of several methods to query the PSU
model/brand/version and operational status, to set
  voltage and current, to control the load switch, and
  to read current voltage and current readings back from
  the PSU.
  
API | Type | Remark
--- | --- | ---
`psu = PSU('COMx')` | construct | create new control object and bind to TTY
`psu.open()` | method | start serial communication to device
`psu.close()` | method | stop serial communication to device
`psu.set(volt, amps)` | method | set new maximum voltage and current
`psu.get()` | method | read current and voltage, together with CV/CC and output status. Returns a tuple.
`psu.volt` | property | get current voltage reading from device, or assign new set point
`psu.amps` | property | get current ampere reading from device, or assign new amperes set point
`psu.enable()` | method | enable PSU output (i.e. load switch on)
`psu.disable()` | method | disable PSU output (i.e. load switch off)
`psu.status` | property | get current PSU output status and CV/CC status as a list of strings
`psu.name` | property | get the brand, name and hardware/firmware version of the PSU
`psu.is_availabl()` | method | query for availability of a PSU on the TTY
`psu_is_open()` | method | query for the TTY channel to be opened
`psu.is_enabled` | property | query the PSU for the current output status
`psu.mode` | property | query the PSU if it is currently running in CV or CC mode

## Limits Of The PSU Hardware And Firmware ##

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

## About The Code ##

The code was developed and tested with python 3.8. May also run with
earlier or subsequent versions of python.

It comes with some examples and demos, how the interface class is
intended to be used.

Other requirements: `pyserial`.

---