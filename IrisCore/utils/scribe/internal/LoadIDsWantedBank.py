from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, overload

from utils import Log
from utils.scribe import IExposable, Scribe

@dataclass
class LoadIDsWantedBank:
	
	idsRead: dict[tuple[IExposable, str], LoadIDsWantedBank.IdRecord] = field(init=False, default_factory=dict)
	idListsRead: dict[tuple[IExposable, str], LoadIDsWantedBank.IdListRecord] = field(init=False, default_factory=dict)


	def ConfirmClear(self) -> None:
		if len(self.idsRead) > 0 or len(self.idListsRead) > 0:
			stringBuilder = "Not all loadIDs which were read were consumed.\n"
			if len(self.idsRead) > 0:
				stringBuilder += "Singles:\n"
				for key in self.idsRead:
					value = self.idsRead[key]
					stringBuilder += f"  {Log.ToStringSafe(value.targetLoadID, str)} of type {value.targetType}. pathRelToParent={value.pathRelToParent}, parent={Log.ToStringSafe(value.parent, IExposable)}\n"
			if len(self.idListsRead) > 0:
				stringBuilder += "Lists:\n"
				for key in self.idListsRead:
					value = self.idListsRead[key]
					stringBuilder += f"  List with {len(value.targetLoadIDs) if value.targetLoadIDs else 0} elements. pathRelToParent={value.pathRelToParent}, parent={Log.ToStringSafe(value.parent, IExposable)}\n"
			Log.Warning(Log.LogLevel.Warning, stringBuilder.rstrip());
		self.Clear();

	def Clear(self) -> None:
		self.idsRead.clear()
		self.idListsRead.clear()

	@overload
	def RegisterLoadIDReadFromXml(self, targetLoadID: str, targetType: Type, pathRelToParent: str, parent: IExposable) -> None: ...
	@overload
	def RegisterLoadIDReadFromXml(self, targetLoadID: str, targetType: Type, toAppendToPathRelToParent: str) -> None: ...
	def RegisterLoadIDReadFromXml(self, targetLoadID: str, targetType: Type, path: str, parent: IExposable = None) -> None:
		if parent is None:
			pathRelToParent = Scribe.loader.curPathRelToParent or ''
			if path:
				pathRelToParent += f"/{path}"
			path = pathRelToParent
			parent = Scribe.loader.curParent

		if (parent, path) in self.idsRead:
			Log.Error(Log.LogLevel.Error, f"Tried to register the same load ID twice: {targetLoadID}, pathRelToParent={path}, parent={Log.ToStringSafe(parent, IExposable)}")
		else:
			idRecord = LoadIDsWantedBank.IdRecord(targetLoadID, targetType, path, parent)
			self.idsRead[(parent, path)] = idRecord

	@overload
	def RegisterLoadIDListReadFromXml(self, targetLoadIDList: list[str], pathRelToParent: str, parent: IExposable) -> None: ...
	@overload
	def RegisterLoadIDListReadFromXml(self, targetLoadIDList: list[str], toAppendToPathRelToParent: str) -> None: ...
	def RegisterLoadIDListReadFromXml(self, targetLoadIDList: list[str], path: str, parent: IExposable = None) -> None:
		if parent is None:
			pathRelToParent = Scribe.loader.curPathRelToParent or ''
			if path:
				pathRelToParent += f"/{path}"
			path = pathRelToParent
			parent = Scribe.loader.curParent

		if (parent, path) in self.idListsRead:
			Log.Error(Log.LogLevel.Error, f"Tried to register the same list of load IDs twice. pathRelToParent={path}, parent={Log.ToStringSafe(parent, IExposable)}")
		else:
			idListRecord = LoadIDsWantedBank.IdListRecord(targetLoadIDList, path, parent);
			self.idListsRead[(parent, path)] = idListRecord

	def Take(self, pathRelToParent: str, parent: IExposable) -> str:
		if idRecord := self.idsRead.get((parent, pathRelToParent)):
			targetLoadId = idRecord.targetLoadID;
			#if type(parent) != idRecord.targetType:
			#	Log.Error(Log.LogLevel.Error, f"Trying to get load ID of object of type {type(parent)}, but it was registered as {idRecord.targetType}. pathRelToParent={pathRelToParent}, parent={Log.ToStringSafe(parent, IExposable)}")
			del self.idsRead[(parent, pathRelToParent)]
			return targetLoadId
		Log.Error(Log.LogLevel.Error, "Could not get load ID. We're asking for something which was never added during LoadingVars. pathRelToParent=" + pathRelToParent + ", parent=" + parent.ToStringSafe<IExposable>());
		return None

	def TakeList(self, pathRelToParent: str, parent: IExposable) -> list[str]:
		if idListRecord := self.idListsRead.get((parent, pathRelToParent)):
			targetLoadIds = idListRecord.targetLoadIDs
			del self.idListsRead[(parent, pathRelToParent)]
			return targetLoadIds
		Log.Error(Log.LogLevel.Critical, f"Could not get load IDs list. We're asking for something which was never added during LoadingVars. pathRelToParent={pathRelToParent}, parent={Log.ToStringSafe(parent, IExposable)}")
		return []
	
	@dataclass
	class IdRecord:
		targetLoadID: str
		targetType: Type
		pathRelToParent: str
		parent: IExposable
	
	@dataclass
	class IdListRecord:
		targetLoadIDs: list[str]
		pathRelToParent: str
		parent: IExposable