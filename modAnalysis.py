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

BNW_THRESHOLD           = 180                           # threshold for generating black and white image
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
        cv.line(image,(x1,y1),(x2,y2),(0,0,255),2)


# -------------------------------------------------------------------------------
# Calculate the parameters rho and theta for the left and the right line
def find_all_lines(image):
    
    lines = []

    # Find all lines in the image
    lines = cv.HoughLines(image,1,np.pi/180, DOTS_PER_LINE)

    # remove unnecessary brackets
    line_list = []
    
    if hasattr(lines, 'size'):       # if lines is not empty; this is the only method that works!!
        for i in range(len(lines)):
            line_list.append(lines[i][0])

    return line_list


# -------------------------------------------------------------------------------
# update the parameters for the left and the right line
def find_lines_LR(line_list,prev_left,prev_right,div):

    # initialize empty lists for left line and right line
    left_line_list = []
    right_line_list = []

    # convert previous left and right line to offset and alpha 
    prev_left = get_offset_alpha2(prev_left)
    prev_right = get_offset_alpha2(prev_right)

    # line_image = cam.get_image('color')

    # from all lines that were found filter out the ones that have a similar offset and angle as the previous left and right line
    for line in line_list:
        line  = [float(i) for i in line]                                                                    # convert values to float
        [offset, alpha] = get_offset_alpha2(line)                                                           # get angle and offset of the lines
        if abs(offset - prev_left[0]) < div[0] and abs(alpha - prev_left[1]) < div[1]:                      # check deviance to previous left line
            left_line_list.append(line)
            #draw_lines(line_image,line) 
        if abs(offset - prev_right[0]) < div[0] and abs(alpha- prev_right[1]) < div[1]:                     # check deviance to previous left line
            right_line_list.append(line)
            #draw_lines(line_image,line) 

    # cam.show_image('All detected left and right lines', line_image)

    # calculate mean of all left lines and all right lines
    line_left = []
    line_right = []
    if any(left_line_list):
        line_left = np.mean(left_line_list, axis = 0)
    if any(right_line_list):
        line_right = np.mean(right_line_list, axis = 0)

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


# -------------------------------------------------------------------------------
# generate comparable offset and angle
# the offset of the left line is measured from the  upper left corner
# the offset of the right line is measured from the upper right corner
# offsets are always positive
# angle ist positive for left line and negative for right line
def get_offset_alpha2(line):
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
# input: positive offsets relative to left and right corner
# positive angle for left line and negative angle for right line in degrees
def get_rho_theta(line):
    offset = line[0]
    alpha = line[1]
    theta = (np.pi/2-np.radians(alpha))
    if(alpha > 0):                # left line
        rho = np.cos(np.radians(alpha))*offset
    if(alpha < 0):
        rho = np.cos(np.pi-theta)*(np.tan(np.pi-theta)*offset-IMAGE_WIDTH)
    return([rho,theta])


# -------------------------------------------------------------------------------
# get the x-coordinate of the vanishing point
# TO BE MODIFIED; doesn't work right now
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


    if (alpha_R and alpha_L):
        # print("alpha_R: " + str(alpha_R))
        # print("alpha_L: " + str(alpha_L))
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
    

# -------------------------------------------------------------------------------
# calculate the new lines and draw them into the image
def getCommand():
    global line_image
    global prev_left
    global prev_right

    # calculate left and right line
    image_bnw = cam.get_image('bnw',BNW_THRESHOLD)
    # image_bnw = cam.get_image('canny')
    line_list = find_all_lines(image_bnw)
    lines_LR = find_lines_LR(line_list,prev_left,prev_right,DIV_ITER)
    
    # update lines and draw them in global line_image
    image_color = cam.get_image('color')

    if(len(lines_LR[0]) == 2):
        prev_left  = [float(i) for i in lines_LR[0]]   # remember last detected line left
        draw_lines(image_color,prev_left) 
        print('line left:')
        print(prev_left)

    if(len(lines_LR[1]) == 2):
        prev_right =  [float(i) for i in lines_LR[1]]  # remember last detected line right
        draw_lines(image_color,prev_right)
        print('line right:')
        print(prev_right)

    line_image = image_color
    
           # cam.show_image_shortly('new lines',image_color)

    #return get_vp(lines_LR)


# -------------------------------------------------------------------------------
# initialize left and right line
def init_lines():
    global prev_left
    global prev_right

    # approximate initial parameters of the lines
    prev_left = get_rho_theta([280, 50])
    prev_right = get_rho_theta([280, -50])


    # show image with lines before initialization
    image_color1 = cam.get_image('color')
    draw_lines(image_color1, prev_left)
    draw_lines(image_color1, prev_right)
    cam.show_image('Lines before init',image_color1)


    # get black and white image
    image_bnw = cam.get_image('bnw',BNW_THRESHOLD)
    #image_bnw = cam.get_image('canny')
    cam.show_image('Black and white image',image_bnw)
   
    # find all lines in the black an white image
    line_list = find_all_lines(image_bnw) 

    # show image with all found lines
    line_image1 = cam.get_image('color')
    for line in line_list:
        draw_lines(line_image1,line)
    cam.show_image('All detected lines',line_image1)

    # calculate the new left and right line
    lines_LR = find_lines_LR(line_list,prev_left,prev_right,DIV_INIT)

    
    image_color2 = cam.get_image('color')
        
    # if left line was found
    if(len(lines_LR[0]) == 2):
        # set the new values and convert to float
        prev_left  = [float(i) for i in lines_LR[0]]
        draw_lines(image_color2, prev_left)

    if(len(lines_LR[1]) == 2):
        prev_right =  [float(i) for i in lines_LR[1]]
        draw_lines(image_color2, prev_right)
        
    cam.show_image('Lines after init',image_color2)

    if(len(lines_LR[0]) == 2 and len(lines_LR[1]) == 2):
        print('lines LR initialized: ' + str(get_offset_alpha2(prev_left)) + '\t' + str(get_offset_alpha2(prev_right)))


# -------------------------------------------------------------------------------
def set_threshold(threshold):
    global BNW_THRESHOLD
    BNW_THRESHOLD = threshold


