from typing import Type
import lxml.etree as ET

from utils import Log
from utils.scribe import LoadSaveMode, Scribe
from utils.scribe.internal import ParseHelper


def ValueFromNode[T](subNode: ET.ElementBase, vType: Type[T], defaultValue: T) -> T:
	if subNode is None:
		return defaultValue
	attribNull = subNode.get("IsNull")
	if attribNull is not None and attribNull.casefold() == 'true':
		return None
	try:
		try:
			return ParseHelper.FromString(subNode.text, subNode.attrib, vType)
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"Exception parsing node {ET.tostring(subNode)} into a {vType}:\n{ex}")
		return defaultValue
	except Exception as ex:
		Log.Error(Log.LogLevel.Critical, f"Exception loading XML: {ex}")
		return defaultValue


def SaveableFromNode[T](subNode: ET.ElementBase, vType: Type[T], *args, **kwargs) -> T:
	if Scribe.mode != LoadSaveMode.LoadingVars:
		Log.Error(Log.LogLevel.Critical, f"Called SaveableFromNode(), but mode is {Scribe.mode.name}");
		return None
	if subNode is None:
		return None
	attribNull = subNode.get("IsNull")
	if attribNull is not None and attribNull.casefold() == 'true':
		return None
	else:
		try:
			attribName = subNode.get("class")
			providedType = vType if attribName is None else ParseHelper.GetTypeFromName(attribName)
			obj = providedType(*args, **kwargs)
			Scribe.loader.crossRefs.RegisterForCrossRefResolve(obj)
			curXmlParent = Scribe.loader.curXmlParent
			curParent = Scribe.loader.curParent
			curPathRelToParent = Scribe.loader.curPathRelToParent
			Scribe.loader.curXmlParent = subNode
			Scribe.loader.curParent = obj
			Scribe.loader.curPathRelToParent = None
			try:
				obj.ExposeData()
			finally:
				Scribe.loader.curXmlParent = curXmlParent
				Scribe.loader.curParent = curParent
				Scribe.loader.curPathRelToParent = curPathRelToParent
			Scribe.loader.initer.RegisterForPostLoadInit(obj)
			return obj
		except Exception as ex:
			Log.Error(Log.LogLevel.Critical, f"SaveableFromNode exception: {ex}\nSubnode:\n{ET.tostring(subNode)}")
			return None