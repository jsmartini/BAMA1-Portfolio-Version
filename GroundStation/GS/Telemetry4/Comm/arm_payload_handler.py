from . error import *
from . config import *
from . csp_macros import *

def arm_payload_handler(conn):
    spam = 5
    try:
        data = csp_recv(
                conn=conn,
                fmt_str= API["ARM"]["req_fmt_str"],
                timeout = API["ARM"]["TIMEOUT"],
                encryption = True
            )
        if data == None:
           return False
            
        print(data)

            # make sure data conforms to api standard, redundant error checking code
        assert type(data) == list
        assert len(data) == 2


        password = data[0]
        spam = data[1]

        ARM = False
        if password.decode() == CONFIG["ARM"]["password"]:
            ARM = True
        
        for i in range(spam):
            print(f"Sending Message {i+1}/{spam}")
            csp_send(
                conn = conn,
                data = [ARM, spam],
                fmt_str = API["ARM"]["res_fmt_str"],
                timeout = API["ARM"]["TIMEOUT"],
                encryption = False
            )

        libcsp.close(conn)
        return ARM

    except BaseException as e:
        error_trace(e)
        for i in range(spam):
            print(f"Sending Error Message {i+1}/{spam}")
            csp_send(
                conn = conn,
                data = [-1, i+1],
                fmt_str = API["ERROR"]["msg_fmt_str"],
                timeout = API["ERROR"]["TIMEOUT"],
                encryption = False
               )
        libcsp.close(conn)
        return False