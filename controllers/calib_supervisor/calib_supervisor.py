"""calib_supervisor controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Supervisor

import cv2
import numpy as np
from itertools import product
import yaml

supervisor = Supervisor()

SQUARE_SIZE = 1.25e-2 #cm
CALIB_NUM = 80

# get the time step of the current world.
timestep = int(supervisor.getBasicTimeStep())

chessboard = supervisor.getFromDef('CHESSBOARD')
chessboard_position = chessboard.getField('translation').getSFVec3f()

robot_node = supervisor.getFromDef('TESTCAM')
robot_translation_field = robot_node.getField('translation')
print(robot_translation_field.getSFVec3f())
camera = supervisor.getDevice('camera')
camera.enable(timestep)
# camera = supervisor.getDevice('camera')
# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
num = 0
# Main loop:
# - perform simulation steps until Webots is stopping the controller
init = True
while supervisor.step(timestep) != -1:
    if num == CALIB_NUM:
        break
    img = camera.getImageArray()
    img = np.asarray(img, dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (9,6),None)

    if ret == True:
        if init:
            square_pixels = np.linalg.norm(corners[0,0] - corners[1,0])
            # print(square_pixels)
            w,h = camera.getWidth(), camera.getHeight()  
            vertical_points = np.linspace(50 + square_pixels*5,h-(50+ square_pixels*5),int(np.floor((h-100)/(square_pixels*10))))
            horizontal_points = np.linspace(50 + square_pixels*3.5,h-(50+ square_pixels*3.5),int(np.floor((w-100)/(square_pixels*7))))
            points = np.array(list(product(vertical_points,horizontal_points)))    
            # print(points)
            center = (corners[21,0] + corners[32,0])/2 
            center = np.array([center[1],center[0]])
            # print(center)           
            offset = (points-center)*SQUARE_SIZE/square_pixels
            i = 0
            init = False
        else:
           
            chessboard.getField('rotation').setSFRotation([1,0,0,-np.pi])
            chessboard.getField('translation').setSFVec3f([chessboard_position[0]+offset[i][0],chessboard_position[1]-offset[i][1],chessboard_position[2]])
            center = (corners[21,0] + corners[32,0])/2 
            print(center)
            cv2.imwrite(f"camera{i+np.random.randint(1000)}.jpg",img)
            i += 1
            if i == len(offset):
                i = 0
            # create a random float between -0.2 and 0.2           
            chessboard.getField('rotation').setSFRotation([1,np.random.uniform(-0.2, 0.2),np.random.uniform(-0.3, 0.3),-np.pi])

        objpoints.append(objp)   # Certainly, every loop objp is the same, in 3D.
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        # img = cv2.drawChessboardCorners(img, (9,6), corners2, ret)
        # cv2.imshow('img',img)
        # cv2.waitKey(10)
        num += 1
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)

# Enter here exit cleanup code.
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

data = {'camera_matrix': np.asarray(mtx).tolist(), 'dist_coeff': np.asarray(dist).tolist()}

with open("calibration.yaml", "w") as f:
    yaml.dump(data, f)
