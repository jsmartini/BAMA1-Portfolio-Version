!!KEY FILES ARE REMOVED ON PURPOSE!!
If you want access to the working version, contact me at jsmartini@crimson.ua.edu.

# BAMA-1 CubeSat Mission

Codebase for BAMA-1 CubeSat Mission

Jonathan Martini and Chet Wiltshire

jsmartini@crimson.ua.edu

Encryption Key Was regenerated for this version.

offline_testing

    - runs virtual twin and test suite

online_testing

    - runs grounstation and simulator application with zmqproxy

    - run mission app in online testing configuration on BAMA-1

production

    - runs satellite in mission configuration

    - restarts if crash is detected (5 minute wait)

    - use RadioBro Corp. Groundstation api for groundstation application // satnogs


To build networking library, navigate to BAMA1-Telemetry/libcsp and 

    run python3 ./examples/buildall.py

    - requires socketcan development libraries

    - requires 0MQ v3 development libraries

    - waf build system

Project Structure

BAMA1-Telemetry

    - C3/ : all satellite software

        - Comm/ RPC framework built on struct format strings and Cubesat Protocol

        - api.toml - api for endpoints

    - libcsp/ : libcsp source and build directory

Bdot-Controller

    - BDOT Control Law Implementation

    - MMC5883MA C++ Drivers
    - DRV8830 C++ Drivers

    - 0MQ/Sensor Input Programs for testing and validation

GroundStation

    - Not Final Application

    - cli.py - rpc cli for satellite over ethernet Command and Data Handling testing (CSP)

Testing Folders
    - offline testing can be ran without mission hardware
