#!/usr/bin/env python

import numpy as np
import cv2
import math
# project
import definitions

class PersonDetection:

    def __init__(self, centroid, width, height):
        self.centroid = centroid    # tuple (x,y) [pixeis]
        self.width = width          # bounding_box width
        self.height = height        # bounding_box height
        self.bottom_point = self.compute_bottom_point() #bottom points is in source image pixel coordinates
        self.safe = True            # person is safe until someone is detected nearby
        self.coordinates = None

    def compute_bottom_point(self):
        return (self.centroid[0], self.centroid[1] + self.height/2)


def detect_people(args, W, H, layerOutputs):
    boxes = []
    confidences = []
    centroids = []
    people_detected = []

    for output in layerOutputs:

        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]

            if (definitions.LABELS[classID] == "person" and confidence > args["confidence"]):
                # scale the bounding box coordinates back relative to the size of the image
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                centroids.append((centerX, centerY))

    detection_ids = cv2.dnn.NMSBoxes(boxes, confidences, args["confidence"], args["threshold"])

    if (len(detection_ids) > 0):
        detection_ids_flattened = detection_ids.flatten()
        for i in detection_ids_flattened:
            (w, h) = (boxes[i][2], boxes[i][3])
            people_detected.append(PersonDetection(centroids[i], w, h))

    return people_detected
