######## MODULE ANALYSIS #####################
# processing command data from camera images #
##############################################

import numpy as np
import cv2 as cv
import io
import time
import modCamera as cam
import importlib
# import direction as dir


# init global variables and macros
DOTS_PER_LINE = 100

# DIVERGENCE in offset and alpha to find left and right line
DIV_INIT                = [100.0, 30]        # divergence to find lines in the beginning
DIV_ITER                = [20.0, 5]         # divergence to find lines iteratively using the previous lines

BNW_THRESHOLD           = 180               # threshold for generating black and white image
IMAGE_WIDTH             = 640
IMAGE_HEIGHT            = 380
FWD                     = 9001
STOP                    = 9002
LEFT                    = 9003
RIGHT                   = 9005

color_image = None
gray_image = None
line_image = None                   # image with lines
canny_image = None                  # canny image
bnw_image = None
vp = None                           # vanishing point
moving = False

prev_left = None
prev_right = None


# -------------------------------------------------------------------------------
# color: (b,g,r)
def draw_lines(image,line_data):
    #print("draw lines running ...")
    if all(line_data):
        try:
            rho = line_data[0]
            theta = line_data[1]
            #print('rho = ' + str(rho) + ' theta = ' + str(theta * 57.2958))
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 2000*(-b))
            y1 = int(y0 + 2000*(a))
            x2 = int(x0 - 2000*(-b))
            y2 = int(y0 - 2000*(a))
            cv.line(image,(x1,y1),(x2,y2),(0,0,255),2)

            #print('draw_lines - EXIT SUCCESS')
        except Exception:
            pass
            print('ERROR in draw_lines()')


# -------------------------------------------------------------------------------
# Calculate the parameters rho and theta for the left and the right line
def find_all_lines(image):
    #print("find_all_lines running ...") 
    lines = []

    # Find all lines in the image
    lines = cv.HoughLines(image,1,np.pi/180, DOTS_PER_LINE)

    # remove unnecessary brackets
    line_list = []
    # if lines is not empty; this is the only method that works!
    if hasattr(lines, 'size'):
        for i in range(len(lines)):
            line_list.append(lines[i][0])
    if not line_list:
        print("find_all_lines: Empty line list!")
    return line_list


# -------------------------------------------------------------------------------
# update the parameters for the left and the right line
# returns: line_left  =
#           line_right = 


def find_lines_LR(line_list,prev_left,prev_right,div):
    #print("find_linesLR running ...")
    # initialize empty lists for left line and right line
    left_line_list  = []
    right_line_list = []

    # convert previous left and right line to offset and alpha 
    prev_left  = get_offset_alpha2(prev_left)
    prev_right = get_offset_alpha2(prev_right)

    # line_image = cam.get_image('color')

    # from all lines that were found, filter out the ones that have a similar 
    # offset and angle as the previous left and right line
    if not line_list:
        print("Empty line_list!")
    if line_list:
        for line in line_list:
            # convert values to float
            line  = [float(i) for i in line]
            # get angle and offset of the lines
            [offset, alpha] = get_offset_alpha2(line)
            # check deviance to previous left line
            if abs(offset - prev_left[0]) < div[0] and abs(alpha - prev_left[1]) < div[1]:
                left_line_list.append(line)
                #draw_lines(line_image,line)
            # check deviance to previous right line
            if abs(offset - prev_right[0]) < div[0] and abs(alpha- prev_right[1]) < div[1]:
                right_line_list.append(line)
                #draw_lines(line_image,line) 

    # cam.show_image('All detected left and right lines', line_image)

    # calculate mean of all left lines and all right lines
    line_left  = []
    line_right = []
    
    # left/right_line_list has format [offset, alpha]
    if any(left_line_list):
        line_left = np.mean(left_line_list, axis = 0)
    else:
        line_left = prev_left

    if any(right_line_list):
        line_right = np.mean(right_line_list, axis = 0)
    else:
        line_right = prev_right

    return [line_left,line_right]


# -------------------------------------------------------------------------------
# generate comparable offset and angle
# the offset of both lines (right and left) is measured from the upper left corner
def get_offset_alpha1(line):
    rho = line[0]
    theta = line[1]
    offset = None
    alpha = None

    if(isinstance(rho,np.float)):
        if(theta < np.pi/2):    # left line
            offset = -rho/(np.cos((np.pi/2)-theta))
            alpha = (np.pi/2)-theta
        if(theta > np.pi/2):    # right line
            offset = -rho/np.cos(theta-(np.pi/2))
            alpha = theta-(np.pi/2)
 
    return([offset, alpha])


def get_offset_alpha2(line):
# -------------------------------------------------------------------------------
# get_offset_alpha2: generate comparable offset and angle alpha
#
# arguments
# rho:   distance from upper left corner
# theta: ancle of rho - guess: positive is anti-clockwise
# line discribed: detected line is ortogonal to rho-line
#
# return
# offset: offset of the left line is measured from the  upper left corner
#         offset of the right line is measured from the upper right corner
#         offsets are always positive
# alpha:  the angle ist positive for left line and negative for right line
#--------------------------------------------------------------------------------
    #print("get_offset_alpha2 running ... ")
    rho = line[0]
    theta = line[1]
    offset = None
    alpha = None
    if(isinstance(rho,np.float)):
        alpha = np.degrees((np.pi/2)-theta)
        if(theta < np.pi/2):    # left line
            offset = rho/(np.cos((np.pi/2)-theta))
        if(theta > np.pi/2):    # right line
            offset = (IMAGE_WIDTH+(rho/np.cos(np.pi-theta))) / np.tan(np.pi-theta) 

    return([offset, alpha])


# -------------------------------------------------------------------------------
# input: positive offsets relative to upper left and right corner
# positive angle for left line and negative angle for right line in degrees
def get_rho_theta(line):
    print("get_rho_theta running ...")
    offset = line[0]
    alpha = line[1]
    theta = (np.pi/2-np.radians(alpha))
    # left line
    if(alpha > 0):
        rho = np.cos(np.radians(alpha))*offset
    # right line
    if(alpha < 0):
        rho = np.cos(np.pi-theta)*(np.tan(np.pi-theta)*offset-IMAGE_WIDTH)
    return([rho,theta])


# -------------------------------------------------------------------------------
# get the x-coordinate of the vanishing point
# TO BE MODIFIED; doesn't work right now
def get_vp(lines_LR):
    
    global moving
    global vp

    vp_x = None
    alpha_L = None
    alpha_R = None
    offset_L = None
    offset_R = None

    [offset_L,alpha_L] = get_offset_alpha1(lines_LR[0])
    [offset_R,alpha_R] = get_offset_alpha1(lines_LR[1])

    if (alpha_R and alpha_L):
        # print("alpha_R: " + str(alpha_R))
        # print("alpha_L: " + str(alpha_L))

        # if car is not moving, turn on motor
        if moving == False:
            moving = True
            return FWD
        vp_x = (offset_R-offset_L)/(np.tan(alpha_L)+np.tan(alpha_R))
        
        # set global variable for drawing the steering line
        vp = int(vp_x)

        # vanishing point relative to the middle of the window
        vp_x = vp_x - IMAGE_WIDTH/2
        command = int(vp_x/5)
        return command
    
    #print('vp_x: ', str(type(vp_x)))
    
    # if no lines are found, stop
    elif (not alpha_R and not alpha_L):
        moving = False
        return STOP
    # if only right line is found, steer left
    elif (alpha_R and not alpha_L):
        return LEFT
    # if only left line is found, steer right
    elif (not alpha_R and alpha_L):
        return RIGHT

    # print('tan(alpha_L:' + str(np.tan(alpha_L)))
    # print('tan(alpha_R:' + str(np.tan(alpha_R)))
    
    

# -------------------------------------------------------------------------------
# calculate the new lines and draw them into the image
def getCommand():
    
    print("getCommand running ...")
    cv.wait(3)

    global line_image
    global prev_left
    global prev_right

    # calculate left and right line
    image_bnw = cam.get_image('bnw',BNW_THRESHOLD)
    # image_bnw = cam.get_image('canny')

    line_list = find_all_lines(image_bnw)
    
    # in case no lines found use previous lines
    if (not line_list):
        print('No lines detected - using previous Lines!')
        line_list = [prev_left, prev_right]

    # get new lines - return format [[left offset, alpha][right offset, alpha]]
    lines_LR = find_lines_LR(line_list,prev_left,prev_right,DIV_ITER)
    
    # update lines and draw them in global line_image
    image_color = cam.get_image('color')

    # if current lines are detected use them ...
    # left line
    if(len(lines_LR[0]) == 2):
        prev_left  = [float(i) for i in lines_LR[0]]
        draw_lines(image_color,prev_left)
    # ... or if no lines use prev ...
#    else:
#        lines_LR[0] = prev_left;
    # righ tline
    if(len(lines_LR[1]) == 2):
        prev_right =  [float(i) for i in lines_LR[1]]
        draw_lines(image_color, prev_right)
    # ... or if no lines use prev ...
#    else:
#        lines_LR[1] = prev_right;
    # or write prev_left and prev_right into lines_LR



    # pref_left & prev_right beinhalten hier die Informationen mit denen
    # weitergearbeitet wird, also schreibe

    # write camera-image with drawed lines to global variable
    line_image = image_color

    # Annahme: Hier sind die Werte rho und theat
    print('lines_LR: LEFT: ' + str(lines_LR[0]) + ' RIGHT: ' + str(lines_LR[1]))
   
    
    vanishing_point = get_vp(lines_LR)
    
    print('getCommand returns: ' + str(vanishing_point))

    return vanishing_point


# -------------------------------------------------------------------------------
# initialize left and right line
def init_lines():
    print("init_lines running ...")
    global prev_left
    global prev_right

    # approximate initial parameters of the lines
    # args: x-direction offset, angle
    prev_left = get_rho_theta([280, 60])
    prev_right = get_rho_theta([280, -60])

# HIER HABE ICH WAS GELÖSCHT ....

# -------------------------------------------------------------------------------
def set_threshold(value):
    global BNW_THRESHOLD
    BNW_THRESHOLD = value

            
