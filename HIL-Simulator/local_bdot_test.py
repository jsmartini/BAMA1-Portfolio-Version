import scipy as sci
import scipy.integrate
import matplotlib.pyplot as plt
import numpy as np
import zmq
import pyIGRF
import json

from zmq.error import ZMQError
from log import * 
from datetime import timedelta
from colorama import Fore
import ast
from time import sleep

from posix_ipc import *
import sys

global BDOTSemaphore 
BDOTSemaphore = Semaphore(name="/iceman", flags=O_CREAT)

norm = lambda *args: np.sqrt(np.sum([np.power(i, 2) for i in args]))

parse_arg = lambda key, default, argdict: default if key not in argdict.keys() else argdict[key]

def setup_simulation_client(argdict: dict):
    target = parse_arg("target", "127.0.0.1", argdict)
    port   = parse_arg("port", 7777, argdict)
    ctx = zmq.Context()
    skt = ctx.socket(zmq.REQ)
    try:
        info(f"Connecting to Simulator Server on {target}:{port}")
        skt.connect(f"tcp://{target}:{port}")
        info(f"Connection Successful")
    except Exception as e:
        critical(f"Could not connect to {target}:{port}\n\t{e}")
        exit(-1)
    return skt, ctx
    
class bdot:

    def __init__(self, **kwargs):
        self.gains = kwargs['gains']
        self.time_step = kwargs['time_step']
        self.last_reading = np.zeros(3)
        self.max = np.diag([0.1, 0.1, 0.1])
        if kwargs["sim"]:
            self.skt, self.ctx = setup_simulation_client(kwargs)

    def __call__(self, reading):
        bdot = (self.last_reading - reading)/self.time_step
        bdot_normed = bdot/norm(*bdot.tolist())
        requested_mag_moment = np.matmul(-self.gains,bdot_normed)
        requested_torque = np.cross(requested_mag_moment, reading)
        self.last_reading = reading
        return requested_mag_moment, requested_torque

    def run_simulation(self):
        global BDOTSemaphore
        while 1:
            try:
                self.skt.send_string("next")
            except ZMQError as e:
                critical("Crashed on Send next flag")
                print(e)
                exit(-1)
            
            pkt = json.loads(self.skt.recv_string())
            reading, time_c = pkt["data"], pkt["time"]
            if BDOTSemaphore.value == 0:
                reading = np.array(reading)
                #update(time_c, reading, color = Fore.BLUE, units="Gauss")
                mag_moment, torque = self(reading)
                #update(time_c, mag_moment, color = Fore.CYAN, units="Am^2")
                #update(time_c, torque, color=Fore.MAGENTA, units="Nm")
            else:
                # set variables to 0 so the REP/REQ process is not interrupted by semaphore lock
                torque = np.zeros(3)
                mag_moment = np.zeros(3)
                info("I2C Semaphore Lock Detected, Paused BDOT Control System")
            print("MAGNETIC MOMENT")
            print(mag_moment)
            self.skt.send_string(json.dumps({"torque":torque.tolist(), "mag_moment":mag_moment.tolist()}))
            ack = self.skt.recv_string()
            assert ack == "ACK"
            
    def run_hardware(self):
        pass

if __name__ == '__main__':
    gains = [0.3, 0.23, 0.23]
    controller = bdot(gains=np.diag(gains), time_step=0.1, sim=True)
    controller.run_simulation()
