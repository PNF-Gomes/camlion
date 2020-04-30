#!/usr/bin/env python

import numpy as np
import cv2
import math

class Homography:

    def __init__(self):
        pass

    def transform_point(self, src_point):
        pt1 = np.array([src_point[0], src_point[1], 1])
        pt1 = pt1.reshape(3, 1)
        pt2 = np.dot(self.H, pt1)
        pt2 = pt2/pt2[2]
        trg_point = (int(pt2[0]), int(pt2[1]))
        return trg_point

    def compute_homography(self, src_pts, trg_pts):
        self.H, _ = cv2.findHomography(np.array(src_pts), np.array(trg_pts))
