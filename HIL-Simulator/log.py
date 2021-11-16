from colorama import init, Fore, Back, Style
import json
import datetime
import numpy as np

np.set_printoptions(precision=3)

TS = lambda: datetime.datetime.now()
datafmt = lambda s: s.tolist()

global LEVEL
LEVEL = "info"
init(autoreset=True)

def log(**kwargs):
    global LEVEL
    text = kwargs["text"]
    level = kwargs["level"]
    if level == LEVEL or "all":         print(Fore.GREEN + f"[{TS()}]\t" + Style.RESET_ALL + text)
    elif level == LEVEL or "all":      print(Fore.YELLOW + f"[{TS()}]\t"  + text + Style.RESET_ALL)
    elif level == "critical":   print(Fore.RED + f"[{TS()}]\t" +  text + Style.RESET_ALL)

info = lambda text: log(text = text, level="info")
debug = lambda text: log(text = text, level="debug")
critical = lambda text: log(text = text, level="critical")
update = lambda time, data, color, units: print(color+ f"[{time}] {data} | {units}")

