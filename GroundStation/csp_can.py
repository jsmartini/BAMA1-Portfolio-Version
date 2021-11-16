import libcsp_py3 as libcsp # using modified python bindings
import can

"""

From csp_if_can.h



 /*CAN BUS FLAGS  - Jonathan Martini*/
    PyModule_AddIntConstant(m, "CAN_ERR_FLAG", CAN_ERR_FLAG);
    PyModule_AddIntConstant(m, "CAN_RTR_FLAG", CAN_RTR_FLAG);
    PyModule_AddIntConstant(m, "CAN_EFF_MASK", CAN_EFF_MASK);
    PyModule_AddIntConstant(m, "CAN_OFFSET", sizeof(csp_id_t) + sizeof(uint16_t)); // csp_if_can.c
    PyModule_AddIntConstant(m, "CSP_ID_T_SZ", sizeof(csp_id_t));    

add this to pycsp.c
"""

CFP_HOST_SIZE = 5
# Type - \a begin fragment or \a more fragments. */
CFP_TYPE_SIZE = 1
# Remaining fragments */
CFP_REMAIN_SIZE = 8
# CFP identification. */
CFP_ID_SIZE = 10
# @} */


# Helper macro */
CFP_FIELD = lambda id,rsiz,fsiz: ((((id) >> (rsiz)) & ((1 << (fsiz)) - 1)))
# Extract source address */
CFP_SRC = lambda id:		CFP_FIELD(id, CFP_HOST_SIZE + CFP_TYPE_SIZE + CFP_REMAIN_SIZE + CFP_ID_SIZE, CFP_HOST_SIZE)
# Extract destination address */
CFP_DST = lambda id:		CFP_FIELD(id, CFP_TYPE_SIZE + CFP_REMAIN_SIZE + CFP_ID_SIZE, CFP_HOST_SIZE)
# Extract type (begin or more) */
CFP_TYPE = lambda id:		CFP_FIELD(id, CFP_REMAIN_SIZE + CFP_ID_SIZE, CFP_TYPE_SIZE)
# Extract remaining fragments */
CFP_REMAIN = lambda id:		CFP_FIELD(id, CFP_ID_SIZE, CFP_REMAIN_SIZE)
# Extract CFP identification */
CFP_ID = lambda id:		CFP_FIELD(id, 0, CFP_ID_SIZE)
# @} */


# Helper macro */
CFP_MAKE_FIELD = lambda id,fsiz,rsiz: ((((id) & ((1 << (fsiz)) - 1)) << (rsiz)))
# Make source */
CFP_MAKE_SRC = lambda id:	CFP_MAKE_FIELD(id, CFP_HOST_SIZE, CFP_HOST_SIZE + CFP_TYPE_SIZE + CFP_REMAIN_SIZE + CFP_ID_SIZE)
# Make destination */
CFP_MAKE_DST = lambda id:	CFP_MAKE_FIELD(id, CFP_HOST_SIZE, CFP_TYPE_SIZE + CFP_REMAIN_SIZE + CFP_ID_SIZE)
# Make type */
CFP_MAKE_TYPE = lambda id:	CFP_MAKE_FIELD(id, CFP_TYPE_SIZE, CFP_REMAIN_SIZE + CFP_ID_SIZE)
# Make remaining fragments */
CFP_MAKE_REMAIN = lambda id:	CFP_MAKE_FIELD(id, CFP_REMAIN_SIZE, CFP_ID_SIZE)
# Make CFP id */
CFP_MAKE_ID = lambda id:		CFP_MAKE_FIELD(id, CFP_ID_SIZE, 0)
# @} */

# Mask to uniquely separate connections */
CFP_ID_CONN_MASK =	(CFP_MAKE_SRC((1 << CFP_HOST_SIZE) - 1) | \
				 CFP_MAKE_DST((1 << CFP_HOST_SIZE) - 1) | \
				 CFP_MAKE_ID((1 << CFP_ID_SIZE) - 1))

MAX_BYTES_IN_CAN_FRAME =  8
CFP_OVERHEAD = (libcsp.CSP_ID_T_SZ + libcsp.sizeofUint16_t)
MAX_CAN_DATA_SIZE = (((1 << CFP_REMAIN_SIZE) * MAX_BYTES_IN_CAN_FRAME) - CFP_OVERHEAD)

BEGIN = 0 
MORE  = 1




class can_csp_assembler:

    def __init__(self):
        print("Waiting to assemble next packet")
        self.pkt_bytes_array = bytearray()
        self.assembled = False
        self.fail = False
        self.remain = 0

    def can_csp_rx(self, frame: can.message.Message):    
        get_id_extended = lambda id: id#int("{0:08x}".format(id))
        id = get_id_extended(frame.arbitration_id)
        frame_type = CFP_TYPE(get_id_extended(id))
        if frame_type == BEGIN:
            print("Begin Frame Hit")
            self.remain = CFP_REMAIN(id)
            self.pkt_bytes_array.extend(frame.data)
            return
        elif frame_type == MORE:
            print("More Frame Hit")
            self.pkt_bytes_array.extend(frame.data)
            self.remain -= 1
            
        print(f"Remaining Frames: {self.remain}")
        if (CFP_REMAIN(id) == self.remain) and (self.remain == 0):
            self.assembled = True

    def get_packet(self):
        return self.pkt_bytes_array

    
def csp_disassembler_can(packet: bytearray) -> list:
    pass

