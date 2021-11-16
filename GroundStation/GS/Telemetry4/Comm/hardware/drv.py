from numpy import sign

#DDV8830 is itself a multiplexer
control = 0x00
fault= 0x01

# magnet torquer i2c addresses
# from power point i2c schematic
# read write form [0] -> write, [1] -> read
#address_x = [0xC2, 0xC3] ->revision 2.7 
address_x = [0xC8, 0xC9] #revision 2.6 -> enable channel 4
#address_y = [0xC6, 0xC7] ->revision 2.7 
address_y = [0xC8, 0xC9] #revision 2.6 -> enable channel 5
address_z = [0xC8, 0xC9] #enable channel 6

# control register logic values for magnet torquer
ctrl_standby = 0x00 # off
ctrl_reverse = 0x01 # reverse voltage direction
ctrl_forward = 0x02 # forward voltage direction
ctrl_full    = 0x03 # full on

# voltage -> register value mappings
output_voltage = [
    0.48,
    0.56,
    0.64,
    0.72,
    0.80,
    0.88,
    0.96,
    1.04,
    1.12,
    1.20,
    1.29,
    1.37,
    1.45,
    1.53,
    1.61,
    1.69,
    1.77,
    1.85,
    1.93,
    2.01,
    2.09,
    2.17,
    2.25,
    2.33,
    2.41,
    2.49,
    2.57,
    2.65,
    2.73,
    2.81,
    2.89,
    2.97,
    3.05,
    3.13,
    3.21,
    3.29,
    3.37,
    3.45,
    3.53,
    3.61,
    3.69,
    3.77,
    3.86,
    3.94,
    4.02,
    4.1,
    4.18,
    4.26,
    4.34,
    4.42,
    4.5,
    4.58,
    4.66,
    4.74,
    4.82,
    4.9,
    4.98,
    5.06
]

output_keys = [
    0x06,
    0x07,
    0x08,
    0x09,
    0x0A,
    0x0B,
    0x0C,
    0x0D,
    0x0E,
    0x0F,
    0x10,
    0x11,
    0x12,
    0x13,
    0x14,
    0x15,
    0x16,
    0x17,
    0x18,
    0x19,
    0x1A,
    0x1B,
    0x1C,
    0x1D,
    0x1E,
    0x1F,
    0x20,
    0x21,
    0x22,
    0x23,
    0x24,
    0x25,
    0x26,
    0x27,
    0x28,
    0x29,
    0x2A,
    0x2B,
    0x2C,
    0x2D,
    0x2E,
    0x2F,
    0x30,
    0x31,
    0x32,
    0x33,
    0x34,
    0x35,
    0x36,
    0x37,
    0x38,
    0x39,
    0x3A,
    0x3B,
    0x3C,
    0x3D,
    0x3E,
    0x3F
]

output_keys_length = len(output_keys)

assert len(output_keys) == len(output_voltage)

# implement balanced binary search tree to make this faster
def match_Vkey(v_cmd):
    i = 1
    while i <= output_keys_length:
        if v_cmd < output_voltage[i] and v_cmd >= output_voltage[i-1]:
            return output_keys[i-1] # return conservative estimate
        i+=1


class DRV8830:
    
    def __init__(self, multiplexer, channel, address):
        self.channel = channel
        self.address = address
        self.mux = multiplexer

    def write_ctrl(self, v):
        self.mux.channel(self.channel)
        self.mux.write_device(self.channel, self.address, control, v)

    def req_V(self, v_req):
        # change to correct channel
        self.mux.channel(self.channel)
        if v_req != 0:
            polarity = sign(v_req)
            if polarity > 0:
                direction = ctrl_forward
            else:
                direction = ctrl_reverse
            mag = abs(v_req)
            VRegValue = match_Vkey(mag)
            print(f"Base Register = {hex(VRegValue)} ; direction = {direction}")
            # shift [8,3] 2 bits left and or the direction bits into the final value
            VRegValue = VRegValue << 2 | direction
        else:
            VRegValue = ctrl_standby
        print(f"reg val: {hex(VRegValue)}")
        self.mux.write_device(self.channel, self.address, control, VRegValue)

