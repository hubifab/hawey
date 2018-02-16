#! /usr/bin/python
from picamera import PiCamera

cam = PiCamera()
cam.resolution = (1280, 720)
# camera.resolution = (128, 72)
cam.contrast = 100
