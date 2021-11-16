from enum import Enum


class RTables(Enum):
    # 5-bit CIDR Format
    # read the documentation for LIBCSP
    testing_mbm2 = "3/1 CAN, 16 ZMQHUB 10, 10 ZMQHUB 16"
    testing_groundstation = "0/0 ZMQHUB"
    production_mbm2 = "0/0 CAN"

    
