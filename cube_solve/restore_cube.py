import time
from kociemba import solve
from serial_core.serial_arduino import SerialArduino

serial_arduino = SerialArduino("COM4")

# res = solve("BBURUDBFUFFFRRFUUFLULUFUDLRRDBBDBDBLUDDFLLRRBRLLLBRDDF")
res = solve("LDBBUFFURFRUBRFDLBLRUFFUFFRDDFDDUDDRBRULLLLLLRRUUBBDBB")

# print(res)

chars = {
    'F': 'a', 'U': 'b', 'R': 'c', 'B': 'd', 'L': 'e', 'D': 'f',
    "F'": '1', "U'": '2', "R'": '3', "B'": '4', "L'": '5', "D'": '6',
    'F2': 'h', 'U2': 'i', 'R2': 'j', 'B2': 'k', 'L2': 'l', 'D2': 'm'
}

solve = []
for s in res.split(' '):
    solve.append(chars[s])

# print(solve)
A = input("input A")
serial_arduino.send_msg('A')

C = input("input C")
serial_arduino.check_cube()

input("input T")
for s in solve:
    serial_arduino.send_msg(s)

# python setup.py install
# U、R、F、D、L、B顺序传入值
# U R' F2 L2 D R2 B2 D' R D F2 L2 U R2 B2 U2 R2 U' R2
