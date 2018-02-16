#! /usr/bin/python
from time import sleep
import modSonic as sonic
import modAct as act

distance = 200


act.sendCommand(act.FWD)

try:
    while True:
        if (sonic.getDistance() < 50):
            act.sendCommand(act.STOP)
            sleep(2)
            act.sendCommand(act.FWD)
except KeyboardInterrupt:  
    print "KeyboardInterrupt: Cleaning up before exit."
    act.sendCommand(act.STOP)
    sonic.GPIO.cleanup()
    print "Done. Bye!"



