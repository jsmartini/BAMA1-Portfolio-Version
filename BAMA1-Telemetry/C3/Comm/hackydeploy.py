import time
from  . csp_macros import *
from time import sleep

# copy pasted from the second iteration
# that is why the nested class is here

# hacky deploy uses remote cli over CAN to execute output channel commands
# Nano Avionics Botched Documenmtation on Bianry Commands so here we are
class NA_API:


    class NA_Shared:
        # services shared across Nano Avionics Products

        class RemoteCLI:
            csp_service_port = 13
            RequestPktFmt = "<H128p"		# EPS only (pascal string padded array
            cspReq_fmt_1 = lambda s: f"<H{len(s)}s"	# UHF only (variable string)
            SerializeReq = lambda s: struct.pack(RequestPktFmt, f" {s}")
            cspRes_fmt_pre = "<BB?"
            DeserializeRes = lambda data: f"<BBB{len(data) - struct.calcsize(NA_API.NA_Shared.RemoteCLI.cspRes_fmt_pre)}s"
            
            @staticmethod
            def assemble_response(conn, timeout_cnt = 5, timeout_ms=2000):
                response_string = ""
                while True:
                    info("waiting for the next packet")
                    pkt = libcsp.read(conn, timeout_ms)
                    if pkt == None:
                        timeout_cnt -= 1
                        if timeout_cnt == 0:
                            break
                        continue
                    timeout_cnt = 5
                    info(pkt)
                    data = libcsp.packet_get_data(pkt)
                    error_code, is_final, packet_id, msg = struct.unpack(NA_API.NA_Shared.RemoteCLI.DeserializeRes(data), data)
                    log(f"{error_code} {packet_id} {is_final}")
                    response_string += msg.decode("ascii")
                    if is_final:
                        break
                if len(response_string) == 0: error("RemoteCLI Timed Out")
                return response_string


def deploy_remoteCLI(sequence, msg):
    time_out = 2 * 60 * 1000
    errors = 0
    try:

        print("CMP ident:", libcsp.cmp_ident(4))
        print("Ping: %d mS" % libcsp.ping(4))

        conn = connect(
            4,
            NA_API.NA_Shared.RemoteCLI.csp_service_port
        )
        for cmd in sequence:
            cmd = cmd + "\r\n"
            data = bytearray(struct.pack(NA_API.NA_Shared.RemoteCLI.RequestPktFmt, 2, cmd.encode()))
            info(data)
            pkt = libcsp.buffer_get(1)
            libcsp.packet_set_data(pkt ,data)
            libcsp.send(conn, pkt)
            libcsp.buffer_free(pkt)
            res = NA_API.NA_Shared.RemoteCLI.assemble_response(conn,timeout_cnt=3, timeout_ms=1000)
            info(res)
            if '\x01OK\r\nEPS>' != res:
                error(f"{msg} failed to deploy")
                errors += 1
                continue

            sleep(1)
            log (f"{msg} deployed successfully . . . ")
        return True if errors == 0 else False

    except BaseException as e:
        print(e)
        error(f"{msg} failed to deploy . . .")
        return False

def deploy_procedure_antenna():
    sequence = [
        # sequence goes here
    ]
    print("Running Sequence: 5 second buffer")
    print(sequence)
    sleep(5)
    #return deploy_remoteCLI(sequence, "Antennas")
    return False

def deploy_procedure_payload():
    sequence = [
        # sequence goes here
    ]
    print("Running Sequence: 5 second buffer")
    print(sequence)
    sleep(5)
    #return deploy_remoteCLI(sequence, "Payload")
    return False

def remoteCLI(sequence, msg):
    time_out = 2 * 60 * 1000
    errors = 0
    try:

        print("CMP ident:", libcsp.cmp_ident(4))
        print("Ping: %d mS" % libcsp.ping(4))

        conn = connect(
            4,
            NA_API.NA_Shared.RemoteCLI.csp_service_port
        )
        for cmd in sequence:
            cmd = cmd + "\r\n"
            data = bytearray(struct.pack(NA_API.NA_Shared.RemoteCLI.RequestPktFmt, 2, cmd.encode()))
            info(data)
            pkt = libcsp.buffer_get(1)
            libcsp.packet_set_data(pkt ,data)
            libcsp.send(conn, pkt)
            libcsp.buffer_free(pkt)
            res = NA_API.NA_Shared.RemoteCLI.assemble_response(conn,timeout_cnt=3, timeout_ms=1000)
            info(res)
            print(repr(res))
            if '\r\nOK\r\nEPS>' != res[:-5]:
                error(f"{msg} failed to deploy")
                errors += 1
                continue

            sleep(1)
            log (f"{msg} deployed successfully . . . ")
        return res 

    except BaseException as e:
        print(e)
        error(f"{msg} failed to deploy . . .")
        return False