"""snapshot controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot


import numpy as np
import cv2

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# Enable camera
camera = robot.getDevice("camera")
camera.enable(timestep)

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    if robot.getTime() > 1:

        img = camera.getImageArray()
        img = np.asarray(img, dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        num = np.random.randint(1000, size=1)
        print(num[0])
        cv2.imwrite(f"camera{num[0]}.jpg",img)
        break
        
        
        arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)
        arucoParams = cv2.aruco.DetectorParameters_create()
        (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict,
                    parameters=arucoParams)
        if np.all(ids is not None):
            print(f"{len(ids)} Markers found")
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
