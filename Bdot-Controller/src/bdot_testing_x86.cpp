#include "bdot.hpp"
#include "zmqclient.hpp"
#include "sensor.hpp"
#include <Eigen/Dense>
#include <iostream>
#include <memory>

using namespace Eigen;

int main(int argc, char* argv[])
{
    auto simulator = std::make_shared<Sim0MQClient>(argv[1], std::stoi(argv[2]));
    auto sensorfeed = std::make_shared<SensorInput::SimulationSensorInput>(simulator);
    Vector3d Gains;
    Gains << 0.3, 0.3, 0.34;
    Matrix3d gain_diagonal = Gains.asDiagonal();
    cout << "Gain Matrix" << endl;
    cout << gain_diagonal << endl;
    auto controller = controlsystem::BDotDetumbler<SensorInput::SimulationSensorInput>(sensorfeed, gain_diagonal, 0.1);
    while (true)
    {
        sensorfeed->next();
        Vector3d magnetic_moment = controller.update();
        sensorfeed->sendtorque(magnetic_moment.cross(controller.CurrentReading));
        sensorfeed->ack(); // makes sure 0MQ Rep/Req comm sequence isn't broken.
    }
    return 0;
}