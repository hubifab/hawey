# MAIN #############################################################

#! /usr/bin/python

###########################################################
## live preview - > terminal commnad: "raspistill -f -t 0"

from time import sleep
# import modSonic as sonic
import modAct as act
import modCamera as cam
import modAnalysis as ana
import modCarTest
# import tkinter
import cv2 as cv

distance = 200
command = None

# act.sendCommand(act.FWD)
sleep(2)

# setup preview window
# cam.cv.namedWindow('Raw')
# cam.cv.moveWindow('Raw',0,50)
# cam.cv.namedWindow('Lines')
# cam.cv.moveWindow('Lines',650,50)
# cam.cv.namedWindow('Canny')
# cam.cv.moveWindow('Canny',0,50)
# cam.cv.namedWindow('BnW')
# cam.cv.moveWindow('BnW',0,50)

def outputCommand(command):
    if (command == 9001):
        return "FWD"
    elif (command == 9002):
        return "STOP"
    elif (command == 9003) or (command > 0):
        return "LEFT"
    elif (command == 9004):
        return "CENTER"
    elif (command == 9005) or (command < 0):
        return "RIGHT"
    else:
        return ('Servo: ' + str(command))

def outputVideo(command):
    # cam.cv.imshow('Raw', cam.vs.read())
    image = ana.line_image
    # x = cam.vp 
    # if (x):
    #     cam.cv.line(image, (x, 0), (320, 380), 0, thickness=2, lineType=4, shift=0)
    #     cam.cv.putText(image, outputCommand(command), (250,300), cam.cv.FONT_HERSHEY_SIMPLEX, 2, 255)
    cam.cv.imshow('realtimeOutputVideo', image)
    # cam.cv.imshow('BnW', bnw_image)
    # cam.cv.imshow('Canny', cam.canny_image)
    cam.cv.waitKey(20)

#  to run test
#################################################################################
#modCarTest
##################################################################################

# STOP motor as a reset
act.sendCommand(9002)

try:
    # set BNW(Black And White image)-treshold 
    ana.set_threshold(170)
    ana.init_lines()
 # WHAT IS THIS FOR?
    #top = tkinter.Tk()
    #top.mainloop()
    #while True:
    #    if ana.getCommand() != act.STOP:
    #        break

    while True:
        image = cam.get_image('color')
        cam.cv.waitKey(20)
        
        # if (sonic.getDistance() < 60):
        #     print("Proximity alert!")
        #     # act.sendCommand(act.STOP)
        #     # sleep(5)
        #     # act.sendCommand(act.FWD)
        # else:
        command = ana.getCommand()
        # cam.cv.waitKey()

        # send to motor control
        message = act.sendCommand(command)
        if message == act.ERROR:
            # raise Exception('modAct returned ERROR')
            print ('modAct Error: ' + str(message))
            cam.cv.waitKey(0)
        print ("Command received: " + outputCommand(command) + ' (Code: ' + str(command) + ')')
        print ("Command return value: " + message)
        # display current camera stream with lines and command
        outputVideo(command)

except KeyboardInterrupt:  
    print("KeyboardInterrupt: Cleaning up before exit.")
    act.sendCommand(act.CENTER)
    act.sendCommand(act.STOP)
    cam.vs.stop()
    cv.destroyAllWindows()
    #sonic.GPIO.cleanup()
    print("Done. Bye!")

except Exception as e:
    print("--------------------------------------------------------------------")
    print("Error occured!")
    print("--------------------------------------------------------------------")
    print(str(type(e)))
    print(str(e))
    print("--------------------------------------------------------------------")
    print("Cleaning up before exit...")
    print("--------------------------------------------------------------------")
    print("STOP and CENTER")
    act.sendCommand(act.CENTER)
    act.sendCommand(act.STOP)
    
    cam.vs.stop()
    # sonic.GPIO.cleanup()
    cv.destroyAllWindows()
    print("Done. Bye!")




