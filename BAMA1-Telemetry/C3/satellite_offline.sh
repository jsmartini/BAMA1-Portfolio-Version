#!/bin/bash


build="../libcsp/build"

echo $(pwd)

csprun="LD_LIBRARY_PATH=${build} PYTHONPATH=${build} python3"

eval $csprun Sat.py --offlinetesting 
