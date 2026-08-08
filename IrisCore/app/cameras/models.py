from __future__ import annotations
import os
import typing
import cv2 as cv
from cv2.typing import MatLike, Rect
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo
from flask import render_template, request
import numpy as np

from app.main.modal import modal_success
from app.dataproviders import IDataSource
from app.synchronize import source_registry_lock
from app import lifecycle
from utils.registry import IThing, ThingDatabase
from utils.scribe import  IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Values, Scribe_Collections

class CameraReference(IDataSource, IExposable, ThingName='CameraReference'):
	parent: Camera

	autostart: bool
	_active: bool

	def __init__(self):
		super().__init__()
		self.parent = None
		self.autostart = False
		self._active = False

	@property
	def display_name(self) -> str:
		return None

	@property
	def active(self):
		return self._active

	@active.setter
	def active(self, value: bool):
		active_ref = self.parent._active_reference
		if value:
			if active_ref and active_ref != self:
				active_ref.RequestStop(source=self)
			self.parent._active_reference = self
		elif active_ref == self:
			self.parent._active_reference = None
		self._active = value



	def ExposeData(self):
		super().ExposeData()
		self.autostart = Scribe_Values.Look(self.autostart, 'autostart', bool, defaultValue=False)

	def RequestStart(self, *args, **kwargs) -> bool:
		return False
	
	def RequestStop(self, *args, **kwargs):
		pass

	def RequestAutoStart(self) -> bool:
		return self.RequestStart(source='autostart')
	
	def HasUpdate(self) -> bool:
		return False

	def GetData(self):
		pass

	def RenderView(self):
		pass

	def RequestImage(self) -> tuple[bool, MatLike]:
		return False, None
	
	
type CameraIdent = tuple[str, int | None, int | None, str | None]
def MakeCamIdent(cam: CameraInfo) -> CameraIdent:
	usb = None
	if cam.path.startswith(r"\\?\usb#"):
		try:
			usb = cam.path.split("#")[2].lower()
		except IndexError:
			pass
	return (cam.name, cam.vid, cam.pid, usb)

class LocalCameraReference(CameraReference):

	name: str
	vid: int
	pid: int
	usb: str
	
	cap: cv.VideoCapture

	def __init__(self):
		super().__init__()
		self.name = None
		self.vid = None
		self.pid = None
		self.usb = None

		self.cap = None
	
	def ExposeData(self):
		super().ExposeData()
		self.name = Scribe_Values.Look(self.name, 'name', str)
		self.vid = Scribe_Values.Look(self.vid, 'vid', int)
		self.pid = Scribe_Values.Look(self.pid, 'pid', int)
		self.usb = Scribe_Values.Look(self.usb, 'usb', str)
		
	@property
	def display_name(self):
		return self.name

	def RequestStart(self, *args, **kwargs):
		for cam in enumerate_cameras():
			if MakeCamIdent(cam) == (self.name, self.vid, self.pid, self.usb):
				break
		else: cam = None
		if not cam:
			return False
		self.cap = cv.VideoCapture(cam.index, cam.backend) # add params?

		if 'target_resolution' in kwargs:
			pass
		else:
			self.cap.set(cv.CAP_PROP_FRAME_WIDTH, self.parent.calib_res_width)
			self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, self.parent.calib_res_height)

		if not self.cap.isOpened():
			return False
		# start thread
		self.active = True
		with source_registry_lock:
			ThingDatabase(IDataSource).Add(self)
		return True
	
	def RequestStop(self, *args, **kwargs):
		if self.active:
			self.cap.release()
			self.active = False
			with source_registry_lock:
				ThingDatabase(IDataSource).Remove(self)

	@staticmethod
	def EnumerateCameras():
		
		known: dict[CameraIdent, CameraReference] = {}
		for cam in ThingDatabase(Camera).AllThingsListForReading():
			for ref in cam.references:
				if isinstance(ref, LocalCameraReference):
					known[(ref.name, ref.vid, ref.pid, ref.usb)] = ref

		found: list[tuple[CameraReference, CameraInfo]] = []
		new: list[tuple[CameraIdent, CameraInfo]] = []
		for cam in enumerate_cameras():
			ident = MakeCamIdent(cam)
			if ident in known:
				found.append((known[ident], cam))
			else:
				new.append([ident, cam])

		return found, new

	def RenderView(self):
		form = CameraReferenceForm()
		if form.validate_on_submit():
			self.autostart = form.autostart.data
			return modal_success()
		elif request.method == 'GET':
			form.autostart.data = self.autostart
		return render_template('_view_lref.html', ref=self, form=form, other_source_active=((r := self.parent.ActiveReference()) and r != self))

	def RequestImage(self):
		if not (self.cap and self.cap.isOpened()):
			return False, None
		return self.cap.read()
	

class Camera(IThing, IExposable, ILoadReferenceable, ThingName='Camera'):
	
	display_name : str
	transform: np.ndarray | None
	
	calib_res_width: int
	calib_res_height: int
	camera_matrix: np.ndarray | None
	dist_coeffs: np.ndarray | None
	calib_rms: float
	fisheye: bool

	references: list[CameraReference]
	_active_reference: CameraReference | None
	
	#functions
	def __init__(self):
		super().__init__()
		self.display_name = None
		self.calib_res_width = 0
		self.calib_res_height = 0
		self.camera_matrix = None
		self.dist_coeffs = None
		self.calib_rms = -1.0
		self.fisheye = False
		self.transform = None
		self.references = []
		self._active_reference = None

	def __repr__(self):
		return '<Camera - "{}">'.format(self.display_name)
	
	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'name', str)

		self.calib_res_width = Scribe_Values.Look(self.calib_res_width, 'CalibResWidth', int, defaultValue=0)
		self.calib_res_height = Scribe_Values.Look(self.calib_res_height, 'CalibResHeight', int, defaultValue=0)
		self.camera_matrix = Scribe_Values.Look(self.camera_matrix, 'CameraMatrix', np.ndarray)
		self.dist_coeffs = Scribe_Values.Look(self.dist_coeffs, 'DistCoeffs', np.ndarray)
		self.calib_rms = Scribe_Values.Look(self.calib_rms, 'CalibRMS', float, defaultValue=-1.0)
		self.fisheye = Scribe_Values.Look(self.fisheye, 'fisheye', bool, defaultValue=False)

		self.transform = Scribe_Values.Look(self.transform, 'transform', np.ndarray)

		self.references = Scribe_Collections.LookList(self.references, 'references', CameraReference, Scribe_Collections.LookMode.Deep)
		if Scribe.mode == LoadSaveMode.LoadingVars:
			for ref in self.references:
				ref.parent = self

	def GetUniqueLoadID(self) -> str:
		return self.ThingID

	def ActiveReference(self) -> CameraReference | None:
		return self._active_reference

	def get_file_path(self, *path_ext: str) -> tuple[str, bool]:
		path = os.path.join(lifecycle.app.config["APPDATA_PATH"], 'cameras', self.ThingID, *path_ext)
		return path, os.path.isdir(path)

	def set_camera_params(self, height: int, width: int, camera_matrix: np.ndarray, dist_coeffs: np.ndarray, rms: float, fisheye: bool):
		self.calib_res_width = width
		self.calib_res_height = height
		self.camera_matrix = camera_matrix
		self.dist_coeffs = dist_coeffs
		self.calib_rms = rms
		self.fisheye = fisheye

	def get_camera_params(self):
		return (self.camera_matrix, self.dist_coeffs, self.fisheye)

	def rescale_camera_matrix(self, shape):
		sy = shape[0] / self.calib_res_height
		
		mat = self.camera_matrix.copy()
		mat *= sy
		mat[0, 2] += (shape[1] - sy * self.calib_res_width) / 2
		mat[2, 2] = 1

		return mat
	
	@typing.overload
	def undistortImage(self, image: MatLike): ...
		
	def undistortImage(self, image: MatLike, camera_matrix: np.ndarray = None, dist_coeffs: np.ndarray = None, fisheye: bool = None) -> tuple[MatLike, Rect]:
		"""
		Undistorts an image and gives cropped rectangle

		dst = cv.undistort(img, mtx, dist, None, newcameramtx)
		# crop the image
		x, y, w, h = roi
		dst = dst[y:y+h, x:x+w]
		"""
		if camera_matrix == None:
			camera_matrix, dist_coeffs, fisheye = self.get_camera_params()

		h, w = image.shape[:2]

		if fisheye:
			new_k = cv.fisheye.estimateNewCameraMatrixForUndistortRectify(camera_matrix, dist_coeffs, (w, h), np.eye(3), balance=1)
			return cv.fisheye.undistortImage(image, camera_matrix, dist_coeffs, Knew=new_k), new_k, None # need to figure out rect?
		else:
			newcameramtx, roi = cv.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w,h), 1, (w,h))
			return cv.undistort(image, camera_matrix, dist_coeffs, newCameraMatrix=newcameramtx), newcameramtx, roi

	def UndistortPoints(self, data: np.ndarray):
		return Camera.UndistortPoints(data, *self.get_camera_params())

	@staticmethod
	def UndistortPoints(data: np.ndarray, new_camera_matrix: np.ndarray, camera_matrix: np.ndarray, dist_coeffs: np.ndarray, fisheye: bool):
		data = np.array(data)

		if fisheye:
			return np.squeeze(cv.fisheye.undistortPoints(data, camera_matrix, dist_coeffs, P=new_camera_matrix))
		else:
			return np.squeeze(cv.undistortPoints(data, camera_matrix, dist_coeffs, P=new_camera_matrix))

	
from app.cameras.forms import CameraReferenceForm