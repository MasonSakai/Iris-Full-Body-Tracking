from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type

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
					value = self.idsListsRead[key]
					stringBuilder += f"  List with {len(value.targetLoadIDs) if value.targetLoadIDs else 0} elements. pathRelToParent={value.pathRelToParent}, parent={Log.ToStringSafe(value.parent, IExposable)}\n"
			Log.Warning(Log.LogLevel.Warning, stringBuilder.rstrip());
		self.Clear();

	def Clear(self) -> None:
		self.idsRead.clear()
		self.idListsRead.clear()


	def RegisterLoadIDReadFromXml(self, targetLoadID: str, targetType: Type, pathRelToParent: str, parent: IExposable) -> None:
		if (parent, pathRelToParent) in self.idsRead:
			Log.Error(Log.LogLevel.Error, f"Tried to register the same load ID twice: {targetLoadID}, pathRelToParent={pathRelToParent}, parent={Log.ToStringSafe(parent, IExposable)}")
		else:
			idRecord = LoadIDsWantedBank.IdRecord(targetLoadID, targetType, pathRelToParent, parent)
			self.idsRead[(parent, pathRelToParent)] = idRecord

	def RegisterLoadIDReadFromXmlCurrent(self, targetLoadID: str, targetType: Type, toAppendToPathRelToParent: str) -> None:
		pathRelToParent = Scribe.loader.curPathRelToParent
		if pathRelToParent is None:
			pathRelToParent = ''
		if toAppendToPathRelToParent:
			pathRelToParent += f"/{toAppendToPathRelToParent}"
		self.RegisterLoadIDReadFromXml(targetLoadID, targetType, pathRelToParent, Scribe.loader.curParent)

	def RegisterLoadIDListReadFromXmlList(self, targetLoadIDList: list[str], pathRelToParent: str, parent: IExposable) -> None:
		if (parent, pathRelToParent) in self.idListsRead:
			Log.Error(Log.LogLevel.Error, f"Tried to register the same list of load IDs twice. pathRelToParent={pathRelToParent}, parent={Log.ToStringSafe(parent, IExposable)}")
		else:
			idListRecord = LoadIDsWantedBank.IdListRecord(targetLoadIDList, pathRelToParent, parent);
			self.idListsRead[(parent, pathRelToParent)] = idListRecord

	def RegisterLoadIDListReadFromXmlListCurrent(self, targetLoadIDList: list[str], toAppendToPathRelToParent: str) -> None:
		pathRelToParent = Scribe.loader.curPathRelToParent
		if toAppendToPathRelToParent:
			pathRelToParent += f"/{toAppendToPathRelToParent}"
		self.RegisterLoadIDListReadFromXmlList(targetLoadIDList, pathRelToParent, Scribe.loader.curParent);

	def Take(self, pathRelToParent: str, parent: IExposable) -> str:
		if idRecord := self.idsRead.get((parent, pathRelToParent)):
			targetLoadId = idRecord.targetLoadID;
			if type(parent) != idRecord.targetType:
				Log.Error(Log.LogLevel.Error, f"Trying to get load ID of object of type {type(parent)}, but it was registered as {idRecord.targetType}. pathRelToParent={pathRelToParent}, parent={Log.ToStringSafe(parent, IExposable)}")
			del self.idsRead[(parent, pathRelToParent)]
			return targetLoadId
		Log.Error(Log.LogLevel.Error, "Could not get load ID. We're asking for something which was never added during LoadingVars. pathRelToParent=" + pathRelToParent + ", parent=" + parent.ToStringSafe<IExposable>());
		return None

	def TakeList(self, pathRelToParent: str, parent: IExposable) -> list[str]:
		if idListRecord := self.idListsRead.get((parent, pathRelToParent)):
			targetLoadIds = idListRecord.targetLoadIDs
			del self.idListsRead[(parent, pathRelToParent)]
			return targetLoadIds
		Log.Error(Log.LogLevel.Error, f"Could not get load IDs list. We're asking for something which was never added during LoadingVars. pathRelToParent={pathRelToParent}, parent={Log.ToStringSafe(parent, IExposable)}")
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