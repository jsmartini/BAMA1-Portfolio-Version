import subprocess
import sys
import signal
import signal
import sys
import shlex
import threading
import os


gs = subprocess.Popen(shlex.split("xterm -hold -e ./cli.sh")) 
hil = subprocess.Popen(shlex.split("xterm -hold -e ./sim.sh"))
zmq = subprocess.Popen(shlex.split("xterm -hold -e ./zmqproxy.sh"))

procs = [hil, gs]


def signal_handler(sig, frame):
    for proc in procs: proc.terminate()
    print("Finished Testing")
    os.system("rm -rf /dev/shm/sem.fs-semaphore")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to end session')
signal.pause()
