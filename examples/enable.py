"""
Switch PSU output on.
"""
from psu.QJ3005P import PSU

if __name__ == '__main__':
    with PSU('COM3') as psu:
        if psu.is_available():
            psu.enable()
        else:
            print('PSU not found. Please check your lab setup.')
