import atexit
from math import sqrt
import time
from flask import Flask
from threading import Thread, Lock
from app import socketio
from app.dataproviders.position import RayPositionSource, ScoredPositionSource
import app.synchronize as sync
from app.dataproviders import DataSource, source_registry
import numpy as np

def callAllIn(T: type, method_name: str, *args, **kwargs):
    for klass in T.mro():
        if klass is object:  # Skip the base object class
                continue
        if method_name in klass.__dict__ and callable(getattr(klass, method_name)):
            # Get the method from the current class in MRO and call it
            getattr(klass, method_name)(*args, **kwargs)

def project(x, on): return on * np.dot(x, on) / np.dot(on, on)
def reject(x, on): return x - project(x, on)

def closest_points_between_rays(O1: np.array, D1: np.array, O2: np.array, D2: np.array):
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

publishers = []

class MathWorker:

    _app: Flask
    _has_init = False
    running_lock: Lock
    running = False
    worker_thread: Thread

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
        try:
            while True:
                with self.running_lock:
                    if not self.running:
                        break

                self.UpdateSources()
                self.CalculatePositions()
                self.PositionPostProcessing()
                self.CalculateRotations()
                self.PostData()

                time.sleep(0.05)
        except BaseException as e:
            print(e)
            
        with self.running_lock:
            self.running = False
        print ('bw thread stop')
    

    def InitSources(self):
        with sync.source_registry_lock:
            for source in source_registry:
                try:
                    source.init()
                except BaseException as e:
                    print(e)

    sources: list[DataSource] = []
    def UpdateSources(self):
        self.sources.clear()
        with sync.source_registry_lock:
            for source in source_registry:
                try:
                    callAllIn(type(source), 'update', source)
                    self.sources.append(source)
                except BaseException as e:
                    print(e)

    pose_data: dict[str, np.array] = {}
    last_pose_data: dict[str, np.array] = {}

    position_data: dict[str, np.array] = {}
    def CalculatePositions(self):
        self.position_data.clear()
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
        pass

    def CalculateRotations(self):
        pose = {}
        for ident, data in self.pose_data.items():
            trans = np.identity(4)
            trans[:3, 3] = data
            pose[ident] = trans
        self.pose_data = pose


    def PostData(self):
        for p in publishers:
            p(self.pose_data)

    

math_worker = MathWorker()
@socketio.on('connect', namespace='*')
def start_worker():
    math_worker.start()