#! /usr/bin/python
from time import sleep
import modSonic as sonic
import modAct as act
import modCamera as cam

distance = 200
pferd = 0

act.sendCommand(act.FWD)
sleep(2)

try:
    while True:
        if (sonic.getDistance() < 50):
            act.sendCommand(act.STOP)
            sleep(2)
            act.sendCommand(act.FWD)
        else:
            vorpferd = pferd
            pferd = cam.getCommand()
            act.sendCommand(pferd)
            print str(pferd)
except KeyboardInterrupt:  
    print "KeyboardInterrupt: Cleaning up before exit."
    act.sendCommand(act.STOP)
    cam.vs.stop()
    sonic.GPIO.cleanup()
    print "Done. Bye!"



