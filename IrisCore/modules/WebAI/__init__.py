from flask import Blueprint
from app import Config

cam_web_blueprint = Blueprint('WebAI', __name__, static_folder='static', template_folder='templates', url_prefix='/webai')
cam_web_module = None

from WebAIModule import WebAIModule

def GetIrisModule(app, config_class=Config):
    global cam_web_module
    if cam_web_module is None:
        cam_web_module = WebAIModule(app, config_class)
    return cam_web_module