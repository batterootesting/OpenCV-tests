#!/usr/bin/python
#
# measures the lap count and times of a model train
# usage notes:
# - create a video with a fixed camera of the test run
# - open a frame in an image editor and find two rectangle at opposite sides of the track, adjust "rect1" and "rect2" below
# - change the name of video file below in the function call cv2.VideoCapture
# - set interactive to True
# - run the script. You'll see the first frame of the video
# - hold down a key until the train is inside the first rect
# - press "h" to display a histogram. Use a value between the two peaks for the "threshold" variable
# - modify the isTrain dection function, if the simple dark/bright detection doesn't work
# - open the video in a video player
# - define the test cases in the startStop array
# - change interactive to False
# - run the script again
# more details are here: http://www.eevblog.com/forum/projects/batteroo-testing/msg1098831/#msg1098831
# the current values for this script were used to measure the lap counts and times for this video: http://www.frank-buss.de/batteroo/batteroo-full.mp4

import cv2
import sys
import math
from matplotlib import pyplot as plt

# in interactive mode, hold down a key to show the video, press "h" to draw the histogram
# and esc to stop (you have to close the histogram window, first)
interactive = False

# open video file
video = cv2.VideoCapture("./batteroo-full.mp4")

# regions for analyzing where the train is
# first rect for detecting round start, second rect to arm the first rect detection
rect1 = [ (387, 79), (404, 128) ]
rect2 = [ (384, 457), (398, 499) ]

# gray threshold to distinguish dark from bright pixels
# use the interactive mode to determine a good value
threshold = 80

# track length, in feet
trackDiameterCm = 21.8
trackLengthCm = math.pi * trackDiameterCm
trackLength = trackLengthCm * 0.0328084

# define measure cycles, with start and stop time in seconds
def hms2sec(h, m, s):
  return (h * 60.0 + m) * 60.0 + s
startStop = [
  ("fresh battery, no Batteroo sleeve", hms2sec(0, 0, 26), hms2sec(2, 8, 7)),
  ("fresh battery, with Batteroo sleeve", hms2sec(2, 9, 15), hms2sec(3, 7, 58)),
  ("battery from first test, with Batteroo sleeve", hms2sec(3, 8, 49), hms2sec(3, 12, 35))
]

# train detection:
# if the number of dark pixels is greater than the number of bright pixels, the train is detected
def isTrain(grayValues):
  dark = 0
  bright = 0
  for v in grayValues:
    if v > threshold:
      bright += 1
    else:
      dark += 1
  return dark > bright

# get a rectangle area from an image and convert it to gray
def getGrayRect(image, rect):
  roi = image[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]]
  return cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)

# init runtime variables
armed = False
lapCount = 0
lastFrameCount = 0
frameCount = 0
cylceRunning = False

# show video information
fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
print("fps: " + str(fps))
print("track length in cm: " + str(trackLengthCm))
print("track length in feet: " + str(trackLength))

# start lap counting
print("lap number,lap start time,lap end time,total lap time,feet per minute speed")
while True:
  if video .grab():
    # get next frame
    flag, frame = video.retrieve()
    
    # test cycle
    test, start, stop = startStop[0]
    timeIndex = frameCount / fps
    frameCount += 1
    if not interactive:
      if cylceRunning:
        # if a cycle has started, wait for stop
        if timeIndex > stop:
          cylceRunning = False
          startStop = startStop[1:]
          if len(startStop) == 0: break
      else:
        # otherwise wait for start
        if timeIndex >= start:
          print(test + ", start at " + str(start) + " s, stop at " + str(stop) + " s")
          cylceRunning = True
          lastFrameCount = 0
          lapCount = 0
        else:
          continue

    # get the two detection areas
    roi1 = getGrayRect(frame, rect1)
    roi2 = getGrayRect(frame, rect2)

    # flatten values
    grayValues1 = roi1.ravel()
    grayValues2 = roi2.ravel()
    
    # check if the train is inside
    train1 = isTrain(grayValues1)
    train2 = isTrain(grayValues2)
    
    # draw marker in interactive mode and show image
    if interactive:
      if train1:
        cv2.rectangle(frame, rect1[0], rect1[1], (0, 255, 0), 2)
      if train2:
        cv2.rectangle(frame, rect2[0], rect2[1], (0, 255, 0), 2)
      cv2.imshow('video', frame)
    
    # wait until train enters rect2, then arm
    if train2:
      armed = True

    # when armed and train enters rect1, then count a lap and disarm
    if armed and not train2:
      if train1:
        armed = False
        # count only if train was once inside rect1
        if lastFrameCount > 0:
          lapCount += 1
          lapStartTime = lastFrameCount / fps
          lapStopTime = frameCount / fps
          totalLapTime = lapStopTime - lapStartTime
          speed = trackLength / totalLapTime * 60
          print(str(lapCount) + "," + str(lapStartTime) + "," + str(lapStopTime) + "," + str(totalLapTime) + "," + str(speed))
        lastFrameCount = frameCount

    # wait for key press in interactive mode
    if interactive: 
      key = cv2.waitKey()
      if key == 27:
          break
      if key == ord("h"):
        plt.hist(grayValues1, bins = 32)
        plt.hist(grayValues2, bins = 32)
        plt.show()
print("frames: " + str(frameCount))
