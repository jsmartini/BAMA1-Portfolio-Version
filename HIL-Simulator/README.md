# HIL-Simulator
Hardware-in-Loop simulator server and test client for localhost testing. (Day in the Life Testing)
2body_orbital is the initial implementation Alex Boehm made

python3 2body_simulation [log level]
  - command to start server
    -log levels
      -info
      -debug
      -all
      
 python3 local_bdot_test.py
 
 -bdot zmq verification script
    
    
 TODO:
 
 
  - actually factor in the torques calculated by the controller into the dynamic model
  - may have to expand the state space to take into account the acceleration of the quaternion if it
  - is not already factored in
  
  - @ alex my interpretation is that pqrdot is the derivative of the euler angles from the rotation matrix of the quaternion
