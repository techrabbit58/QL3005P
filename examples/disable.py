"""
Switch PSU output off.
Copyright (c) 2021 Karl-Dieter Zimmer-Bentin
"""
from psu.QJ3005P import PSU

if __name__ == '__main__':
    with PSU('COM3') as psu:
        if psu.is_available():
            psu.disable()
        else:
            print('PSU not found. Please check your lab setup.')
