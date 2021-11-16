#include "sensor.hpp"
#include "bdot.hpp"
#include "semaphore.hpp"
#include "hardware.hpp"
#include <Eigen/Dense>
#include <iostream>
#include <vector>
#include <string>
#include "toml.h"               // tinytoml https://github.com/mayah/tinytoml
#include <unistd.h>
#define FMT_HEADER_ONLY         // other local headers reference fmt, we want the header only version

using namespace std;
using namespace Eigen;



// boilerplat functions to load toml vectors to eigen matrices
auto
load_mat_general = [](vector<double> data)
{
    Matrix3d mat;
    for (int i=0; i<3; i++) for(int j = 0; j < 3; j++) mat(i, j) = data.at(i*3 + j);
    return mat;
};

auto
load_mat_vec_diagonal = [](vector<double> data)
{
    Vector3d v;
    for (int i = 0; i < 3; i++) v(i) = data.at(i);
    return v.asDiagonal();
};

#define delay_ms 10000

int main(int argc, char* argv[])
{
    // couldn't figure out how to get the keys for each toml table
    // from this toml lib, so here is the gross super hardcoded mess to load the values
    // parse toml configuration file
    std::ifstream cfgifs(argv[1]);
    toml::ParseResult pr = toml::parse(cfgifs);
    const toml::Value& cfg = pr.value;
    shared_ptr<Locks::SemaphoreLock> lock_ptr = std::make_shared<Locks::SemaphoreLock>(DEFAULT_LOCK_NAME);
    shared_ptr<hardware::MUX> mux = make_shared<hardware::MUX>(cfg.find("MUX.path")->as<string>().c_str());
    double sample_rate_delay = cfg.get<double>("MISC.rate");
    cout << "sample time read:\t " << sample_rate_delay << endl;
    hardware::HardwareDevices<hardware::DRV8830> drivers_ptr;
    hardware::HardwareDevices<hardware::MMC5883MA> sensors_ptr;
    cout << "Hardware Devices Initialized" << endl;
    // tiny toml does not like anything other than int for uint8_t, do the cast later or have compiler interpret it, not going to fight it
    vector<int> drvx = cfg.find("DRV8830.x")->as<vector<int>>();
    vector<int> drvy = cfg.find("DRV8830.y")->as<vector<int>>();
    vector<int> drvz = cfg.find("DRV8830.z")->as<vector<int>>();
    uint8_t s1ch = cfg.find("MMC.s1")->as<int>();
    uint8_t s2ch = cfg.find("MMC.s2")->as<int>();
    uint8_t s3ch = cfg.find("MMC.s3")->as<int>();
    cout << "Hardware Configurations Initialized" << endl;
    drivers_ptr.push_back(make_shared<hardware::DRV8830>(mux, drvx.at(0), drvx.at(1)));
    drivers_ptr.push_back(make_shared<hardware::DRV8830>(mux, drvy.at(0), drvy.at(1)));
    drivers_ptr.push_back(make_shared<hardware::DRV8830>(mux, drvz.at(0), drvz.at(1)));
    cout << "DRV Drivers Initialized" << endl;
    sensors_ptr.push_back(make_shared<hardware::MMC5883MA>(mux, s1ch));
    sensors_ptr.push_back(make_shared<hardware::MMC5883MA>(mux, s2ch));
    sensors_ptr.push_back(make_shared<hardware::MMC5883MA>(mux, s3ch));
    cout << "MMC Drivers Initialized" << endl;
    SensorInput::calibration cals;
    cals.push_back(load_mat_general(cfg.get<vector<double>>("CALS.s1")));
    cals.push_back(load_mat_general(cfg.get<vector<double>>("CALS.s2")));
    cals.push_back(load_mat_general(cfg.get<vector<double>>("CALS.s3")));
    cout << "Calibration Matrices Loaded" << endl;
    SensorInput::weights w = cfg.find("FILTER.w")->as<vector<double>>();
    cout << "Filter Weights Initialized"  << endl;
    Matrix3d gains = load_mat_vec_diagonal(cfg.get<vector<double>>("GAINS.xyz"));
    cout << "Controller Gains Loaded" << endl;
    shared_ptr<SensorInput::HardwareSensorInput<hardware::MMC5883MA>> input_sys_ptr = make_shared<SensorInput::HardwareSensorInput<hardware::MMC5883MA>>(sensors_ptr, cals, w);
    cout << "Input System Loaded" << endl;
    controlsystem::BDotDetumbler<SensorInput::HardwareSensorInput<hardware::MMC5883MA>> controller(input_sys_ptr, lock_ptr, gains, sample_rate_delay);
    cout << "Controller Loaded" << endl;
    cout << "Great Success" << endl;
    // slope of line from Figure 1, measured, maps magnetic moment to voltage
    double magmoment2voltage = 6/0.55; //https://satsearch.s3.eu-central-1.amazonaws.com/datasheets/satsearch_datasheet_o7p08b_nanoavionics_magnetorquers-mtq3x.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJLB7IRZ54RAMS36Q%2F20211004%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20211004T205828Z&X-Amz-Expires=86400&X-Amz-Signature=db11fcb3bfb31dd37d1269746d865654123584dff0215dd01358b8d13dd55d88&X-Amz-SignedHeaders=host 
    unsigned long long lock_counter = 0;
    while (true)
    {
        if (controller.hardwarelock->check_lock()) 
        {
            lock_counter += 1;
            if (lock_counter % 10 == 0) 
                cout << "SEMAPHORE LOCKED" << endl;
            continue;
        }        // if flight controller is deploying payload on same I2C Bus
        Vector3d torque = magmoment2voltage * controller.update();
        for (int i = 0; i < 3; ++i) drivers_ptr.at(i)->VCMD(torque(i));
        usleep(delay_ms);
    }
    return 0;
}
