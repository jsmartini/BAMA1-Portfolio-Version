import subprocess
import sys
import signal
import signal
import sys
import shlex
import threading
import os
from time import sleep

if os.geteuid() != 0:
    print("this should be root .  . . !")
    exit(-1)

control_system = subprocess.Popen(shlex.split("./controlsys.sh &")) 
satellite = subprocess.Popen(shlex.split("./sat.sh &"))

procs = [satellite, control_system]

def signal_handler(sig, frame):
    for proc in procs: proc.terminate()
    print("Finished Testing")
    os.system("rm -rf /dev/shm/sem.fs-semaphore")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to end session')

while 1:
    sleep(30)       # every 30 seconds check proc statuses

    for proc in procs: 
        if proc.poll() != None:
            for process in procs:           # kill other scripts if other processes fail and start restart process
                try: process.terminate()
                except BaseException as e: pass
            print("Failure Detected, processes killed, starting reboot")
            sleep(5*60)# sleep 5 minutes so we have time to ssh in and fix issues if debugging mission application
            os.system("reboot -d")





