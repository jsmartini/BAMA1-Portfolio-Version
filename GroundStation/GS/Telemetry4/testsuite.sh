#!/bin/bash


build="../libcsp/build"

csprun="LD_LIBRARY_PATH=${build} PYTHONPATH=${build} python3"

eval $csprun testsuite.py

