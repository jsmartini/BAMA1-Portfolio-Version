#include "sensor.hpp"
#include "bdot.hpp"
#include "semaphore.hpp"
#include "hardware.hpp"
#include <Eigen/Dense>
#include <iostream>
#include <vector>
#include <string>
#include <cpptoml.h>
#include <unistd.h>
#define FMT_HEADER_ONLY         // other local headers reference fmt, we want the header only version

using namespace std;
using namespace Eigen;


auto load_mat_toml = [](cpptoml::table& table, string key)
{
    Matrix3d mat;
    auto vals = table.get_array_of<double>(key);
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) mat(i,j) = vals->at(i*3 + j);    
    return mat;
};

int main(int argc, char* argv[])
{
    auto cfg = cpptoml::parse_file(argv[1]);
    cout << "parsed" << endl;
    auto mmc_cfg = cfg->get_table("MMC5883MA");
    auto drv_cfg = cfg->get_table("DRV8830");
    cout << "Got hardware tables" << endl;
    auto mux_dir = cfg->get_table("MUX")->get_as<string>("MUX");
    cout << "arry" << endl;
    auto gains_cfg = cfg->get_table("GAINS")->get_qualified_array_of<double>("xyz");
    auto cal_cfg = cfg->get_table("CALIBRATION");
    auto w_cfg = cfg->get_table("FILTERWEIGHT");
    cout << "Loaded Configuration File Successfully" << endl;
    std::shared_ptr<hardware::MUX> mux = std::make_shared<hardware::MUX>(mux_dir->c_str());
    cout << "Loaded I2C Multiplexer Successfully" << endl;
    std::shared_ptr<Locks::SemaphoreLock> lock_ptr = std::make_shared<Locks::SemaphoreLock>(DEFAULT_LOCK_NAME);
    cout << "Initialized Semaphore Lock on:\t" << DEFAULT_LOCK_NAME << endl;
    hardware::HardwareDevices<hardware::DRV8830> drivers_ptr;
    cout << "Initialized Hardware Drivers for DRV8830" << endl;
    hardware::HardwareDevices<hardware::MMC5883MA> sensors_ptr;
    cout << "Initialized Hardware Drivers for MMC5883MA" << endl;
    Matrix3d gains = Matrix3d::Zero();
    Matrix3d calibration_s1, calibration_s2, calibration_s3;
    SensorInput::weights w;
    cout << "Loaded Sensor Calibrations and Weights" << endl;
     // set gains
    for (int i = 0; i < 3; i++) gains(i,i) = gains_cfg->at(i);  // diagonal gains matrix
    //auto drv_x = drv_cfg->get_qualified_array_of<unsigned char>("x");     // cpptoml::option<vector<uint8_t>>
    //auto drv_y = drv_cfg->get_qualified_array_of<unsigned char>("y");
    //auto drv_z = drv_cfg->get_qualified_array_of<unsigned char>("z");
    //drivers_ptr.push_back(std::make_shared<hardware::DRV8830>(mux, drv_x->at(0), drv_x->at(1)));
    //drivers_ptr.push_back(std::make_shared<hardware::DRV8830>(mux, drv_y->at(0), drv_y->at(1)));
    //drivers_ptr.push_back(std::make_shared<hardware::DRV8830>(mux, drv_z->at(0), drv_z->at(1)));
    sensors_ptr.push_back(std::make_shared<hardware::MMC5883MA>(mux, *mmc_cfg->get_as<uint8_t>("s1")));
    sensors_ptr.push_back(std::make_shared<hardware::MMC5883MA>(mux, *mmc_cfg->get_as<uint8_t>("s2")));
    sensors_ptr.push_back(std::make_shared<hardware::MMC5883MA>(mux, *mmc_cfg->get_as<uint8_t>("s3")));
    calibration_s1 = load_mat_toml(*cal_cfg, "s1");                      // calibration and rotation matrix for each sensor; each is rotated by 90deg
    calibration_s2 = load_mat_toml(*cal_cfg, "s2");
    calibration_s3 = load_mat_toml(*cal_cfg, "s3");
    auto w_list = w_cfg->get_qualified_array_of<double>("w");           // waited moving average filter values
    SensorInput::calibration cal = std::vector<Matrix3d>({calibration_s1, calibration_s2, calibration_s3});
    auto input_system_ptr = std::make_shared<SensorInput::HardwareSensorInput<hardware::MMC5883MA>>(sensors_ptr, cal, *w_list); // flesh out hardwaresensorinput class
    controlsystem::BDotDetumbler<SensorInput::HardwareSensorInput<hardware::MMC5883MA>> controller(input_system_ptr, lock_ptr, gains, 0.1);
    while (true)
    {
        if (controller.hardwarelock->check_lock()) continue;        // if flight controller is deploying payload on same I2C Bus
        Vector3d torque = controller.update();
        for (int i = 0; i < 3; ++i) drivers_ptr.at(i)->VCMD(torque(i));
    }
    return 0;
}
