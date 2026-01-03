

from utils import Log
from utils.scribe import Scribe, IExposable, LoadSaveMode


class PostLoadIniter:
	saveablesToPostLoad: set[IExposable] = set()

	def RegisterForPostLoadInit(self, s: IExposable) -> None:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			Log.Error(Log.LogLevel.Error, f"Registered {s} for post load init, but current mode is {Scribe.mode.name}")
		elif s is None:
			Log.Warning("Trying to register null in RegisterforPostLoadInit.")
		else:
			try:
				if s not in self.saveablesToPostLoad:
					self.saveablesToPostLoad.add(s)
					return
				Log.Warning(Log.LogLevel.Warning, f"Tried to register in RegisterforPostLoadInit when already registered: {s}")
			except Exception as ex:
				Log.Error(Log.LogLevel.Error, f"Could not register an object for post load init: {ex}")
				
	def DoAllPostLoadInits(self) -> None:
		Scribe.mode = LoadSaveMode.PostLoadInit
		for exposable in self.saveablesToPostLoad:
			try:
				Scribe.loader.curParent = exposable
				Scribe.loader.curPathRelToParent = None
				exposable.ExposeData()
			except Exception as ex:
				Log.Error(Log.LogLevel.Error, f"Could not do PostLoadInit on {Log.ToStringSafe(exposable, IExposable)}: {ex}")
		self.Clear()
		Scribe.loader.curParent = None
		Scribe.loader.curPathRelToParent = None
		Scribe.mode = LoadSaveMode.Inactive

	def Clear(self) -> None:
	   self.saveablesToPostLoad.Clear()