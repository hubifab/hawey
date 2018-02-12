#! /usr/bin/python

import curses

keyLeftMode = False
keyRightMode = False
keyUpMode = False
keyDownMode = False

screen = curses.initscr()

while True:
    try:
        curses.noecho()
        curses.curs_set(0)
        screen.keypad(1)
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
            pwm.set_pwm(0,0,331) # turn motor on
            screen.addstr("Motor on\n")
        keyUpMode = not keyUpMode

    elif event == curses.KEY_DOWN:
        screen.addstr("Up")
    else:
        screen.addstr("other")
