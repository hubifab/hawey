#! /usr/bin/python
from time import sleep
import modSonic as sonic
import modAct as act
import modCamera as cam

distance = 200
command = None

act.sendCommand(act.FWD)
sleep(2)

try:
    while True:
        if (sonic.getDistance() < 50):
                print "Proximity alert!"
            # act.sendCommand(act.STOP)
            # sleep(2)
            # act.sendCommand(act.FWD)
        else:
            command = cam.getCommand()
            act.sendCommand(command)
            print str(command)
except KeyboardInterrupt:  
    print "KeyboardInterrupt: Cleaning up before exit."
    act.sendCommand(act.STOP)
    act.sendCommand(act.CENTER)
    cam.vs.stop()
    sonic.GPIO.cleanup()
    print "Done. Bye!"



