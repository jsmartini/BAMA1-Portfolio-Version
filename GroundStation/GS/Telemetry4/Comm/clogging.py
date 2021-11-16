from colorama import Fore, Back, Style
import os
width = lambda: os.get_terminal_size().columns

def log(msg, level=0): 
    msg = str(msg)
    payload = "\t" * level+ "[##] " + msg
    padding = width() - len(payload)
    print(Fore.BLUE + Back.GREEN + Style.DIM + payload + " "*padding + Style.RESET_ALL)
def error(msg, level=0):
    msg = str(msg)
    payload = "\t" * level + "[!!] " + msg
    padding = width() - len(payload)
    print(Fore.BLUE + Back.RED + payload + " "*padding + Style.RESET_ALL)
def info(msg, level= 0):
    msg = str(msg)
    payload = "\t" * level + "[++] " + msg
    padding = width() - len(payload) 
    print(Fore.BLUE + Back.YELLOW + payload + " "*padding + Style.RESET_ALL) 



if __name__ == "__main__":
    log("Works")
    error("Fail")
    info("eh")
