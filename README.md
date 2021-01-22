# A Remote Control Class For QJE3005P Like PSUs #

QJ3005P is a remote control interface class for bench power
supplies that have a couple of
remote control capabilities, like QuatPower LN-3005P, QJE QJ-3005P, TEK3005P
etc. There are a lot of very similar devices available from chinese manufacturers,
all sharing the same look and feel, and more or less the same
remote control capabilities.

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

The code was developed and tested with python 3.8. May also run with
earlier or subsequent versions of python.

It comes with some examples and demos, how the interface class is
intended to be used.

Other requirements: `pyserial`.