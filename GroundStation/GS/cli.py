from cmd import Cmd
from datetime import datetime
from  . Telemetry4.Comm import CDH
from  . msgs import store
from  . flags import COMMAND_HOLD, toggle
import libcsp_py3 as libcsp

def print_success_response(res):
    print("== Successfully Received Response ==")
    for item in res:
        print(f"\t {item}")
    print("== End RPC Session")

def print_error_response():
    print("== Error == \n\t: No Packet Receieved or Timeout Occured")
    print("== End RPC Session")

class BAMA1Cli(Cmd):

    prompt = "UASpaceCLI>"

    def do_arm(self, line):
        line = line.split()
        if COMMAND_HOLD: 
            print("Command Hold Activated, Skipping")
            return
        toggle(COMMAND_HOLD)
        try:
            passwd = line[0]
            spam   = int(line[1])
            res = CDH.arm_payload_rpc(password=passwd, spam=spam)
            if res == None: print_error_response()
            else: print_success_response(res)
            store(res)
        except:
            print("Bad Input or Failure")
            print("ARM PAYLOAD:\nUSAGE\t arm <PASSWORD> <SPAM #>")
        toggle(COMMAND_HOLD)

    def do_stepper(self, line):
        line = line.split()
        if COMMAND_HOLD: 
            print("Command Hold, Skipping")
            return
        toggle(COMMAND_HOLD)
        try:
            distance = float(line[0])
            brake    = int(line[1])
            spam     = int(line[2])
            res = CDH.stepper_rpc(distance=distance, brake=brake, spam=spam)
            if res == None: print_error_response()
            else: print_success_response(res)
            store(res)
        except:
            print("Bad Input or Failure")
            print("Stepper Deployment:\nUSAGE\t stepper <distance float> <direction 0/1> <SPAM #>")
        toggle(COMMAND_HOLD)

    def do_deploy(self, line):
        line = line.split()
        if COMMAND_HOLD: 
            print("Command Hold, Skipping")
            return
        toggle(COMMAND_HOLD)
        try:
            flag = bool(line[0])
            spam     = int(line[1])
            res = CDH.deploy_payload_rpc(flag=flag, spam=spam)
            if res == None: print_error_response()
            else: print_success_response(res)
            store(res)
        except:
            print("Bad Input or Failure")
            print("Payload Deployment:\nUSAGE\t deploy <flag bool> <SPAM #>")
        toggle(COMMAND_HOLD)

    def do_bincmd(self, line):
        line = line.split()
        if COMMAND_HOLD: 
            print("Command Hold, Skipping")
            return
        toggle(COMMAND_HOLD)
        try:
            cmd = int(line[0])
            spam     = int(line[1])
            res = CDH.binary_command_rpc(cmd=cmd, spam=spam)
            if res == None: print_error_response()
            else: print_success_response(res)
            store(res)
        except BaseException as e:
            print(e)
            print(line)
            print("Bad Input or Failure")
            print("Binary Command:\nUSAGE\t bincmd <cmd id#> <SPAM #>")
        toggle(COMMAND_HOLD)


    

        

        


    