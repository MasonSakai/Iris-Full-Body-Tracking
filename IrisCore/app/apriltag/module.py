from __future__ import annotations
import os
from utils.modules.iris_modules import IrisModule
from utils.registry import ThingDatabase
from utils.scribe import Scribe_Collections
from utils.scribe import Scribe, Scribe_Collections

class AprilTagModule(IrisModule):

	def load(self):
		if Scribe.loader.LoadFile(os.path.join(self.app.config['APPDATA_PATH'], 'apriltags.xml')):
			tags = Scribe_Collections.LookList(None, 'tags', AprilTag, Scribe_Collections.LookMode.Deep)
			ThingDatabase(AprilTag).Add(*tags)
			detectors = Scribe_Collections.LookList(None, 'detectors', AprilTagDetector, Scribe_Collections.LookMode.Deep)
			ThingDatabase(AprilTagDetector).Add(*detectors)
			Scribe.loader.CloseFile()
			
	def save(self):
		db_tags = ThingDatabase(AprilTag)
		db_detectors = ThingDatabase(AprilTagDetector)

		if db_tags.ThingCount() > 0 or db_detectors.ThingCount() > 0:
			Scribe.saver.InitSaving('config')
			if db_tags.ThingCount() > 0: Scribe_Collections.LookList(db_tags.AllThingsListForReading(), 'tags', AprilTag, Scribe_Collections.LookMode.Deep)
			if db_detectors.ThingCount() > 0: Scribe_Collections.LookList(db_detectors.AllThingsListForReading(), 'detectors', AprilTagDetector, Scribe_Collections.LookMode.Deep)
			Scribe.saver.FinalizeSaving(os.path.join(self.app.config['APPDATA_PATH'], 'apriltags.xml'))

	def build_runtime(self):
		from app.apriltag import routes, AprilTag3DSocket
		self.app.register_blueprint(routes.bp_aptg)

def create_module(app) -> IrisModule:
	return AprilTagModule(app)

from app.apriltag.models import AprilTag, AprilTagDetector