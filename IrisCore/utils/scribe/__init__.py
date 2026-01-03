"""
A Rimworld-based xml loading system
"""

from __future__ import annotations
from asyncio import Lock
from enum import Enum
from abc import ABC, abstractmethod

class LoadSaveMode(Enum):
	"""
	Enum for the current state of the Scribe
	"""
	Inactive = 0
	Saving = 1
	LoadingVars = 2
	ResolvingCrossRefs = 3
	PostLoadInit = 4

class IExposable:
	"""
	Interface for Scribe_Deep
	Use scribes to save and load persistent data
	"""
	def ExposeData(self):
		"""
		Used by Scribe_Deep
		Use scribes to save and load persistent data
		general format for scribe use is:
		self.param = Scribe_XXX.Look(self.param, 'param', paramType)
		"""

class ILoadReferenceable(ABC):
	"""
	Interface for Scribe_Reference
	"""
	@abstractmethod
	def GetUniqueLoadID(self) -> str:
		"""
		A unique (and persistent) id for loading persistent references
		Is not used until after LoadSaveMode.LoadingVars
		"""

class Scribe:

	scribeLock = Lock()
	
	mode = LoadSaveMode.Inactive
	loader: ScribeLoader
	saver: ScribeSaver

	@staticmethod
	def ForceStop():
		Scribe.mode = LoadSaveMode.Inactive
		Scribe.loader.ForceStop()
		Scribe.saver.ForceStop()


	@staticmethod
	def EnterNode(nodeName: str) -> bool:
		match Scribe.mode:
			case LoadSaveMode.Inactive:
				return False
			case LoadSaveMode.Saving:
				return Scribe.saver.EnterNode(nodeName)
			case LoadSaveMode.LoadingVars | LoadSaveMode.ResolvingCrossRefs | LoadSaveMode.PostLoadInit:
				return Scribe.loader.EnterNode(nodeName)
			case _:
			  return True


	@staticmethod
	def ExitNode():
		match Scribe.mode:
			case LoadSaveMode.Saving:
				Scribe.saver.ExitNode()
			case LoadSaveMode.LoadingVars | LoadSaveMode.ResolvingCrossRefs | LoadSaveMode.PostLoadInit:
				Scribe.loader.ExitNode()
			case _:
				pass


from utils.scribe.internal.ScribeLoader import ScribeLoader
from utils.scribe.internal.ScribeSaver import ScribeSaver

Scribe.loader = ScribeLoader()
Scribe.saver = ScribeSaver()