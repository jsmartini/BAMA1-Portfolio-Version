import libcsp_py3 as libcsp

"""

Initializes LIBCSP for connecting

"""



def startup_info():
    libcsp.route_start_task()
    print("Hostname: %s" % libcsp.get_hostname())
    print("Model:    %s" % libcsp.get_model())
    print("Revision: %s" % libcsp.get_revision())
    print("Routes:")
    libcsp.print_routes()

def zmq_can_init_sat(zmq_target="localhost"):
    libcsp.init(
            10,
            "BAMA-1 Satellite",
            "Testing Network Configuration",
            "1.2.3",
            10,
            500
        )
    libcsp.zmqhub_init(10, zmq_target)
    libcsp.can_socketcan_init("can0")
    libcsp.rtable_load("1/5 CAN, 4/5 CAN, 10/5 ZMQHUB, 16/5 ZMQHUB")
    startup_info()

def zmq_init_sat(zmq_target):
    libcsp.init(
            10,
            "BAMA-1 Satellite",
            "Testing Network Configuration",
            "1.2.3",
            10,
            500
        )

    libcsp.zmqhub_init(10, zmq_target)
    libcsp.rtable_load("0/0 ZMQHUB")
    startup_info()

def zmq_init_gs():
    hostname = "Ground Station CSP Command Line"
    purpose  = "Command Executor"

    csp_id = 2

    libcsp.init(csp_id, hostname, purpose , "1.2.3", 10, 300)
    libcsp.zmqhub_init(csp_id, "localhost")
    libcsp.rtable_set(0, 0, "ZMQHUB")
    startup_info()

def production_init_sat():
    libcsp.init(
            10,
            "BAMA-1 Satellite",
            "Testing Network Configuration",
            "1.2.3",
            10,
            500
        )
    libcsp.can_socketcan_init("can0")
    libcsp.rtable_load("0/0 CAN")
    startup_info()
