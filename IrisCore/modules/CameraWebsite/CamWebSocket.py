from app import db, socketio
import sqlalchemy as sqla
from flask import request
import numpy as np
import cv2 as cv
import base64
from CameraWebsite.models import WebsiteCamera
from app.apriltag.calibration import CalculateCameraPose
from app.dataproviders.position import RayPositionSource, ScoredPositionSource
from flask_socketio import disconnect
from app.dataproviders import TimestampedDataSource, source_registry
from app.synchronize import source_registry_lock

sid_dict = {}
sockets = {}

class CamWebSocket(RayPositionSource, ScoredPositionSource, TimestampedDataSource):
    
    sid: str
    cam: WebsiteCamera
    camCaps: dict[str, dict | int | float] | None = None

    def __init__(self, sid, cam):
        self.sid = sid
        self.cam = cam
        with source_registry_lock:
            source_registry.append(self)

        socketio.emit('caps', namespace='/camsite', to=sid)

    def on_disconnect(self, reason):
        print(reason)
        sockets.pop(self.cam.id)
        with source_registry_lock:
            source_registry.remove(self)

    positions = {}
    scores = {}
    timestamp = 0
    got_new_pose = False

    def on_pose(self, data):
        positions = {}
        scores = {}
        
        pose_positions = []
        pose_scores = {}

        try:
            (camera_matrix, dist_coeffs) = self.cam.get_camera_params()
            if (len(camera_matrix) == 0):
                return

            for pose in data['pose']:
                pose_positions = []
                pose_scores = {}
                pose_keys = pose.keys()
                if len(pose_keys) > 0:
                    for key in pose_keys:
                        pose_scores[key] = pose[key]['score']
                        pose_positions.append([pose[key]['x'], pose[key]['y']])
                
                    pose_positions = np.array(self.cam.undistortPoints(pose_positions, camera_matrix, dist_coeffs))
                    if (len(pose_positions.shape) == 1):
                        pose_positions = pose_positions.reshape(1, -1)
                    pose_positions = np.append(pose_positions, np.ones((len(pose_positions), 1)), axis=1)

                    pose_positions = dict(zip(pose_keys, pose_positions))

                    positions = pose_positions
                    scores = pose_scores

            with self.source_pose_lock:
                self.positions = positions
                self.scores = scores
                self.timestamp = data['time']
                self.got_new_pose = True
        except Exception as e:
            print(e) #, data, positions, pose_positions, scores, pose_scores, sep='\n')

    def on_image(self, data_url):
        img = cv.imdecode(np.frombuffer(base64.b64decode(data_url.split(',')[1]), np.uint8), cv.IMREAD_COLOR)
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        CalculateCameraPose(self.cam, img)
        

    def on_caps(self, caps):
        self.camCaps = caps
        if self.cam.calib_res_width > 0:
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
    
    def get_timestamp(self):
        return self.timestamp

    def should_update(self):
        with self.source_pose_lock:
            return self.got_new_pose

    def update(self):
        with self.source_pose_lock:
            self.got_new_pose = False




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
    except BaseException as e:
        print(e)

@socketio.on('caps', namespace='/camsite')
def on_caps(data):
    sockets[sid_dict[request.sid]].on_caps(data)

