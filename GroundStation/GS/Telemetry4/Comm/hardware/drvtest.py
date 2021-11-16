from mux import multiplex
from drv import DRV8830
import sys

bus = multiplex(2)
drv = DRV8830(bus, 0, 0x60)

while 1:
    d = input("straight value input? y/n")
    if d == "y":
        d = input("Register Value")
        drv.write_ctrl(int(d, base=16))
    else:
        v = float(input("v:\t"))
        drv.req_V(v)
