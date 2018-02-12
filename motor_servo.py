#! /usr/bin/python

from __future__ import division
import time
import curses

import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()

servo_min = 102
servo_mid = 307
servo_max = 512

pwm.set_pwm_freq(50)

keyLeftMode = False
keyRightMode = False
keyUpMode = False
keyDownMode = False

screen = curses.initscr()
curses.noecho()
curses.curs_set(0)
screen.keypad(1)

screen.addstr("Test remote control\n")
screen.addstr("-----------------------------------------------------------------------------\n")
screen.addstr("Press LEFT  to turn LEFT    - press LEFT  again to return to neutral position\n")
screen.addstr("Press RIGHT to turn RIGHT   - press RIGHT again to return to neutral position\n")
screen.addstr("Press UP    to start moving - press UP    again to stop\n")
screen.addstr("-----------------------------------------------------------------------------\n")
screen.addstr("press Ctrl-C to quit\n")



while True:
    try:
        event = screen.getch()
    finally:
        curses.endwin()

    if event == curses.KEY_LEFT:
        if (keyLeftMode):
            pwm.set_pwm(0,0,servo_mid) # turn servo to neutral position
            screen.addstr("Stop left\n")
        else:
            pwm.set_pwm(0,0,servo_max) # turn servo to max
            screen.addstr("Left\n")
        keyLeftMode = not keyLeftMode

    elif event == curses.KEY_RIGHT:
        if (keyRightMode):
            pwm.set_pwm(0,0,servo_mid) # turn servo to neutral position
            screen.addstr("Stop right\n")
        else:
            pwm.set_pwm(0,0,servo_min) # turn servo to min
            screen.addstr("Right\n")
        keyRightMode = not keyRightMode

    elif event == curses.KEY_UP:
        if (keyUpMode):
            pwm.set_pwm(1,0,servo_mid) # turn motor off
            screen.addstr("Stop motor\n")
        else:
            pwm.set_pwm(1,0,331) # turn motor on
            screen.addstr("Motor on\n")
        keyUpMode = not keyUpMode

    elif event == curses.KEY_DOWN:
        screen.addstr("Up")
    else:
        screen.addstr("other")
