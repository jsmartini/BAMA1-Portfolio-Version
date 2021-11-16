from GS import *
import asyncio
import threading
import signal
from progress.bar import ChargingBar as Bar

async def run_cli(loop):
    pass


async def run_watchdog(loop):
    pass

cli_loop = asyncio.new_event_loop()
wg_loop = asyncio.new_event_loop()

cli = threading.Thread(target=run_cli, args=(cli_loop,))
wg  = threading.Thread(target=run_watchdog, args=(wg_loop,))

cli.start()
wg.start()

def ctrlc(signum, frame):
    print("CTRL+C Detected, Exiting . . .")
    with Bar("Saving Transmissions", max=len(GLOBALQUEUE)) as b:
        for m in GLOBALQUEUE:
            b.next()
            archive(m)
        b.finish()
    cli.join()
    wg.join()
    print("BYE!")

signal.signal(signal.SIGINT, ctrlc)
print("Press CTRL+C to Save and Exit Program")
signal.pause()

