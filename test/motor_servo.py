#! /usr/bin/python

from __future__ import division
import time
import curses

import Adafruit_PCA9685
import RPi.GPIO as GPIO


pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

servo_min = 102
servo_mid = 307
servo_max = 512

# setup gpio pins
GPIO.setmode(GPIO.BCM)
TRIG_OUT = 17
ECHO_IN = 27
GPIO.setup(TRIG_OUT, GPIO.OUT)
GPIO.setup(ECHO_IN, GPIO.IN)
GPIO.output(TRIG_OUT, False)

SERVO_OUT = 0
MOTOR_OUT = 1

# setup global variables 
keyLeftMode = False
keyRightMode = False
keyUpMode = False
keyDownMode = False

# setup screen
screen = curses.initscr()
screen.nodelay(1)
curses.noecho() # don't print keys to screen automatically
curses.curs_set(0)
screen.keypad(1) # handle special keys like cursor keys

screen.addstr("Test remote control\n")
screen.addstr("-----------------------------------------------------------------------------\n")
screen.addstr("Press LEFT  to turn LEFT    - press LEFT  again to return to neutral position\n")
screen.addstr("Press RIGHT to turn RIGHT   - press RIGHT again to return to neutral position\n")
screen.addstr("Press UP    to start moving - press UP    again to stop\n")
screen.addstr("-----------------------------------------------------------------------------\n")
screen.addstr("press Ctrl-C to quit\n")

def getDistance():
  # start distance measurement
  screen.addstr("Measuring...\n")
  GPIO.output(TRIG_OUT, True)
  time.sleep(0.00001)
  GPIO.output(TRIG_OUT, False)

  while GPIO.input(ECHO_IN) == 0:
    pulse_start = time.time()
  while GPIO.input(ECHO_IN) == 1:
    pulse_end = time.time()

  # calculate distance from measurement
  pulse_duration = pulse_end - pulse_start
  distance = pulse_duration * 17150
  distance = round(distance, 2)
  screen.addstr("...done measuring: ")
  screen.addstr(str(distance))
  screen.addstr(" cm")
  return distance

# do the magic
while True:
    try:
      event = screen.getch()
      # distance = getDistance()
      #if (distance < 30):
      #    pwm.set_pwm(MOTOR_OUT,0,servo_mid) # turn motor off
      #    screen.addstr("Proximity: Motor stopped!\n")
      #screen.addstr(str(distance))
    #except KeyboardInterrupt:  
        # here you put any code you want to run before the program   
        # exits when you press CTRL+C  
        # GPIO.cleanup()
    #    print "KeyboardInterrupt!"
    #except:  
        # this catches ALL other exceptions including errors.  
        # You won't get any error messages for debugging  
        # so only use it once your code is working  
    #    print "Other error or exception occurred!"  
    finally:
      GPIO.cleanup()
      curses.endwin()

    if event == curses.KEY_LEFT:
        if (keyLeftMode):
            pwm.set_pwm(SERVO_OUT,0,servo_mid) # turn servo to neutral position
            screen.addstr("Stop left\n")
        else:
            pwm.set_pwm(SERVO_OUT,0,servo_max) # turn servo to max
            screen.addstr("Left\n")
        keyLeftMode = not keyLeftMode

    elif event == curses.KEY_RIGHT:
        if (keyRightMode):
            pwm.set_pwm(SERVO_OUT,0,servo_mid) # turn servo to neutral position
            screen.addstr("Stop right\n")
        else:
            pwm.set_pwm(SERVO_OUT,0,servo_min) # turn servo to min
            screen.addstr("Right\n")
        keyRightMode = not keyRightMode

    elif event == curses.KEY_UP:
        if (keyUpMode):
            pwm.set_pwm(MOTOR_OUT,0,servo_mid) # turn motor off
            screen.addstr("Stop motor\n")
        else:
            pwm.set_pwm(MOTOR_OUT,0,331) # turn motor on
            screen.addstr("Motor on\n")
        keyUpMode = not keyUpMode

    elif event == curses.KEY_DOWN:
        if (keyDownMode):
            pwm.set_pwm(MOTOR_OUT,0,servo_mid) # turn motor off
            screen.addstr("Stop motor\n")
        else:
            pwm.set_pwm(MOTOR_OUT,0,290) # turn motor on
            screen.addstr("Reverse on\n")
        keyDownMode = not keyDownMode
#    else:
#        screen.addstr("other")


