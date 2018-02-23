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
# approximate initial parameters of the lines
LINE_LEFT               = [182,0.846]
LINE_RIGHT              = [-276,2.361]
# DIVERGENCE to find left and right line
DIV_INIT                = [100, np.pi/6]      # divergence to find lines in the beginning
DIV_ITER                = [50, np.pi/32]    # divergence to find lines iteratively using the previous lines

IMAGE_WIDTH             = 640
IMAGE_HEIGHT            = 380
FWD                     = 9001
STOP                    = 9002
LEFT                    = 9003
RIGHT                   = 9005

pi = 3.1419
new_element = [0,0]
gray_image = None
line_image = None                   # image with lines
canny_image = None                  # canny image
bnw_image = None
vp = None                           # vanishing point
moving = False

prev_left = None
prev_right = None

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
        rho = line_data[0]
        theta = line_data[1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 2000*(-b))
        y1 = int(y0 + 2000*(a))
        x2 = int(x0 - 2000*(-b))
        y2 = int(y0 - 2000*(a))
        # pink line: cv.line(frame,(x::Q:1,y1),(x2,y2),(147,20,255),2)
        cv.line(frame,(x1,y1),(x2,y2),(0,0,0),2)


# Calculate the parameters rho and theta for the left and the right line
def find_all_lines(image):
    global new_element
    global gray_image

    # Find lane lines
    lines = cv.HoughLines(image,1,np.pi/180, DOTS_PER_LINE)
    # print(lines)
    
    line_list = []
    # find the relevant lane-line
    try:
        for i in range(len(lines)):
            for rho,theta in lines[i]:
                # print "rho: " + str(rho) + "\ttheta: " + str(theta/pi*180)
                new_element = [rho,theta]
                line_list.append(new_element)
                # draw_lines(gray_image,new_element)
    except:
        print "modCamera: No new element added."
    # cv.imshow('Camera',gray_image)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    # sort list by theta        
    # sorted_list = sorted(line_list, key=lambda x: x[1])
    return line_list


def find_lines_LR(line_list,prev_left,prev_right,div):
    global gray_image
    # generate lists for left line and right line
    left_line_list = []
    right_line_list = []
    for line in line_list:
        if (isinstance(prev_left[0], np.float32)):
            if abs(line[0] - prev_left[0]) < div[0] and abs(line[1] - prev_left[1]) < div[1]:
                left_line_list.append(line)
        if (isinstance(prev_right[0], np.float32)):
            if abs(line[0] - prev_right[0]) < div[0] and abs(line[1] - prev_right[1]) < div[1]:
                right_line_list.append(line)

    # calculate mean-lines LEFT and RIGHT and draw lines into current frame
    line_left = "N/A"
    line_right = "N/A"
    if any(left_line_list):
        line_left       = np.mean(left_line_list, axis = 0)
        draw_lines(gray_image,line_left)
    if any(right_line_list):
        line_right      = np.mean(right_line_list, axis = 0)
        draw_lines(gray_image,line_right)

    line_image = gray_image

    # Display the resulting frame:
    # print ("line left: " + str(line_left))
    # print ("line right: " + str(line_right))
    cv.imshow('Camera',line_image)
    cv.waitKey(0)
    cv.destroyAllWindows()

    # prev_line_left  = line_left
    # prev_line_right = line_right

    return [line_left,line_right]

def get_image():
    global canny_image
    global bnw_image
    global gray_image

    image = vs.read()
    cropped = image[100:480, 0:640]
    gray = cv.cvtColor(cropped, cv.COLOR_BGR2GRAY)
    gray_image = gray

    # calculate outlines using canny-method
    canny = cv.Canny(gray, 80,140)
    canny_image = canny

    # convert to black and white image using a threshold
    # thresh = 180
    # image_bw = cv.threshold(gray,thresh,255,cv.THRESH_BINARY)[1]
    # bnw_image = image_bw 

    # cv.imshow('Camera',gray)
    # cv.waitKey(0)
    # cv.destroyAllWindows()

    cv.imshow('Camera',image_bw)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
    # cv.imshow('Camera',canny)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return canny_image

# get the x-coordinate of the vanishing point
def get_vp(lines_LR):
    
    global moving
    vp_x = None
    alpha_L = None
    alpha_R = None
    offset_L = None
    offset_R = None

    rho_L = lines_LR[0][0]
    rho_R = lines_LR[1][0]
    theta_L = lines_LR[0][1]
    theta_R = lines_LR[1][1]
    # print('rho_L: ' + str(rho_L))
    # print('theta_L:' + str(theta_L))
    # print('rho_R: ' + str(rho_R))
    # print('theta_R:' + str(theta_R))

    # generate comparable offsets: offset_L and offset_R; origin is upper left
    # corner
    if (isinstance(rho_L, np.float32) and isinstance(theta_L,np.float32)):
        offset_L = -rho_L/(np.cos((np.pi/2)-theta_L))
    if (isinstance(rho_R, np.float32) and isinstance(theta_R,np.float32)):
        offset_R = -rho_R/np.cos(theta_R-(np.pi/2))
    #    offset_R = (IMAGE_WIDTH+(rho_R/np.cos(np.pi-theta_R))) / np.tan(np.pi-theta_R)
    
    # generate comparable angles alpha_L and alpha_R 
    if (isinstance(theta_L, np.float32)):
        alpha_L = (np.pi/2)-theta_L
    if (isinstance(theta_R, np.float32)):
        alpha_R = theta_R-(np.pi/2)
    
    # print('alpha_L: ' + str(np.rad2deg(alpha_L)))
    # print('offset_L: ' + str(offset_L))
    # print('alpha_R: ' + str(np.rad2deg(alpha_R)))
    # print('offset_R: ' + str(offset_R))

    if (alpha_R and alpha_L):
        print("alpha_R: " + str(alpha_R))
        print("alpha_L: " + str(alpha_L))
        # if car is not moving, turn on motor
        if moving == False:
            moving = not moving
            return FWD
        vp_x = (offset_R-offset_L)/(np.tan(alpha_L)+np.tan(alpha_R))
        # set global variable for drawing the steering line
        global vp
        vp = int(vp_x)
        # vanishing point relative to the middle of the window
        vp_x = vp_x - IMAGE_WIDTH/2
        command = int(vp_x/5)
        return command
    elif (not alpha_R and not alpha_L):
        moving = not moving
        return STOP
    elif (alpha_R and not alpha_L):
        return LEFT
    elif (not alpha_R and alpha_L):
        return RIGHT

    # print('tan(alpha_L:' + str(np.tan(alpha_L)))
    # print('tan(alpha_R:' + str(np.tan(alpha_R)))
    # print('vp_x: ' + str(type(vp_x)))
    

def getCommand():
    global line_image
    image = get_image()
    line_list = find_all_lines(image) 
    lines_LR = find_lines_LR(line_list,prev_left,prev_right,DIV_ITER)
    return get_vp(lines_LR)
    # return dir.getDirection(lines_LR)

def init_lines():
    # initialize the left and right line
    global prev_left
    global prev_right

    image = get_image()
    line_list = find_all_lines(image) 
    lines_LR = find_lines_LR(line_list,LINE_LEFT,LINE_RIGHT,DIV_INIT)

    prev_left  = lines_LR[0]   # remember last detected line left
    prev_right = lines_LR[1]  # remember last detected line right
    print('lines LR initialized: ' + str(prev_left) + '\t' + str(prev_right))


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
