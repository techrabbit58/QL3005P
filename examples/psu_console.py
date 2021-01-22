"""
A console UI for the QL3005P type PSUs.
Copyright (c) 2021 Karl-Dieter Zimmer-Bentin
"""
import os
import re
from cmd import Cmd
from textwrap import dedent
from typing import Optional, List

from psu.QJ3005P import PSU


class PsuConsole(Cmd):
    default_prompt: str = 'PSU > '
    prompt: str = default_prompt
    intro: str = dedent("""\
    
    Console UI for QL-3005P like programmable power supply units.
    Enter "help" to obtain information about the available UI commands.
    Enter "port" followed by a serial device name to connect to
    the PSU connected to that serial channel of your computer.
    Enter "bye" to go back to the operating system prompt.
    """)

    psu: Optional[PSU] = None

    def emptyline(self) -> bool:
        return False

    def do_connect(self, line):
        """Set serial port for PSU communication and connect to the attached PSU. Example: "connect com1"."""
        port = line.split()
        if len(port) != 1:
            self.parameter_error(line)
        else:
            self.psu = PSU(line.split()[0])
            with self.psu as psu:
                if psu.is_available():
                    self.prompt = f'{self.psu.name} > '
                else:
                    self.connection_error()
        return False

    def do_info(self, line) -> bool:
        """Show the current PSU status and operational mode. Example: "info"."""
        args = line.split()
        if len(args):
            self.parameter_error(line)
        elif not self.psu:
            self.not_connected_error()
        else:
            with self.psu as psu:
                if psu.is_available():
                    reading = psu.get()
                    print(f'voltage..: {reading.volt} V')
                    print(f'current..: {reading.amps} A')
                    print(f'output...: {"ON" if reading.enabled else "OFF"}')
                    print(f'mode.....: {reading.mode}')
                else:
                    self.connection_error()
        return False

    def do_volt(self, line: str) -> bool:
        """Set the PSU maximum voltage to a new value. Example: "volt 3.3"."""
        args: List[str] = line.split()
        if len(args) != 1 or not re.match(r'^\d{0,2}(\.\d{0,2})?$', args[0]):
            self.parameter_error(line)
        elif not self.psu:
            self.not_connected_error()
        else:
            with self.psu as psu:
                if psu.is_available():
                    psu.volt = float(args[0])
                else:
                    self.connection_error()
        return False

    def do_amps(self, line: str) -> bool:
        """Set the PSU maximum current to a new value. Example: "amps .1"."""
        args: List[str] = line.split()
        if len(args) != 1 or not re.match(r'^\d?(\.\d{0,3})?$', args[0]):
            self.parameter_error(line)
        elif not self.psu:
            self.not_connected_error()
        else:
            with self.psu as psu:
                if psu.is_available():
                    psu.amps = float(args[0])
                else:
                    self.connection_error()
        return False

    def do_set(self, line: str) -> bool:
        """Set voltage and maximum current at the same time. Example "set 9v .1a"."""
        m = re.match(r'^(?P<VOLT>\d{0,2}(\.\d{0,2})?)[vV]\s+(?P<AMPS>\d?(\.\d{0,3})?)[aA]$', line)
        if not m:
            m = re.match(r'^(?P<AMPS>\d?(\.\d{0,3})?)[aA]\s+(?P<VOLT>\d{0,2}(\.\d{0,2})?)[vV]$', line)
        if not m:
            self.parameter_error(line)
        elif not self.psu:
            self.not_connected_error()
        else:
            with self.psu as psu:
                if psu.is_available():
                    psu.set(**{k.lower(): float(v) for k, v in m.groupdict().items()})
                else:
                    self.connection_error()
        return False

    def do_on(self, line):
        """Switch the PSU output on. Example: "on"."""
        args = line.split()
        if len(args):
            self.parameter_error(line)
        elif not self.psu:
            self.not_connected_error()
        else:
            with self.psu as psu:
                if psu.is_available():
                    psu.enable()
                else:
                    self.connection_error()
        return False

    def do_off(self, line):
        """Switch the PSU output off. Example: "off"."""
        args = line.split()
        if len(args):
            self.parameter_error(line)
        elif not self.psu:
            self.not_connected_error()
        else:
            with self.psu as psu:
                if psu.is_available():
                    psu.disable()
                else:
                    self.connection_error()
        return False

    def do_run(self, line):
        """Run a script from a text file. Example: "run profile1.txt"."""
        if not line.strip():
            self.parameter_error(line)
        else:
            if not os.path.exists(line):
                print(f'File not found: "{line}".')
            else:
                with open(line) as f:
                    self.cmdqueue.extend(f.read().lower().splitlines())
        return False

    def do_EOF(self, line):
        """Exit program at end of input file. Example: "^D"."""
        print('EOF')
        return self.quit(line)

    def do_bye(self, line):
        """Exit program execution and go back to the shell prompt. Example usage: "bye"."""
        print('Bye!')
        return self.quit(line)

    @staticmethod
    def quit(line):
        line.strip()
        return True

    def connection_error(self):
        print(f'Could not connect to a PSU on port {self.psu.com.port.upper()}.')
        print('Please, check your lab setup and cabling and try again.')
        self.prompt = self.default_prompt
        self.psu = None

    def parameter_error(self, line: str) -> None:
        print(f'Bad parameter: "{line}".')
        print(f'Please, try "help {self.lastcmd.split()[0]}" for information about command usage.')

    @staticmethod
    def not_connected_error() -> None:
        print('PSU is disconnected. Please, use the "connect" command first.')


if __name__ == '__main__':
    try:
        PsuConsole().cmdloop()
    except KeyboardInterrupt:
        print('^C')
        raise SystemExit
