from flask import Blueprint
from app import Config

cam_web_blueprint = Blueprint('CameraWebsite', __name__, static_folder='static', template_folder='templates', url_prefix='/camsite')
cam_web_module = None

from CamWebModule import CamWebModule

def GetIrisModule(app, config_class=Config):
    global cam_web_module
    if cam_web_module is None:
        cam_web_module = CamWebModule(app, config_class)
    return cam_web_module