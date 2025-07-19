from app import db
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

class Camera(db.Model):
	__tablename__ = "camera"
	
	id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
	display_name : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)
	
	camera_type : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
	
	__mapper_args__ = {
		'polymorphic_identity': 'camera',
		'polymorphic_on': camera_type}

	
	#functions
	def __init__(self, config):
		self.setConfig(config)
		super().__init__()

	def __repr__(self):
		return '<Camera - {} "{}">'.format(self.id, self.display_name)

	def getImage(self):
		return None

	def correctForStage(self, stage, data):
		return None

	def ready(self):
		return False

	def camera_flags(self):
		return None

	def getTransform(self):
		return None

	def getConfig(self):
		return {
			'id': self.id,
			'name': self.display_name
		}
	
	def setConfig(self, config):
		if 'name' in config:
			self.display_name = config['name']