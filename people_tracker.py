#!/usr/bin/env python

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
from tkinter import *
import argparse
import imutils
import time
import dlib
import cv2
import os
import math
import threading
# project
import definitions
from bird_eye_view import *
from distance_measure import *
from homography import *
from person_detection import *
from utils import *
from contagion_risk_evaluator import *
from database_handle import *
import time


def people_tracker(args, database):

    risk_evaluator = ContagionRiskEvaluator()

    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromDarknet(args["config"], args["model"])
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    writer = None
    W = None
    H = None
    totalFrames = 0
    fps = FPS().start()

    video = get_video(args)

    print_colored(Color.PURPLE, "\nTo caliberate the system, you will be asked to enter 4 information:\n" +
        "  1. Two points - a line (on the floor): this represents a known distance in the real world e.g. the distance between two tables\n"+
        "  2. The length of the line you entered in the real world (in meters)\n" +
        "  3. The ground area (excluding walls) of the field-of-view of the camera e.g the sq meter area of a room\n" +
        "  4. Four points - a rectangle: this is going to be used as reference to the ground. Try to select a clean rectangle in the floor.\n")

    scene_to_ground_distance = setup_scene_to_ground_dist(video, args)
    area = prompt_input_area()
    # [[top-left], [top-right], [bottom-right], [bottom-left]]
    bird_eye_view = setup_bird_eye_view(video, args)
    #pts_src = [[606, 106], [806, 132], [511, 434],[201, 354]]

    #target side points
    # pts_dst = np.array([[int(src_image_width/8),0], [int(src_image_width*3/8),0], [int(src_image_width*3/8),src_image_height], [int(src_image_width/8),src_image_height]])
    pts_dst = [[int(440),250], [int(500),250], [int(500),350], [int(440),350]]

    # Calculate Homography
    homography = Homography()
    homography.compute_homography(bird_eye_view.image_coordinates, pts_dst)

    #display distorted image
    im_out = cv2.warpPerspective(bird_eye_view.frame, homography.H, (bird_eye_view.src_image_width, bird_eye_view.src_image_height))
    cv2.imshow("Top-view transformed image", im_out)

    #transform the 4 corners
    transformedCorners = []
    transformedCorners.append(homography.transform_point((0, 0)))
    transformedCorners.append(homography.transform_point((bird_eye_view.src_image_width, 0)))
    transformedCorners.append(homography.transform_point((bird_eye_view.src_image_width, bird_eye_view.src_image_height)))
    transformedCorners.append(homography.transform_point((0, bird_eye_view.src_image_height)))

    #TODO change this
    transformered_height = transformedCorners[2][1] - transformedCorners[1][1]
    transformered_width = transformedCorners[2][0] - transformedCorners[0][0]

    #transform line
    transformed_line = []
    transformed_line.append(homography.transform_point(scene_to_ground_distance.distance_sample_coordinates[0]))
    transformed_line.append(homography.transform_point(scene_to_ground_distance.distance_sample_coordinates[1]))
    transformed_line = np.array(transformed_line, dtype = "int32")

    grd_dist_scaler = obtain_ground_distance_scaler(
                            transformed_line,
                            scene_to_ground_distance.ground_distance_meters)

    # Initiates Map
    c_width = 499
    c_height = 499
    tk = Tk()
    canvas = Canvas(tk, width=c_width, height=c_height, bd=0, highlightthickness=0, background="black")
    canvas.pack()

    while True:
        frame = video.read()
        frame = frame[1] if args.get("input", False) else frame

        if args["input"] is not None and frame is None:
            break

        frame = imutils.resize(frame, width=1000)
        frame = bightness_contrast_enhance(frame, alpha = args["alpha"], beta = args["beta"])

        if W is None or H is None:
            (H, W) = frame.shape[:2]

        if (totalFrames % args["skip_frames"] != 0):
            totalFrames += 1
            fps.update()
            continue

        # convert the frame to a blob and pass the blob through the
        # network and obtain the detections
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
        swapRB=True, crop=False)
        net.setInput(blob)
        layerOutputs = net.forward(ln)

        people_detected = detect_people(args, W, H, layerOutputs)
        size_people_detected = len(people_detected)

        for i in range(size_people_detected):

            current_person_bp = homography.transform_point(people_detected[i].bottom_point)

            people_detected[i].coordinates = [
                interpolation(transformedCorners[0][0], 0, (transformered_width + transformedCorners[0][0]), c_width, current_person_bp[0]),
                interpolation(transformedCorners[1][1], 0, (transformered_height + transformedCorners[1][1]), c_height, current_person_bp[1])]

            for k in range(2):
                if people_detected[i].coordinates[k] < 0:
                   people_detected[i].coordinates[k] = 0
                elif people_detected[i].coordinates[k] > 499:
                    people_detected[i].coordinates[k] = 499

            for j in range(i+1, size_people_detected):

                neighbor_bp = homography.transform_point(people_detected[j].bottom_point)

                pixel_distance = euclidian_distance(
                    current_person_bp[0], current_person_bp[1], neighbor_bp[0], neighbor_bp[1])

                #hardcoded for now
                distance = grd_dist_scaler * pixel_distance

                if distance < 2:
                    people_detected[i].safe = False
                    people_detected[j].safe = False

        #representation
        for person in people_detected:
            # draw a bounding box rectangle and label on the frame

            #if person is safe color is green otherwise is red
            color = (0, 255, 0) if person.safe else (0, 0, 255)

            #compute bounding box coordinates
            bb_x = int(person.centroid[0] - person.width/2)
            bb_y = int(person.centroid[1] - person.height/2)

            cv2.rectangle(frame, (bb_x, bb_y), (bb_x + person.width, bb_y + person.height), color, 2)

            for infected_with_idx in person.infected_with:
                if euclidian_distance(person.centroid[0], person.centroid[1], people_detected[infected_with_idx].centroid[0], people_detected[infected_with_idx].centroid[1]) < 200:
                    cv2.line(frame, person.centroid, people_detected[infected_with_idx].centroid, (0, 0, 255), 2) 


            color = "green" if person.safe else "red"
            canvas.create_oval(
                (person.coordinates[0] - 5),
                (person.coordinates[1] - 5),
                (person.coordinates[0] + 5),
                (person.coordinates[1] + 5),
                fill=color)

        people_not_safe = 0
        coordinates = []
        for person in people_detected:
            if not person.safe:
                people_not_safe += 1
            coordinates.append(person.coordinates)

        risk_evaluator.update(people_not_safe, size_people_detected, size_people_detected)
        risk = risk_evaluator.compute_risk()
        environmental_risk = risk_evaluator.compute_environmental_risk()
        geographical_risk = risk_evaluator.compute_geo_risk()
        #update database:
        database.update_information(size_people_detected/10, people_not_safe, environmental_risk, geographical_risk, risk, coordinates)

        database.update = True

        print("PEOPLE IN IMAGE: {}".format(len(people_detected)),
                "PEOPLE PER SQ METER: {}".format(len(people_detected)/area if len(people_detected) > 0 else 0))

        canvas.update_idletasks()
        canvas.update()

        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        #To halt process
        if key == ord("q"):
            break

        totalFrames += 1
        fps.update()

        canvas.delete("all")

    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    if writer is not None:
        writer.release()
    if not args.get("input", False):
        video.stop()
    else:
        video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-cfg", "--config", required=True, help="path to the yolo config file.")
    parser.add_argument("-m", "--model", required=True, help="path to the yolo weight file")
    parser.add_argument("-i", "--input", type=str, help="path to optional input video file")
    parser.add_argument("-o", "--output", type=str, help="path to optional output video file")
    parser.add_argument("-c", "--confidence", type=float, default=0.2, help="minimum probability to filter weak detections")
    parser.add_argument("-s", "--skip_frames", type=int, default=3,help="# of skip frames between detections")
    parser.add_argument("-l", "--labels", type=str, help="path to the classes file")
    parser.add_argument("-t", "--threshold", type=float, default=0.2, help="threshold when applying non-maxima suppression")
    parser.add_argument("-a", "--alpha", type=float, default=1.0, help="alpha parameter for for input frame contrast enhancement (0 - 3")
    parser.add_argument("-b", "--beta", type=float, default= 0, help="beta parameter for input frame brightness enhancement (0 - 100)")
    args = vars(parser.parse_args())

    definitions.setup(args)
    database = DataBase()
    t = threading.Thread(target=database.update_database)
    t.start()
   
    people_tracker(args, database)
