from app import db, socketio
import sqlalchemy as sqla
from flask import request
import numpy as np
import cv2 as cv
import base64
from CameraWebsite.models import WebsiteCamera
from app.dataproviders.position import RayPositionSource, ScoredPositionSource
from app.synchronize import source_pose_lock
from app.apriltag.models import AprilTagDetector
from flask_socketio import disconnect


sid_dict = {}
sockets = {}

class CamWebSocket(RayPositionSource, ScoredPositionSource):
	
	sid: str
	cam: WebsiteCamera

	def __init__(self, sid, cam):
		self.sid = sid
		self.cam = cam

		socketio.emit('image', 'max', namespace='/camsite', to=sid)

	def on_disconnect(self, reason):
		print(reason)
		sockets.pop(self.cam.id)

	positions = []
	scores = []

	def on_pose(self, data):
		positions = []
		scores = []

		try:
			(camera_matrix, dist_coeffs) = self.cam.get_camera_params()

			for pose in data['pose']:
				pose_positions = []
				pose_scores = {}
				pose_keys = pose.keys()
				for key in pose_keys:
					pose_scores[key] = pose[key]['score']
					pose_positions.append([pose[key]['x'], pose[key]['y']])
				
				pose_positions = self.cam.undistortPoints(pose_positions, camera_matrix, dist_coeffs)
				pose_positions = np.append(pose_positions, np.ones((len(pose_positions), 1)), axis=1)
				pose_positions /= np.linalg.norm(pose_positions, axis=1, keepdims=True)

				pose_positions = dict(zip(pose_keys, pose_positions))

				positions.append(pose_positions)
				scores.append(pose_scores)

			with source_pose_lock:
				self.positions = positions
				self.scores = scores
		except Exception as e:
			print(e)
			disconnect(self.sid, '/camsite')

	def on_image(self, data_url):
		(camera_matrix, dist_coeffs) = self.cam.get_camera_params()

		image = cv.imdecode(np.frombuffer(base64.b64decode(data_url.split(',')[1]), np.uint8), cv.IMREAD_COLOR)
		print(image.shape)
		image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
		image = self.cam.undistortImage(image, camera_matrix, dist_coeffs)

		detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()
		for detector in detectors:
			detector = detector.createDetector()
			res = detector.detect(image, True, [camera_matrix[0, 0], camera_matrix[0, 2], camera_matrix[1, 1], camera_matrix[1, 2]], 0.11176022352)
			print(self.cam.id, res)


	def get_priority_positions(self):
		return 20

	def get_source_transform(self):
		return self.cam.get_transform()

	def get_data_positions(self):
		return self.positions
	
	def get_scores_positions(self):
		return self.scores



@socketio.on('connect', namespace='/camsite')
def on_connect(auth):
	if auth['id'] in sockets:
		if 'force' in auth and auth['force']:
			socket = sockets[auth['id']]
			print('warning: {} is overriding {} on camera {}'.format(request.sid, socket.sid, auth['id']))
			disconnect(socket.sid)
		else:
			raise ConnectionRefusedError('Camera already taken')

	sid_dict[request.sid] = auth['id']
	sockets[auth['id']] = CamWebSocket(request.sid, db.session.get(WebsiteCamera, auth['id']))

@socketio.on('disconnect', namespace='/camsite')
def on_disconnect(reason):
	sockets[sid_dict[request.sid]].on_disconnect(reason)
	sid_dict.pop(request.sid)

@socketio.on('pose', namespace='/camsite')
def on_pose(data):
	sockets[data['id']].on_pose(data)

@socketio.on('image', namespace='/camsite')
def on_image(data):
	try:
		sockets[sid_dict[request.sid]].on_image(data)
	except ... as e:
		print(e)

