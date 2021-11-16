from time import sleep
from mux import *
from mmc import *

import numpy as np
from collections import deque

mux = multiplex(2)

#s1 = MMC5883MA(mux, 0)
s2 = MMC5883MA(mux, 0)

sensor = [s2]

def bdot(current, past, gains, sampling_time):
    normB = (current - past) / sampling_time
    normB /= np.sqrt(np.dot(normB.T, normB))
    return -gains @ normB



def read(s_list):
    
    return np.sum([s.mag() for s in s_list], axis=0)/len(s_list)
        
def MAFilter(s_list, calibration, Ts):
    d = deque(maxlen=10)
    for i in range(calibration):
        sleep(Ts)
        d.append(read(s_list))
    bias = np.average(d,axis=0)
    while 1:
        d.append(read(s_list))
        yield np.average(d, axis=0) - bias

    

Ts = 0.1
last = np.zeros(shape=(3,1))
gain = np.diag([0.3, 0.3, 0.3])


data = MAFilter(sensor, calibration=30, Ts=Ts)

N = []

while 1:
    sleep(Ts)
    print("="*30)
    current = next(data)
    print(f"{bdot(current, last, gain, Ts)} @ {current} Gauss")
    last = current
