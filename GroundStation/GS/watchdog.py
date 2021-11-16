from . Telemetry4 import CDH
from . flags import COMMAND_HOLD, toggle
from . msgs import GLOBALQUEUE, store
import asyncio

class CommandScheduler:

    sat_available = False

    def __init__(self):
        pass

    async def check_orbit(self):
        # determine if the satellite is available for transmissions
        # sets sat_available flag
        pass

    def auto_ping(self):
        if COMMAND_HOLD: 
            print("Command Hold, Skipping")
            return
        toggle(COMMAND_HOLD)
        try:
            cmd = 1
            spam = 5
            res = CDH.binary_command_rpc(cmd=cmd, spam=spam)
            if res == None: return False
            store(res)
        except:
            print("Auto Ping Failed")
        toggle(COMMAND_HOLD)
        return res

    def auto_hk(self):
        if COMMAND_HOLD: 
            print("Command Hold, Skipping")
            return
        toggle(COMMAND_HOLD)
        try:
            cmd = 0
            spam = 5
            res = CDH.binary_command_rpc(cmd=cmd, spam=spam)
            if res == None: return 
            store(res)
        except:
            print("Automated House Keeping Failed")
        toggle(COMMAND_HOLD)
        return res

    def automated_telemetry():
        
        async def heart_beat():
            while True:
                                

                await asyncio.sleep(5 * 60**2)




    



