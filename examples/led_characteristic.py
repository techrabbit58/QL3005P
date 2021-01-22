"""
Drive increasing current through a LED and read back the resulting voltage.
Start with 1 mA and increase in 1 mA steps up to 20 mA.
Read back the voltage for each step.
The maximum allowed voltage shall be set to 4 V.
Disable after having taken the last measure.
Save the result as CSV file.
Connect the LED directly to the PSU. Obey polarity.
No resistors etc. The PSU runs in C.C. mode during the whole test.
Can test LEDs of any colour, as long as the LED forward current
maximum rating is greater or equal 20 mA.
"""
import time

from psu.QJ3005P import PSU

if __name__ == '__main__':
    results = []
    with PSU('COM3') as psu:
        if not psu.is_available():
            print('PSU does not answer. Please check your setup.')
        else:
            psu.disable()
            psu.set(volt=4, amps=.001)
            psu.enable()
            time.sleep(3)
            for milli_amps in range(2, 21):
                psu.amps = float(milli_amps) / 1000
                time.sleep(1)
                readings = psu.get()
                results.append((readings.amps, readings.volt))
            psu.disable()
            with open('green_led.csv', 'w') as output:
                print('forward current [mA],forward voltage [V],power [mW]', file=output)
                for pair in results:
                    amps, volt = pair
                    print(f'{amps * 1000:3.0f},{volt:5.2f},{amps * 1000 * volt:4.0f}', file=output)
