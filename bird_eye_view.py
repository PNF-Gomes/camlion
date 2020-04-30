#!/usr/bin/env python

import argparse
import cv2
import imutils
import numpy as np
# project
from color import Color
from utils import *

MAX_COORDINATES = 4

class BirdEyeView(object):

    def __init__(self, capture):
        self.capture = capture
        self.frame = np.array([])
        self.image_coordinates = []
        self.coordinates_sizes = []
        self.src_image_width = 0
        self.src_image_height = 0

    def set_frame(self, args):
        if (self.capture.isOpened()):
            (self.status, self.frame) = self.capture.read()
            self.frame = imutils.resize(self.frame, width=1000)
            self.frame = bightness_contrast_enhance(self.frame, alpha = args["alpha"], beta = args["beta"])

            self.src_image_height = self.frame.shape[0]
            self.src_image_width = self.frame.shape[1]

    def get_four_point_view(self, args = None):
        if (not self.frame.any()):
            if (not args):
                print("Frame not defined.")
                exit(-1)
            self.set_frame(args)

        cv2.imshow('First frame', self.frame)

        self.clone = self.frame.copy()
        cv2.namedWindow('First frame')
        cv2.setMouseCallback('First frame', self.extract_coordinates)

        key = cv2.waitKey(0) & 0xFF
        if (key == ord('q')):
            cv2.destroyAllWindows()
            exit(1)
        else:
            cv2.destroyWindow('First frame')

    def extract_coordinates(self, event, x, y, flags, parameters):
        if (event != cv2.EVENT_LBUTTONDOWN or len(self.image_coordinates) == MAX_COORDINATES):
            return

        radius = 2
        thickness = 3
        color = (0,0,255) # Red
        cv2.circle(self.clone, (x,y), radius, color, thickness)
        self.image_coordinates.append((x,y))

        last_coord = len(self.image_coordinates)-1
        if (last_coord > 0):
            cv2.line(self.clone, self.image_coordinates[last_coord], self.image_coordinates[last_coord-1], color, 1)

        if (len(self.image_coordinates) == MAX_COORDINATES):
            print('Maximum numbers of coordinates entried. Please click any key to continue.')
            radius = 3
            thickness = 4
            color = (255,0,0) # Blue
            for i in range(0, MAX_COORDINATES):
                connect = i-1 if (i != 0) else (MAX_COORDINATES-1)
                cv2.circle(self.clone, self.image_coordinates[i], radius, color, thickness)
                cv2.line(self.clone, self.image_coordinates[i], self.image_coordinates[connect], color, 2)

        cv2.imshow('First frame', self.clone)

    def order_points(self):
        pts = np.array(self.image_coordinates, dtype = "int32")
        rect = np.zeros((MAX_COORDINATES, 2), dtype = "int32")

        sum = pts.sum(axis = 1)
        top_left = np.argmin(sum)
        bottom_right = np.argmax(sum)
        rect[0] = pts[top_left] # top-left
        rect[2] = pts[bottom_right] # bottom-right

        pts = np.delete(pts, top_left, 0)
        bottom_right = bottom_right if (bottom_right < top_left) else (bottom_right - 1)
        pts = np.delete(pts, bottom_right, 0)

        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)] # top-right
        rect[3] = pts[np.argmax(diff)] # bottom-left

        self.image_coordinates = rect

    def print_plane_coordinates(self):
        print(Color.LIGHTGRAY, end='')
        print('******************* Plane coordinates ***********************')
        print("Top-left: {}".format(self.image_coordinates[0]))
        print("Top-right: {}".format(self.image_coordinates[1]))
        print("Bottom-right: {}".format(self.image_coordinates[2]))
        print("Bottom-left: {}".format(self.image_coordinates[3]))
        print('************************************************************')
        print(Color.ENDC)


def setup_bird_eye_view(video, args):
    start = False
    while (not start):
        print_colored(Color.CYAN, "\n4. Please input the 4 coordinates in image.")
        birdEyeView = BirdEyeView(video)
        birdEyeView.set_frame(args)
        birdEyeView.get_four_point_view()
        start = continue_after_bird_eye()

    birdEyeView.order_points()
    birdEyeView.print_plane_coordinates()

    return birdEyeView

def continue_after_bird_eye():
    print(Color.BLUE, end='')
    start = input("Are you satisfied with the points marked? [Y/n/q] ")
    print(Color.ENDC, end='')

    if (start.lower() == 'y'):
        return True
    elif(start.lower() == 'n'):
        return False
    elif(start.lower() == 'q'):
        print("\nQuitting the program...")
        return exit(1)
    else:
        print("Didn't get that...")
        return continue_after_bird_eye()
