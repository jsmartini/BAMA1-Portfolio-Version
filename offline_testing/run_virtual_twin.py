import subprocess
import sys
import signal
import signal
import sys
import shlex
import threading
import os



simulator = subprocess.Popen(shlex.split("xterm -hold -e ./sim.sh"))
control_system = subprocess.Popen(shlex.split("xterm -hold -e ./controlsys.sh")) 
zmqproxy = subprocess.Popen(shlex.split("xterm -hold -e ./zmqproxy.sh"))
satellite = subprocess.Popen(shlex.split("xterm -hold -e ./sat.sh"))
terminal = subprocess.Popen(shlex.split("xterm -hold -e ./testsuite.sh"))


procs = [zmqproxy, satellite,]# terminal]

def signal_handler(sig, frame):
    for proc in procs: proc.terminate()
    print("Finished Testing")
    os.system("rm -rf /dev/shm/sem.fs-semaphore")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to end session')
signal.pause()
