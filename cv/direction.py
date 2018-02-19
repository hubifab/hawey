import numpy as np

STOP    = 9002
LEFT    = 9003
CENTER  = 9004
RIGHT   = 9005

L = 0
R = 1

#############################################################################
# DEF DIRECTION DESCRIPTION:
# argument THETA[] inlcudes ancle values for left and right line
# generated with cv2.houghLine - function
#############################################################################
def direction(thetas):
    direction = CENTER
    theta_l = None
    theta_r = None
    
    # generate comparable ancles theta_l & theta_r 
    if (isinstance(thetas[L], float)):
        theta_l = (np.pi / 2) - thetas[L]
    if (isinstance(thetas[R], float)):
        theta_r = -(0.5 * np.pi) + thetas[R]
    
    print('transfomred data: ' + str(theta_l), str(theta_r))

    # CASE both ancles are detected
    if (isinstance(theta_l, float)) and (isinstance(theta_r, float)): 
        if (theta_l > theta_r):
            print('theta_l = ' + str(theta_l) + '\t\ttheta_r = ' + str(theta_l) )
            direction = RIGHT
            print('beides floates')
        elif (theta_r > theta_l):
            direction = LEFT 
        else:
            direction = CENTER
            print('left: '+ str(theta_l)+  '\tright: ' + str(theta_r) )

    # CASE there is no right line value -> turn right
    print('right is NOT a float: ' + str(not isinstance(thetas[R], float)))
    if (isinstance(theta_l, float)) and (not isinstance(thetas[R], float)):
        direction = RIGHT
    # CASE there is no left line value -> turn left
    elif (isinstance(theta_r, float)) and (not isinstance(thetas[L], float)):
        direction = LEFT
    # CASE no lines are detected -> stop
    elif  (not isinstance(thetas[L], float)) and (not isinstance(thetas[R], float)):
        direction = STOP

    return direction

empty_list = [[np.pi / 4, 3*np.pi / 4],['N/A',1.1],[1.1,'N/A'],['N/A','N/A']]

print('np.pi: ' + str(np.pi))

for data in empty_list:
    print('\n############### data sent: ' + str(data))
    print('direction: ' + str(direction(data)))





