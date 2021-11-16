from . hardware import DRV8830, multiplex, MMC5883MA
from time import sleep
import numpy as np
from . config import *
from . lock import LOCK

global ADCSSystem
ADCSSystem = None

class ADCSInterface:

    def __init__(self):
        try:
            self.MUX = multiplex(1)

            sensors = [2,3,4]
            drivers = [(4, 97),(5, 99),(6, 100)]

            self.MMCs = [MMC5883MA(self.MUX, i) for i in sensors]
            self.DRVs = [DRV8830(self.MUX, i, j) for (i,j) in drivers]
        except BaseException as e:
            print(e)

    def reset_drivers(self):
        try:
            [drv.req_V(0) for drv in self.DRVs]
        except BaseException as e:
            print(e)

    def grab_bdot(self):
        try:
            mag1 = self.MMCs[0].mag()
            sleep(0.1)
            mag2 = self.MMCs[0].mag()
            bdot = (mag1 - mag2) / 0.1
            bdot = bdot/np.linalg.norm(bdot)
            return bdot
        except BaseException as e:
            print(e)
            return np.array([-7,-7,-7])

class SimADCSInterface:

    def __init__(self):
        print("simulated ADCS interface ")

    def reset_drivers(self):
        pass

    def grab_bdot(self):
        # simluated values
        # not connecting this to the HIL simulator because it would be way too much effort
        # might implement feature if presented as a AIAA student project
        
        sleep(1)
        b1 =  (2*np.random.rand(3))
        b2 = (2*np.random.rand(3))
        bdot = (b1-b2)/0.1
        bdot /= np.linalg.norm(bdot)
        
        return bdot



