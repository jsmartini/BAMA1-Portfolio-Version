#pragma once
#include <iostream>
#include <fcntl.h>
#include <stdint.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <memory>
#include <Eigen/Dense>
#include <algorithm>
#include <vector>
#include <stdexcept>

// C Libraries for i2c devices
extern "C" {
    #include "i2c.h"
}

using namespace std;
using namespace Eigen;

#define MUX_ADDR    0x70
#define MUX_CH_REG  0x04

//////////////////////////////////////////////////////////////
// MMC5883MA Registers and Values
#define resolution 65536
#define m_rng      0.000244140625
#define uncertainy 8
#define XoutLSB  0x00
#define XoutMSB  0x01
#define YoutLSB  0x02
#define YoutMSB  0x03
#define ZoutLSB  0x04
#define ZoutMSB  0x05
#define TMPout   0x06
#define DEVStat  0x07
#define INTCTRL0 0x08
#define INTCTRL1 0x09
#define INTCTRL2 0xA
#define XThresh  0xB
#define YThresh  0xC
#define ZThresh  0xD

#define MMC5883MA_REFRESH_RATE_MicroSeconds 1666.6666666667 // 600 Hz

#define MMC5883MA_ADDR 0x30
const uint8_t XYZLSB[] = {XoutLSB, YoutLSB, ZoutLSB};
const uint8_t XYZMSB[] = {XoutMSB, YoutMSB, ZoutMSB};

const uint8_t XYZ[2][3] = {
    {XoutLSB, YoutLSB, ZoutLSB},
    {XoutMSB, YoutMSB, ZoutMSB}
};

////////////////////////////////////////////////////////////////////////
// DRV8830 Constants
#define CTRL_STANDBY  0x00
#define CTRL_NEGATIVE 0x01
#define CTRL_POSITIVE 0x02
#define CTRL_FULL     0x03
#define DRV_FAULT_REG 0x01

//DRV8830 register tables
const std::vector<double>  voltages = {0.48, 0.56, 0.64, 0.72, 0.8, 0.88, 0.96, 1.04, 1.12, 1.2, 1.29, 1.37, 1.45, 1.53, 1.61, 1.69, 1.77, 1.85, 1.93, 2.01, 2.09, 2.17, 2.25, 2.33, 2.41, 2.49, 2.57, 2.65, 2.73, 2.81, 2.89, 2.97, 3.05, 3.13, 3.21, 3.29, 3.37, 3.45, 3.53, 3.61, 3.69, 3.77, 3.86, 3.94, 4.02, 4.1, 4.18, 4.26, 4.34, 4.42, 4.5, 4.58, 4.66, 4.74, 4.82, 4.9, 4.98, 5.06};
const std::vector<uint8_t> values   = {0x6, 0x7, 0x8, 0x9, 0xa, 0xb, 0xc, 0xd, 0xe, 0xf, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f};

auto u2f = [](uint8_t LSB, uint8_t MSB) {return (double)((MSB << 8 | LSB) * m_rng - uncertainy);};

// bitwises the direction and voltage/register value into a payload
auto bitwise_reg_value = [](uint8_t reg_value, uint8_t dir) {return reg_value << 2 | dir;};

template<typename T>
unsigned bsearch(vector<T> arry, T value, unsigned lower_bound, unsigned upper_bound)
{
    unsigned mdpt = (unsigned) (upper_bound + lower_bound) / 2;
    if (value > arry.at(mdpt) && upper_bound - lower_bound > 2)         return bsearch(arry, value, mdpt, upper_bound);
    else if (value < arry.at(mdpt) && upper_bound - lower_bound > 2)    return bsearch(arry, value, lower_bound, mdpt);
    else                                                                return mdpt;
};


namespace hardware
{

    Vector3d ERRVEC(-999, -999, -999);
    template <class T>
    using HardwareDevices = std::vector<std::shared_ptr<T>>;

    const uint8_t MUX_CHANNELS[] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
    class MUX
    {
        private:
            int fd;
            uint8_t current_ch = 9; // uninitialized channel
        public:
            MUX(const char* DeviceHandle)
            {
                this->fd = i2c_init(DeviceHandle);
            };
            void ch(uint8_t ch)
            {
                if (this->current_ch != ch)
                {
                    if(i2c_write(this->fd, MUX_ADDR, MUX_CH_REG, MUX_CHANNELS[ch]) < 0) exit(-1);
                    this->current_ch = ch;
                }
            };
            void write_data(uint8_t ch, uint8_t addr, uint8_t reg, uint8_t value)
            {
                this->ch(ch);
                if(i2c_write(this->fd, addr, reg, value) < 0) exit(-1);
            };
            uint8_t read_data(uint8_t ch, uint8_t addr, uint8_t reg)
            {
                this->ch(ch);
                u8 result;
                if (i2c_read(this->fd, addr, reg, &result) < 0) exit(-1);
                return result;
            };
    };

    class MMC5883MA
    // Magnetometers
    {
        private:
            shared_ptr<MUX> mux;
            uint8_t channel;
            
        public:
            MMC5883MA(shared_ptr<MUX> mux, uint8_t ch) : mux(mux){this->channel = ch;};
            void reset() const
            {
                this->mux->write_data(this->channel, MMC5883MA_ADDR, INTCTRL0, 0x4);
            };
            uint8_t status() const
            {
                return this->mux->read_data(this->channel, MMC5883MA_ADDR, DEVStat);
            };
            void wait() const
            {
                while (this->status() == 0) usleep(MMC5883MA_REFRESH_RATE_MicroSeconds); // sleep for 0.01 seconds and refresh the sensor
            };
            Vector3d read() const
            {
                try{
                    this->reset();
                    Vector3d res;
                    this->mux->write_data(this->channel, MMC5883MA_ADDR, INTCTRL0, 1);
                    this->wait();
                    uint8_t readings[2][3];
                    for(int i = 0; i < 2; i++) for(int j=0; j < 3; j++) readings[i][j] = this->mux->read_data(this->channel,MMC5883MA_ADDR,XYZ[i][j]);
                    for(int k = 0; k <3; k++) res(k) = u2f(readings[0][k], readings[1][k]);
                    return res;
                } catch(const std::system_error& e) {
                    cout << "MMC5883MA Failed on channel: " << this->channel << endl;
                    cout << "Error: " << e.what() << endl;
                    Vector3d err(-999, -999, -999);
                    return err;
                }
            };
    };

    class DRV8830
    // Voltage Driver for Magnet Torquers
    {
        private:
            shared_ptr<MUX> mux;
            uint8_t ch;
            uint8_t wAddr;
        public:
            DRV8830(shared_ptr<MUX> mux, unsigned ch, uint8_t wAddr): mux(mux)
            {
                this->wAddr = wAddr;
                this->ch = ch;
            };
            void VCMD(double v_req) const
            {
                // implement standby mode
                uint8_t direction = (v_req > 0) ? CTRL_POSITIVE : CTRL_NEGATIVE;
                unsigned key = bsearch<double>(voltages, std::abs(v_req), 0, 32);
                uint8_t reg_value = values[key];
                this->mux->write_data(this->ch, this->wAddr, 0x00, reg_value << 2 | direction);
                Fault(); // check for faults
            };
            void Fault() const
            {
                uint8_t fault_value = this->mux->read_data(this->ch, this->wAddr, 0x01);
                if(fault_value != 0)
                {
                    cout << "Fault Cleared. Fault Value:\t" << hex << (unsigned short)fault_value << endl;
                    this->mux->write_data(this->ch, this->wAddr, 0x01, 0x00);
                }            
            };
    };
};