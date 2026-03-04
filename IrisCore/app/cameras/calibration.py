
import os
from pathlib import Path
import shutil
import tempfile
import cv2 as cv
import numpy as np
from flask import redirect, render_template, request, url_for
from werkzeug.datastructures import FileStorage
from app.cameras.forms import CalibrationConfigForm, FileUploadForm
from app.cameras.models import Camera
from app.cameras.routes import bp_cam
from utils.registry import ThingDatabase
from utils.scribe import IExposable, Scribe_Values

class CalibrationConfig(IExposable):

    def __init__(self):
        self.checkerboard_x = 7
        self.checkerboard_y = 9
        self.checkerboard_w = 0.2

    def ExposeData(self):
        self.checkerboard_x = Scribe_Values.Look(self.checkerboard_x, 'width', int, 7)
        self.checkerboard_y = Scribe_Values.Look(self.checkerboard_y, 'height', int, 9)
        self.checkerboard_w = Scribe_Values.Look(self.checkerboard_w, 'size', float, 0.2)

    def WriteForm(self, form: CalibrationConfigForm):
        form.checkerboard_x.data = self.checkerboard_x
        form.checkerboard_y.data = self.checkerboard_y
        form.checkerboard_w.data = self.checkerboard_w * 100.

    def ReadForm(self, form: CalibrationConfigForm):
        self.checkerboard_x = form.checkerboard_x.data
        self.checkerboard_y = form.checkerboard_y.data
        self.checkerboard_w = form.checkerboard_w.data / 100.

config = CalibrationConfig()

def GetCameraFileList(camera: Camera, path: str = None) -> list[Path]:
    if not path:
        path, exists = camera.get_file_path('calibration')
        if not exists:
            return []
    if not os.path.isdir(path):
        return []
    return [f for f in Path(path).iterdir() if f.is_file()]


def CalibrateCamera(camera: Camera, path: str = None) -> tuple[bool, str]:
    files = GetCameraFileList(camera, path)
    if len(files) == 0:
        return False, 'No images to calibrate with'

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    objp = np.zeros((config.checkerboard_y * config.checkerboard_x,3), np.float32)
    objp[:,:2] = np.mgrid[0:config.checkerboard_y, 0:config.checkerboard_x].T.reshape(-1,2)
    objp *= config.checkerboard_w

    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    w = 0
    h = 0

    for file in files:
        img = cv.imread(file.resolve())
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        h, w = img.shape[:2]
 
        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (config.checkerboard_y, config.checkerboard_x), None)
        
        if ret == True:
            objpoints.append(objp)
 
            corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)

            cv.drawChessboardCorners(img, (config.checkerboard_y, config.checkerboard_x), corners2, ret)
            
    if len(objpoints) == 0:
        return False, 'Found no valid checkerboards in {} images'.format(len(files))

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
        mean_error += error
    err = mean_error/len(objpoints)

    camera.set_camera_params(h, w, mtx, dist, err)

    return False, f"Successfully calibrated with {len(objpoints)} images"



@bp_cam.route('/<id>/calibrate', methods=['GET', 'POST'])
def calibrate(id):
    cam = ThingDatabase(Camera).Get(id)
    file_form = FileUploadForm()
    config_form = CalibrationConfigForm()
    path, exists = cam.get_file_path('calibration')
    feedback = None
    if request.method == 'POST':
        success, feedback = CalibrateCamera(cam, path)
    config.WriteForm(config_form)

    return render_template('_calib_cam.html', file_form=file_form, config_form=config_form, feedback=feedback, camera=cam, files=GetCameraFileList(cam))

@bp_cam.route('/<id>/calibrate/config', methods=['POST'])
def calibrate_config(id):
    form = CalibrationConfigForm()
    if form.validate_on_submit():
        config.ReadForm(form)
    return redirect(url_for('cameras.calibrate', id=id))

@bp_cam.route('/<id>/calibrate/files/upload', methods=['POST'])
def calibrate_files_upload(id):
    cam = ThingDatabase(Camera).Get(id)
    form = FileUploadForm()
    path, exists = cam.get_file_path('calibration')
    if form.validate_on_submit():
        if not exists:
            os.makedirs(path, exist_ok=True)
        data: list[FileStorage] = form.image_files.data
        if data:
            for file in data:
                f = tempfile.NamedTemporaryFile(dir=path, suffix='.png', delete=False)
                file.save(f)
                f.close()
    return redirect(url_for('cameras.calibrate', id=id))

@bp_cam.route('/<id>/calibrate/files/clear')
def calibrate_clear_files(id):
    cam = ThingDatabase(Camera).Get(id)
    path, exists = cam.get_file_path('calibration')
    if exists:
        shutil.rmtree(path)
    return redirect(url_for('cameras.calibrate', id=id))