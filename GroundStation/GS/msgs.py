from queue import LifoQueue
from typing import MutableSequence
from  . util import *
global GLOBALQUEUE
import json

GLOBALQUEUE = LifoQueue(1024)

def store(msg):
    GLOBALQUEUE.put([TS(), msg])

import os

print(f"* Currently Operating in PATH: {os.getcwd()}")

global message_directory

try:

    os.mkdir("./archive")
    print("* Created Message Archive Directory in Current Directory")

except FileExistsError as e:
    print("* ./archive exists, moving on")

def archive():
    data = GLOBALQUEUE.get_nowait()
    if data == False: return
    with open(f"{data[0]}.json", 'w') as f:
        json.dump({
            "time": data[0],
            "data": data[1]
        }, f)
        f.close()


