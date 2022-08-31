import getopt
import os.path
import sys
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt


def CalcHistograms(objects):
    Histograms = []
    for i in range(len(objects)):
        hist1 = cv2.calcHist(objects[i][:, :, 0], [0], None, [256], [1, 254])
        hist2 = cv2.calcHist(objects[i][:, :, 1], [0], None, [256], [1, 254])
        hist3 = cv2.calcHist(objects[i][:, :, 2], [0], None, [256], [1, 254])

        cv2.normalize(hist1, hist1, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(hist3, hist3, 0, 255, cv2.NORM_MINMAX)

        Histograms.append([hist1, hist2, hist3])

    return Histograms


def CompHistograms(hist1, hist2):
    mean_j = []
    sum = 0

    for i in range(len(hist1)):
        sum = 0
        for j in range(len(hist2)):
            comparison1 = cv2.compareHist(hist1[i][0], hist2[j][0], cv2.HISTCMP_BHATTACHARYYA)
            comparison2 = cv2.compareHist(hist1[i][1], hist2[j][1], cv2.HISTCMP_BHATTACHARYYA)
            comparison3 = cv2.compareHist(hist1[i][2], hist2[j][2], cv2.HISTCMP_BHATTACHARYYA)
            comparison = (comparison1 + comparison2 + comparison3) * 0.33
            print("Comparing " + str(i + 1) + " histogram of current frame with " + str(
                j + 1) + " histogram of previous frame")
            comparison = 1 - comparison
            sum += comparison

        if len(hist2) != 0:
            sum = sum / len(hist2)
        mean_j.append(sum)

    print("sum j" + str(mean_j))

    return mean_j


def CoordinatesConversion(coordinates_as_str):
    dim = int(len(coordinates_as_str))
    coordinates_as_int = []
    for i in range(int(len(coordinates_as_str))):
        x = int(float(coordinates_as_str[i][0]))
        y = int(float(coordinates_as_str[i][1]))
        w = int(float(coordinates_as_str[i][2]))
        h = int(float(coordinates_as_str[i][3]))
        coordinates_as_int.append(x)
        coordinates_as_int.append(y)
        coordinates_as_int.append(w)
        coordinates_as_int.append(h)

    Converted2Int = np.reshape(coordinates_as_int, (dim, 4))

    return Converted2Int


def GetBBoxesFromFrames(frame, number, coordinates):
    objects = []
    shrink = 0.2
    for i in range(int(number)):
        x = coordinates[i][0]
        y = coordinates[i][1]
        width = coordinates[i][2]
        widths = int(coordinates[i][2] * shrink)
        height = coordinates[i][3]
        heights = int(coordinates[i][3] * shrink)

        cropped = frame[y + heights:y + height - heights, x + widths:x + width - widths]
        cropped = cv2.resize(cropped, (360, 360))
        objects.append(cropped)

    cv2.imshow("test", frame)
    for i in range(int(number)):
        cv2.imshow('crop', objects[i])
        cv2.waitKey(1)

    return objects


def SetUpFiles(directory_path="", description_file="bboxes.txt"):
    path_to_images = directory_path + "/frames/"
    path_to_description = directory_path + "/" + description_file

    files = os.path.join(path_to_images)
    description = os.path.join(path_to_description)

    file = open(description, "r")

    prev_name = 0
    prev_number_of_bb = 0
    previous_bboxes = []
    prev_coordinates = []

    while True:

        images = []
        objects = []
        number_of_bb = []
        coordinates = []

        name = file.readline().rstrip("\n")
        if not name:
            break
        print("\n" + name)
        number_of_bb = file.readline().rstrip("\n")
        print(number_of_bb)
        for number in range(int(number_of_bb)):
            position = file.readline().rstrip("\n").split()
            coordinates.append(position)

        img = cv2.imread(files + name)

        if prev_name != 0:
            prev_img = cv2.imread(files + prev_name)
            previous_bboxes = GetBBoxesFromFrames(prev_img, prev_number_of_bb, prev_coordinates_int)

        prev_name = name
        prev_number_of_bb = number_of_bb
        prev_coordinates = coordinates

        coordinates_int = CoordinatesConversion(coordinates)
        prev_coordinates_int = CoordinatesConversion(prev_coordinates)
        current_bboxes = []
        current_bboxes = GetBBoxesFromFrames(img, number_of_bb, coordinates_int)

        hist = CalcHistograms(current_bboxes)
        if previous_bboxes != 0:
            prev_hist = CalcHistograms(previous_bboxes)
            CompHistograms(hist, prev_hist)


if __name__ == '__main__':

    # Empty string for directory name
    image_directory_name = " "

    # Input reading
    arg = sys.argv[1:]
    try:
        if len(arg) == 1:
            if os.path.exists(arg[0]) and os.path.isdir(arg[0]):
                # If given directory is correct data is saved to a variable
                image_directory_name = arg[0]
            else:
                print("Path error")
        else:
            print("Input error")

    except getopt.GetoptError as error:
        print(error)
        sys.exit(1)

    SetUpFiles(image_directory_name)

    print("End")