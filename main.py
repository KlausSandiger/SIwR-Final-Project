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

def CalcHistograms(objects):

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

        tmp = DiscreteFactor([str(i)], [len(hist2) + 1], [[0.29] + mean_j])
        G.add_factors(tmp)
        G.add_edge(str(i),tmp)

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

    Converted2Int = np.reshape(coordinates_as_int,(dim,4))

    return Converted2Int

def GetBBoxesFromFrames(frame,number,coordinates):

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
        cropped = cv2.resize(cropped,(360,360))
        objects.append(cropped)

    return objects

def SetUpFiles(directory_path = "", description_file = "bboxes.txt"):

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

        name = file.readline().rstrip("\n")
        if not name:
            break
        number_of_bb = file.readline().rstrip("\n")

        if number_of_bb == "0":
            print('')
            emergency_situation = 1
            continue

        for number in range(int(number_of_bb)):
            G.add_node(str(number))
            position = file.readline().rstrip("\n").split()
            coordinates.append(position)
        img = cv2.imread(files + name)

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

        if prev_name != 0:
            prev_img = cv2.imread(files + prev_name)
            previous_bboxes = GetBBoxesFromFrames(prev_img, prev_number_of_bb, prev_coordinates_int)

        prev_name = name
        prev_number_of_bb = number_of_bb
        prev_coordinates = coordinates

        coordinates_int = CoordinatesConversion(coordinates)
        prev_coordinates_int = CoordinatesConversion(prev_coordinates)
        current_bboxes = []
        current_bboxes = GetBBoxesFromFrames(img,number_of_bb,coordinates_int)

        hist = CalcHistograms(current_bboxes)

        if previous_bboxes != 0:
            prev_hist = CalcHistograms(previous_bboxes)
            CompHistograms(hist,prev_hist,G)

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

    SetUpFiles(image_directory_name)