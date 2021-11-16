from . csp_macros import *
from . hackydeploy import deploy_procedure_payload

def deploy_payload_handler(conn, arm_flag):
    spam = 5
    while conn:
        try:
            data = csp_recv(
                conn=conn,
                fmt_str= API["DEPLOY"]["req_fmt_str"],
                timeout = API["DEPLOY"]["TIMEOUT"],
                encryption = True
            )
            if data == None:
                break
            
            deploy_flag = data[0]
            spam = data[1]
            # make sure data conforms to api standard, redundant error checking code
            assert type(data) == list
            assert len(data) == 2
            
            try:
                result = False
                if arm_flag:    result = deploy_procedure_payload()
            except libcsp.error as e:
                print(e)
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
                

            for i in range(spam):
                print(f"Sending Response Message {i+1}/{spam}")
                csp_send(
                    conn = conn,
                    data = [result, i+1],
                    fmt_str= API["DEPLOY"]["res_fmt_str"],
                    timeout = API["DEPLOY"]["TIMEOUT"],
                    encryption = False
                )
            
            libcsp.close(conn)
            return result

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