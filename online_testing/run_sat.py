import subprocess
import sys
import signal
import signal
import sys
import shlex
import threading
import os


control_system = subprocess.Popen(shlex.split("./controlsys.sh &")) 
satellite = subprocess.Popen(shlex.split("./sat.sh &"))

procs = [satellite]#, #control_system]

def signal_handler(sig, frame):
    for proc in procs: proc.terminate()
    print("Finished Testing")
    os.system("rm -rf /dev/shm/sem.fs-semaphore")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to end session')
signal.pause()
