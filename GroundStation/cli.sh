#!/bin/bash
build="../BAMA1-Telemetry/libcsp/build"

csprun="LD_LIBRARY_PATH=${build} PYTHONPATH=${build} python3"

eval $csprun cli.py
