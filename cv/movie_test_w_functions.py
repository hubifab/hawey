import numpy as np
import cv2 as cv
import io
import time
# from picamera import PiCamera as camera
from picamera import PiCamera
camera = PiCamera()

from picamera.array import PiRGBArray
videostream = PiRGBArray(camera)

DOTS_PER_LINE = 100

pi = 3.1419
theta_left_line 	= 0.40 	# mean value in RAD of vertical-angle LEFT line
theta_right_line 	= 2.74	# mean value in RAD of vertical-angle RIGHT line
divergence 		= 0.1	# angle tolerance for values close to the line

cv.namedWindow('Bildchen')
cv.moveWindow('Bildchen',10,10)

def draw_lines(frame,line_data):
    # print line
    if all(line_data):
        rho		= line_data[0]
        theta	= line_data[1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        cv.line(frame,(x1,y1),(x2,y2),(147,20,255),2)


def process_line_infos(frame):
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Convert to Canny image
    start = time.time() 
    canny = cv.Canny(gray, 80,100)
    end = time.time()
    print "Canny \ttime: " + str(end - start) + " s\n"
    # cv.imshow('canny', canny)
    # cv.waitKey()
    # cv.destroyAllWindows()

    # Find lane lines
    start = time.time()
    lines = cv.HoughLines(canny,1,np.pi/180, DOTS_PER_LINE)
    end = time.time()
    print "Houghlines \ttime: " + str(end - start) + " s\n"
    print 'return value HoughLines: ' + str(lines) 
    return lines

def edit_frames(frame):
# 2nd argument 0: import as gray-scale-frame
# while(True):
    # Capture frame-by-frame
    # ret, frame = cap.read()
        
    lines = process_line_infos(frame)
    
    line_list = []
    # find the relevant lane-line
    for i in range(len(lines)):
        for rho,theta in lines[i]:
            print "rho: " + str(rho) + "\ttheta: " + str(theta/pi*180)
            new_element = [rho,theta]
            line_list.append(new_element)

    # sort list by theta 	
    sorted_list = sorted(line_list, key=lambda x: x[1])

    # generate lists for left line and right line
    left_line_list = []
    right_line_list = []
    for line in sorted_list:
        # show all detected line infos:
        # print(line)
        if abs(line[1] - theta_left_line) < divergence:
            left_line_list.append(line)
        if abs(line[1] - theta_right_line) < divergence:
            right_line_list.append(line)
    
    # print line infos

    # print('left_line_list')
    # print(left_line_list)
    # print('right_line_list')
    # print(right_line_list)
    

    # calculate mean-lines LEFT and RIGHT
    if any(left_line_list):
        line_left 	= np.mean(left_line_list, axis = 0)
        draw_lines(frame,line_left)
    if any(right_line_list):
        # draw lines into current frame
        line_right 	= np.mean(right_line_list, axis = 0)
        draw_lines(frame,line_right)
        # Display the resulting frame
    cv.imshow('Bildchen',frame)
    cv.waitKey(100)
    #cv.destroyAllWindows()
# if cv.waitKey(1) & 0xFF == ord('q'):
    #    break

   

# When everything done, release the capture
# cap = cv.VideoCapture(0)
while(True):
    start = time.time()

    # to speed up capturing process: not working yet
    # camera.capture(videostream, format='bgr')
    # image = stream.array

    stream = io.BytesIO()
    camera.capture(stream, format = 'png', use_video_port=True)

    # Construct a numpy array from the stream
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    image = cv.imdecode(data, 1)

    image = image[200:500, 0:600]
    end = time.time()
    print "Capture \ttime: " + str(end - start) + " s\n"
    # cv.imshow('test',image)
    # cv.waitKey()
    # cv.destroyAllWindows()
    edit_frames(image) 
    time.sleep(0.5)
# cap.release()

