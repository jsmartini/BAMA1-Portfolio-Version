global COMMAND_HOLD
global WATCHDOG_TIMING_HK           # Seconds
global WATCHDOG_TIMING_PING         # Seconds

COMMAND_HOLD = False
WATCH_TIMING_HK = 60**2
WATCH_TIMING_PING = 60**2

def toggle(flag):
    if flag: flag = False
    else: flag = True
    

