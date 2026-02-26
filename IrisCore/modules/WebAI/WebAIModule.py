from utils.modulemanager.IrisModules import IrisModule
from app import Config

from WebAI import cam_web_blueprint as bp_cam

class WebAIModule(IrisModule):
    
    def __init__(self, app, config_class=Config):
        from WebAI import models, routes
        import WebAISocket

        app.register_blueprint(bp_cam)