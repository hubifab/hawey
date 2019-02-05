# Test all car functions: START, STOP, LEFT, RIGHT,ect.

import modAct
import carControlMacros as macro
from time import sleep


# MACROS
#FWD  = 9001
#STOP = 9002

def RunTest():
    print('------------------------------------------------------------')
    print('Test Car Functions')
    print('------------------------------------------------------------')

    # check servo
    returnValue = modAct.sendCommand(macro.CENTER)
    print('Servo Test CENTER, return value: ' + returnValue)
    sleep(2)
    returnValue = modAct.sendCommand(macro.LEFT)
    print('Servo Test LEFT, return value: ' + returnValue)
    sleep(2)
    returnValue = modAct.sendCommand(macro.RIGHT)
    print('Servo Test RIGHT, return value: ' + returnValue)
    sleep(2)
    returnValue = modAct.sendCommand(macro.CENTER)
    print('Servo Test CENTER, return value: ' + returnValue)
    sleep(2)

    # check motor
    modAct.sendCommand(macro.STOP)
    print('Motor Test STOP, return value: ' + returnValue)
    sleep(1)
    returnValue = modAct.sendCommand(macro.FWD)
    print('Motor Test FWD, return value: ' + returnValue)
    sleep(2)
    # stop motor
    returnValue = modAct.sendCommand(macro.STOP)
    print('Motor Test STOP, return value: ' + returnValue)
    sleep(1)

    print('------------------------------------------------------------')
    print('Test finished succesfully')
    print('------------------------------------------------------------')
