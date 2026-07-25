
from utils.modules.iris_modules import IrisModule

class LocalizationModule(IrisModule):

	def build_runtime(self):
		from app.localizationsolver.routes import bp_loc
		self.app.register_blueprint(bp_loc)

def create_module(app) -> IrisModule:
	return LocalizationModule(app)