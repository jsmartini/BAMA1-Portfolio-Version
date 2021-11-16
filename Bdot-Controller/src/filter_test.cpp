#include "sensor.hpp"
#include <Eigen/Dense>
#include "hardware.hpp"
#include <memory>
#include <vector>
#include <deque>

using namespace Eigen;
using namespace std;

class test_sensor_data
    {
        public:
            test_sensor_data(){};
            Vector3d read(){return Vector3d::Random();};
    };

int main(int argc, char* argv[])
{
    

    hardware::HardwareDevices<test_sensor_data> data_ptr;
    SensorInput::calibration cal;
    SensorInput::weights w;

    for (int i = 0; i < 3; i++)
    {
        data_ptr.push_back(make_shared<test_sensor_data>());
        cal.push_back(Matrix3d::Random());
        w.push_back(0.333);
    }

    SensorInput::HardwareSensorInput<test_sensor_data> filter(data_ptr, cal, w);
    data_ptr.at(0)->read();

    while (1)
    {
        cout << "============================" << endl;
        cout << filter.read() << endl;
    }

}