#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv2
import os
import sys
import os.path
import numpy as np
import math

# importes para emular precionamento de teclas
from pynput.keyboard import Key, Controller
import pynput
import time
import random

keys = {
    'A': pynput.keyboard.KeyCode.from_char('a'),  
    'D': pynput.keyboard.KeyCode.from_char('d'),  
    'W': pynput.keyboard.KeyCode.from_char('w'),  
    'S': pynput.keyboard.KeyCode.from_char('s'),  
}

keyboard = Controller()

# HSV color mask for red color
red_lower_hsv = np.array([0, 200, 80])
red_upper_hsv = np.array([30, 255, 255])

# HSV color mask for cyan color
cyan_lower_hsv = np.array([70, 100, 100])
cyan_upper_hsv = np.array([90, 210, 255])

# --------- Methods ---------


def getMask(img):
    # Apply masks
    red_mask = colorFilter(img, red_lower_hsv, red_upper_hsv)
    cyan_mask = colorFilter(img, cyan_lower_hsv, cyan_upper_hsv)

    mask = cv2.bitwise_or(red_mask, cyan_mask)

    mask_copy = mask.copy()
    mask_rgb = cv2.cvtColor(mask_copy, cv2.COLOR_GRAY2RGB)

    # Get Contours and Mass
    mass_red, cX_red, cY_red = drawContourFilter(mask_rgb, red_mask)
    mass_cyan, cX_cyan, cY_cyan = drawContourFilter(mask_rgb, cyan_mask)

    if((cX_red != 0 and cY_red != 0) and (cX_cyan != 0 and cY_cyan != 0)):
        # Draw Center of Mass
        drawCenterOfMass(mask_rgb, cX_red, cY_red, 20, (255, 0, 0))
        drawCenterOfMass(mask_rgb, cX_cyan, cY_cyan, 20, (255, 0, 0))

        # Draw Line
        drawLine(mask_rgb, cX_red, cY_red, cX_cyan, cY_cyan)

        # Draw Angle
        angle = getAngle(mask_rgb, (cX_red, cY_red), (cX_cyan, cY_cyan))

        # Draw Text
        writeImageText(mask_rgb, f'{angle}', (cX_red, cY_red))
        writeImageText(
            mask_rgb, f'Mass Red: {mass_red}', (250, 300), (0, 255, 0))
        writeImageText(
            mask_rgb, f'Mass Cyan: {mass_cyan}', (250, 350), (0, 255, 0))

        if((mass_red > 3000) and (mass_cyan > 3000)):
            if(angle > 12):
                print("Press: ", keys['A'])
                keyboard.press(keys['A'])
                keyboard.release(keys['A'])
                keyboard.release(keys['D'])
            elif(angle < -12):
                print("Press: ", keys['D'])
                keyboard.press(keys['D'])
                keyboard.release(keys['D'])
                keyboard.release(keys['A'])
            if((mass_red > 5000) and (mass_cyan > 5000)):
                keyboard.press(keys['W'])
                keyboard.release(keys['S'])
            if((mass_red > 3000 and mass_red < 4000) and (mass_cyan > 3000 and mass_cyan < 4000)):
                keyboard.press(keys['S'])
                keyboard.release(keys['W'])
        else:
            for key in keys:
                keyboard.release(key)

    return mask_rgb


def colorFilter(img_bgr, low_hsv, high_hsv):
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img, low_hsv, high_hsv)
    return mask


def drawCenterOfMass(img, cX, cY, size, color):
    cv2.line(img, (cX - size, cY), (cX + size, cY), color, 5)
    cv2.line(img, (cX, cY - size), (cX, cY + size), color, 5)


def drawContourFilter(image, mask):
    contour, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    big = None
    big_area = 0
    cX = 0
    cY = 0

    for c in contour:
        area = cv2.contourArea(c)
        if area > big_area:
            big_area = area
            big = c

    M = cv2.moments(big)

    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.drawContours(image, [big], -1, [0, 255, 0], 5)

    return big_area, cX, cY


def drawLine(img, x, y, x2, y2):
    cv2.line(img, (x, y), (x2, y2), (0, 0, 255), thickness=3, lineType=8)


def writeImageText(img, text, position, color=(0, 0, 255)):
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(img, str(text), position, font, 1.2, color, 2, cv2.LINE_AA)


def getAngle(img, point1, point2):
    angRadian = math.atan2(point1[1]-point2[1], point1[0] - point2[0])
    angDegree = round(math.degrees(angRadian))

    return angDegree


# --------- Webcam ---------
def main():
    cv2.namedWindow("preview")
    # sets the video input for webcam
    video = cv2.VideoCapture(1)

    # config windows size
    video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if video.isOpened():  # try to get the first frame
        rval, frame = video.read()
    else:
        rval = False

    while rval:
        # passes the frame to the function and receives treated image in img
        img = getMask(frame)

        cv2.imshow("preview", img)
        cv2.imshow("original", frame)
        rval, frame = video.read()
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

    cv2.destroyWindow("preview")
    cv2.destroyWindow("original")
    video.release()


if __name__ == "__main__":
    main()
