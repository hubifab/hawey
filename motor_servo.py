
from __future__ import division
import time

import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()

servo_min = 102
servo_mid = 307
servo_max = 512

pwm.set_pwm_freq(50)

print('Moving servo on channel 0, press Ctrl-C to quit')


#while True:
pwm.set_pwm(1,0,331)
time.sleep(3)
pwm.set_pwm(1,0,307)
#time.sleep(1)

