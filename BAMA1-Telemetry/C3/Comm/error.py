import traceback
import inspect


get_fail_point = lambda: inspect.currentframe().f_back.f_code.co_name

def error_trace(e):
    print("==="*6 + "Traceback Execution")
    traceback.print_exc()

def error(msg):
    print(msg)

def info(msg):
    print(msg)

def log(msg):
    print(msg)