import libcsp_py3 as libcsp


def cspinit(can=False):
    from time import sleep
    hostname = "Ground Station RPC"
    purpose  = "Command Executor"

    csp_id = 16

    libcsp.init(csp_id, hostname, purpose , "1.2.3", 10, 300)
    if not can:
        libcsp.zmqhub_init(csp_id, "localhost")
        libcsp.rtable_set(0, 0, "ZMQHUB")
    else:
        libcsp.can_socketcan_init("vcan0")
        libcsp.rtable_set(0, 0, "CAN")
    libcsp.route_start_task()
    print("Hostname: %s" % libcsp.get_hostname())
    print("Model:    %s" % libcsp.get_model())
    print("Revision: %s" % libcsp.get_revision())
    print("Routes:")
    libcsp.print_routes()
    sleep(4)
    print("CSP Networking Initialized Successfully")
    
    