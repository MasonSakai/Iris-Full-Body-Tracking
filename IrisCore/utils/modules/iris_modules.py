from flask import Flask
from abc import ABC, abstractmethod


class IrisModule(ABC):

	def __init__(self, app: Flask):
		self.app = app

	module_id: str

	# ---------- Persistence ----------

	def register_databases(self) -> None:
		"""
		Create required ThingDatabases.
		Called before load.
		"""
		pass

	def load(self) -> None:
		"""
		Load persistent state from files into ThingDatabases.
		Called inside Scribe session.
		"""
		pass

	def save(self) -> None:
		"""
		Save persistent state from ThingDatabases.
		"""
		pass

	# ---------- Runtime ----------

	def build_runtime(self) -> None:
		"""
		Create runtime objects (threads, workers, pipelines).
		"""
		pass

	def start_runtime(self) -> None:
		"""
		Start runtime systems.
		"""
		pass

	def shutdown_runtime(self) -> None:
		"""
		Gracefully stop runtime systems.
		"""
		pass