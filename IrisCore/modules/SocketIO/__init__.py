from flask import request
from app import Config, socketio
from app.IrisModules import IrisModule
from app.main.math_worker import math_worker
import numpy as np


class SocketIOModule(IrisModule):
    def __init__(self, app, config_class=Config):
        pass
socket_io_module: SocketIOModule = None

def GetIrisModule(app, config_class=Config):
    global socket_io_module
    if socket_io_module is None:
        socket_io_module = SocketIOModule(app, config_class)
    return socket_io_module

def publisher(pose: dict[str, np.array]):
    data = {}
    for ident, p in pose.items():
        data[ident] = p.tolist()
    socketio.emit('pose', data, namespace='/sioModule')
math_worker.publishers.append(publisher)


@socketio.on('connect', namespace='/sioModule')
def on_connect():
    pass