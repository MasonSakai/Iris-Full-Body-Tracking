from __future__ import annotations

from flask import url_for
from utils.modules.iris_modules import IrisModule
from utils.registry import CreateThingDatabase

class WebAIModule(IrisModule):
	
	def register_databases(self):
		CreateThingDatabase(WebAICameraReference)

	def build_runtime(self):
		from modules.WebAI import routes, WebAISocket
		self.app.register_blueprint(routes.bp_webai)

	def get_index_content(self):
		return f'<a href="{url_for('WebAI.index')}">WebAI</a>'

def create_module(app) -> IrisModule:
	return WebAIModule(app)

from modules.WebAI.models import WebAICameraReference