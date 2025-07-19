from app.IrisModules import IrisModule
from app import Config

from CameraWebsite import cam_web_blueprint as bp_cam

class CamWebModule(IrisModule):
    
    def __init__(self, app, config_class=Config):
        app.register_blueprint(bp_cam)