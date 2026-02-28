from __future__ import annotations
from utils.modules.iris_modules import IrisModule
from utils.registry import CreateThingDatabase

class WebAIModule(IrisModule):
    
    def register_databases(self):
        CreateThingDatabase(WebAICameraReference)

    def build_runtime(self):
        from modules.WebAI import routes, WebAISocket
        self.app.register_blueprint(routes.bp_webai)

def create_module(app) -> IrisModule:
    return WebAIModule(app)

from modules.WebAI.models import WebAICameraReference