from __future__ import annotations
from typing import Any
import cv2 as cv
from cv2.typing import MatLike
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo
import numpy as np

from utils.registry import CreateThingDatabase, IThing, ThingDatabase
from utils.scribe import  IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Values, Scribe_Collections

class CameraReference(IExposable, IThing):
	parent: Camera

	autostart: bool

	def ExposeData(self):
		super().ExposeData()
		self.autostart = Scribe_Values.Look(self.autostart, 'autostart', bool)
		if Scribe.mode == LoadSaveMode.PostLoadInit:
			ThingDatabase(CameraReference).Add(self)

	def ThingName(self):
		return f"{self.__qualname__}:{self.parent.ThingName()}"
		
CreateThingDatabase(CameraReference)

class LocalCameraReference(CameraReference):

	name: str
	vid: int
	pid: int

	cap: cv.VideoCapture
	
	def ExposeData(self):
		super().ExposeData()
		self.name = Scribe_Values.Look(self.name, 'name', str)
		self.vid = Scribe_Values.Look(self.vid, 'vid', int)
		self.pid = Scribe_Values.Look(self.pid, 'pid', int)

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


class Camera(IExposable, IThing, ILoadReferenceable):
	
	display_name : str
	transform: np.ndarray

	references: list[CameraReference]
	
	#functions
	def __init__(self):
		super().__init__()
		self.references = []

	def __repr__(self):
		return '<Camera - {} "{}">'.format(self._index, self.display_name)
	
	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'name', str)
		self.transform = Scribe_Values.Look(self.transform, 'transform', np.ndarray)

		self.references = Scribe_Collections.LookList(self.references, 'references', CameraReference, Scribe_Collections.LookMode.Deep)
		if Scribe.mode == LoadSaveMode.LoadingVars:
			db = ThingDatabase(CameraReference)
			for ref in self.references:
				ref.parent = self
	
	def ThingName(self) -> str:
		return self.display_name

	def GetUniqueLoadID(self) -> str:
		return f'{self.__qualname__}:{self.display_name}'

	def set_transform(self, transform: np.ndarray):
		self.transform = transform

	def get_transform(self) -> np.array:
		return self.transform

	def getConfig(self) -> dict[str, Any]:
		return {
			'index': self._index,
			'name': self.display_name
		}
	
	def setConfig(self, config):
		if 'name' in config:
			self.display_name = config['name']

CreateThingDatabase(Camera)

class CVUndistortableCamera(Camera):

	calib_res_width: int
	calib_res_height: int
	camera_matrix: np.ndarray
	dist_coeffs: np.ndarray

	def __init__(self):
		super().__init__()
		self.calib_res_width = 0
		self.calib_res_height = 0
	
	def ExposeData(self):
		super().ExposeData()
		self.calib_res_width = Scribe_Values.Look(self.calib_res_width, 'CalibResWidth', int, default_value=0)
		self.calib_res_height = Scribe_Values.Look(self.calib_res_height, 'CalibResHeight', int, default_value=0)
		self.camera_matrix = Scribe_Values.Look(self.camera_matrix, 'CameraMatrix', np.ndarray)
		self.dist_coeffs = Scribe_Values.Look(self.dist_coeffs, 'DistCoeffs', np.ndarray)


	def set_camera_params(self, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
		self.camera_matrix = camera_matrix
		self.dist_coeffs = dist_coeffs

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
		
	def undistortImage(self, image: MatLike, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
		return cv.undistort(image, camera_matrix, dist_coeffs)

	def UndistortPoints(self, data: np.ndarray):
		return CVUndistortableCamera.UndistortPoints(data, *self.get_camera_params())

		
	def UndistortPoints(data: np.ndarray, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
		if data is not np.array:
			data = np.array(data)

		return np.squeeze(cv.undistortPoints(data, camera_matrix, dist_coeffs))
