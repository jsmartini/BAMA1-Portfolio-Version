#pragma once
#include <nlohmann/json.hpp>
#include <zmq.hpp>
#include <iostream>
#include <Eigen/Dense>
#include <zmq.hpp>
#define FMT_HEADER_ONLY
#include <fmt/core.h>
#include <array>

using namespace Eigen;
using namespace std;
using json = nlohmann::json;
using namespace fmt;

auto json2vector3d = [](json data, string key)
{
    Vector3d v;
    std::array<double, 3> n = data[key.c_str()];
    for (int i = 0; i < 3; i++) v(i) = n.at(i);
    return v;
};

auto vector3d2json = [](Vector3d data)
{
    json j;
    j["torque"] = json::array();
    for (auto i: data)  j["torque"].push_back((double) i);
    return j;
};

class Sim0MQClient
{
    private:
        zmq::context_t ctx{1};
        zmq::socket_t  skt{this->ctx, zmq::socket_type::req};

    public:
        Sim0MQClient(string addr, unsigned int port)
        {
            this->skt.connect(format("tcp://{0}:{1}", addr, port).c_str());
            //cout << "BDOT:\tConnected to Simulator Successfully!" << endl;
        };
        void sendj(json req)
        {
            
            this->skt.send(zmq::buffer(req.dump(4)), zmq::send_flags::none);
            //cout << "BDOT:\tSending JSON Object to Simulation Server" << endl;
        };
        void sends(string req)
        {
            
            this->skt.send(zmq::buffer(req), zmq::send_flags::none);
            //cout << "BDOT:\tSending JSON String Object to Simulation Server" << endl;
        };
        json recvj()
        {
            
            zmq::message_t rep{};
            this->skt.recv(rep, zmq::recv_flags::none);
            //cout << "BDOT:\tRECV'd JSON Object from Simulation Server" << endl;
            json repj = json::parse(rep.to_string());
            //cout << repj.dump(4) << endl;
            return repj;
        };
        string recvs()
        {
            zmq::message_t rep{};
            this->skt.recv(rep, zmq::recv_flags::none);
            return rep.to_string();
        }
};

