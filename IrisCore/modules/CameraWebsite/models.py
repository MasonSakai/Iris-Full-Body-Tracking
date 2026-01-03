from typing import Any
from app.cameras.models import CameraReference
from utils.scribe import Scribe_Values

class WebsiteCameraReference(CameraReference):

	camera_id : str
	confidence_threshold : float

	def ExposeData(self):
		super().ExposeData()
		self.confidence_threshold = Scribe_Values.Look(self.confidence_threshold, 'ConfidenceThreshold', int)

	def getConfig(self) -> dict[str, Any]:
		data = self.parent.getConfig()
		data.update({
			'index': self.index,
			'camera_id': self.camera_id,
			'autostart': self.autostart,
			'confidence_threshold': self.confidence_threshold
		})
		return data
	
	def setConfig(self, config):
		self.parent.setConfig(config)
		if 'camera_id' in config:
			self.camera_id = config['camera_id']
		if 'autostart' in config:
			self.autostart = config['autostart']
		if 'confidence_threshold' in config:
			self.confidence_threshold = config['confidence_threshold']