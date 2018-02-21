#! /usr/bin/python

from __future__ import division
import Adafruit_PCA9685
import time

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

# set motor and servo values
SERVO_MIN = 295 # 102
SERVO_MID = 307
SERVO_MAX = 319 # 512

MOTOR_FWD = 320
MOTOR_STOP= 307
MOTOR_REV = 295

# specific commands that can be received
# any other numbers between -100 and 100 are values for the servo
FWD   = 9001
STOP  = 9002
LEFT  = 9003
CENTER= 9004
RIGHT = 9005
REV   = 9006

SERVO_OUT = 0
MOTOR_OUT = 1

prev_move = STOP
prev_steer = CENTER
# initialize idle state
pwm.set_pwm(MOTOR_OUT,0,MOTOR_STOP) # turn motor off
pwm.set_pwm(SERVO_OUT,0,SERVO_MID)  # turn servo to neutral position
time.sleep(1)

def sendCommand(command):
    global prev_move
    global prev_steer
    # print "last command: ", prev_command
    # print "new command: ", command
    if command == FWD or command == STOP:
        if (command != prev_move):
            prev_move = command
            if (command == FWD):
                pwm.set_pwm(MOTOR_OUT,0,MOTOR_FWD) # turn motor on
                return "Motor FORWARD"
            elif (command == STOP):
                pwm.set_pwm(MOTOR_OUT,0,MOTOR_REV) # turn motor off
                time.sleep(0.5)
                pwm.set_pwm(MOTOR_OUT,0,MOTOR_STOP) # turn motor off
                return "Motor OFF"

    if (command == LEFT or command == CENTER or command == RIGHT):
        if (command != prev_steer):
            prev_steer = command
            if (command == LEFT):
                pwm.set_pwm(SERVO_OUT,0,SERVO_MAX) # turn servo to max
                return "Servo LEFT"
            elif (command == CENTER):
                pwm.set_pwm(SERVO_OUT,0,SERVO_MID) # turn servo to neutral position
                return "Servo CENTER"
            elif (command == RIGHT):
                pwm.set_pwm(SERVO_OUT,0,SERVO_MIN) # turn servo to min
                return "Servo RIGHT"
            elif (command == REV):
                pwm.set_pwm(MOTOR_OUT,0,MOTOR_STOP) # turn motor off
                time.sleep(0.5)
                pwm.set_pwm(MOTOR_OUT,0,MOTOR_REV) # turn motor to reverse
                return "Motor REVERSE"
    # else:
        # command is a value that can be passed to the servo
        # pwm.set_pwm(SERVO_OUT,0,SERVO_MID + command) # turn servo to min
        # print ("angle difference: " + command)
        # return "Servo RIGHT"


