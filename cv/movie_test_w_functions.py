import numpy as np
import cv2 as cv

pi = 3.1419
theta_left_line 	= 1.27 	# mean value in RAD of vertical-angle LEFT line
theta_right_line 	= 1.95	# mean value in RAD of vertical-angle RIGHT line
divergence 		    = 0.1	# angle tolerance for values close to the line

def draw_lines(frame,line_data):
    # print line 
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
    cv.line(frame,(x1,y1),(x2,y2),(0,0,255),2)


def process_line_infos(frame):
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Convert to Canny image
    canny = cv.Canny(gray, 10,80)
    # Find lane lines
    lines = cv.HoughLines(canny,1,np.pi/180,300) 
    return lines

def edit_frames(cap):
    # 2nd argument 0: import as gray-scale-frame
     while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
   
        lines = process_line_infos(frame)
        
        line_list = []
        # find the relevant lane-line
        for i in range(len(lines)):
            for rho,theta in lines[i]:
                # print('rho: ' + str(rho) +'\ttheta: ' + str(theta/pi*180) )
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
        '''
        print('left_line_list')
        print(left_line_list)
        print('right_line_list')
        print(right_line_list)
        '''

        # calculate mean-lines LEFT and RIGHT
        line_left 	= np.mean(left_line_list, axis = 0)
        line_right 	= np.mean(right_line_list, axis = 0)
        ''' 
        # draw lines into current frame
        draw_lines(frame,line_left)
        draw_lines(frame,line_right)
        '''
        # Display the resulting frame
        cv.imshow('frame',frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

   
def main():
# When everything done, release the capture
    cap = cv.VideoCapture('movies/video.mp4')
    
    edit_frames(cap) 

    cap.release()
    cv.destroyAllWindows()

main()
