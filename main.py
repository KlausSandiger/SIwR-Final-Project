import getopt
import os.path
import sys
import cv2

import frame_operations

def CoordinatesConversion(coordinates_as_str):

    print(len(coordinates_as_str))
    coordinates_as_int = []

    for i in range(int(len(coordinates_as_str))):
        j = int(i)
        x = int(float(coordinates_as_str[i][0]))
        y = int(float(coordinates_as_str[i][1]))
        w = int(float(coordinates_as_str[i][2]))
        h = int(float(coordinates_as_str[i][3]))
        coordinates_as_int.append(x)
        coordinates_as_int.append(y)
        coordinates_as_int.append(w)
        coordinates_as_int.append(h)

    print(coordinates_as_int)



def SetUpFiles(directory_path = "", description_file = "bboxes.txt"):

    path_to_images = directory_path + "/frames/"
    path_to_description = directory_path + "/" + description_file

    files = os.path.join(path_to_images)
    description = os.path.join(path_to_description)

    file = open(description, "r")

    prev_name = 0
    prev_number_of_bb = 0



    while True:

        images = []
        objects = []
        number_of_bb = []
        coordinates = []


#Apending .jpg and .png files to the array
#         for file in files:
#             if file.endswith("jpg") or file.endswith("png"):
#                 images.append(file)


        name = file.readline().rstrip("\n")
        if not name:
            break
        print("\n" + name)
        number_of_bb = file.readline().rstrip("\n")
        print(number_of_bb)
        for number in range(int(number_of_bb)):

            position = file.readline().rstrip("\n").split()
            coordinates.append(position)
        #convert to int
        print(coordinates)

        img = cv2.imread(files + name)
        cv2.imshow("org",img)

        if prev_name != 0:
            prev_img = cv2.imread(files + prev_name)
            cv2.imshow("prev", prev_img)

        print("BBoxes current " + number_of_bb)
        print("BBoxes prev " + str(prev_number_of_bb))
        gap = int(number_of_bb) - int(prev_number_of_bb)

        prev_name = name
        prev_number_of_bb = number_of_bb

        print("Change in between frames " + str(gap))

        print(type(coordinates))

        CoordinatesConversion(coordinates)


        cv2.waitKey(10000)

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



    array_of_images = []

    results = {}
