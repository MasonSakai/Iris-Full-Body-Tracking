from __future__ import annotations
import os
from pathlib import Path
import cv2 as cv
from cv2.typing import MatLike, Rect
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo
from flask import render_template, request
import numpy as np

from app.main.modal import modal_success
from app.cameras.forms import CameraReferenceForm
from app.dataproviders import IDataSource
from app.synchronize import source_registry_lock
from app import lifecycle
from utils.registry import IThing, ThingDatabase
from utils.scribe import  IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Values, Scribe_Collections

class CameraReference(IExposable, IDataSource):
	parent: Camera

	autostart: bool
	active: bool
	display_name: str

	def __init__(self):
		super().__init__()
		self.autostart = False
		self.active = False
		self.display_name = None


	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'display_name', str)
		self.autostart = Scribe_Values.Look(self.autostart, 'autostart', bool, defaultValue=False)

	def ThingID(self):
		return f"{type(self).__qualname__}:{self.parent.ThingID()}"

	def RequestStart(self, *args, **kwargs) -> bool:
		return False
	
	def RequestStop(self, *args, **kwargs):
		pass

	def RequestAutoStart(self) -> bool:
		return False
	
	def HasUpdate(self) -> bool:
		return False

	def GetData(self):
		pass

	def RenderView(self):
		pass
		
class LocalCameraReference(CameraReference):

	name: str
	vid: int
	pid: int
	
	cap: cv.VideoCapture

	def __init__(self):
		super().__init__()
		self.name = None
		self.vid = None
		self.pid = None
		self.cap = None
	
	def ExposeData(self):
		super().ExposeData()
		self.name = Scribe_Values.Look(self.name, 'name', str)
		self.vid = Scribe_Values.Look(self.vid, 'vid', int)
		self.pid = Scribe_Values.Look(self.pid, 'pid', int)
		
	def RequestStart(self, *args, **kwargs):
		return self.RequestAutoStart()
	
	def RequestStop(self, *args, **kwargs):
		if self.active:
			self.cap.release()
			self.active = False
			with source_registry_lock:
				ThingDatabase(IDataSource).Remove(self)

	def RequestAutoStart(self):
		for cam in enumerate_cameras():
			if (cam.name, cam.vid, cam.pid) == (self.config.name, self.config.vid, self.config.pid):
				break
		if not cam:
			return False
		self.cap = cv.VideoCapture(cam.index, cam.backend) # add params?
		# start thread
		self.active = True
		with source_registry_lock:
			ThingDatabase(IDataSource).Add(self)
		return True

	@staticmethod
	def EnumerateCameras() -> tuple[list[tuple[Camera, CameraInfo]], list[CameraInfo]]:
		def MakeID(ref: LocalCameraReference | CameraInfo) -> tuple[str, int, int]:
			return (ref.name, ref.vid, ref.pid)

		known: dict[tuple[str, int, int], Camera] = {}
		for cam in ThingDatabase(Camera).AllThingsListForReading():
			for ref in cam.references:
				if isinstance(ref, LocalCameraReference):
					known[MakeID(ref)] = cam

		found: list[tuple[Camera, CameraInfo]] = []
		new: list[CameraInfo] = []
		for cam in enumerate_cameras():
			id = MakeID(cam)
			if id in known:
				found.append((known[id], cam))
			else:
				new.append(cam)

		return found, new

	def RenderView(self):
		form = CameraReferenceForm(self.parent, self)
		if form.validate_on_submit():
			if self.display_name != form.display_name.data:
				self.display_name = form.display_name.data
			return modal_success()
		elif request.method == 'GET':
			form.display_name.data = self.display_name
		return render_template('_view_lref.html', ref=self, form=form)
	

class Camera(IExposable, IThing, ILoadReferenceable):
	
	display_name : str
	transform: np.ndarray | None

	calib_res_width: int
	calib_res_height: int
	camera_matrix: np.ndarray | None
	dist_coeffs: np.ndarray | None
	calib_err: float

	references: list[CameraReference]
	
	#functions
	def __init__(self):
		super().__init__()
		self.display_name = None
		self.calib_res_width = 0
		self.calib_res_height = 0
		self.camera_matrix = None
		self.dist_coeffs = None
		self.calib_err = -1.0
		self.transform = None
		self.references = []

	def __repr__(self):
		return '<Camera - "{}">'.format(self.display_name)
	
	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'name', str)

		self.calib_res_width = Scribe_Values.Look(self.calib_res_width, 'CalibResWidth', int, defaultValue=0)
		self.calib_res_height = Scribe_Values.Look(self.calib_res_height, 'CalibResHeight', int, defaultValue=0)
		self.camera_matrix = Scribe_Values.Look(self.camera_matrix, 'CameraMatrix', np.ndarray)
		self.dist_coeffs = Scribe_Values.Look(self.dist_coeffs, 'DistCoeffs', np.ndarray)
		self.calib_err = Scribe_Values.Look(self.calib_err, 'CalibError', float, -1.0)

		self.transform = Scribe_Values.Look(self.transform, 'transform', np.ndarray)

		self.references = Scribe_Collections.LookList(self.references, 'references', CameraReference, Scribe_Collections.LookMode.Deep)
		if Scribe.mode == LoadSaveMode.LoadingVars:
			for ref in self.references:
				ref.parent = self
	
	def ThingID(self) -> str:
		return self.display_name

	def Rename(self, new_name: str) -> bool:
		if ThingDatabase(Camera).Get(new_name, False):
			return False
		path, exists = self.get_file_path()
		ThingDatabase(Camera).Remove(self)
		self.display_name = new_name
		ThingDatabase(Camera).Add(self)
		if exists:
			new_path, exists = self.get_file_path()
			os.rename(path, new_path)
		return True

	def GetUniqueLoadID(self) -> str:
		return f'{type(self).__qualname__}:{self.display_name}'

	def get_file_path(self, *path_ext: str) -> tuple[str, bool]:
		path = os.path.join(lifecycle.app.config["APPDATA_PATH"], 'cameras', self.display_name, *path_ext)
		return path, os.path.isdir(path)

	def set_camera_params(self, height: int, width: int, camera_matrix: np.ndarray, dist_coeffs: np.ndarray, error: float):
		self.calib_res_width = width
		self.calib_res_height = height
		self.camera_matrix = camera_matrix
		self.dist_coeffs = dist_coeffs
		self.calib_err = error

	def get_camera_params(self):
		return (self.camera_matrix, self.dist_coeffs)

	def rescale_camera_matrix(self, shape):
		sy = shape[0] / self.calib_res_height
		
		mat = self.camera_matrix
		mat *= sy
		mat[0, 2] += (shape[1] - sy * self.calib_res_width) / 2
		mat[2, 2] = 1

		return mat

	def undistortImage(self, image: MatLike):
		return self.undistortImage(image, *self.get_camera_params())
		
	def undistortImage(self, image: MatLike, camera_matrix: np.ndarray, dist_coeffs: np.ndarray) -> tuple[MatLike, Rect]:
		"""
		Undistorts an image and gives cropped rectangle

		dst = cv.undistort(img, mtx, dist, None, newcameramtx)
		# crop the image
		x, y, w, h = roi
		dst = dst[y:y+h, x:x+w]
		"""
		h, w = image.shape[:2]
		newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w,h), 1, (w,h))
		return cv.undistort(image, camera_matrix, dist_coeffs, None, newcameramtx), roi

	def UndistortPoints(self, data: np.ndarray):
		return Camera.UndistortPoints(data, *self.get_camera_params())

	@staticmethod
	def UndistortPoints(data: np.ndarray, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
		if data is not np.array:
			data = np.array(data)

		return np.squeeze(cv.undistortPoints(data, camera_matrix, dist_coeffs))