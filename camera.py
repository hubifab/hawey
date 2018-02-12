from picamera import PiCamera
from time import sleep
import subprocess

camera = PiCamera()
camera.resolution = (1280, 720)
camera.rotation = 180
#camera.framerate = 15

#sleep(2)

for x in range(0, 15):
    sleep(1)
    camera.capture('/home/pi/project/playground/image.png')
    sleep(1)
    subprocess.call(['scp', 'image.png', 'fab@192.168.0.10:'])
    x += 1

#camera.start_recording('/home/pi/project/playground/video.h264')

#sleep(5)

# copy final video to desktop
#subprocess.call(['scp', 'video.h264', 'fab@192.168.0.10:'])
#subprocess.call(['scp', 'image.png', 'fab@192.168.0.10:'])
#subprocess.call(['scp', 'video.h264', 'fab@192.168.0.10:'])

