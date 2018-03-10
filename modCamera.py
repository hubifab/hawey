from imutils.video.pivideostream import PiVideoStream
import argparse
import imutils
import numpy as np
import cv2 as cv
import io
import time
from picamera import PiCamera
from threading import Thread
from picamera.array import PiRGBArray
import direction as dir


IMAGE_WIDTH             = 640
IMAGE_HEIGHT            = 380

# start video capture as seperate thread
print("starting video stream (call vs.stop() to kill thread)...")
vs = PiVideoStream(resolution=(640,480)).start()
vs.camera.contrast = 100
time.sleep(2.0)

# def show_image():
#     # setup video window
#     cv.namedWindow('Camera')
#     cv.moveWindow('Camera',500,100)
#     image = vs.read()
#     # image = image[200:500, 0:600]
#     cv.imshow('Camera', image)
    
#     # cam = PiCamera()
#     # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
#     # cam.capture('/images/rechts_gerade.png') 
    
#     # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
#     # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
    
    
#     # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
#     # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
#     cv.waitKey(0)
#     cv.destroyAllWindows()

def show_image(title,image):
    cv.imshow(title,image)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
def show_image_shortly(title,image):
    cv.imshow(title,image)
    cv.waitKey(20)


# returns an image with modes 'color', 'canny', 'gray' or 'bnw'
def get_image(mode, threshold=None):

    color = vs.read()
    color = color[100:480, 0:640]

    gray = cv.cvtColor(color, cv.COLOR_BGR2GRAY)

    # calculate outlines using canny-method
    canny = cv.Canny(gray, 80,140)

    if(threshold!=None):
        # convert to black and white image using a threshold
        bnw = cv.threshold(gray,threshold,255,cv.THRESH_BINARY)[1]


    if(mode == 'color'):
        return color
    elif(mode == 'gray'):
        return gray
    elif(mode == 'canny'):
        return canny
    elif(mode == 'bnw'):
        return bnw
    else:
        print("Error, no mode for image specified")
        return color


    
