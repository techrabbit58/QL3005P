"""
Check if QL3005P is physically connected or not.
Copyright (c) 2021 Karl-Dieter Zimmer-Bentin
"""
from psu.QJ3005P import PSU

if __name__ == '__main__':
    with PSU('COM3') as psu:
        if psu.is_available():
            print(f'Connected to PSU: {psu.name}')
        else:
            print('PSU not found.')
