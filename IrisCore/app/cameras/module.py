from __future__ import annotations
import os
from utils.modules.iris_modules import IrisModule
from utils.registry import CreateThingDatabase, ThingDatabase
from utils.scribe import Scribe, Scribe_Collections

class CameraModule(IrisModule):

	def register_databases(self):
		CreateThingDatabase(Camera)
		CreateThingDatabase(CameraReference)

	def load(self):
		if Scribe.loader.LoadFile(os.path.join(self.app.config['APPDATA_PATH'], 'cameras.xml')):
			cameras = Scribe_Collections.LookList(
				None,
				'cameras',
				Camera,
				Scribe_Collections.LookMode.Deep
			)
			ThingDatabase(Camera).Add(*cameras)
			Scribe.loader.CloseFile()

	def save(self):
		db_cams = ThingDatabase(Camera)

		if db_cams.ThingCount() > 0:
			Scribe.saver.InitSaving('config')
			Scribe_Collections.LookList(
				db_cams.AllThingsListForReading(),
				'cameras',
				Camera,
				Scribe_Collections.LookMode.Deep
			)
			Scribe.saver.FinalizeSaving(os.path.join(self.app.config['APPDATA_PATH'], 'cameras.xml'))

	def build_runtime(self):
		from app.cameras import routes
		self.app.register_blueprint(routes.bp_cam)


	def start_runtime(self):
		for cam in ThingDatabase(Camera).AllThings():
			for ref in cam.references:
				if ref.autostart:
					ref.RequestStart()

def create_module(app) -> IrisModule:
	return CameraModule(app)

from app.cameras.models import Camera, CameraReference