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

# init global variables and macros
DOTS_PER_LINE = 100
pi = 3.1419
new_element = [0,0]
THETA_LEFT_LINE         = 0.40      # mean value in RAD of vertical-angle LEFT line
THETA_RIGHT_LINE        = 2.74      # mean value in RAD of vertical-angle RIGHT line
DIVERGENCE              = np.pi/2   # angle tolerance for values close to the line

# setup video window
cv.namedWindow('Camera')
cv.moveWindow('Camera',500,100)

# start video capture
vs = PiVideoStream().start()
time.sleep(2.0)

# Thread wrapper class for capturing frames as discussed in:
# https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class PiVideoStream:
    def __init__(self, resolution=(640,480), framerate=32):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                format="bgr", use_video_port=True)

        # initilize frame and variable used to indicate wether thread should be
        # stopped
        self.frame = None
        self.stopped = False
    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        for f in self.stream:
            self.frame = f.array
            self.rawCapture.truncate(0)
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return most recent frame
        return self.frame

    def stop(self):
        self.stopped = True

# class for counting fps
class FPS:
    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        return (self._end - self._start).total_seconds()

    def fps(self):
        return self._numFrames / self.elapsed()

def draw_lines(frame,line_data):
    if all(line_data):
        rho             = line_data[0]
        theta   = line_data[1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        # pink line: cv.line(frame,(x1,y1),(x2,y2),(147,20,255),2)
        cv.line(frame,(x1,y1),(x2,y2),(0,0,0),2)


def process_line_infos(frame):
    # Our operations on the frame come here
    gray = frame
    # Convert to Canny image
    # start = time.time() 
    canny = cv.Canny(gray, 80,100)
    # end = time.time()
    # print ("Canny \ttime: " + str(end - start) + " s\n")

    # Find lane lines
    # start = time.time()
    lines = cv.HoughLines(canny,1,np.pi/180, DOTS_PER_LINE)
    # end = time.time()
    # print "Houghlines \ttime: " + str(end - start) + " s\n"
    # print 'return value HoughLines: ' + str(lines) 
    return lines

def edit_frames(frame):
    global new_element
    lines = process_line_infos(frame)
    line_list = []
    # find the relevant lane-line
    try:
        for i in range(len(lines)):
            for rho,theta in lines[i]:
                print "rho: " + str(rho) + "\ttheta: " + str(theta/pi*180)
                new_element = [rho,theta]
                line_list.append(new_element)
    except:
        print "No new element added."

    # sort list by theta        
    sorted_list = sorted(line_list, key=lambda x: x[1])

    # generate lists for left line and right line
    left_line_list = []
    right_line_list = []
    for line in sorted_list:
        # show all detected line infos:
        if abs(line[1] - THETA_LEFT_LINE) < DIVERGENCE:
            left_line_list.append(line)
        if abs(line[1] - THETA_RIGHT_LINE) < DIVERGENCE:
            right_line_list.append(line)

    # calculate mean-lines LEFT and RIGHT
    line_left = "N/A"
    line_right = "N/A"
    if any(left_line_list):
        line_left       = np.mean(left_line_list, axis = 0)
        draw_lines(frame,line_left)
    if any(right_line_list):
        # draw lines into current frame
        line_right      = np.mean(right_line_list, axis = 0)
        draw_lines(frame,line_right)

    # Display the resulting frame:
    # print ("line left: " + str(line_left))
    # print ("line right: " + str(line_right))
    # cv.imshow('Camera',frame)
    # cv.waitKey(100)

# When everything done, release the capture
# cap = cv.VideoCapture(0)

# fps = FPS().start()

def getDirection():
    # try:
    # start = time.time()
    image = vs.read()
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = image[200:500, 0:600]
    end = time.time()
    # print "\nCapture \ttime: " + str(end - start) + " s\n"
    edit_frames(image) 
    # except:
    #     cv.destroyAllWindows()
    #     vs.stop()

while True:
    getDirection()




