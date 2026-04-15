# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 15:19:31 2022

@author: HUINS-AI
"""

import cv2
vidcap = cv2.VideoCapture(r"C:\Users\HUINS-AI\Desktop\20220311_134804.mp4")
success,image = vidcap.read()
count = 0
while success:
    # if count % 15 == 0:
    cv2.imwrite(r"C:\Users\HUINS-AI\Desktop\sign\%06d.jpg" % count, image)     # save frame as JPEG file
    success,image = vidcap.read()
    # print('Read a new frame: ', success)
    count += 1