"""geometric_posest controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

import cv2
import numpy as np
from itertools import product
import yaml
import csv
import ast
import matplotlib.pyplot as plt

XLIM = [-16.235, 5.435]
YLIM = [-3.6625, 3.6625]



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

with open('params.yaml') as f:
    loadedparams = yaml.safe_load(f)

GRID_SIZE = loadedparams.get('grid_size')
ROTATION = loadedparams.get('rotation')
# print data types of the loaded parameters
print("GRID_SIZE: ", type(GRID_SIZE), GRID_SIZE)
print("ROTATION: ", type(ROTATION), ROTATION)

inc = GRID_SIZE/100

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
# write loadedparams to params.yaml
with open('params.yaml', 'w') as f:
    yaml.dump({"grid_size": GRID_SIZE, "rotation": ROTATION, "grid_x": len(x), "grid_y": len(y)}, f)

    

# create the Supervisor instance.
supervisor = Supervisor()

# get the time step of the current world.
timestep = int(supervisor.getBasicTimeStep())

robot_node = supervisor.getFromDef('TESTCAM')
robot_translation_field = robot_node.getField('translation')
robot_rotation_field = robot_node.getField('rotation')
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
camera_inv = np.linalg.inv(matrix_coefficient)



step = 0 
robot_translation_field.setSFVec3f([grid[step,0], grid[step,1], 0.01])
#robot_rotation_field.setSFRotation([0,0,1,0.3])
robot_rotation_field.setSFRotation([0,0,1,ROTATION])
init = True 
# Main loop:
# - perform simulation steps until Webots is stopping the controller
grid_errors = []
while supervisor.step(timestep) != -1:
    img = camera.getImageArray()
    img = np.asarray(img, dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    

    # cv2.imwrite(f"camera{step}.jpg",img)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    arucoParams = cv2.aruco.DetectorParameters_create()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict,
	    parameters=arucoParams) 
    tag_errors = []
    if np.all(ids is not None):
        if len(ids) > 2:
            b = np.array([[0]])
            A = np.zeros((1,4))
            for i in range(len(corners)):
                xm = tag_coords[ids[i],0][0]
                ym = tag_coords[ids[i],1][0]
                A = np.append(A,np.array([[-1,0,xm,ym],[0,1,-ym,xm]]),axis=0)
                # tried using inverse of transform, didn't work.
                #A = np.append(A,np.array([[-1,0,xm,ym],[0,-1,ym,-xm]]),axis=0)
                x,y = np.mean(corners[i][0], axis=0)
                v = np.matmul(camera_inv,np.array([[y],[x],[1]]))
                b = np.append(b,v[:2,:],axis=0)
            b = b[1:,:]
            A = A[1:,:]
            # x y cos(theta) sin(theta)
            res = np.linalg.lstsq(A,3.045*b,rcond=None)
            # normalize sin(theta) and cos(theta) to unit magnitude to fix any inconsistencies between the two variables.
            costheta=np.sign(res[0][2])*np.sqrt(res[0][2][0]**2/(res[0][2][0]**2+res[0][3][0]**2))
            sintheta=np.sign(res[0][3])*np.sqrt(res[0][3][0]**2/(res[0][2][0]**2+res[0][3][0]**2))
            # rotate x and y by theta for some reason?????
            position_est = np.array([[res[0][0][0]*costheta[0]-res[0][1][0]*sintheta[0], res[0][0][0]*sintheta[0]+res[0][1][0]*costheta[0], np.arctan2(sintheta[0], costheta[0])]])
            # print(f"Estimated position: {position_est}")
            # print(f"Real position: {robot_node.getField('translation').getSFVec3f()[:2]}")
            position_error = np.linalg.norm(robot_node.getField('translation').getSFVec3f()[:2]-position_est[:,:2])
            tag_errors.append([position_error, 0])
        else:        
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
        print(f"Estimation error is:{tag_errors[0]}")
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
