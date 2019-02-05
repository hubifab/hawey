#! /usr/bin/python

from __future__ import division
import Adafruit_PCA9685
import time

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

# set motor and servo values 
# full left/right at SERVO_MID +/- 30 
# +35 (positive) for max LEFT
# -35 (negative) for max RIGHT
SERVO_MIN = 297 #272 # max right
SERVO_MID = 307
SERVO_MAX = 317 #342 # max left
SERVO_DEFAULT_LEFT = 10
SERVO_DEFAULT_RIGHT = -10

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
ERROR = 9999

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
        print ('modAct: Command is LEFT, CENTER or RIGHT!')
        if (command != prev_steer):
            prev_steer = command
            if (command == LEFT):
                pwm.set_pwm(SERVO_OUT,0, SERVO_MID - SERVO_DEFAULT_LEFT) # turn servo to default right
                return "Servo set: LEFT"
            elif (command == CENTER):
                pwm.set_pwm(SERVO_OUT, 0, SERVO_MID) # turn servo to neutral position
                return "Servo set: CENTER"
            elif (command == RIGHT):
                pwm.set_pwm(SERVO_OUT, 0, SERVO_MID - SERVO_DEFAULT_RIGHT) # turn servo to min
                return "Servo set: RIGHT"
            elif (command == REV):
                pwm.set_pwm(MOTOR_OUT, 0, MOTOR_STOP) # turn motor off
                time.sleep(0.5)
                pwm.set_pwm(MOTOR_OUT, 0, MOTOR_REV) # turn motor to reverse
                return "Motor set: REVERSE"
        else:
            return 'Servo set: no change'
    else:
         # pwm.set_pwm(SERVO_OUT,0,SERVO_MID - command) # turn servo to value
        # command is a value that can be passed to the servo
        if command == 0:
            pwm.set_pwm(SERVO_OUT,0,SERVO_MID) # turn servo to value
            return("Servo set: CENTER")
        if -30 <= command and command < 0:
            pwm.set_pwm(SERVO_OUT,0,SERVO_MID - command) # turn servo to value
            return ("Servo set: LEFT by " + str(command))
        elif (command > 0 and command <= 30) :
            pwm.set_pwm(SERVO_OUT,0,SERVO_MID - command) # turn servo to value
            return ("Servo set: RIGHT by " + str(command))
        else:
            return "ERR: Not a valid command:" + str(command)
    return ERROR

