#include <iostream>
#include <vector>


using namespace std;

const std::vector<double> voltages = {0.48, 0.56, 0.64, 0.72, 0.8, 0.88, 0.96, 1.04, 1.12, 1.2, 1.29, 1.37, 1.45, 1.53, 1.61, 1.69, 1.77, 1.85, 1.93, 2.01, 2.09, 2.17, 2.25, 2.33, 2.41, 2.49, 2.57, 2.65, 2.73, 2.81, 2.89, 2.97, 3.05, 3.13, 3.21, 3.29, 3.37, 3.45, 3.53, 3.61, 3.69, 3.77, 3.86, 3.94, 4.02, 4.1, 4.18, 4.26, 4.34, 4.42, 4.5, 4.58, 4.66, 4.74, 4.82, 4.9, 4.98, 5.06};
const std::vector<uint8_t> values   = {0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f};

template<typename T>
unsigned bsearch(vector<T> arry, T value, unsigned lower_bound, unsigned upper_bound)
{
    unsigned mdpt = (int) (upper_bound + lower_bound) / 2;
    if (value > arry.at(mdpt) && upper_bound - lower_bound > 2)         return bsearch(arry, value, mdpt, upper_bound);
    else if (value < arry.at(mdpt) && upper_bound - lower_bound > 2)    return bsearch(arry, value, lower_bound, mdpt);
    else                                                                return mdpt;
};

int main(int argc, char* argv[])
{
    unsigned idx = bsearch<double>(voltages, std::stof(argv[1]), 0 ,58);
    cout << "Voltage Requiired: " << voltages.at(idx) << "\tRegister Value\t" << +values.at(idx) << endl;
    return 0;
}