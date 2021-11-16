Send 5V to magnetorquer load switch
-> GPIO command, set "P8_28" high
-> Send commands to X, Y, and/or Z Axis Magnetorquer Driver (DRV8830)
-> Address:x->0x61, y->0x62, z->0x64
-> Registers: control->0x00, fault ->0x01
-> Control commands -> 1V,2V,3V,4V,5V

#!/usr/bin/env python3
import Adafruit_BBIO.GPIO as GPIO
import smbus
import time
BUS = 1
bus = smbus.SMBus(BUS)

def enable():
        # P8_28 on BBB must be set to high to send power to magnetorquers
        GPIO.setup("P8_28", GPIO.OUT)
        GPIO.output("P8_28", GPIO.HIGH)
        time.sleep(1)
        GPIO.cleanup()

def disable():
        # P8_28 on BBB must be set to low to cut power to magnetorquers
        GPIO.setup("P8_28", GPIO.OUT)
        GPIO.output("P8_28", GPIO.LOW)
        time.sleep(1)
        GPIO.cleanup()

# magnetorquer drivers
ADD_MTQ_X = 0x60 # actual is 0x61 on ICB, but using 0x60 for testing
ADD_MTQ_X = 0x62
ADD_MTQ_X = 0x64

# registers
CONTROL = 0x00               
FAULT = 0x01

def magnetorquer_driver():
        fault=0
        enable()
        steps = [0x06,0x0D,0x19,0x25,0x3E,0x06]
        seq_counter=0
        #print(steps)
        while seq_counter<6 and fault==0:
        
                bus.write_byte_data(0x70,0x04,0x10)
                time.sleep(0.01)
                print("Command to CONTROL:",steps[seq_counter])
                bus.write_byte_data(ADD_MTQ_X,CONTROL,steps[seq_counter])
                time.sleep(0.02)
                CONTROL_R = bus.read_byte_data(ADD_MTQ_X, CONTROL)
                time.sleep(0.001)
                FAULT_R = bus.read_byte_data(ADD_MTQ_X, FAULT)
                time.sleep(0.001)
                print("I2C Registers:",CONTROL_R, FAULT_R)
                if CONTROL_R==steps[seq_counter]:
                    seq_counter=seq_counter+1
                else:
                    step_skip=step_skip+1
                if FAULT_R != 0x00:
                    fault=1
                    print('Fault detected in magnetorquer driver!')
                    break
            if step_skip==5:
                print('I2C register is not writing to CONTROL correctly.')
                break
        disable() #send command to disable stepper motor

def main():
        driver_decision=input("Type Y and enter to continue")
        if 'y' in driver_decision.lower():
                driver()

if __name__ == "__main__":
        main()
