import getopt
import os.path
import sys
import cv2
import numpy as np
from pgmpy.models import FactorGraph
from pgmpy.factors.discrete import DiscreteFactor
from pgmpy.inference import BeliefPropagation
from itertools import combinations
from collections import OrderedDict

# TODO Jakość kodu i raport (4/5)
# TODO Raport w miarę kompletny i zrozumiały, jednak przydałby się jeszcze rysunek.
# TODO Kod przejrzysty i dobrze udokumentowany.

# TODO Skuteczność śledzenia 0.734 (4/5)
# TODO [0.00, 0.0] - 0.0
# TODO (0.0, 0.1) - 0.5
# TODO [0.1, 0.2) - 1.0
# TODO [0.2, 0.3) - 1.5
# TODO [0.3, 0.4) - 2.0
# TODO [0.4, 0.5) - 2.5
# TODO [0.5, 0.6) - 3.0
# TODO [0.6, 0.7) - 3.5
# TODO [0.7, 0.8) - 4.0
# TODO [0.8, 0.9) - 4.5
# TODO [0.9, 1.0) - 5.0

def CalcHistograms(objects):
# This function calculate histograms from collected bounding boxes. In order to improve the results, histograms were
# calculated for 3 channels separatelly than normalized.

    Histograms = []
    for i in range(len(objects)):

        hist1 = cv2.calcHist(objects[i][:,:,0],[0],None, [256],[1,254])
        hist2 = cv2.calcHist(objects[i][:,:,1],[0],None, [256],[1,254])
        hist3 = cv2.calcHist(objects[i][:,:,2],[0],None, [256],[1,254])

        cv2.normalize(hist1,hist1,0,255,cv2.NORM_MINMAX)
        cv2.normalize(hist2,hist2,0,255,cv2.NORM_MINMAX)
        cv2.normalize(hist3,hist3,0,255,cv2.NORM_MINMAX)

        Histograms.append([hist1,hist2,hist3])

    return Histograms

def CompHistograms(hist1,hist2,G):
# In this function, histogram from both previous and current frame are compared against each other. Comparison value is
# a mean value for comparing considered channels. For comparing I used ready Bhattacharyya method.

    sum = 0
    for i in range(len(hist1)):
        mean_j = []
        sum = 0
        for j in range(len(hist2)):
            comparison1 = cv2.compareHist(hist1[i][0],hist2[j][0],cv2.HISTCMP_BHATTACHARYYA)
            comparison2 = cv2.compareHist(hist1[i][1],hist2[j][1],cv2.HISTCMP_BHATTACHARYYA)
            comparison3 = cv2.compareHist(hist1[i][2],hist2[j][2],cv2.HISTCMP_BHATTACHARYYA)
            comparison = (comparison1 + comparison2 + comparison3)*0.33
            comparison = 1 - comparison
            mean_j.append(comparison)

# Adding DiscreteFactor to the FactorGraph()
        tmp = DiscreteFactor([str(i)], [len(hist2) + 1], [[0.29] + mean_j])
        G.add_factors(tmp)
        G.add_edge(str(i),tmp)

    return mean_j

def CoordinatesConversion(coordinates_as_str):
# This function take coordinates read from the bboxes.txt file. Since values were read as strings this function converts
# them to int for calculation purposes

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

    Converted2Int = np.reshape(coordinates_as_int,(dim,4))

    return Converted2Int

def GetBBoxesFromFrames(frame,number,coordinates):
# In this function previously converted coordinates are used to crop the bounding boxes from frame for further
# processing. Cropped images were shrinked by 0.3 in order to ignore unwanted background.

    objects = []
    shrink = 0.3
    for i in range(int(number)):
        x = coordinates[i][0]
        y = coordinates[i][1]
        width = coordinates[i][2]
        widths = int(coordinates[i][2] * shrink)
        height = coordinates[i][3]
        heights = int(coordinates[i][3] * shrink)

        cropped = frame[y+heights:y+height-heights,x+widths:x+width-widths]
        # TODO Czy to jest konieczne?
        cropped = cv2.resize(cropped,(360,360))
        objects.append(cropped)

    return objects

def SetUpFiles(directory_path = "", description_file = "bboxes.txt"):
# This function is the biggest processing part of project. In next lines data is downloaded from the path and initial
# values are set. Then read data is set up for calculations.

    path_to_images = directory_path + "/frames/"
    path_to_description = directory_path + "/" + description_file

    files = os.path.join(path_to_images)
    description = os.path.join(path_to_description)

    file = open(description, "r")

    prev_name = 0
    prev_number_of_bb = 0
    previous_bboxes = []
    prev_coordinates = []
    emergency_situation = 0

    while True:

        G = FactorGraph()
        coordinates = []

# bboxes.txt data is divided into: NAME, NUMBER OF BOUNDING BOXES and their respective COORDINATES
        name = file.readline().rstrip("\n")
        if not name:
            break
        number_of_bb = file.readline().rstrip("\n")

# This condition is met when there are no bounding boxes on frame. Therefore we can just omit this frame and continue.
        if number_of_bb == "0":
            print('')
            emergency_situation = 1
            continue

# Number of bounding boxes read from file determines how many following lines are obtaining the coordinates.
        for number in range(int(number_of_bb)):
            G.add_node(str(number))
            position = file.readline().rstrip("\n").split()
            coordinates.append(position)
        img = cv2.imread(files + name)

# This condition is met when previous frame had no bounding boxes. We can assume, that all bounding boxes
# had just appeared and proceed to continue.
        if emergency_situation == 1:
            emergency_situation = 0
            solution = []
            for i in range(int(number_of_bb)):
                solution.append(-1)
                i += 1
            print(*solution,sep = ' ')
            prev_name = name
            prev_number_of_bb = number_of_bb
            prev_coordinates = coordinates
            continue

# In first instance we have no previous bounding boxes to compare the current ones to.
        if prev_name != 0:
            prev_img = cv2.imread(files + prev_name)
            previous_bboxes = GetBBoxesFromFrames(prev_img, prev_number_of_bb, prev_coordinates_int)

# Values from current frame are saved for next loop calculations.
        prev_name = name
        prev_number_of_bb = number_of_bb
        prev_coordinates = coordinates

        coordinates_int = CoordinatesConversion(coordinates)
        prev_coordinates_int = CoordinatesConversion(prev_coordinates)
        current_bboxes = []
        current_bboxes = GetBBoxesFromFrames(img,number_of_bb,coordinates_int)

        hist = CalcHistograms(current_bboxes)

# This part of code is omitted in case on the previous frame there were no bounding boxes or first frame is considered.
        if previous_bboxes != 0:
            prev_hist = CalcHistograms(previous_bboxes)
            CompHistograms(hist,prev_hist,G)

# In this section I made a matrix, that prevent a situation, that more than one current histogram is assigned to a
# single histogram from the previous frame using itertools.combinations()
            matrix = np.ones((len(prev_hist)+1,len(prev_hist)+1))

            for i in range(len(prev_hist)+1):
                for j in range(len(prev_hist)+1):
                    if i != 0:
                        if i == j:
                            matrix[i][j] = 0

            for current_histrogram1, current_histrogram2 in combinations(range(int(number_of_bb)), 2):
                tmp = DiscreteFactor([str(current_histrogram1), str(current_histrogram2)], [len(prev_hist) + 1,
                                                                                        len(prev_hist) + 1],
                                                                                        matrix)
                G.add_factors(tmp)
                G.add_edge(str(current_histrogram1), tmp)
                G.add_edge(str(current_histrogram2), tmp)

# Lastly results are reformatted to an expected format and printed for each frame.
            BP = BeliefPropagation(G)
            BP.calibrate()

            pre_result = (BP.map_query(G.get_variable_nodes(),show_progress=False))
            pre_result2 = OrderedDict(sorted(pre_result.items()))
            result = list(pre_result2.values())
            final_result = []
            for i in range(len(result)):
                value = result[i] - 1
                final_result.append(value)
            print(*final_result,sep = ' ')

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
# Data is now taken for processing
    SetUpFiles(image_directory_name)