#include "bdot.hpp"
#include "zmqclient.hpp"
#include "sensor.hpp"
#include <Eigen/Dense>
#include "semaphore.hpp"
#include <iostream>
#include <memory>
#include "toml.h"   //tiny toml
#include <unistd.h>

using namespace Eigen;
using namespace std;

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

int main(int argc, char* argv[])
{
    cout << "Parsing Config File" << endl;
    toml::ParseResult pr = toml::parseFile(argv[1]);
    const toml::Value& cfg = pr.value;
    if (!pr.valid()) 
    {
        cout << pr.errorReason << endl;
        return 0;
    }
    cout << "Loaded TOML Tables" << endl;
    SensorInput::weights w = cfg.find("FILTER.w")->as<vector<double>>();
    cout << "Loaded Sensor Weights" << endl;
    vector<int> drvx = cfg.find("DRV8830.x")->as<vector<int>>();
    vector<int> drvy = cfg.find("DRV8830.y")->as<vector<int>>();
    vector<int> drvz = cfg.find("DRV8830.z")->as<vector<int>>();
    cout << "Loaded DRV Config" << endl;
    hardware::HardwareDevices<hardware::DRV8830> drivers_ptr;
    double sample_rate_delay = cfg.get<double>("MISC.rate");
    cout << "sample time read:\t " << sample_rate_delay << endl;
    shared_ptr<hardware::MUX> mux = make_shared<hardware::MUX>(cfg.find("MUX.path")->as<string>().c_str());
    cout << "Loaded Mux" << endl;
    drivers_ptr.push_back(make_shared<hardware::DRV8830>(mux, drvx.at(0), drvx.at(1)));
    drivers_ptr.push_back(make_shared<hardware::DRV8830>(mux, drvy.at(0), drvy.at(1)));
    drivers_ptr.push_back(make_shared<hardware::DRV8830>(mux, drvz.at(0), drvz.at(1)));
    cout << "Loaded DRV8830 Devices" << endl;
    auto simulator = std::make_shared<Sim0MQClient>(cfg.get<string>("TESTING.target"), cfg.get<int>("TESTING.port"));
    cout << "Loaded Simulator" << endl;
    auto sensorfeed = std::make_shared<SensorInput::SimulationSensorInput>(simulator);
    cout << "Initialized SensorFeed" << endl;
    hardware::HardwareDevices<SensorInput::SimulationSensorInput> sensors_ptr;
    sensors_ptr.push_back(sensorfeed);
    SensorInput::calibration cals;
    cals.push_back(Matrix3d::Identity());   // one sensor input, one calibration Identity matrix
    Matrix3d gains = load_mat_vec_diagonal(cfg.get<vector<double>>("GAINS.xyz"));
    cout << "Initialized Gains" << endl;
    shared_ptr<Locks::SemaphoreLock> lock_ptr = std::make_shared<Locks::SemaphoreLock>(DEFAULT_LOCK_NAME);
    cout << "Loaded Semaphore Lock" << endl;
    //shared_ptr<SensorInput::HardwareSensorInput<SensorInput::SimulationSensorInput>> input_sys_ptr = make_shared<SensorInput::HardwareSensorInput<SensorInput::SimulationSensorInput>>(sensors_ptr, cals, w);
    cout << "Configured Input System" << endl;
    auto controller = controlsystem::BDotDetumbler<SensorInput::SimulationSensorInput>(sensorfeed, lock_ptr, gains, sample_rate_delay);
    cout << "Initialized Controller" << endl;
    vector<double> resistences_xyz = cfg.get<vector<double>>("GAINS.xyz_ohms");
    // slope of line from Figure 1, measured, maps magnetic moment to voltage
    double magmoment2voltage = 6/0.55; //https://satsearch.s3.eu-central-1.amazonaws.com/datasheets/satsearch_datasheet_o7p08b_nanoavionics_magnetorquers-mtq3x.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJLB7IRZ54RAMS36Q%2F20211004%2Feu-central-1%2Fs3%2Faws4_request&X-Amz-Date=20211004T205828Z&X-Amz-Expires=86400&X-Amz-Signature=db11fcb3bfb31dd37d1269746d865654123584dff0215dd01358b8d13dd55d88&X-Amz-SignedHeaders=host 
    cout << "Running Control Validation Program" << endl;
    while (true)
    {
        sensorfeed->next();
        Vector3d magnetic_moment = controller.update();
        if (!controller.hardwarelock->check_lock())
        {
            // convert magnetic moment to voltages and then command magnet toquers with the correct voltage
            sensorfeed->sendtorque(magnetic_moment.cross(controller.CurrentReading));
            Vector3d VoltagesXYZ = magmoment2voltage * magnetic_moment;
            for (int i = 0; i < 3; ++i) drivers_ptr.at(i)->VCMD(VoltagesXYZ(i));
        }
        else
        {
            // simulate no output on magnet toquers when stepper motor is in use through hardware bus lock
            sensorfeed->sendtorque(Vector3d::Zero());
        }
        sensorfeed->ack(); // makes sure 0MQ Rep/Req comm sequence isn't broken.
        usleep(sample_rate_delay);
    }
    return 0;
}