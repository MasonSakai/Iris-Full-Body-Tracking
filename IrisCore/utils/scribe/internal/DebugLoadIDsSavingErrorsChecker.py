


from dataclasses import dataclass
from utils import Log
from utils.debug import DebugViewSettings
from utils.scribe import ILoadReferenceable, LoadSaveMode, Scribe


class DebugLoadIDsSavingErrorsChecker:
	deepSaved: set[str]
	deepSavedInfo: dict[str, str]
	referenced: set['DebugLoadIDsSavingErrorsChecker.ReferencedObject']

	def __init__(self):
		self.deepSaved = set()
		self.deepSavedInfo = {}
		self.referenced = set()

	def Clear(self):
		if not DebugViewSettings.ScribeDebugLoadIDs:
			return
		self.deepSaved.clear()
		self.deepSavedInfo.clear()
		self.referenced.clear()

	def CheckForErrorsAndClear(self):
		if not DebugViewSettings.ScribeDebugLoadIDs:
			return
		if not Scribe.saver.savingForDebug:
			for referencedObject in self.referenced:
				if referencedObject.loadID not in self.deepSaved:
					Log.Warning(Log.LogLevel.Critical, f"Object with load ID {referencedObject.loadID} is referenced (xml node name: {referencedObject.label}) but is not deep-saved. This will cause errors during loading.")
		self.Clear()

	def RegisterDeepSaved(self, obj: ILoadReferenceable, label: str):
		if not DebugViewSettings.ScribeDebugLoadIDs:
			return
		if Scribe.mode != LoadSaveMode.Saving:
			Log.Error(Log.LogLevel.Error, f"Registered {obj}, but current mode is {Scribe.mode.name}")
		else:
			if obj is None:
				return
			if not isinstance(obj, ILoadReferenceable):
				return
			try:
				uniqueLoadId = obj.GetUniqueLoadID();
				if uniqueLoadId in self.deepSaved:
					Log.Warning(Log.LogLevel.Critical, f"DebugLoadIDsSavingErrorsChecker error: tried to register deep-saved object with loadID {uniqueLoadId}, but it's already here. label={label} (not cleared after the previous save? different objects have the same load ID? the same object is deep-saved twice?)")
					if uniqueLoadId not in self.deepSavedInfo:
						return
					Log.Warning(Log.LogLevel.Critical, f"{type(obj)} was already deepsaved at {self.deepSavedInfo[uniqueLoadId]}.")
				else:
					self.deepSaved.add(uniqueLoadId)
					self.deepSavedInfo[uniqueLoadId] = Scribe.saver.CurPath
			except Exception as ex:
				Log.Error(Log.LogLevel.Critical, f"Error in GetUniqueLoadID(): {ex}")

	def RegisterReferenced(self, obj: ILoadReferenceable, label: str):
		if not DebugViewSettings.ScribeDebugLoadIDs:
			return
		if Scribe.mode != LoadSaveMode.Saving:
			Log.Error(Log.LogLevel.Error, f"Registered {obj}, but current mode is {Scribe.mode.name}")
		else:
			if obj is None:
				return
			try:
				self.referenced.add(DebugLoadIDsSavingErrorsChecker.ReferencedObject(obj.GetUniqueLoadID(), label))
			except Exception as ex:
				Log.Error(Log.LogLevel.Critical, f"Error in GetUniqueLoadID(): {ex}")


	@dataclass(frozen=True)
	class ReferencedObject:
		loadID: str
		label: str