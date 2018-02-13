import cv2
import numpy as np

pi = 3.1419
theta_left_line 	= 2.08	# mean value in RAD of vertical-angle LEFT line
theta_right_line 	= 1.06	# mean value in RAD of vertical-angle RIGHT line
divergence 			= 0.03	# angle tolerance for values close to the line
# described in "learning opencv", Bradski, Kaehler, p. 155

# import image
image = cv2.imread('images/lane_lines_02.jpg')
# image = cv2.imread(/images/'lane_lines.jpg')
# convert image
gray_image	= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
canny		= cv2.Canny(gray_image, 190, 210)
cv2.waitKey(0)                 # Waits forever for user to press any key
cv2.destroyAllWindows()
# cv2.imwrite('gray_image.png',gray_image)
# cv2.imshow('color_image',image)
cv2.imshow('current version',canny) 


lines = cv2.HoughLines(canny,1,np.pi/180,200)

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
cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)	# color order: BLUE-GREEN-RED

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
cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)	# color order: BLUE-GREEN-RED


'''
minLineLength = 30
maxLineGap = 10
lines = cv2.HoughLinesP(canny,1,np.pi/180,100,minLineLength,maxLineGap)
for x1,y1,x2,y2 in lines[0]:
    cv2.line(image,(x1,y1),(x2,y2),(0,255,0),2)
'''


cv2.imshow('with lines',image) 

cv2.waitKey(0)                 # Waits forever for user to press any key
cv2.destroyAllWindows()  
