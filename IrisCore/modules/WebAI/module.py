from utils.modules.iris_modules import IrisModule

class WebAIModule(IrisModule):
    
    def build_runtime(self):
        from modules.WebAI import routes, WebAISocket
        self.app.register_blueprint(routes.bp_webai)

def create_module(app) -> IrisModule:
    return WebAIModule(app)

from modules.WebAI import models