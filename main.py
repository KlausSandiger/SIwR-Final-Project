import argparse
from pathlib import Path
import getopt
import os.path
import sys
from processing.image import perform_processing


def SetUpFiles(directory_path = "", description_file = "bboxes.txt"):

    path_to_images = directory_path + "/frames"
    path_to_description = directory_path + "/" + description_file

    files = os.listdir(path_to_images)
    description = os.path(path_to_description)

    images = []
    objects = []
    number_of_bb = []
    coordinates = []


# Appending .jpg and .png files to the array
    for file in files:
        if file.endswith("jpg") or file.endswith("png"):
            images.append(file)




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
                print("OK")
            else:
                print("Path error")
        else:
            print("Input error")

    except getopt.GetoptError as error:
        print(error)
        sys.exit(1)

    array_of_images = []

    results = {}
