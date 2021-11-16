#include <iostream>
#include <Eigen/Dense>
#include "hardware.hpp"
#include <memory>

using namespace Eigen;
using namespace std;


auto input = [](string prompt)
{
    string in;
    cout << "prompt";
    cin >> in;
    cout << endl;
    return stof(in);
};

int main(int argc, char* argv[])
{
    shared_ptr<hardware::MUX> mux = make_shared<hardware::MUX>(argv[1]);
    hardware::DRV8830 drv(mux, stoi(argv[2]), stoi(argv[3]));
    while (true) drv.VCMD(input("DRV8830"));
}
