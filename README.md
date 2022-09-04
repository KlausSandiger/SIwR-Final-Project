# SIwR-Final-Project

## Project concept

Project idea was to create a pedestrian tracking system using probabilistic graph models. Trackers goal was to identify a person from a camera frame using Bounding Boxes (BBoxes) and try to locate the same person on following frames. 
Data file contained name of the frame. number of bounding boxes on frame and their coordinates accordingly.

## Chosen method

In order to solve described above problem, firstly I read data from file and divided it into variables storing them for calculation. Each frame has it own set of variables and tracking takes place only between current and previous frame. 
Having collected the data from given file I converted them to usable values. Frame with name matching the first variable is loaded and precise amount of bounding boxes with assigned coordinates are cropped from the original image. Cropped boxes and than compared to the boxes from previous frame using histogram matching and the result of histogram comparison is added to the factor graph, that makes the final decision about assigning the boxes to their apperances on neighboured frames.

## Results improvement moves

In order to increase the accuracy of the program some adjustments had been made:

###### No people on screen

To prevent program from crashing when ordered to divide by 0, I had created the condition, that when data about boxes on a current frame is read as 0 the code jumps to output since there is no boxes to compare against each other. Additionally, next frame number also jumps straight to the result, because the code knows, that all the boxes must have just appeared.

###### Channel division

Cropped images are divided into 3 color channels and each version of it has it's histogram calculated separatedly to improve matching by colors.

###### Shrinking images

Before calculating histograms the images cropped for frames are cropped even more (30%). The reason for it was to avoid taking unnecessary background into consideration. This way only the people in the picture are taken into comparison process

###### Choice locking

In order to prevent several boxes to assign the tracking to same box from diffent frame a matrix was created. The dimension of this matrix was number of bounding boxes + 1 (for new apperance instance). All values of the matrix except the diagonal values (  exception : [1][1] - new apperance) are set to 1 to allow for assignment and the rest are not permitted to be assigned.
