
import numpy as np

# define constants
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 380


#############################################################################
# DEF VANISHING POINT DESCRIPTION:
# argument THETA[] inlcudes ancle values for left and right line
# generated with cv2.houghLine - function
#############################################################################
def vp(lines_LR):
    
    vp_x = None
    alpha_L = None
    alpha_R = None
    offset_L = None
    offset_R = None

    rho_L = lines_LR[0][0]
    rho_R = lines_LR[1][0]
    theta_L = lines_LR[0][1]
    theta_R = lines_LR[1][1]
    print('rho_L: ' + str(rho_L))
    print('theta_L:' + str(theta_L))
    print('rho_R: ' + str(rho_R))
    print('theta_R:' + str(theta_R))

    # generate comparable offsets: offset_L and offset_R; origin is upper left
    # corner
    if (isinstance(rho_L, np.float32) and isinstance(theta_L,np.float32)):
        offset_L = -rho_L/(np.cos((np.pi/2)-theta_L))
    if (isinstance(rho_R, np.float32) and isinstance(theta_R,np.float32)):
        offset_R = -rho_R/np.cos(theta_R-(np.pi/2))
    #    offset_R = (IMAGE_WIDTH+(rho_R/np.cos(np.pi-theta_R))) / np.tan(np.pi-theta_R)
    
    
    # generate comparable angles alpha_L and alpha_R 
    if (isinstance(theta_L, np.float32)):
        alpha_L = (np.pi/2)-theta_L
    if (isinstance(theta_R, np.float32)):
        alpha_R = theta_R-(np.pi/2)
    
    print('alpha_L: ' + str(np.rad2deg(alpha_L)))
    print('offset_L: ' + str(offset_L))
    print('alpha_R: ' + str(np.rad2deg(alpha_R)))
    print('offset_R: ' + str(offset_R))

    vp_x = (offset_R-offset_L)/(np.tan(alpha_L)+np.tan(alpha_R))

    print('tan(alpha_L:' + str(np.tan(alpha_L)))
    print('tan(alpha_R:' + str(np.tan(alpha_R)))
    print('vp_x: ' + str(vp_x))

    return vp_x
