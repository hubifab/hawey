import numpy as np

# define constants
STOP    = 9002
LEFT    = 9003
CENTER  = 9004
RIGHT   = 9005
FWD     = 9001
L = 0
R = 1
IMAGE_WIDTH = 640

local_status = STOP

#############################################################################
# DEF DIRECTION DESCRIPTION:
# argument THETA[] inlcudes ancle values for left and right line
# generated with cv2.houghLine - function
#############################################################################
def getDirection(lines_LR):
    direction = CENTER
    global local_status
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

    # generate comparable offsets: offset_L and offset_R 
    if (isinstance(rho_L, np.float32) and isinstance(theta_L,np.float32)):
        offset_L = rho_L/(np.cos((np.pi/2)-theta_L))
    if (isinstance(rho_R, np.float32) and isinstance(theta_R,np.float32)):
        offset_R = (IMAGE_WIDTH+(rho_R/np.cos(np.pi-theta_R))) / np.tan(np.pi-theta_R)
    
    # generate comparable angles alpha_L and alpha_R 
    if (isinstance(theta_L, np.float32)):
        alpha_L = (180/np.pi) * ((np.pi/2)-theta_L)
    if (isinstance(theta_R, np.float32)):
        alpha_R = (180/np.pi) * (theta_R-(np.pi/2)) 
    
    # print('alpha_L: ' + str(alpha_L))
    # print('offset_L: ' + str(offset_L))
    # print('alpha_R: ' + str(alpha_R))
    # print('offset_R: ' + str(offset_R))


    # CASE both angles are detected
    if (isinstance(alpha_L, float)) and (isinstance(alpha_R, float)): 
        # direction = alpha_L - alpha_R
        # if car is standing, call FWD
        if local_status == STOP:
            local_status = FWD
            print ("direction: commencing forward movement...")
            return FWD

        if (alpha_L < alpha_R):
            # print('alpha_L = ' + str(alpha_L) + '\t\talpha_R = ' + str(alpha_L) )
            direction = RIGHT
            # print('beides floates')
        elif (alpha_R > alpha_L):
            direction = LEFT 
        else:
            direction = CENTER
            # print('left: '+ str(alpha_L)+  '\tright: ' + str(alpha_R) )

    # CASE there is no right line value -> turn right
    # print('right is NOT a float: ' + str(not isinstance(alpha_R, float)))
    if (isinstance(alpha_L, float)) and (not isinstance(alpha_R, float)):
        direction = RIGHT
    # CASE there is no left line value -> turn left
    elif (isinstance(alpha_R, float)) and (not isinstance(alpha_L, float)):
        direction = LEFT
    # CASE no lines are detected -> stop
    elif  (not isinstance(alpha_L, float)) and (not isinstance(alpha_R, float)):
        direction = STOP
        local_status = STOP
        print ("direction: STOP (no lines detected)")


    return direction

# empty_list = [[np.pi / 4, 3*np.pi / 4],['N/A',1.1],[1.1,'N/A'],['N/A','N/A']]

# print('np.pi: ' + str(np.pi))

# for data in empty_list:
#     print('\n############### data sent: ' + str(data))
#     print('direction: ' + str(direction(data)))





