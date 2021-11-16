
from csp_can import *
import can


bustype = "socketcan"
channel = "vcan0"

bus = can.interface.Bus(channel=channel, bustype=bustype)

assembler = can_csp_assembler()

while True:
    data = bus.recv()
    print(" == pkt == ")
    print(data)
    #print(int("{0:08x}".format(data.arbitration_id)))
    print(f"channel {data.channel}")
    print(f"data {data.data}")
    print(f"dlc {data.dlc}")
    assembler.can_csp_rx(data)

    if assembler.fail:
        print("Failed to Assemble CSP Packet")
        assembler = can_csp_assembler()
    elif assembler.assembled:
        print("Full Packet Assembled")
        print(assembler.get_packet())
        msg = ''.join([hex(i) for i in assembler.get_packet()])
        print(msg)
        
        assembler = can_csp_assembler()

    
