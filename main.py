#! /usr/bin/python
from time import sleep
import modSonic as sonic
import modAct as act
import modCamera as cam

distance = 200
command = None

# act.sendCommand(act.FWD)
sleep(2)

# setup preview window
# cam.cv.namedWindow('Raw')
# cam.cv.moveWindow('Raw',0,50)
cam.cv.namedWindow('Lines')
cam.cv.moveWindow('Lines',650,50)
# cam.cv.namedWindow('Canny')
# cam.cv.moveWindow('Canny',0,50)

def outputCommand(command):
    if (command == 9001):
        return "START"
    elif (command == 9002):
        return "STOP"
    elif (command == 9003):
        return "LEFT"
    elif (command == 9004):
        return "CENTER"
    elif (command == 9005):
        return "RIGHT"

try:
    while True:
        if (sonic.getDistance() < 30):
            print "Proximity alert!"
            # act.sendCommand(act.STOP)
            # sleep(2)
            # act.sendCommand(act.FWD)
        else:
            command = cam.getCommand()
            # send to motor control
            # act.sendCommand(command)
            # cam.cv.imshow('Raw', cam.vs.read())
            cam.cv.imshow('Lines', cam.line_image)
            # cam.cv.imshow('Canny', cam.canny_image)
            cam.cv.waitKey(100)
            print outputCommand(command) 
except KeyboardInterrupt:  
    print "KeyboardInterrupt: Cleaning up before exit."
    act.sendCommand(act.CENTER)
    act.sendCommand(act.STOP)
    cam.vs.stop()
    sonic.GPIO.cleanup()
    print "Done. Bye!"



