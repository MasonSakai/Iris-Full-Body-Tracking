from app import Config, socketio
from app.IrisModules import IrisModule
from app.main.math_worker import math_worker


class SocketIOModule(IrisModule):
    def __init__(self, app, config_class=Config):
        pass
socket_io_module: SocketIOModule = None

def GetIrisModule(app, config_class=Config):
    global socket_io_module
    if socket_io_module is None:
        socket_io_module = SocketIOModule(app, config_class)
    return socket_io_module

def publisher(pose):
    socketio.emit('pose', pose, namespace='/sioModule')
math_worker.publishers.append(publisher)