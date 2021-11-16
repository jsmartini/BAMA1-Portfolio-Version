import numpy as np
# helping source code
# https://gist.github.com/ubi-gists/d87189ebf8216c427f92064ab593a3ce
# Register Map
Xout_LSB = 0x00
Xout_MSB = 0x01
Yout_LSB = 0x02
Yout_MSB = 0x03
Zout_LSB = 0x04
Zout_MSB = 0x05
Temp_Out = 0x06
Dev_Stat = 0x07
IntCTRL0 = 0x08
IntCTRL1 = 0x09
IntCTRL2 = 0x0A
X_Thresh = 0x0B
Y_Thresh = 0x0C
Z_Thresh = 0x0D
Prod_ID  = 0x2F
ADDRESS = 0x30

xyzLSBRegs = [Xout_LSB, Yout_LSB, Zout_LSB]
xyzMSBRegs = [Xout_MSB, Yout_MSB, Zout_MSB]
from time import sleep
# cache these
dynamic = 16
resolution = 2**16 # bits
m_rng = dynamic/resolution
uncertainty = dynamic/2

# ( left shift MSB 8 bits then min bitwise OR with LSB ) * (dynamic rng/ max resolution bits) - uncertainty)
uToFloat = lambda LSB, MSB: float((MSB << 8 | LSB) * m_rng - uncertainty) 

class MMC5883MA:

    # slave init
    def __init__(self, multiplexer, channel): 
        self.mux = multiplexer
        self.channel = channel
        self._reset()

    def calibrate(self):
        pass

    def _reset(self): 
        self.mux.write_device(
            self.channel,
            ADDRESS,
            IntCTRL0,
            0x4, # reset flag page 8
        )

    def _status(self):
        return self.mux.read_device(
            self.channel,
            ADDRESS,
            Dev_Stat
        )

    def _orientation(self):
        pass
        # implement to orient the different sensors around the sat to correct position

    def _wait(self):
        sleep(0.01)
        i = -1
        while i ==0:
            i = self._status()
            #print(i)
            sleep(0.01)
            pass # measurement is being read currently, waiting for device reset
    
    def mag(self):
#        self._reset()
        sleep(0.01)
        self.mux.write_device(self.channel, ADDRESS, IntCTRL0, 0b00000001) # TM_M High - Magnetic reading to follow
        #self.mux.write_device(self.channel, ADDRESS, Dev_Stat, 0b00000111) # send to device's status register to read
        self._wait()
        xyz_lsb = [self.mux.read_device(self.channel, ADDRESS, reg) for reg in xyzLSBRegs]  
        xyz_msb = [self.mux.read_device(self.channel, ADDRESS, reg) for reg in xyzMSBRegs]
#        for r in xyzLSBRegs:
#            print(self.mux.read_device(self.channel, ADDRESS, r))
        #print(list(map(bin, xyz_lsb)))
        #print(list(map(bin, xyz_msb)))
        return np.array([uToFloat(*lsb_msb_tuple) for lsb_msb_tuple in zip(xyz_lsb, xyz_msb)])

if __name__ == "__main__":
    from mux import *
    mux = multiplex(2)
    mag = MMC5883MA(mux, 0)
#    mag._reset()
    print(mag._status())
    print(mag.mag())

    from time import sleep
    while 1:
        sleep(1)
        #print(mag._status())
        print(mag.mag())
