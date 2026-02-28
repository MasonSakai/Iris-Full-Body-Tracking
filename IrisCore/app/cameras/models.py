from __future__ import annotations
import cv2 as cv
from cv2.typing import MatLike
from cv2_enumerate_cameras import enumerate_cameras
from cv2_enumerate_cameras.camera_info import CameraInfo
import numpy as np

from app.dataproviders import IDataSource
from app.synchronize import source_registry_lock
from utils.registry import IThing, ThingDatabase
from utils.scribe import  IExposable, ILoadReferenceable, LoadSaveMode, Scribe, Scribe_Values, Scribe_Collections

class CameraReference(IExposable, IDataSource):
	parent: Camera

	autostart: bool
	active: bool

	def __init__(self):
		super().__init__()
		self.autostart = False
		self.active = False


	def ExposeData(self):
		super().ExposeData()
		self.autostart = Scribe_Values.Look(self.autostart, 'autostart', bool, False)

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
	

class Camera(IExposable, IThing, ILoadReferenceable):
	
	display_name : str
	transform: np.ndarray | None

	references: list[CameraReference]
	
	#functions
	def __init__(self):
		super().__init__()
		self.display_name = None
		self.transform = None
		self.references = []

	def __repr__(self):
		return '<Camera - {} "{}">'.format(self._index, self.display_name)
	
	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'name', str)
		self.transform = Scribe_Values.Look(self.transform, 'transform', np.ndarray)

		self.references = Scribe_Collections.LookList(self.references, 'references', CameraReference, Scribe_Collections.LookMode.Deep)
		if Scribe.mode == LoadSaveMode.LoadingVars:
			for ref in self.references:
				ref.parent = self
	
	def ThingID(self) -> str:
		return self.GetUniqueLoadID()

	def GetUniqueLoadID(self) -> str:
		return f'{type(self).__qualname__}:{self.display_name}'
	
class CVUndistortableCamera(Camera):

	calib_res_width: int
	calib_res_height: int
	camera_matrix: np.ndarray | None
	dist_coeffs: np.ndarray | None

	def __init__(self):
		super().__init__()
		self.calib_res_width = 0
		self.calib_res_height = 0
		self.camera_matrix = None
		self.dist_coeffs = None
	
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

	@staticmethod
	def UndistortPoints(data: np.ndarray, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
		if data is not np.array:
			data = np.array(data)

		return np.squeeze(cv.undistortPoints(data, camera_matrix, dist_coeffs))