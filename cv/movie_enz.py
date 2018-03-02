import numpy as np
import cv2 as cv
import io
import time
# from picamera import PiCamera as camera
from picamera import PiCamera
camera = PiCamera()

from picamera.array import PiRGBArray
videostream = PiRGBArray(camera)

DOTS_PER_LINE = 50

pi = 3.1419
new_element = [0,0]
THETA_LEFT_LINE         = 0.40      # mean value in RAD of vertical-angle LEFT line
THETA_RIGHT_LINE        = 2.74      # mean value in RAD of vertical-angle RIGHT line
DIVERGENCE              = np.pi/2   # angle tolerance for values close to the line

cv.namedWindow('Camera')
cv.moveWindow('Camera',500,100)

def draw_lines(frame,line_data):
    # print line
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
        # cv.line(frame,(x1,y1),(x2,y2),(147,20,255),2)
        cv.line(frame,(x1,y1),(x2,y2),(0,0,0),2)


def process_line_infos(frame):
    # Our operations on the frame come here
    # gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    gray = frame
    # Convert to Canny image
    start = time.time() 
    canny = cv.Canny(gray, 80,100)
    end = time.time()
    # print "Canny \ttime: " + str(end - start) + " s\n"
    # cv.imshow('canny', canny)
    # cv.waitKey()
    # cv.destroyAllWindows()

    # Find lane lines
    start = time.time()
    lines = cv.HoughLines(canny,1,np.pi/180, DOTS_PER_LINE)
    end = time.time()
    # print "Houghlines \ttime: " + str(end - start) + " s\n"
    # print 'return value HoughLines: ' + str(lines) 
    return lines

def edit_frames(frame):
    global new_element
# 2nd argument 0: import as gray-scale-frame
# while(True):
    # Capture frame-by-frame
    # ret, frame = cap.read()
        
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
        # print(line)
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
        # Display the resulting frame
    print ("line left: " + str(line_left))
    print ("line right: " + str(line_right))
    cv.imshow('Camera',frame)
    cv.waitKey(100)
    # cv.destroyAllWindows()
    
    return [line_left,line_right]

def capture_frame():
    start = time.time()

    # to speed up capturing process: not working yet
    camera.capture(videostream, format='bgr')
    image = videostream.array

    #stream = io.BytesIO()
    #camera.capture(stream, format = 'png', use_video_port=True)

    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # cv.imshow('frame', gray)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
    # reset the stream # before the next # capture
    videostream.seek(0)
    videostream.truncate()

    # Construct a numpy array from the stream
    #data = np.fromstring(videostream.getvalue(), dtype=np.uint8)
    #image = cv.imdecode(data, 1)

    image = image[200:500, 0:600]
    end = time.time()
    print "Capture \ttime: " + str(end - start) + " s\n"
    # cv.imshow('test',image)
    # cv.waitKey()
    # cv.destroyAllWindows()
    return image 
  
# When everything done, release the capture
# cap = cv.VideoCapture(0)

def init_lines():
    global THETA_LEFT_LINE
    global THETA_RIGHT_LINE
    image = capture_frame()
    theta_LR = edit_frames(image)
    THETA_LEFT_LINE = theta_LR[0][1]
    THETA_RIGHT_LINE = theta_LR[1][1]

# init_lines()
# print("Hier:")
# print(THETA_LEFT_LINE)
# print(THETA_RIGHT_LINE)

while(True):

    image = capture_frame()
    theta_LR = edit_frames(image) 

    global THETA_LEFT_LINE
    global THETA_RIGHT_LINE
    THETA_LEFT_LINE = theta_LR[0][1]
    THETA_RIGHT_LINE = theta_LR[1][1]
    time.sleep(0.5)
# cap.release()

