import posix_ipc

global DEFAULTLOCKNAME

# system wide sempahore lock in /dev/shm
DEFAULTLOCKNAME = "/fs-semaphore"

global LOCKED_FLAG

class LCK:
    # lock class that wraps posix_ipc python3 api for semaphores
    def __init__(self, name = DEFAULTLOCKNAME):
        self.sem = posix_ipc.Semaphore(name, posix_ipc.O_CREAT, initial_value=1)
        self.name = name

    def lock(self):
        global LOCKED_FLAG
        LOCKED_FLAG = True
        print(f"Locking {self.name}")
        self.sem.acquire()
        print("\tLocked")

    def unlock(self):
        global LOCKED_FLAG
        LOCKED_FLAG = False
        print(f"Unlocking {self.name}")
        self.sem.release()
        print(f"\tUnlocked {self.name}")

    def __del__(self):
        self.sem.close()
        print(f"{self.name} Semaphore Closed")

global LOCK
LOCK = LCK()

from time import sleep
if __name__ == "__main__":
    lck = LOCK
    lck.lock()
    sleep(5)
    lck.unlock()
    del lck
