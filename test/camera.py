#! /usr/bin/python
# this is a small test program for the picamera


from picamera import PiCamera
from time import sleep
import subprocess

cam = PiCamera()
cam.resolution = (640, 480)
# camera.resolution = (128, 72)
cam.contrast = 100
index = 0
#camera.rotation = 180
#camera.framerate = 15

#sleep(2)

#cam.start_preview()
# sleep(120)
# camera.stop_preview()

# for x in range(0, 1):
def take_photo():
    global index
    cam.start_preview()
    sleep(1)
    cam.capture('/home/pi/hawey/images/photo' + str(index) + '.png')
    cam.stop_preview()
    index += 1
#     sleep(1)
#subprocess.call(['scp', 'enzo2.png', 'fab@141.22.76.138:'])
#     x += 1

#camera.start_recording('/home/pi/project/playground/video.h264')

#sleep(5)

# copy final video to desktop
#subprocess.call(['scp', 'video.h264', 'fab@192.168.0.10:'])
#subprocess.call(['scp', 'image.png', 'fab@192.168.0.10:'])
#subprocess.call(['scp', 'video.h264', 'fab@192.168.0.10:'])

