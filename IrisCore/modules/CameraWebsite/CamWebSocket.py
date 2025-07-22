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
	camCaps: dict[str, dict | int | float] | None = None

	def __init__(self, sid, cam):
		self.sid = sid
		self.cam = cam

		socketio.emit('caps', namespace='/camsite', to=sid)

	def on_disconnect(self, reason):
		print(reason)
		sockets.pop(self.cam.id)

	positions = []
	scores = []

	def on_pose(self, data):
		positions = []
		scores = []
		
		pose_positions = []
		pose_scores = {}

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
			print(e, data) #, positions, pose_positions, scores, pose_scores, sep='\n')

	def on_image(self, data_url):
		(_, dist_coeffs) = self.cam.get_camera_params()

		img = cv.imdecode(np.frombuffer(base64.b64decode(data_url.split(',')[1]), np.uint8), cv.IMREAD_COLOR)
		img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
		camera_matrix = self.cam.rescale_camera_matrix(img.shape)
		img = self.cam.undistortImage(img, camera_matrix, dist_coeffs)
		
		scale = 3
		if scale > 1 and img.shape == (480, 640):
			kern = np.array([[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]])
			img = cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)
			img = cv.filter2D(img, -1, kern)
			
		camera_matrix = self.cam.rescale_camera_matrix(img.shape)
		params = [camera_matrix[0, 0], camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2]]

		image = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
		hasTag = False

		sd = 0.1016
		sr = 0.1095

		detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()
		for detector in detectors:
			detector = detector.createDetector()
			res = detector.detect(img, True, params, sd)
			print(self.cam.id, len(res))
			for r in res:
				hasTag = True
				# extract the bounding box (x, y)-coordinates for the AprilTag
				# and convert each of the (x, y)-coordinate pairs to integers
				(ptA, ptB, ptC, ptD) = r.corners
				ptB = (int(ptB[0]), int(ptB[1]))
				ptC = (int(ptC[0]), int(ptC[1]))
				ptD = (int(ptD[0]), int(ptD[1]))
				ptA = (int(ptA[0]), int(ptA[1]))
				# draw the bounding box of the AprilTag detection
				cv.line(image, ptA, ptB, (0, 255, 0), 2)
				cv.line(image, ptB, ptC, (0, 255, 0), 2)
				cv.line(image, ptC, ptD, (0, 255, 0), 2)
				cv.line(image, ptD, ptA, (0, 255, 0), 2)
				# draw the center (x, y)-coordinates of the AprilTag
				(cX, cY) = (int(r.center[0]), int(r.center[1]))
				cv.circle(image, (cX, cY), 5, (0, 0, 255), -1)
				# draw the tag family on the image
				dist = np.linalg.norm(r.pose_t * (sr/sd))
				cv.putText(image, '{}:{} @ {}'.format(r.tag_family.decode("utf-8"), r.tag_id, dist),
					(ptA[0], ptA[1] - 15), cv.FONT_HERSHEY_SIMPLEX, 0.25 * scale, (255, 0, 0), scale)

		cv.imwrite('{}_{}_t.png'.format(self.cam.id, scale), image)

	def on_caps(self, caps):
		self.camCaps = caps
		socketio.emit('image', {
			'width': caps['width']['max'],
			'height': caps['height']['max']
		}, namespace='/camsite', to=self.sid)

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

@socketio.on('caps', namespace='/camsite')
def on_caps(data):
	sockets[sid_dict[request.sid]].on_caps(data)

