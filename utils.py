#!/usr/bin/env python

import numpy as np
import cv2
import math
# project
from color import Color

def get_video(args):
    if not args.get("input", False):
        print("[INFO] starting video stream...")
        video = VideoStream(src=0).start()
        time.sleep(2.0)
    else:
        print("[INFO] opening video file...")
        video = cv2.VideoCapture(args["input"])
    return video

def euclidian_distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

def interpolation(x1, y1, x2, y2, x):
    return y1 + ((x-x1)/(x2-x1))*(y2-y1)

def bightness_contrast_enhance(image, alpha = 1.6, beta = 0):
    """
        alpha  = Contrast control (1.0-3.0)
        beta = # Brightness control (0-100)
    """
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def obtain_ground_distance_scaler(coord, meters):
    pixel_distance = euclidian_distance(coord[0][0], coord[0][1], coord[1][0], coord[1][1])
    return (meters/pixel_distance)

def print_colored(color, text):
    print("{color}{text}{reset}".format(color=color, text=text, reset=Color.ENDC))

def prompt_input_area():
    accept = False
    while not accept:
        print(Color.BLUE, end='')
        get_value = input("\n3. Please input the area of the field-of-view(in sq meters): ")
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

def confirm_choice():
    print(Color.BLUE, end='')
    start = input("Are you satisfied? [Y/n/q] ")
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
        return confirm_choice()
