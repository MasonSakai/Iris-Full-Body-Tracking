
from utils.modules.iris_modules import IrisModule

class MainModule(IrisModule):

	def build_runtime(self):
		from app.main import main_blueprint as bp_main
		self.app.register_blueprint(bp_main)

def create_module(app) -> IrisModule:
	return MainModule(app)