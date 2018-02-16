#! /usr/bin/python
import cv2
import numpy as np

img = cv2.imread('../images/bild.png')


# cv2.imshow('hallo',img)
# cv2.waitKey()
# cv2.destroyAllWindows()

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# Canny(name, lower threshold, upper threshold)
edges = cv2.Canny(gray,80,100)

# cv2.imshow('hallo',edges)
# cv2.waitKey()
# cv2.destroyAllWindows()

#minLength = 20
#maxGap = 5
#HoughLinesP(output, offset resolution (1pixel), resolution angle(1 degree), threshold)
#lines: rho,theta
lines = cv2.HoughLines(edges,1,np.pi/180,200)
print(lines)


#show lines
for i in range(len(lines)):
    for rho, theta in lines[i]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 2000*(-b))
            y1 = int(y0 + 2000*(a))
            x2 = int(x0 - 2000*(-b))
            y2 = int(y0 - 2000*(a))
            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)     # color order: BLUE-GREEN-RED

# cv2.imshow('with lines',img) 
# cv2.waitKey()
# cv2.destroyAllWindows()

for i in range(len(lines)):
    lines[i][0][1] = lines[i][0][1]*(180/np.pi)

rightLines = []
leftLines = []


for line in lines:
    print(line)
    
    #if line[1] > 90
    #  rightLines.append(line)
    #if line[1] < 90
    #  leftLines.append(line)

print("Hallo")
print(rightLines)















