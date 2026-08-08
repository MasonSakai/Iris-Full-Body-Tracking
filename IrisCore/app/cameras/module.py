from __future__ import annotations
import os
from lxml import etree as ET

from flask import url_for
from app.cameras import calibration
from utils.modules.iris_modules import IrisModule
from utils.registry import CreateThingDatabase, ThingDatabase
from utils.scribe import Scribe, Scribe_Collections, Scribe_Deep

class CameraModule(IrisModule):

	def register_databases(self):
		CreateThingDatabase(Camera)
		CreateThingDatabase(CameraReference)

	def load(self):
		if Scribe.loader.LoadFile(os.path.join(self.app.config['APPDATA_PATH'], 'cameras.xml')):
			calibration.config = Scribe_Deep.Look(calibration.config, 'calibration', calibration.CalibrationConfig)
			if calibration.config == None: calibration.config = calibration.CalibrationConfig()

			cameras = Scribe_Collections.LookList(
				None,
				'cameras',
				Camera,
				Scribe_Collections.LookMode.Deep
			)
			ThingDatabase(Camera).Add(*cameras)
			Scribe.loader.CloseFile()

	def save(self):
		Scribe.saver.InitSaving('config')

		Scribe_Deep.Look(calibration.config, 'calibration', calibration.CalibrationConfig)

		db_cams = ThingDatabase(Camera)
		Scribe_Collections.LookList(
			db_cams.AllThingsListForReading(),
			'cameras',
			Camera,
			Scribe_Collections.LookMode.Deep
		)
		
		Scribe.saver.FinalizeSaving(os.path.join(self.app.config['APPDATA_PATH'], 'cameras.xml'))

	def build_runtime(self):
		from app.cameras.routes import bp_cam
		self.app.register_blueprint(bp_cam)

	def start_runtime(self):
		for cam in ThingDatabase(Camera).AllThings():
			for ref in cam.references:
				if ref.autostart and ref.RequestAutoStart():
					break

	def get_index_content(self):
		return f'<a href="{url_for('cameras.index')}">Cameras</a>'


def create_module(app) -> IrisModule:
	return CameraModule(app)

from app.cameras.models import Camera, CameraReference