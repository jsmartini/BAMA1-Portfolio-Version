#!/bin/bash

#export CC=clang++
export CC="g++"

echo "Building Simulation Software"
$CC -w bdot_testing.cpp -lzmq -lfmt  -I ../eigen-3.4.0 -lpthread --std=c++17 -o ../binaries/simdot
echo "\tFinished building Simulation Software with DRV8830 and config file"
$CC -w bdot_testing_x86.cpp -lzmq -lfmt -I ../eigen-3.4.0 -lpthread --std=c++17 -o ../binaries/simdotx86
echo "\tbuilding sim software BBB only full featured"
$CC -w bdot_testing_BBB_only.cpp -lzmq -lfmt -I ../eigen-3.4.0 -lpthread --std=c++17 -o ../binaries/simdot_bbb_o
echo "\tFinished building Simulation Software, x86 zmq test program"
echo "Building Production Software"
$CC -w bdot_production.cpp -lfmt -li2c -I ../eigen-3.4.0 -lpthread --std=c++17 -o ../binaries/bdot
echo "\tFinished building Production Software"
echo "Building Hardware Tests"
$CC -w drv8830_test.cpp -lfmt -li2c -lfmt -I ../eigen-3.4.0 --std=c++17 -o ../binaries/DRV8830Test
echo "\t Built DRV8830 Voltage Driver Test Program"
$CC -w mmc5883ma_test.cpp -lfmt -li2c -lfmt -I ../eigen-3.4.0 --std=c++17 -o ../binaries/MMC5883maTest
echo "\t Built MMC5883MA Magnetometer Test Program"
echo "FINISHED!"

