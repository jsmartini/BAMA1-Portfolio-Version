#include <iostream>
#include <Eigen/Dense>
#include "hardware.hpp"
#include <memory>

using namespace Eigen;
using namespace std;

auto log_data = [](Vector3d data)
{
    for (int i = 0; i < 3; i++) cout << data(i) << "\t";
    cout << endl;
};

int main(int argc, char* argv[])
{
    // ./exe /dev/i2c-# ch#
    shared_ptr<hardware::MUX> mux = make_shared<hardware::MUX>(argv[1]);     // initialize multiplexer
    hardware::MMC5883MA sensor(mux, stoi(argv[2]));
    while (true) log_data(sensor.read());
    return 0;
}