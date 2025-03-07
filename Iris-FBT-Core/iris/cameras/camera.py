from ctypes import ArgumentError
import cv2 as cv


class Camera:
    cameraMatrix = None
    distCoeffs = None
    rvecs = None
    tvecs = None

    capture = None

    def __init__(self, ident):

        if type(ident) is int:
            self.capture = cv.VideoCapture(ident)
            self.capture.set(cv.CAP_PROP_FPS, 90)
            self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 640)
            self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 640)
            return
        
        raise ArgumentError(f"Camera Type not valid: {type(ident)}")
