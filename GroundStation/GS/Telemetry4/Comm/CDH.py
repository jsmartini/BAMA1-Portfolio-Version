from . config import *
from . csp_macros import *
from . security import *
from . error import *
from time import sleep, time

global MBM2_ID

MBM2_ID = 10

def stepper_rpc(distance:float, brake: bool, spam: int):
    conn = connect(MBM2_ID, API["STEPPER"]["csp_service_id"])
    csp_send(
        conn = conn,
        data = [distance, brake, spam],
        fmt_str = API["STEPPER"]["req_fmt_str"],
        timeout = API["STEPPER"]["TIMEOUT"],
        encryption = True
    )
     
    return csp_recv(
        conn = conn,
        fmt_str = API["STEPPER"]["res_fmt_str"],
        timeout = API["STEPPER"]["TIMEOUT"],
        encryption = False
    )

def arm_payload_rpc(password, spam: int):
    conn = connect(MBM2_ID, API["ARM"]["csp_service_id"])
    csp_send(
        conn = conn,
        data = [password.encode(), spam],
        fmt_str = API["ARM"]["req_fmt_str"],
        timeout = API["ARM"]["TIMEOUT"],
        encryption = True
    )

    return csp_recv(
        conn = conn,
        fmt_str = API["ARM"]["res_fmt_str"],
        timeout = API["ARM"]["TIMEOUT"],
        encryption = False
    )

def deploy_payload_rpc(flag:bool, spam:int):
    conn = connect(MBM2_ID, API["DEPLOY"]["csp_service_id"])
    csp_send(
        conn = conn,
        data = [flag, spam],
        fmt_str = API["DEPLOY"]["req_fmt_str"],
        timeout = API["DEPLOY"]["TIMEOUT"],
        encryption=True
    )
    return csp_recv(
        conn = conn,
        fmt_str = API["DEPLOY"]["res_fmt_str"],
        timeout = API["DEPLOY"]["TIMEOUT"],
        encryption = False
    )

# run once, no need to waste compute
BIN = API["BIN"]
cmd_idx = [[BIN[cmd_i]["res_fmt_str"], BIN[cmd_i]["TIMEOUT"]] for cmd_i in list(BIN.keys())[3:]]

def binary_command_rpc(cmd:int, spam:int):
    conn = connect(MBM2_ID, API["BIN"]["csp_service_id"])
    csp_send(
        conn = conn,
        data = [cmd, spam],
        fmt_str = API["BIN"]["req_fmt_str"],
        timeout = API["BIN"]["TIMEOUT"],
        encryption=False
    )

    fmt_str = cmd_idx[cmd][0]
    timeout = cmd_idx[cmd][1]

    return csp_recv(
        conn = conn,
        fmt_str = fmt_str,
        timeout = timeout,
        encryption = False
    )