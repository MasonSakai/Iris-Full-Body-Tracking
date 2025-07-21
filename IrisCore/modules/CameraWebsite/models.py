from app import db
from app.main.models import CVUndistortableCamera
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

class WebsiteCamera(CVUndistortableCamera):
	__tablename__ = "website_camera"
	id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey("cv_undistortable_camera.id"), primary_key=True)
	__mapper_args__ = {'polymorphic_identity': 'website_camera'}

	camera_id : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)
	autostart : sqlo.Mapped[bool] = sqlo.mapped_column(sqla.Boolean)
	confidence_threshold : sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float)

	#functions
	def __repr__(self):
		return '<Website Camera - {} "{}">'.format(self.id, self.display_name)

	def getConfig(self):
		data = super().getConfig()
		data.update({
			'camera_id': self.camera_id,
			'autostart': self.autostart,
			'confidence_threshold': self.confidence_threshold
		})
		return data
	
	def setConfig(self, config):
		super().setConfig(config)
		if 'camera_id' in config:
			self.camera_id = config['camera_id']
		if 'autostart' in config:
			self.autostart = config['autostart']
		if 'confidence_threshold' in config:
			self.confidence_threshold = config['confidence_threshold']
	