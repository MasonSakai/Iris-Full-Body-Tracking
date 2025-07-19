from config import Config
from app import db

import os
import sys
import importlib


class IrisModule:
	pass

imported_modules : dict[str, IrisModule] = {}


def getSubModules(app, config_class=Config):

	if config_class.MODULE_PATH not in sys.path:
		sys.path.insert(0, config_class.MODULE_PATH)

	for item in os.listdir(config_class.MODULE_PATH):
		# Construct the full path to the item
		full_path = os.path.join(config_class.MODULE_PATH, item)

		if os.path.isdir(full_path) and "__init__.py" in os.listdir(full_path):
			subpackage_name = item
			try:
				if full_path not in sys.path:
					sys.path.insert(0, full_path)
				subpackage = importlib.import_module(subpackage_name)
				imported_modules[subpackage_name] = subpackage.GetIrisModule(app, config_class)
				print(f"Imported subpackage: {subpackage_name}")
			except ImportError as e:
				print(f"Could not import subpackage {subpackage_name}: {e}")

def startSubModules():
	print("Starting modules")

def stopSubModules():
	print("Stopping modules")