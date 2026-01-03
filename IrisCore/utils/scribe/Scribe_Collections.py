from enum import Enum, auto
from typing import Type
from utils import Log
from utils.scribe import IExposable, ILoadReferenceable, Scribe, LoadSaveMode, Scribe_Deep, Scribe_Values, Scribe_References
from utils.scribe.internal import ScribeExtractor


class LookMode(Enum):
	Value = auto()
	Deep = auto()
	Reference = auto()

def LookList[T](value: list[T], label: str, vType: Type[T], lookMode: LookMode, *args, **kwargs) -> list[T]:
	if Scribe.EnterNode(label):
		try:
			match Scribe.mode:
				case LoadSaveMode.Saving:
					if value is None:
						Scribe.saver.WriteAttribute("IsNull", "True")
						return value
					for current in value:
						match lookMode:
							case LookMode.Value:
								Scribe_Values.Look(current, "li", vType, forceSave = True)
							case LookMode.Deep:
								Scribe_Deep.Look(current, "li", vType, *args, **kwargs)
							case LookMode.Reference:
								if current is None or isinstance(current, ILoadReferenceable):
									Scribe_References.Look(current, "li", vType)
								else:
									s: str = None
									if current is not None:
										s = Log.ToStringSafe(type(current), Type) if type(current) is not None else None
									raise Exception(f"Cannot save reference to {s} item if it is not ILoadReferenceable")
							case _:
								pass
				case LoadSaveMode.LoadingVars:
					curXmlParent = Scribe.loader.curXmlParent;
					attribNull = curXmlParent.get("IsNull")
					if attribNull is not None and attribNull.casefold() == 'true':
						if lookMode == LookMode.Reference:
							Scribe.loader.crossRefs.loadIDs.RegisterLoadIDListReadFromXml(None, None)
						return None
					match lookMode:
						case LookMode.Value:
							value = []
							try:
								for child in curXmlParent:
									obj = ScribeExtractor.ValueFromNode(child, vType, vType())
									value.append(obj)
								return value
							finally:
								pass
						case LookMode.Deep:
							value = []
							try:
								for child in curXmlParent:
									obj = ScribeExtractor.SaveableFromNode(child, vType, *args, **kwargs)
									value.append(obj)
								return value
							finally:
								pass
						case LookMode.Reference:
							targetLoadIDList = []
							for childNode in curXmlParent:
								targetLoadIDList.append(childNode.InnerText)
							Scribe.loader.crossRefs.loadIDs.RegisterLoadIDListReadFromXml(targetLoadIDList, "")
							return value
				
						case _:
							return value
				case LoadSaveMode.ResolvingCrossRefs:
					match lookMode:
						case LookMode.Reference:
							value = Scribe.loader.crossRefs.TakeResolvedRefList("", vType)
							return value
						case _:
							return value
		finally:
			Scribe.ExitNode()
	else:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			return value
		if lookMode == LookMode.Reference:
			Scribe.loader.crossRefs.loadIDs.RegisterLoadIDListReadFromXml(None, label)
		value = None
	return value

def LookDict[K, V](value: dict[K, V], label: str, kType: Type[K], vType: Type[V], keyLookMode: LookMode, valueLookMode: LookMode) -> dict[K, V]:
	pass