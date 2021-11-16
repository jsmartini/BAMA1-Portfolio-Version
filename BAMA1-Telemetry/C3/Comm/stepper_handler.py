from . hardware.stepper_motor_driver import stepper_driver_execute
from . lock import *
from . error import *
from . config import *
from . csp_macros import *

def stepper_handler(conn, sim_flag=False):

    success, distance, faults = 0,0,0

    def stepper(distance, brake, conn):
        LOCK.lock()
        try:
            distance, faults = stepper_driver_execute(distance, brake)
            LOCK.unlock()
            return True, distance if brake else -1*distance, faults
        except BaseException as e:
            error_trace(e)
            if not RUNTIME_STATES["CTRL_OFF"]:
                LOCK.unlock()
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
            return False, 0, 0

    while conn:
        try:
            data = csp_recv(
                conn=conn,
                fmt_str= API["STEPPER"]["req_fmt_str"],
                timeout = API["STEPPER"]["TIMEOUT"],
                encryption = True
            )
            if data == None:
                break

            # make sure data conforms to api standard, redundant error checking code
            assert type(data) == list
            assert len(data) == len(API["STEPPER"]["req_fmt_str"][1:])
            
            distance = data[0]
            brake = data[1]
            spam = data[2]

            if not sim_flag:
                # real hardware execution
            
                success, distance, faults = stepper(distance, brake, conn)
        
            else:
                # offline simulation
                from random import randint
                success, distance, faults = True, distance, randint(0,15) 

            if success:
                for i in range(spam):
                    print(f"Sending Message {i+1}/{spam}")
                    csp_send(
                        conn = conn,
                        data = [distance, faults, i+1],
                        fmt_str = API["STEPPER"]["res_fmt_str"],
                        timeout = API["STEPPER"]["TIMEOUT"],
                        encryption = False
                    )
                # close connection to ignore spammed packets
                libcsp.close(conn)

        except BaseException as e:
            error_trace(e)
            continue

        return success, distance, faults

        
        