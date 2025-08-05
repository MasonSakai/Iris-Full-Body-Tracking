import atexit
from flask import Flask
from app import Config
from app.IrisModules import IrisModule
from app.main.math_worker import math_worker
import numpy as np
import quaternion

from vmcp.osc import OSC
from vmcp.osc.backend.osc4py3 import as_eventloop as backend # as_allthreads if I can figure out the error
from vmcp.osc.channel import Sender
from vmcp.osc.typing import Message
from vmcp.typing import (
    CoordinateVector,
    Quaternion,
    Bone,
    ModelState,
    Timestamp
)
from vmcp.protocol import (
    root_transform,
    bone_transform,
    state,
    time
)

server: OSC = None
sender: Sender = None

def start_server():
    global server, sender
    if server != None:
        return
    
    server = OSC(backend).open()
    sender = server.create_sender("0.0.0.0", 33779, "iris_fbt").open()

class SocketIOModule(IrisModule):
    def __init__(self, app: Flask, config_class=Config):
        app.before_request(start_server)
socket_io_module: SocketIOModule = None

def GetIrisModule(app, config_class=Config):
    global socket_io_module
    if socket_io_module is None:
        socket_io_module = SocketIOModule(app, config_class)
    return socket_io_module

bone_keys = {
    'head': Bone.HEAD,
    'chest': Bone.CHEST,
    'hip': Bone.HIPS,
    'left_shoulder': Bone.LEFT_UPPER_ARM,
    'right_shoulder': Bone.RIGHT_UPPER_ARM,
    'left_elbow': Bone.LEFT_LOWER_ARM,
    'right_elbow': Bone.RIGHT_LOWER_ARM,
    'left_wrist': Bone.LEFT_HAND,
    'right_wrist': Bone.RIGHT_HAND,
    'left_hip': Bone.LEFT_UPPER_LEG,
    'right_hip': Bone.RIGHT_UPPER_LEG,
    'left_knee': Bone.LEFT_LOWER_LEG,
    'right_knee': Bone.RIGHT_LOWER_LEG,
    'left_ankle': Bone.LEFT_FOOT,
    'right_ankle': Bone.RIGHT_FOOT,
}
def publisher(pose: dict[str, np.array]):
    if server and sender and server.is_open:
        data: list[Message] = []
        for ident, p in pose.items():
            if not ident in bone_keys:
                continue
            q = quaternion.from_rotation_matrix(p[:3, :3]).normalize()
            data.append(Message(*bone_transform(
                bone_keys[ident],
                CoordinateVector(p[0][3], p[1][3], p[2][3]),
                Quaternion(q.x, q.y, q.z, q.w)
            )))
        data.append(Message(*state(ModelState.LOADED)))
        data.append(Message(*time(Timestamp())))
        sender.send(data)
        server.run()
math_worker.publishers.append(publisher)

def on_close():
    if server and server.is_open:
        server.close()
atexit.register(on_close)