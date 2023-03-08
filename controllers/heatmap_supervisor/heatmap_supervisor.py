"""heatmap_supervisor controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

import cv2
import numpy as np
from itertools import product
import yaml
import csv
import ast



XLIM = [-16.235, 5.435]
YLIM = [-3.6625, 3.6625]
GRID_NUM = 100

ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL}


# find the ratio of the limits to each other
inc = np.sqrt((XLIM[1] - XLIM[0]) * (YLIM[1] - YLIM[0])/GRID_NUM)
# create an array of the grid points starting from XLIM[0] increasing by inc not including XLIM[0]
x = np.arange(XLIM[0], XLIM[1], inc)
x = x + np.array([(XLIM[1]-x[-1])*0.5])
y = np.arange(YLIM[0], YLIM[1], inc)
y = y + np.array([(YLIM[1]-y[-1])*0.5])

# load tag cooardinates from txt file
with open('../../misc/tagcoords.txt', 'r') as f:
    tag_coords = f.readlines()
tag_coords = tag_coords[0].split(",")
tag_coords = [i.replace("[","") for i in tag_coords]
tag_coords = [i.replace("]","") for i in tag_coords]
tag_coords = np.array(tag_coords, dtype=np.float32)
tag_coords = np.reshape(tag_coords, (-1,2))

with open('../../misc/tagsettings.txt', 'r') as f:
    tag_set = f.read()
    tag_dict, tag_size = ast.literal_eval(tag_set)

# create combinations of the grid points
grid = np.array(list(product(x, y)))

# create the Supervisor instance.
supervisor = Supervisor()

# get the time step of the current world.
timestep = int(supervisor.getBasicTimeStep())

robot_node = supervisor.getFromDef('TESTCAM')
robot_translation_field = robot_node.getField('translation')
camera = supervisor.getDevice('camera')
camera.enable(timestep)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[tag_dict])
with open('../calib_supervisor/calibration.yaml') as f:
    loadeddict = yaml.safe_load(f)

matrix_coefficient = np.array(loadeddict.get('camera_matrix'))
distortion_coefficient = np.array(loadeddict.get('dist_coeff'))





step = 0 
robot_translation_field.setSFVec3f([grid[step,0], grid[step,1], 0.01])
init = True 
# Main loop:
# - perform simulation steps until Webots is stopping the controller
grid_errors = []
while supervisor.step(timestep) != -1:
    img = camera.getImageArray()
    img = np.asarray(img, dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    

    cv2.imwrite(f"camera{step}.jpg",img)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    arucoParams = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict,
	    parameters=arucoParams) 
    tag_errors = []
    if np.all(ids is not None):
        for i,id in enumerate(ids):
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i], tag_size*0.01, matrix_coefficient,
                                                                       distortion_coefficient)
            
            tvec[0][0][1] = -tvec[0][0][1]
            position_est = tag_coords[id] + tvec[0][0][1::-1]
            position_error = np.linalg.norm(robot_node.getField('translation').getSFVec3f()[:2]-position_est)
            
            tag_errors.append([position_error, id[0]])  
    else:
        pass
        # The camera is not able to see any markers
    if tag_errors:
        tag_errors.sort(key=lambda x: x[0])
        print(tag_errors[0])
    grid_errors.append(tag_errors)
    if step == 107:
        break
    step += 1
    robot_translation_field.setSFVec3f([grid[step,0], grid[step,1], 0.01])

# Enter here exit cleanup code.
# save the grid errors to a csv file
with open('grid_errors.csv', 'w', newline='') as f:
    csvw=csv.writer(f)
    csvw.writerows(grid_errors)
#    for i in grid_errors:
#        f.write(f"{i} \n")
