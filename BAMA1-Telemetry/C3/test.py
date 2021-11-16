"""

Automated Testing Script to Fuzz/Validate Telemetry and Command Handling Software for Satellite and Ground Station

"""
import subprocess
import sys
import signal
import signal
import sys
import shlex
import threading

zmqproxy = subprocess.Popen("../libcsp/build/zmqproxy")
satellite = subprocess.Popen(shlex.split("xterm -hold -e ./satellite.sh"))
terminal = subprocess.Popen(shlex.split("xterm -hold -e ./testsuite.sh"))

procs = [zmqproxy, satellite, terminal]

def signal_handler(sig, frame):
    for proc in procs: proc.terminate()
    print("Finished Testing")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C to end session')
signal.pause()