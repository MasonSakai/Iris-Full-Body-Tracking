import atexit
from math import sqrt
from typing import Callable
from flask import Flask
from threading import Thread, Lock
from app import socketio
from app.dataproviders.position import RayPositionSource, ScoredPositionSource
import app.synchronize as sync
from app.dataproviders import DataSource, source_registry
import numpy as np
from app.dataprocessing.rollingaverage import RollingAverageFilter

def callAllIn(T: type, method_name: str, *args, **kwargs):
    for klass in T.mro():
        if klass is object:  # Skip the base object class
                continue
        if method_name in klass.__dict__ and callable(getattr(klass, method_name)):
            # Get the method from the current class in MRO and call it
            getattr(klass, method_name)(*args, **kwargs)

def project(x, on): return on * np.dot(x, on) / np.dot(on, on)
def reject(x, on): return x - project(x, on)

def closest_points_between_rays(O1: np.ndarray, D1: np.ndarray, O2: np.ndarray, D2: np.ndarray):
    norm = np.cross(D1, D2)
    o1 = reject(O1, norm)
    o2 = reject(O2, norm)
    d1 = reject(D1, norm)
    d2 = reject(D2, norm)

    conv_dist = np.linalg.norm(reject(o2 - o1, d1))
    conv_rate = np.linalg.norm(reject(d2, d1))
    t2 = conv_dist / conv_rate
    
    rel_rate = np.dot(d1, d2) / np.dot(d1, d1)
    rel_dist = np.dot(o2 - o1, d1) / np.dot(d1, d1)
    t1 = t2 * rel_rate + rel_dist

    # Calculate the closest points on each ray
    P1_closest = O1 + t1 * D1
    P2_closest = O2 + t2 * D2

    return P1_closest, P2_closest

def calc_mid_point(data1, data2):
    (d1, o1, s1) = data1
    (d2, o2, s2) = data2
    p1, p2 = closest_points_between_rays(o1, d1, o2, d2)

    s = sqrt(s1*s2)
    t = 0.5 if s1 == s2 else (1 - (s - s1) / (s2 - s1))

    return p1 + t * (p2 - p1), s

class MathWorker:

    _app: Flask
    _has_init = False
    running_lock: Lock
    running = False
    worker_thread: Thread
    filters: dict[str, RollingAverageFilter] = {}

    publishers: list[Callable[[np.ndarray], None]] = []

    def __init__(self, app: Flask = None):
        self.running_lock = Lock()
        self.worker_thread = Thread(target=self.worker_func, daemon=True)
        if (app): self.init_app(app)

    def init_app(self, app: Flask):
        self._app = app
        app.before_request(self.start)

    def start(self):
        if self._has_init: return
        self._has_init = True
        atexit.register(self.teardown)
        with self.running_lock:
            self.running = True
        self.worker_thread.start()
    
    def teardown(self):
        with self.running_lock:
            self.running = False
        if (self.worker_thread):
            self.worker_thread.join()

    def worker_func(self):
        print ('bw thread start')
        self.InitSources()
        while True:
            try:
                with self.running_lock:
                    if not self.running:
                        break

                if self.ShouldUpdate():
                    self.UpdateSources()
                    self.CalculatePositions()
                    self.PositionPostProcessing()
                    self.CalculateRotations()
                    self.PrePostData()
                    self.PostData()

            except BaseException as e:
                print('bw thread except:', e)
            
        with self.running_lock:
            self.running = False
        print ('bw thread stop')
    

    def InitSources(self):
        with sync.source_registry_lock:
            for source in source_registry:
                try:
                    source.init()
                except BaseException as e:
                    print('init sources', source, e)

    sources: list[DataSource] = []
    def UpdateSources(self):
        self.sources.clear()
        with sync.source_registry_lock:
            for source in source_registry:
                try:
                    callAllIn(type(source), 'update', source)
                    self.sources.append(source)
                except BaseException as e:
                    print('update sources', source, e)

    def ShouldUpdate(self):
        with sync.source_registry_lock:
            for source in source_registry:
                try:
                    if source.should_update():
                        return True
                except BaseException as e:
                    print('should update', source, e)
        return False

    pose_data: dict[str, np.ndarray] = {}
    last_pose_data: dict[str, np.ndarray] = {}

    def CalculatePositions(self):
        self.pose_data.clear()
        self.last_pose_data = self.pose_data
        self.pose_data.clear()

        ray_data: dict[str, list[(np.array, np.array, float)]] = {}
        for source in self.sources:
            if isinstance(source, RayPositionSource):
                directions = source.worker_data_positions
                trans = source.worker_source_transform
                scores = {}
                if isinstance(source, ScoredPositionSource):
                    scores = source.worker_scores_positions

                for ident in directions:
                    if ident not in ray_data: ray_data[ident] = []

                    ray_data[ident].append((
                        np.linalg.matmul(trans[:3, :3], directions[ident]),
                        trans[:3, 3],
                        scores[ident] if ident in scores else 1
                    ))

        for ident, data in ray_data.items():
            if len(data) < 2:
                continue

            else:
                points = []

                for i in range(1, len(data)):
                    d1 = data[i]
                    for j in range(0, i):
                        d2 = data[j]
                        points.append(calc_mid_point(d1, d2))

                point = np.zeros((1, 3))
                score = 0
                for (p, s) in points:
                    point += p * s
                    score += s
                point /= score
                self.pose_data[ident] = point

    
    def PositionPostProcessing(self):
        for key in self.pose_data:
            if key not in self.filters:
                self.filters[key] = RollingAverageFilter(3, 4, 0.6)
            self.pose_data[key] = self.filters[key].apply(self.pose_data[key])
        
        if 'left_shoulder' in self.pose_data and 'right_shoulder' in self.pose_data:
            self.pose_data['chest'] = (self.pose_data['left_shoulder'] + self.pose_data['right_shoulder']) / 2
        
        if 'left_hip' in self.pose_data and 'right_hip' in self.pose_data:
            self.pose_data['hip'] = (self.pose_data['left_hip'] + self.pose_data['right_hip']) / 2
        
        if 'left_ear' in self.pose_data and 'right_ear' in self.pose_data:
            self.pose_data['head'] = (self.pose_data['left_ear'] + self.pose_data['right_ear']) / 2

    def CalculateRotations(self): #+x left, -y up, -z forward
        
        #self.do_head('head', 'left_ear', ['nose', 'left_eye', 'right_eye'], ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear'])

        self.do_chest_hip('hip', 'chest', 'left_hip', False)
        self.do_chest_hip('chest', 'hip', 'left_shoulder', True)

        do_arm_rotation(self, 'left_shoulder', 'left_elbow', 'left_wrist', 'chest', False)
        do_arm_rotation(self, 'right_shoulder', 'right_elbow', 'right_wrist', 'chest', True)

        
        do_leg_rotation(self, 'left_hip', 'left_knee', 'left_ankle', 'hip')
        do_leg_rotation(self, 'right_hip', 'right_knee', 'right_ankle', 'hip')

        
        pose = {}
        for ident, data in self.pose_data.items(): #remove, make clients handle this
            if data.size > 3:
                pose[ident] = data
                continue
            trans = np.identity(4)
            trans[:3, 3] = data
            pose[ident] = trans
        self.pose_data = pose

    def do_head(self, key_head: str, key_left: str, keys_forward: list[str], rot_copy: list[str]):
        if key_head in self.pose_data:
            if key_left in self.pose_data and all(key in self.pose_data for key in keys_forward):
                pos_head = self.pose_data[key_head][:3, 3]
                pos_forward = sum(map(lambda key: self.pose_data[key][:3, 3], keys_forward)) / len(keys_forward)
                pos_left = self.pose_data[key_left][:3, 3]

                d_back = pos_head - pos_forward
                d_back /= np.linalg.norm(d_back)
                d_left = pos_left - pos_head
                d_left /= np.linalg.norm(d_left)
                
                d_y = np.cross(d_back, d_left)
                d_y /= np.linalg.norm(d_y)
                
                d_x = np.cross(d_y, d_back)
                d_x /= np.linalg.norm(d_x)

                self.pose_data[key_head][:3, 0] = d_x
                self.pose_data[key_head][:3, 1] = d_y
                self.pose_data[key_head][:3, 2] = d_back

            else:
                pass
        
            mat = self.pose_data[key_head][:3, :3]
            for ident in rot_copy:
                self.pose_data[ident][:3, :3] = mat

    def do_chest_hip(self, key_source: str, key_target: str, key_left: str, inv_target: bool):
        if key_source in self.pose_data and key_target in self.pose_data and key_left in self.pose_data:
            pos_source = self.pose_data[key_source]
            pos_target = self.pose_data[key_target]
            if pos_target.size > 3:
                pos_target = pos_target[:3, 3]
            pos_left = self.pose_data[key_left]
            if pos_left.size > 3:
                pos_left = pos_left[:3, 3]

            d_target = pos_target - pos_source
            d_target /= np.linalg.norm(d_target)
            if (inv_target):
                d_target *= -1
            d_left = pos_left - pos_source
            d_left /= np.linalg.norm(d_left)

            d_z = np.cross(d_target, d_left)
            d_z /= np.linalg.norm(d_z)

            d_x = np.cross(d_z, d_target)
            d_x /= np.linalg.norm(d_x)
            
            pose = np.identity(4)
            pose[:3, 0] = d_x
            pose[:3, 1] = -d_target
            pose[:3, 2] = d_z
            pose[:3, 3] = pos_source
            self.pose_data[key_source] = pose
        else:
            pass

    post_filter = ['head', 'chest', 'hip',
                   'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist',
                   'left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle']
    post_data: dict[str, np.array] = {}
    def PrePostData(self):
        self.post_data.clear()
        for key in self.post_filter:
            if key in self.pose_data:
                self.post_data[key] = self.pose_data[key]

    def PostData(self):
        for p in self.publishers:
            p(self.post_data)

from app.posehelpers.legs import do_leg_rotation
from app.posehelpers.arms import do_arm_rotation

math_worker = MathWorker()
@socketio.on('connect', namespace='*')
def start_worker():
    math_worker.start()