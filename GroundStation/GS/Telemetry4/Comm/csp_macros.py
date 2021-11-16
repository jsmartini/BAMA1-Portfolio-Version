import enum
import libcsp_py3 as libcsp
from . security import *
import struct
from enum import Enum
from time import sleep
from . error import *
from . config import *


metadata_conn = lambda conn: [libcsp.conn_src(conn), libcsp.conn_sport(conn), libcsp.conn_dst(conn),libcsp.conn_dport(conn)]
metadata_pkt = lambda pkt: print(f"PKT[{pkt}]: {libcsp.packet_get_length(pkt)}")
connect = lambda dst, dst_port: libcsp.connect(0, dst, dst_port, 100, 0)
service = lambda conn: libcsp.conn_dport(conn)    #dst port
parse_kwargs = lambda kwargs, key, default:kwargs[key] if key in list(kwargs.keys()) else default
dst = lambda conn: libcsp.conn_dport(conn)
src = lambda conn: libcsp.conn_sport(conn)


def csp_send(**kwargs):
    conn = kwargs["conn"]
    data = kwargs["data"]
    fmt_str = kwargs["fmt_str"]
    timeout = kwargs["timeout"]
    encryption = kwargs["encryption"]

    def payload_processor(payload):
        if type(payload) != list:
            payload =  [payload]
        # strings are the only annoying datatype to handle
        for i, elm in enumerate(payload):
            if type(elm) == str: payload[i] = elm.encode()           # encode a string and convert to bytearray
        #print([type(i) for i in payload])
        return payload
        """
            Returns a string to send to struct.pack's *args parameter for concise code
        """
    try:
        data = payload_processor(data)
        payload = struct.pack(fmt_str, *data)
        pkt = libcsp.buffer_get(1)
        
        if encryption: payload = encrypt(payload)
        libcsp.packet_set_data(pkt, bytearray(payload))
        libcsp.send(conn, pkt, timeout)
        return True

    except BaseException as e:
        error_trace(e)
        return False

def csp_recv(**kwargs):
    # returns a list of the data unpacked
    conn = kwargs["conn"]
    fmt_str = kwargs["fmt_str"]
    timeout = kwargs["timeout"]
    encryption = kwargs["encryption"]
    pkt = libcsp.read(conn, timeout)

    if pkt == None:
        return None
    payload = libcsp.packet_get_data(pkt)
    try:
        if encryption: payload = decrypt(payload)
        try:
            data = struct.unpack(fmt_str, payload)
            return list(data)
        except struct.error as e:
            data = struct.unpack(API["ERROR"]["msg_fmt_str"], payload)
            return list(data)
    except BaseException as e:
        error_trace(e)
        return None








