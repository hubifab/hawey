
from imutils.video.pivideostream import PiVideoStream
import argparse
import cv2 as cv
import io
import time
from picamera import PiCamera
from threading import Thread
from picamera.array import PiRGBArray


IMAGE_WIDTH             = 640
IMAGE_HEIGHT            = 380

# start video capture as seperate thread
print("starting video stream (call vs.stop() to kill thread)...")
vs = PiVideoStream(resolution=(640,480)).start()
vs.camera.contrast = 100
time.sleep(2.0)

image = vs.read()
cv.imshow('image',image)
cv.waitKey(0)
cv.destroyAllWindows()

for i in range(0,100):
    cv.imshow('Raw', vs.read())
    cv.waitKey(20)

vs.stop()
