from app import socketio
from flask import request
from CameraWebsite.models import WebsiteCameraReference
from flask_socketio import disconnect
from modules.CameraWebsite.models import WebsiteCameraReference
from utils.registry import ThingDatabase

sockets: dict[str, WebsiteCameraReference] = {}

@socketio.on('connect', namespace='/camsite')
def on_connect(auth):
	if request.sid in sockets:
		if 'force' in auth and auth['force']:
			socket = sockets[auth['id']]
			print('warning: {} is overriding {} on camera {}'.format(request.sid, socket.sid, auth['name']))
			disconnect(socket.sid)
		else:
			raise ConnectionRefusedError('Camera already taken')

	ref = ThingDatabase(WebsiteCameraReference).GetNamed(auth['name'])
	ref.RequestStart(sid=request.sid)
	sockets[request.sid] = ref

@socketio.on('disconnect', namespace='/camsite')
def on_disconnect(reason):
	sockets[request.sid].RequestStop(reason)

@socketio.on('pose', namespace='/camsite')
def on_pose(data):
	sockets[request.sid].on_pose(data)

@socketio.on('caps', namespace='/camsite')
def on_caps(data):
	sockets[request.sid].on_caps(data)



# class CamWebSocket(RayPositionSource, ScoredPositionSource, TimestampedDataSource):
	
# 	sid: str
# 	cam: WebsiteCameraReference
# 	camCaps: dict[str, dict | int | float] | None = None

# 	def __init__(self, sid, cam):
# 		self.sid = sid
# 		self.cam = cam
# 		with source_registry_lock:
# 			source_registry.append(self)

# 		socketio.emit('caps', namespace='/camsite', to=sid)

# 	def on_disconnect(self, reason):
# 		print(reason)
# 		sockets.pop(self.cam.id)
# 		with source_registry_lock:
# 			source_registry.remove(self)
		
# 	def get_priority_positions(self):
# 		return 20

# 	def get_source_transform(self):
# 		return self.cam.get_transform()

# 	def get_data_positions(self):
# 		return self.positions
	
# 	def get_scores_positions(self):
# 		return self.scores
	
# 	def get_timestamp(self):
# 		return self.timestamp

# 	def should_update(self):
# 		with self.source_data_lock:
# 			return self.got_new_pose

# 	def update(self):
# 		with self.source_data_lock:
# 			self.got_new_pose = False

