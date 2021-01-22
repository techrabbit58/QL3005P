"""
Set current and voltage to specific values and enable.
"""
from psu.QJ3005P import PSU

if __name__ == '__main__':
    with PSU('COM3') as psu:
        if psu.is_available():
            psu.disable()
            psu.set(volt=5, amps=.5)
            print(f'OK | {psu.volt:5.2f} V | {psu.amps:5.3f} A')
        else:
            print('PSU not found. Please check your lab setup.')
