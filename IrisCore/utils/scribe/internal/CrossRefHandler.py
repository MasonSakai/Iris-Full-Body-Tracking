from utils import Log
from utils.debug import DebugViewSettings
from utils.scribe import IExposable, ILoadReferenceable, LoadSaveMode, Scribe
from utils.scribe.internal.LoadIDsWantedBank import LoadIDsWantedBank


class CrossRefHandler:
	
	allObjectsByLoadID: dict[str, ILoadReferenceable]
	loadIDs: LoadIDsWantedBank
	crossReferencingExposables: list[IExposable]

	def __init__(self):
		self.allObjectsByLoadID = {}
		self.loadIDs = LoadIDsWantedBank()
		self.crossReferencingExposables = []

	def RegisterLoaded(self, reffable: ILoadReferenceable) -> None:
		if DebugViewSettings.logLoadLevel >= Log.LogLevel.Error:
			key = "[excepted]"
			try:
				key = reffable.GetUniqueLoadID()
			except:
				pass
			str1 = "[excepted]"
			try:
				str1 = str(reffable)
			except:
				pass
			loadReferenceable: ILoadReferenceable
			if loadReferenceable := self.allObjectsByLoadID.get(key):
				Log.Error(Log.LogLevel.Error, f"Cannot register {type(reffable)} {str1}, (id={key} in loaded object directory. Id already used by {type(loadReferenceable)} {Log.ToStringSafe(loadReferenceable, ILoadReferenceable)}.");
				return;
		try:
			self.allObjectsByLoadID[reffable.GetUniqueLoadID()] = reffable
		except Exception as ex:
			if DebugViewSettings.logLoadLevel >= Log.LogLevel.Error:
				key = "[excepted]"
				try:
					key = reffable.GetUniqueLoadID()
				except:
					pass
				str1 = "[excepted]";
				try:
					str1 = str(reffable)
				except:
					pass
				Log.Error(Log.LogLevel.Error, f"Exception registering {type(reffable)} {str1} in loaded object directory with unique load ID {key}: {str(ex)}")

	def ResolveAllCrossReferences(self) -> None:
		Scribe.mode = LoadSaveMode.ResolvingCrossRefs
		Log.Message(Log.LogLevel.Verbose, "==================Register the saveables all so we can find them later")
		for referencingExposable in self.crossReferencingExposables:
			if isinstance(referencingExposable, ILoadReferenceable):
				Log.Message(Log.LogLevel.Verbose, f"RegisterLoaded {type(referencingExposable)}")
				self.allObjectsByLoadID[referencingExposable.GetUniqueLoadID()] = referencingExposable
		Log.Message(Log.LogLevel.Verbose, "==================Fill all cross-references to the saveables")
		for referencingExposable in self.crossReferencingExposables:
			Log.Message(Log.LogLevel.Verbose, f"ResolvingCrossRefs ExposeData {referencingExposable}")
			try:
				Scribe.loader.curParent = referencingExposable
				Scribe.loader.curPathRelToParent = None
				referencingExposable.ExposeData()
			except Exception as ex:
				Log.Error(Log.LogLevel.Error, f"Could not resolve cross refs: {ex}")
		Scribe.loader.curParent = None
		Scribe.loader.curPathRelToParent = None
		Scribe.mode = LoadSaveMode.Inactive
		self.Clear(True)

	def Clear(self, errorIfNotEmpty: bool) -> None:
		if errorIfNotEmpty:
			self.loadIDs.ConfirmClear()
		else:
			self.loadIDs.Clear()
		self.crossReferencingExposables.clear()
		self.allObjectsByLoadID.clear()