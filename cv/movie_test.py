import numpy as np
import cv2 as cv

pi = 3.1419
theta_left_line 	= 1.27 	# mean value in RAD of vertical-angle LEFT line
theta_right_line 	= 1.95	# mean value in RAD of vertical-angle RIGHT line
divergence 		= 0.1	# angle tolerance for values close to the line
# described in "learning opencv", Bradski, Kaehler, p. 155

# 2nd argument 0: import as gray-scale-frame
cap = cv.VideoCapture('movies/video.mp4')

while(True):
    # Capture frame-by-frame
	ret, frame = cap.read()
    # Our operations on the frame come here
	gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Convert to Canny image
	canny = cv.Canny(gray, 10,80)
    # Find lane lines
	lines = cv.HoughLines(canny,1,np.pi/180,300)    
	'''   
    # show all identified lines
	for i in range(len(lines)):
		for rho, theta in lines[i]:
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))
			cv.line(frame,(x1,y1),(x2,y2),(0,0,255),2)	# color order: BLUE-GREEN-RED
	cv.imshow('with lines',image) 
	cv.waitKey(0)            		# Waits forever for user to press any key
	cv.destroyAllWindows()  
	'''

	# find the relevant lane-lines
	line_list = []
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
		print(line)
		if abs(line[1] - theta_left_line) < divergence:
			left_line_list.append(line)
		if abs(line[1] - theta_right_line) < divergence:
			right_line_list.append(line)

	print('left_line_list')
	print(left_line_list)
	print('right_line_list')
	print(right_line_list)

	# calculate mean-lines LEFT and RIGHT
	line_left 	= np.mean(left_line_list, axis = 0)
	line_right 	= np.mean(right_line_list, axis = 0)

	# print left line 
	rho		= line_left[0]
	theta	= line_left[1]
	a = np.cos(theta)
	b = np.sin(theta)
	x0 = a*rho
	y0 = b*rho
	x1 = int(x0 + 1000*(-b))
	y1 = int(y0 + 1000*(a))
	x2 = int(x0 - 1000*(-b))
	y2 = int(y0 - 1000*(a))
	cv.line(frame,(x1,y1),(x2,y2),(0,0,255),2)	# color order: BLUE-GREEN-RED


	# print right line 
	rho		= line_right[0]
	theta	= line_right[1]
	a = np.cos(theta)
	b = np.sin(theta)
	x0 = a*rho
	y0 = b*rho
	x1 = int(x0 + 1000*(-b))
	y1 = int(y0 + 1000*(a))
	x2 = int(x0 - 1000*(-b))
	y2 = int(y0 - 1000*(a))
	cv.line(frame,(x1,y1),(x2,y2),(0,0,255),2)	# color order: BLUE-GREEN-RED
	
    
    
    # Display the resulting frame
	cv.imshow('frame',frame)
	if cv.waitKey(1) & 0xFF == ord('q'):
		break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
