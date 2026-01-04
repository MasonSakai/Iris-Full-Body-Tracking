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
					curXmlParent = Scribe.loader.curXmlParent
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
								targetLoadIDList.append(childNode.text)
							Scribe.loader.crossRefs.loadIDs.RegisterLoadIDListReadFromXml(targetLoadIDList, "")
							return value
				
						case _:
							return value
				case LoadSaveMode.ResolvingCrossRefs:
					match lookMode:
						case LookMode.Reference:
							value = Scribe.loader.crossRefs.TakeResolvedRefList("")
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
	if keyLookMode != LookMode.Value:
		Log.Error(Log.LogLevel.Critical, f"Error in LookDict(): KeyLookMode only supports LookMode.Value at the moment.")
		keyLookMode = LookMode.Value
	if Scribe.EnterNode(label):
		try:
			match Scribe.mode:
				case LoadSaveMode.Saving:
					if value is None:
						Scribe.saver.WriteAttribute("IsNull", "True")
						return value

					for k, v in value.items():
						if Scribe.EnterNode("li"):
							try:
								k = Scribe_Values.Look(k, 'key', kType, forceSave=True)

								match valueLookMode:
									case LookMode.Value:
										v = Scribe_Values.Look(v, 'value', vType)
									case LookMode.Deep:
										v = Scribe_Deep.Look(v, 'value', vType)
									case LookMode.Reference:
										v = Scribe_References.Look(v, 'value', vType)
							finally:
								Scribe.ExitNode()
				case LoadSaveMode.LoadingVars:
					curXmlParent = Scribe.loader.curXmlParent
					attribNull = curXmlParent.get("IsNull")
					if attribNull is not None and attribNull.casefold() == 'true':
						return None
					parent = Scribe.loader.curParent
					result = {}
					try:
						children = list(curXmlParent)
						for index in range(len(children)):
							if Scribe.EnterNode(str(index)):
								try:
									key = Scribe_Values.Look(None, 'key', kType)
									if key is None: continue

									val = None
									match valueLookMode:
										case LookMode.Value:
											val = Scribe_Values.Look(val, 'value', vType)
										case LookMode.Deep:
											val = Scribe_Deep.Look(val, 'value', vType)
										case LookMode.Reference:
											node = children[index].find('value')
											Scribe.loader.crossRefs.loadIDs.RegisterLoadIDReadFromXml(node.text, vType, (label, key), parent)

									result[key] = val
								finally:
									Scribe.ExitNode()
					finally:
						return result
				case LoadSaveMode.ResolvingCrossRefs:
					if value and valueLookMode == LookMode.Reference:
						parent = Scribe.loader.curParent
						for key in value.keys():
							value[key] = Scribe.loader.crossRefs.TakeResolvedRef((label, key), parent)
				case _:
					pass
		finally:
			Scribe.ExitNode()
	else:
		if Scribe.mode != LoadSaveMode.LoadingVars:
			return value
		return None
	return value