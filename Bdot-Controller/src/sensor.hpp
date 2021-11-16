#pragma once

#include "zmqclient.hpp"
#include "hardware.hpp"
#include <Eigen/Dense>
#include <iostream>
#include <memory>
#include <vector>
#include <deque>

auto logdata = [](string time, Vector3d data, string units)
{
    cout << time << "\t";
    for (int i = 0; i < 3; i++) cout << data << "\t";
    cout << units << endl;
};

namespace SensorInput
{
    class SimulationSensorInput
    {
        private:
            std::shared_ptr<Sim0MQClient> simulator;
        public:
            SimulationSensorInput(std::shared_ptr<Sim0MQClient> simulator): simulator(simulator) {};
        void next() const
        {
            this->simulator->sends("next");
        };
        Vector3d read()
        {
            json data = simulator->recvj();
            cout << data << endl;
            return json2vector3d(data, "data");
            //logdata (data["time"],reading, "Gauss");
            
        };
        void reset() const {};
        void sendtorque(Vector3d torque) const
        {
            json msg;
            msg = vector3d2json(torque);
            this->simulator->sendj(msg.dump(4));
        };
        void ack() const
        {
            this->simulator->recvs();
        }
    };

    typedef std::vector<Matrix3d> calibration;
    typedef std::vector<double> weights;
    typedef std::deque<Vector3d> history;

    template<class Device>
    class HardwareSensorInput
    {
        
            weights w;
            calibration cal;
            hardware::HardwareDevices<Device> sensor_ptr_vec;
            history h;
            unsigned max_size;
        public:
            HardwareSensorInput(hardware::HardwareDevices<Device> sensor_ptr_vec, calibration cal, weights w): sensor_ptr_vec(sensor_ptr_vec), cal(cal), w(w) {this->max_size = this->w.size();};
            
            Vector3d read()
            {
                if (this->sensor_ptr_vec.size() == 0) exit(-3);     // terminate if no hardware available
                Vector3d Reading = Vector3d::Zero();
                for (int i = 0; i < sensor_ptr_vec.size(); i++) 
                {
                    Matrix3d cal_tmp = this->cal.at(i);
                    Vector3d reading = sensor_ptr_vec.at(i)->read();
                    if (reading.isApprox(hardware::ERRVEC))
                    {
                        // remove sensor pointer and calibration matrix if os error is thrown
                        this->cal.erase(this->cal.begin() + i);
                        this->sensor_ptr_vec.erase(this->sensor_ptr_vec.begin() + i);
                        continue;
                    }
                    Reading +=  cal_tmp * reading; 
                }
                //cout << "UnFiltered Reading" << endl;
                //cout << Reading << endl;
                //cout <<"End UnFiltered Reading" << endl;
                Reading /= sensor_ptr_vec.size();
                //cout << "hardwaareSensorInpit.read()" << endl;
                //cout << Reading << endl;
                this->h.push_back(Reading);
                //cout << "History" << endl;
                //for (auto i : this->h) 
                //{
                //cout << "Entry" << endl;
                //cout << i << endl;
                //}
                //cout << "End history" << endl;
                if (this->h.size() > this->max_size) this->h.pop_front();
                Reading = Vector3d::Zero();
                for (int i = 0; i < h.size(); i++) Reading += this->w.at(i) * this->h.at(i);
                //cout << "Filtered Reading" << endl;
                //cout << Reading << endl;
                //cout <<"End Filtered Reading" << endl;
                return Reading; 
            };
    };
};
