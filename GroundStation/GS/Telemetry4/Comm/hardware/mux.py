import smbus
from time import sleep    
class multiplex:
        #Multiplexer functions
        def __init__(self, bus):

            # @2019 ARA OG Senior Design Zack Comose
                self.bus = smbus.SMBus(bus)
                # self.current_channel = 0       # uncomment when not testing
                #print("Select channel (0-7):") # comment out when not testing
                self.current_channel = -1 # comment out when not testing
        # for tca multiplexer
        
        def channel(self,channel, register=0x04,address=0x70):
#                print(self.current_channel)
                if self.current_channel == channel: return # already here so why write again and waste time
                elif (channel==0): action = 0x01
                elif (channel==1): action = 0x02
                elif (channel==2): action = 0x04
                elif (channel==3): action = 0x08
                elif (channel==4): action = 0x10
                elif (channel==5): action = 0x20
                elif (channel==6): action = 0x40
                elif (channel==7): action = 0x80
                self.bus.write_byte_data(address,register,action) #0x04 is the regi$)
                sleep(0.01)
        # write for slave devices
        def write_device(self, channel, address, register, action):
            # change channel
            self.channel(channel)
            # write action -> @channel@device@register
            self.bus.write_byte_data(
                address,
                register,
                action
                )
        
        # read for slave devices
        def read_device(self, channel, address, register):
            # change channel
            self.channel(channel)
            # return value @ the address
            return self.bus.read_byte_data(address, register)

        def read_device_block(self, channel, address, register, words):
            # read n words from device
            self.channel(channel)
            return self.bus.read_i2c_block_data(address, register, words)
