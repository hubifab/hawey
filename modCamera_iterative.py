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

# init global variables and macros
DOTS_PER_LINE = 100
pi = 3.1419
new_element = [0,0]
THETA_LEFT_LINE         = 0.40      # mean value in RAD of vertical-angle LEFT line
THETA_RIGHT_LINE        = 2.74      # mean value in RAD of vertical-angle RIGHT line
DIVERGENCE              = np.pi/2   # angle tolerance for values close to the line
DIV_2_PREV              = np.pi/32  # angle tolerance for subsequent lines
line_image = None                   # image with lines
canny_image = None                  # canny image
prev_line_left  = [0,THETA_LEFT_LINE]   # remember last detected line left
prev_line_right = [0,THETA_RIGHT_LINE]  # remember last detected line right

print('pre_line LR initialized: ' + prev_line_left + '\t' + prev_line_right)

# start video capture as seperate thread
print ("starting video stream (call vs.stop() to kill thread)...")
vs = PiVideoStream(resolution=(640,480)).start()
vs.camera.contrast = 100
time.sleep(2.0)

def show_image():
    # setup video window
    cv.namedWindow('Camera')
    cv.moveWindow('Camera',500,100)
    image = vs.read()
    # image = image[200:500, 0:600]
    cv.imshow('Camera', image)
    
    # cam = PiCamera()
    # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
    # cam.capture('/images/rechts_gerade.png') 
    
    # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
    # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
    
    
    # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
    # print("alpha links = ",alpha_L,"\nalpha rechts = ",alpha_R)
    cv.waitKey(0)
    cv.destroyAllWindows()
    

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
        # pink line: cv.line(frame,(x::Q:1,y1),(x2,y2),(147,20,255),2)
        cv.line(frame,(x1,y1),(x2,y2),(0,0,0),2)


# def process_line_infos(frame):
#     # Our operations on the frame come here
#     gray = frame
#     # Convert to Canny image
#     # start = time.time() 
#     canny = cv.Canny(gray, 80,100)
#     # end = time.time()
#     # print ("Canny \ttime: " + str(end - start) + " s\n")

#     # Find lane lines
#     # start = time.time()
#     lines = cv.HoughLines(canny,1,np.pi/180, DOTS_PER_LINE)
#     # end = time.time()
#     # print "Houghlines \ttime: " + str(end - start) + " s\n"
#     # print 'return value HoughLines: ' + str(lines) 
#     return lines

def process_lines(frame):
    global new_element
    global line_image
    global canny_image
    
    # remember last lines detected to compare with
    global prev_line_left
    global prev_line_right

    print('prev_line values in function: ' + prev_line_left + '\t' + prev_line_right)

    gray = frame
    canny = cv.Canny(gray, 80,120)
    canny_image = canny
    # Find lane lines
    lines = cv.HoughLines(canny,1,np.pi/180, DOTS_PER_LINE)
    
    line_list = []
    # find the relevant lane-line
    try:
        for i in range(len(lines)):
            for rho,theta in lines[i]:
                # print "rho: " + str(rho) + "\ttheta: " + str(theta/pi*180)
                new_element = [rho,theta]
                line_list.append(new_element)
    except:
        print "modCamera: No new element added."
    # sort list by theta        
    sorted_list = sorted(line_list, key=lambda x: x[1])

    # generate lists for left line and right line
    left_line_list = []
    right_line_list = []
    for line in sorted_list:
        # show all detected line infos:
        if abs(line[1] - prev_line_left[1]) < DIV_2_PREV:
            left_line_list.append(line)
        if abs(line[1] - prev_line_right[1]) < DIV_2_PREV:
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
    
    line_image = frame

    # Display the resulting frame:
    # print ("line left: " + str(line_left))
    # print ("line right: " + str(line_right))
    # cv.imshow('Camera',frame)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    prev_line_left  = line_left
    prev_line_right = line_right
    
    return [line_left,line_right]

def get_image():
    image = vs.read()
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    image = image[100:480, 0:640]
    return image

def getCommand():
    global THETA_LEFT_LINE
    global THETA_RIGHT_LINE
    # try:
    # start = time.time()
    image = get_image()
    # end = time.time()
    # print "\nCapture \ttime: " + str(end - start) + " s\n"
    lines_LR = process_lines(image) 
    # print([theta_LR[0][1],theta_LR[1][1]])
    # command = dir.getDirection([theta_LR[0][1],theta_LR[1][1]])
    # if (command == 9001):
    #     print "START"
    # elif (command == 9002):
    #     print "STOP"
    # elif (command == 9003):
    #     print "LEFT"
    # elif (command == 9004):
    #     print "CENTER"
    # elif (command == 9005):
    #     print "RIGHT"
    return dir.getDirection(lines_LR)

def init_lines():
    # initialize the angles of the left and right line
    image = get_image()

    theta_LR = edit_frames(image) 
    THETA_LEFT_LINE = theta_LR[0][1]
    THETA_RIGHT_LINE = theta_LR[1][1]
    print([theta_LR[0][1],theta_LR[1][1]])


# i = 0
# while (i < 50):
#     try:
#         getCommand()
#         cv.waitKey(500)
#     except:
#         cv.destroyAllWindows()
#         vs.stop()
#     i += 1
# cv.destroyAllWindows()
# vs.stop()
