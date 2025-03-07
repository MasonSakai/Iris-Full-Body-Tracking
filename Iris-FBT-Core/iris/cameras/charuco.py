import cv2 as cv
import cv2.aruco as aruco
import numpy as np
from iris.cameras.camera import Camera

class CharucoConfig:
    squaresX = 7
    squaresY = 5
    squareLength = 1.0
    markerLength = 0.8
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    board = aruco.CharucoBoard_create(squaresX, squaresY, squareLength, markerLength, aruco_dict)


class CharucoCalib:
    
    def calibrate(camera, config_class=CharucoConfig):
        pass