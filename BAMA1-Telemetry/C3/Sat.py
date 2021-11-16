
import os
from Comm.deploy_payload_handler import deploy_payload_handler

from Comm.hackydeploy import deploy_procedure_antenna

print(f"Operating Directory: {os.getcwd()}")

import libcsp_py3 as libcsp

from Comm import stepper_handler
from Comm import arm_payload_handler
from Comm import binary_command_handler
from Comm.csp_macros import *
from Comm import csp_init
from Comm import statedict
from Comm import config
from Comm.controlsystem import ADCSInterface, SimADCSInterface, ADCSSystem
from Comm.binarycmd_handler import binary_command_handler

import argparse
global ARGS

def parse_args():
    parser = argparse.ArgumentParser("BAMA-1 Satellite C&DH Program")
    parser.add_argument("--offlinetesting", help="Only use the ZMQ Interface for Testing", action="store_true")
    parser.add_argument("--zmq", help="zmq target", default="localhost")
    parser.add_argument("--onlinetesting", help="Use ZMQ and CAN Interface", action="store_true")
    parser.add_argument("--mission", help="Use Mission Hardware Configuration", action="store_true")
    return parser.parse_args()

def server(sim_flag):

    # load and update the permanent state dict
    mission_state_dict = statedict.load_statedict()
    mission_state_dict["CYCLES"] += 1
    if not mission_state_dict["ANTENNA_DEPLOYED"]:
        mission_state_dict["ANTENNA_DEPLOYED"] = deploy_procedure_antenna()
    statedict.update_statedict(mission_state_dict)

    sck = libcsp.socket()
    libcsp.bind(sck, libcsp.CSP_ANY)
    libcsp.listen(sck, 5)

    while True:
        
        mission_state_dict = statedict.update_statedict(mission_state_dict)
        print("Waiting for new Connection")
        conn = libcsp.accept(sck, libcsp.CSP_MAX_TIMEOUT)

        if not conn: 
            print("Bad Connection")
            continue

        target_service = service(conn)
            
        if target_service == API["DEPLOY"]["csp_service_id"]:
            mission_state_dict["PAYLOAD_DEPLOYED"] = deploy_payload_handler(conn, RUNTIME_STATES["ARMED"])
        elif target_service == API["ARM"]["csp_service_id"]:
            RUNTIME_STATES["ARMED"] = arm_payload_handler(conn)
        elif target_service == API["STEPPER"]["csp_service_id"]:
            success, distance, faults = stepper_handler(conn, sim_flag=sim_flag)
            print(f"Stepper RPC Call Results: Success: {'great' if success else 'fail'} {distance}mm faults:{faults}")
            if success:
                mission_state_dict["STEPPER"]["POSITION"] += distance
                mission_state_dict["STEPPER"]["FAULTS"] += faults
        elif target_service == API["BIN"]["csp_service_id"]:
            binary_command_handler(conn, mission_state_dict, RUNTIME_STATES)

if __name__ == "__main__":
    ARGS = parse_args()
    print(f"ARGS:\n\n{ARGS}")
    hardware_sim_flag = False
    if ARGS.offlinetesting:
        # testing functionalities with bullshit hardware input
        csp_init.zmq_init_sat(ARGS.zmq)
        hardware_sim_flag = True
    elif ARGS.onlinetesting:
        # testing functionalities with real hardware through ethernet radio simulation routing configuration
        csp_init.zmq_can_init_sat(ARGS.zmq)
    elif ARGS.mission:
        # testng actual satellite
        csp_init.production_init_sat()

    if ARGS.mission or ARGS.onlinetesting:
        # allow hardware access to ADCS Components
        RUNTIME_STATES["ADCS"] = True  
    
    if RUNTIME_STATES["ADCS"]: 
        print("Using Real Hardware ADCSInterface")
        RUNTIME_STATES["ADCSSystem"] = ADCSInterface()
    else: 
        print("Using Fake ADCSInterface")
        RUNTIME_STATES["ADCSSystem"] = SimADCSInterface()


    # run server loop
    server(hardware_sim_flag)
    

    