#!/usr/bin/python

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
TRIG_OUT = 17
ECHO_IN = 27

while True:
  print "Measuring Distance...\n"

  GPIO.setup(TRIG_OUT, GPIO.OUT)
  GPIO.setup(ECHO_IN, GPIO.IN)

  GPIO.output(TRIG_OUT, False)
  print "Waiting for sensor...\n"
  time.sleep(2)

  GPIO.output(TRIG_OUT, True)
  time.sleep(0.00001)
  GPIO.output(TRIG_OUT, False)

  while GPIO.input(ECHO_IN) == 0:
    pulse_start = time.time()
  while GPIO.input(ECHO_IN) == 1:
    pulse_end = time.time()

  pulse_duration = pulse_end - pulse_start
  distance = pulse_duration * 17150
  distance = round(distance, 2)
  print "Distance: ", distance, " cm"
  time.sleep(1)

GPIO.cleanup()


