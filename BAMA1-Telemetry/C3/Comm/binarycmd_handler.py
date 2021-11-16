from Comm.CDH import deploy_payload_rpc
from . config import *
import libcsp_py3 as libcsp
from . csp_macros import *
from . error import *
from . hackydeploy import remoteCLI # issue hk command
from . lock import LOCK
from . controlsystem import ADCSSystem

global BINCONFIG
BINCONFIG = API["BIN"]

from . hardware import *
from . controlsystem import *

def hk_parse(body:str):
    """
    Parses house keeping from EPS System

    God bless JupyterLab


    """

    tables = body.split("\r\n\r\n")
    print(tables)
    battery = tables[1]
    battery, MPPT = battery.split("\n\n")
    MPPT = [MPPT]
    battery_parsed = [i.split(":") for i in battery.split("\n")]
    battery_processed = [[i.strip() for i in j] for j in battery_parsed]
    voltage = float(battery_processed[1][1])
    input_i = float(battery_processed[2][1])
    MPPT.extend(tables[2:6])
    Upanels = MPPT[3].split("  ")
    for j in range(2): 
    # idk why remove doesnt fully work the first time
        for _ in Upanels: Upanels.remove('')
    Upanels = [float(i) for i in Upanels[1:]]
    charge = tables[7].split("\n")[1:4]
    charges = [i.split(":") for i in charge]
    charges = [float(i[1]) for i in charges[:-1]]
    power = tables[8:19]
    power_arrys = [l.split("      ") for l in power]
    for i, elm in enumerate(power_arrys): 
        if '' in elm:
            power_arrys[i].remove('')
    states = [int(i[1]) for i in power_arrys[2:]]
    AO33 = power_arrys[0][6]
    AO5 = power_arrys[1][6]
    
    return [voltage, input_i, *charges, *Upanels, *states]


def SystemInfo(system_state:dict, runtime_state:dict, spam:int):
    global ADCSSystem
    def get_uptime():
                                # SOURCE: https://stackoverflow.com/questions/42471475/fastest-way-to-get-system-uptime-in-python-in-linux
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        return uptime_seconds

    # system statuses
    stepper_distance = float(system_state["STEPPER"]["POSITION"])
    stepper_faults   = int(system_state["STEPPER"]["FAULTS"])
    reboots          = int(system_state["CYCLES"])
    deployed_payload = bool(system_state["PAYLOAD_DEPLOYED"])
    deployed_antenna = bool(system_state["ANTENNA_DEPLOYED"])


    # runtime status
    
    #try:
    #    response = remoteCLI(["hk"], "House Keeping - EPS")
    #   print(response)
    #    hk = hk_parse(response)
    #except BaseException as e:
    #    error_trace(e)
    #    # offline testing or error
    #    #sleep(60)
    hk = [0 for _ in range(17)]

    ARMED = bool(runtime_state["ARMED"])
    CTRL_OFF = bool(runtime_state["CTRL_OFF"])
    ADCS = bool(runtime_state["ADCS"])    

    uptime = float(get_uptime())

    LOCK.lock()
    bdot = runtime_state["ADCSSystem"].grab_bdot()
    if not runtime_state["CTRL_OFF"]:
        LOCK.unlock()

    system_state = [stepper_distance, stepper_faults, reboots, deployed_payload, deployed_antenna]
    runtime_state = [ARMED, CTRL_OFF, ADCS]


    payload = [*system_state, *runtime_state, uptime, *hk, *bdot]

    return payload

def Ping(spam:int):
    return ["BAMA-1 - RTR".encode(), spam]

def BDOT(runtime_dict:dict, spam:int):
    global ADCSSystem
    try:
        LOCK.lock()
        bdot = runtime_dict["ADCSSystem"].grab_bdot().append(spam)
        if runtime_dict["CTRL_OFF"]:
            return bdot
        LOCK.unlock()
        print(bdot)
        return bdot
    except:
        bdot = [-3,-3,-3, spam]
        if runtime_dict["CTRL_OFF"]:
            return bdot
        LOCK.unlock()
        print(bdot)
        return bdot

def CTRL_OFF(runtime_dict:dict, spam:int):
    print(runtime_dict["CTRL_OFF"])
    if not runtime_dict["CTRL_OFF"]:
        LOCK.lock()
    else:
        LOCK.unlock()
    runtime_dict["CTRL_OFF"] = not runtime_dict["CTRL_OFF"]
    print(runtime_dict["CTRL_OFF"])
    return [runtime_dict["CTRL_OFF"], spam]


def binary_command_handler(conn, system_state:dict, runtime_state:dict):
    # received the command and returns a struct serialized output from the command
    spam = 5
    try:

        data = csp_recv(
                conn = conn,
                fmt_str = BINCONFIG["req_fmt_str"],
                timeout = BINCONFIG["TIMEOUT"],
                encryption=False
            )
        print(data)

        cmd = data[0]
        spam = data[1]



        if cmd == BINCONFIG["SystemInfo"]["command_id"]:
            print("SYSTEMINFO QUERIED")
            data =SystemInfo(system_state, runtime_state, spam)
            for i in range(spam):
                csp_send(
                    conn = conn,
                    data = data,
                    fmt_str= BINCONFIG["SystemInfo"]["res_fmt_str"],
                    timeout = BINCONFIG["SystemInfo"]["TIMEOUT"],
                    encryption = False
                )
        elif cmd == BINCONFIG["PING"]["command_id"]:
            print("PING QUERIED")
            for i in range(spam):
                csp_send(
                    conn = conn,
                    data = Ping(spam),
                    fmt_str= BINCONFIG["PING"]["res_fmt_str"],
                    timeout = BINCONFIG["PING"]["TIMEOUT"],
                    encryption = False
                )
        elif cmd == BINCONFIG["BDOT"]["command_id"]:
            print("BDOT QUERIED")
            data = BDOT(runtime_state, spam)
            for i in range(spam):
                csp_send(
                    conn = conn,
                    data = data,
                    fmt_str= BINCONFIG["BDOT"]["res_fmt_str"],
                    timeout = BINCONFIG["BDOT"]["TIMEOUT"],
                    encryption = False
                )
        elif cmd == BINCONFIG["CTRL"]["command_id"]:
            print("CTRL TOGGLED")
            data = CTRL_OFF(runtime_state, spam)
            for i in range(spam):
                csp_send(
                    conn = conn,
                    data = data ,
                    fmt_str= BINCONFIG["CTRL"]["res_fmt_str"],
                    timeout = BINCONFIG["CTRL"]["TIMEOUT"],
                    encryption = False
                )
        else:
            # jump to error handling in exception clause
            raise BaseException("Invalid Binary Command")
        libcsp.close(conn)

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




if __name__ == "__main__":
    pass