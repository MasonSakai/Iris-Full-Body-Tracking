import numpy as np
import cv2 as cv
import base64

from app import socketio
from app.cameras.models import CVUndistortableCamera, CameraReference
from app.dataproviders import IDataSource
from utils.registry import ThingDatabase
from utils.scribe import LoadSaveMode, Scribe, Scribe_Values
from app.synchronize import source_registry_lock
from app.apriltag.calibration import CalculateCameraPose

class WebAICameraReference(CameraReference):

	parent: CVUndistortableCamera

	socket_sid : str
	confidence_threshold : float

	def __init__(self):
		super().__init__()
		self.positions = {}
		self.scores = {}
		self.timestamp = 0
		self.got_new_pose = False

	def ExposeData(self):
		super().ExposeData()
		self.confidence_threshold = Scribe_Values.Look(self.confidence_threshold, 'ConfidenceThreshold', int)
		if Scribe.mode == LoadSaveMode.LoadingVars:
			ThingDatabase(WebAICameraReference).Add(self)

	def RequestStart(self, *args, **kwargs) -> bool:
		self.socket_sid = kwargs['sid']
		self.active = True
		with source_registry_lock:
			ThingDatabase(IDataSource).Add(self)
		return True

	def RequestStop(self, *args, **kwargs):
		print(args)
		if self.active:
			with source_registry_lock:
				ThingDatabase(IDataSource).Remove(self)
			self.active = False
			self.socket_sid = None

			
	positions: dict[str, np.ndarray]
	scores: dict[str, float]
	timestamp: float
	got_new_pose: bool

	def on_pose(self, data):
		positions = {}
		scores = {}
		
		pose_positions = []
		pose_scores = {}

		try:
			(camera_matrix, dist_coeffs) = self.parent.get_camera_params()
			if not camera_matrix or not dist_coeffs:
				return

			for pose in data['pose']:
				pose_positions = []
				pose_scores = {}
				pose_keys = pose.keys()
				if len(pose_keys) > 0:
					for key in pose_keys:
						pose_scores[key] = pose[key]['score']
						pose_positions.append([pose[key]['x'], pose[key]['y']])
				
					pose_positions = np.array(self.parent.UndistortPoints(pose_positions, camera_matrix, dist_coeffs))
					if (len(pose_positions.shape) == 1):
						pose_positions = pose_positions.reshape(1, -1)
					pose_positions = np.append(pose_positions, np.ones((len(pose_positions), 1)), axis=1)

					pose_positions = dict(zip(pose_keys, pose_positions))

					positions = pose_positions
					scores = pose_scores

			with self.source_data_lock:
				self.positions = positions
				self.scores = scores
				self.timestamp = data['time']
				self.got_new_pose = True
		except Exception as e:
			print(e) #, data, positions, pose_positions, scores, pose_scores, sep='\n')

	def on_caps(self, caps):
		self.camCaps = caps
		if self.cam.calib_res_width > 0:
			socketio.emit('image', {
				'width': caps['width']['max'],
				'height': caps['height']['max']
			}, namespace='/camsite', to=self.sid)

	def on_image(self, data_url):
		img = cv.imdecode(np.frombuffer(base64.b64decode(data_url.split(',')[1]), np.uint8), cv.IMREAD_COLOR)
		img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		CalculateCameraPose(self.cam, img)


	def HasUpdate(self):
		with self.source_data_lock:
			return self.got_new_pose

	def GetData(self):
		with self.source_data_lock:
			self.got_new_pose = False
			return {
				"transform": self.parent.transform,
				"timestamp": self.timestamp,
				"proj_positions": self.positions,
				"scores": self.scores
			}

