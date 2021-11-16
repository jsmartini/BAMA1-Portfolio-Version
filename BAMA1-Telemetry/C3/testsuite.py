import libcsp_py3 as libcsp
from Comm import CDH
from time import sleep
from Comm.config import *
from Comm.clogging import *

TEST = lambda testname: info("="* 10 + str(testname) + "="*10)
PASS = lambda testname: log("".join(["="*10, "PASS " , testname , "="*10]))
FAIL = lambda testname: error("".join(["="*10, "FAIL " , testname , "="*10]))
VALIDATE = lambda function_res, API_ref: PASS(str(API_ref) + str(function_res)) if function_res != None and function_res != -1 else FAIL(str(API_ref) + f" {function_res}")

def VALIDATE2(function_res, API_ref, check_output = False, correct_output = None):
    if not check_output:
        VALIDATE(function_res, API_ref)
    else:
        if function_res != correct_output:
            error(f"{API_ref}: Failed with Response :{function_res}")
        else:
            log(f"{API_ref} Passed Test")

print("*"*20 + "CONFIGURATION" + "*"*20 )
print(CONFIG)
print("*"*20 + "API" + "*"*20 )
print(API)
from time import sleep
def test_suite():
    hostname = "Ground Station RPC"
    purpose  = "Command Executor"

    csp_id = 2
    sleep(10)
    libcsp.init(csp_id, hostname, purpose , "1.2.3", 10, 300)
    libcsp.zmqhub_init(csp_id, "localhost")
    libcsp.rtable_set(0, 0, "ZMQHUB")
    libcsp.route_start_task()
    print("Hostname: %s" % libcsp.get_hostname())
    print("Model:    %s" % libcsp.get_model())
    print("Revision: %s" % libcsp.get_revision())
    print("Routes:")
    libcsp.print_routes()
    sleep(4)

    TEST("Stepper Motor Driver")
    VALIDATE(CDH.stepper_rpc(10, 1, 5), "Stepper Motor")
    sleep(1)
    TEST("ARM Payload - Failure Case")
    VALIDATE(CDH.arm_payload_rpc("bad pass", 5), "ARM Payload Failure")
    sleep(1)
    TEST("Deploy Payload - Failure Case")
    VALIDATE(CDH.deploy_payload_rpc(True, 5), "Deploy Payload Failure")
    sleep(1)
    TEST("ARM Payload - Successful Case")
    VALIDATE(CDH.arm_payload_rpc(CONFIG["ARM"]["password"], 5), "ARM Payload")
    sleep(1)
    TEST("Deploy Payload - Successful Case - Offline")
    VALIDATE2(CDH.deploy_payload_rpc(True, 5)[0], "Deploy Payload", check_output=True, correct_output=False)
    
    sleep(1)
    TEST("BINARY COMMANDS SystemInfo")
    VALIDATE(CDH.binary_command_rpc(0, 5), "SystemInfo")
    sleep(1)
    TEST("BINARY COMMANDS Ping")
    VALIDATE(CDH.binary_command_rpc(1, 5), "Ping")
    sleep(1)
    TEST("BINARY COMMANDS BDOT")
    VALIDATE(CDH.binary_command_rpc(2, 5), "BDOT")
    sleep(1)
    TEST("BINARY COMMANDS CTRL OFF")
    VALIDATE(CDH.binary_command_rpc(3, 5), "CTRL OFF")
    TEST("BINARY COMMANDS CTRL ON")
    VALIDATE(CDH.binary_command_rpc(3, 5), "CTRL ON")

if __name__ == "__main__":
    test_suite()
