from app import db, socketio
from flask import request
import numpy as np
from CameraWebsite.models import WebsiteCamera
from app.dataproviders.position import RayPositionSource, ScoredPositionSource
from app.synchronize import source_pose_lock
from flask_socketio import emit, disconnect


sid_dicts = {}
sockets = {}

class CamWebSocket(RayPositionSource, ScoredPositionSource):
	
	sid: str
	cam: WebsiteCamera

	def __init__(self, sid, cam):
		self.sid = sid
		self.cam = cam

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

	sid_dicts[request.sid] = auth['id']
	sockets[auth['id']] = CamWebSocket(request.sid, db.session.get(WebsiteCamera, auth['id']))

@socketio.on('disconnect', namespace='/camsite')
def on_disconnect(reason):
	sockets[sid_dicts[request.sid]].on_disconnect(reason)
	sid_dicts.pop(request.sid)

@socketio.on('pose', namespace='/camsite')
def on_pose(data):
	sockets[data['id']].on_pose(data)

