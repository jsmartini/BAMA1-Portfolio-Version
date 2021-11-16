#pragma once

#include "semaphore.hpp"
#include <Eigen/Dense>
#include <iostream>
#include <memory>
#include <vector>
using namespace Eigen;
/*

        Whatever the template Class T is that is passed to the BDotDetumbler class, it must have a method that returns a Vector3d from the read function

*/


namespace controlsystem 
{
    template <class T>
    class BDotDetumbler 
    {
        public:
            Vector3d    CurrentReading;
            Vector3d    LastReading = Vector3d::Zero();
            std::shared_ptr<T> datafeed;
            Matrix3d    Gains;
            double sampling_time;
            std::shared_ptr<Locks::SemaphoreLock> hardwarelock;
            BDotDetumbler(std::shared_ptr<T> datafeed, Matrix3d Gains, double sampling_time): Gains(Gains), sampling_time(sampling_time), datafeed(datafeed) {};
            BDotDetumbler(std::shared_ptr<T> datafeed, std::shared_ptr<Locks::SemaphoreLock> lock, Matrix3d Gains, double sampling_time): Gains(Gains), sampling_time(sampling_time), datafeed(datafeed), hardwarelock(lock) {this->LastReading = Vector3d::Zero();};
            Vector3d update();
            
    };
    template <class T>
    Vector3d BDotDetumbler<T>::update()
    // Returns the magnetic moment commanded
    {
        this->CurrentReading = this->datafeed->read();
        Vector3d bdot_norm = ((this->CurrentReading - this->LastReading) / sampling_time);
        bdot_norm /= bdot_norm.norm();
        this->LastReading = this->CurrentReading;
        Vector3d magnetic_moment =  -this->Gains * bdot_norm; 
        //cout << "Requested Magnetic Moment" << endl;
        //cout << magnetic_moment << endl;
        //cout << "End Requested Magnetic Moment" << endl;
        return magnetic_moment;
    };
}