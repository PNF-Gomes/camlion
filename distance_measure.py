#!/usr/bin/env python

import argparse
import cv2
import imutils
import numpy as np
# project
from utils import *
from color import Color

LINE_EDGES = 2

class SceneToGroundDistance(object):

    def __init__(self, capture):
        self.capture = capture
        self.frame = np.array([])
        self.distance_sample_coordinates = []
        self.ground_distance_meters = 0

    def set_frame(self, args):
        if (self.capture.isOpened()):
            (self.status, self.frame) = self.capture.read()
            self.frame = imutils.resize(self.frame, width=1000)
            self.frame = bightness_contrast_enhance(self.frame, alpha = args["alpha"], beta = args["beta"])

    def get_two_points_view(self, args = None):
        """
            Groud sampled distance
        """
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
        if (event != cv2.EVENT_LBUTTONDOWN or len(self.distance_sample_coordinates) == LINE_EDGES):
            return

        radius = 2
        thickness = 3
        color = (0,0,255) # Red
        cv2.circle(self.clone, (x,y), radius, color, thickness)
        self.distance_sample_coordinates.append((x,y))

        if (len(self.distance_sample_coordinates) == LINE_EDGES):
            print('Line drawn. Please click any key to continue.')

            radius = 3
            thickness = 4
            color = (255,0,0) # Blue
            for i in range(0, LINE_EDGES):
                cv2.circle(self.clone, self.distance_sample_coordinates[i], radius, color, thickness)
            cv2.line(self.clone, self.distance_sample_coordinates[1], self.distance_sample_coordinates[0], color, 2)

        cv2.imshow('First frame', self.clone)

    def order_points(self):
        pts = np.array(self.distance_sample_coordinates, dtype = "int32")
        #rect = np.zeros((LINE_EDGES, 2), dtype = "int32")

        #sum = pts.sum(axis = 1)

        """
        left = np.argmin(sum)
        right = np.argmax(sum)
        rect[0] = pts[left] # left
        rect[1] = pts[right] # right
        """

        self.distance_sample_coordinates = pts[pts[:,0].argsort()]

    def ground_distance_input(self):
        accept = False
        while not accept:
            print(Color.BLUE, end='')
            get_value = input("\n3. Please inform the distance between these 2 points (in meters): ")
            print(Color.ENDC, end='')

            try:
                input_value = float(get_value)
                accept = True
                return input_value
            except ValueError:
                if(get_value.lower() == 'q'):
                    print("\nQuitting the program...")
                    return exit(1)
                else:
                    print('Input must be numeric, e.g 1.5, 12, 50, 100.58, 200....')
                    return prompt_input_area()


    def print_plane_coordinates(self):
        print(Color.LIGHTGRAY, end='')
        print('******************* Line coordinates ***********************')
        print("Point A: {}".format(self.distance_sample_coordinates[0]))
        print("Point B: {}".format(self.distance_sample_coordinates[1]))
        print('************************************************************')
        print(Color.ENDC)


def setup_scene_to_ground_dist(video, args):
    start = False
    while (not start):
        print_colored(Color.CYAN, "\n2. Please input coordinates of line in image.")
        sceneToGroundDistance = SceneToGroundDistance(video)
        sceneToGroundDistance.set_frame(args)
        sceneToGroundDistance.get_two_points_view()
        sceneToGroundDistance.ground_distance_meters = sceneToGroundDistance.ground_distance_input()
        start = continue_after_bird_eye()

    sceneToGroundDistance.order_points()
    sceneToGroundDistance.print_plane_coordinates()

    return sceneToGroundDistance

def continue_after_bird_eye():
    print(Color.BLUE, end='')
    start = input("Are you satisfied with the line drawn? [Y/n/q] ")
    print(Color.ENDC, end='')

    if (start.lower() == 'y'):
        return True
    elif(start.lower() == 'n') or ():
        return False
    elif(start.lower() == 'q'):
        print("\nQuitting the program...")
        return exit(1)
    else:
        print("Didn't get that...")
        return continue_after_bird_eye()
