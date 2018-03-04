import numpy as np
import cv2 as cv
import io
import time
import modCamera as cam
# import direction as dir


# init global variables and macros
DOTS_PER_LINE = 100
# approximate initial parameters of the lines
LINE_LEFT               = [182.0,0.846]
LINE_RIGHT              = [-276.0,2.361]

# DIVERGENCE in offset and alpha to find left and right line
DIV_INIT                = [20.0, np.deg2rad(10)]      # divergence to find lines in the beginning
DIV_ITER                = [20.0, np.deg2rad(5)]    # divergence to find lines iteratively using the previous lines

IMAGE_WIDTH             = 640
IMAGE_HEIGHT            = 380
FWD                     = 9001
STOP                    = 9002
LEFT                    = 9003
RIGHT                   = 9005

pi = 3.1419
new_element = [0,0]
color_image = None
gray_image = None
line_image = None                   # image with lines
canny_image = None                  # canny image
bnw_image = None
vp = None                           # vanishing point
moving = False

prev_left = None
prev_right = None


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
        # pink line: cv.line(frame,(x::Q:1,y1),(x2,y2),(147,20,255),2)
        cv.line(image,(x1,y1),(x2,y2),(0,0,255),2)


# Calculate the parameters rho and theta for the left and the right line
def find_all_lines(image):
    global new_element
    global color_image

    # Find lane lines
    lines = cv.HoughLines(image,1,np.pi/180, DOTS_PER_LINE)
    # print(lines)
    
    line_list = []
    # find the relevant lane-line
    try:
        for i in range(len(lines)):
            for rho,theta in lines[i]:
                new_element = [rho,theta]
                line_list.append(new_element)
                # draw_lines(color_image,new_element)
    except:
        print("modCamera: No new element added.")
        

    # cam.show_image(color_image)

    # sort list by theta        
    # sorted_list = sorted(line_list, key=lambda x: x[1])
    return line_list


def find_lines_LR(line_list,prev_left,prev_right,div):
    global line_image

    line_image = cam.get_image('color')

    # generate lists for left line and right line
    left_line_list = []
    right_line_list = []
    for line in line_list:
        print(line)
        line  = [float(i) for i in line]   # remember last detected line left
        [offset, alpha] = get_offset_alpha(line)
        if (isinstance(prev_left[0], np.float)):
            [prev_offset, prev_alpha] = get_offset_alpha(prev_left)
            print([offset,alpha])
            print([prev_offset,prev_alpha])
            # print(div[0])
            if abs(offset - prev_offset) < div[0] and abs(alpha - prev_alpha) < div[1]:
                left_line_list.append(line)
                draw_lines(line_image,line)
        if (isinstance(prev_right[0], np.float)):
            [prev_offset, prev_alpha] = get_offset_alpha(prev_right)
            print([offset,alpha])
            print([prev_offset,prev_alpha])
            if abs(offset - prev_offset) < div[0] and abs(alpha- prev_alpha) < div[1]:
                right_line_list.append(line)
                draw_lines(line_image,line)

    cam.show_image('All left and right lines', line_image)

    # calculate mean-lines LEFT and RIGHT and draw lines into current frame
    line_left = "N/A"
    line_right = "N/A"
    if any(left_line_list):
        line_left = np.mean(left_line_list, axis = 0)
        # draw_lines(line_image,line_left)
    if any(right_line_list):
        line_right = np.mean(right_line_list, axis = 0)
        # draw_lines(line_image,line_right)

    # cam.show_image(line_image)

    return [line_left,line_right]

# generate comparable offset and angle; origin is upper left corner
def get_offset_alpha(line):
    rho = line[0]
    theta = line[1]
    offset = None
    alpha = None
    print(np.pi/2)
    print(theta)
    print(type(rho))
    if(isinstance(rho,np.float)):
        if(theta < np.pi/2):    # left line
            offset = -rho/(np.cos((np.pi/2)-theta))
            alpha = (np.pi/2)-theta
        if(theta > np.pi/2):    # right line
            offset = -rho/np.cos(theta-(np.pi/2))
            alpha = theta-(np.pi/2)
    #    offset_R = (IMAGE_WIDTH+(rho_R/np.cos(np.pi-theta_R))) / np.tan(np.pi-theta_R)
 
    print('offset: ' + str(offset))
    print('alpha: ' + str(np.rad2deg(alpha)))

    return([offset, alpha])


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
    

def getCommand():
    global line_image
    global prev_left
    global prev_right

    image_bnw = cam.get_image('bnw')
    line_list = find_all_lines(image_bnw)
    # print(prev_left,prev_right)
    lines_LR = find_lines_LR(line_list,prev_left,prev_right,DIV_ITER)

    
    prev_left  = [float(i) for i in lines_LR[0]]   # remember last detected line left
    prev_right =  [float(i) for i in lines_LR[1]]  # remember last detected line right
    image_color = cam.get_image('color')
    draw_lines(image_color,lines_LR[0])
    draw_lines(image_color,lines_LR[1])
    cam.show_image('New left and right line', image_color)

    return get_vp(lines_LR)

# initialize left and right line
def init_lines():
    global prev_left
    global prev_right


    image_bnw = cam.get_image('bnw')
    cam.show_image('Black and white image',image_bnw)
    line_list = find_all_lines(image_bnw) 
    # print(line_list)
    lines_LR = find_lines_LR(line_list,LINE_LEFT,LINE_RIGHT,DIV_INIT)

    image_color1 = cam.get_image('color')
    draw_lines(image_color1,LINE_LEFT)
    draw_lines(image_color1,LINE_RIGHT)
    cam.show_image('Lines before init',image_color1)

    prev_left  = [float(i) for i in lines_LR[0]]   # remember last detected line left
    prev_right =  [float(i) for i in lines_LR[1]]  # remember last detected line right
    
    image_color2 = cam.get_image('color')
    draw_lines(image_color2,lines_LR[0])
    draw_lines(image_color2,lines_LR[1])
    cam.show_image('Lines after init',image_color2)

    if(isinstance(prev_left[0],float) and isinstance(prev_right[0],float)):
        print('lines LR initialized: ' + str(prev_left) + '\t' + str(prev_right))
    else:
        print('could not initialize both lines')

def stop_camera():
    cam.vs.stop()
