#!/bin/bash


build="../libcsp/build"

csprun="LD_LIBRARY_PATH=${build} PYTHONPATH=${build} python3"

eval $csprun Sat.py --onlinetesting --zmq 10.42.0.1
