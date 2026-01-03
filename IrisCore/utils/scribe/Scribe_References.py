
from lxml import etree as ET
from typing import Type, TypeVar

from utils import Log
from utils.scribe import IExposable, ILoadReferenceable, LoadSaveMode, Scribe

T = TypeVar('T_Refee', bound=ILoadReferenceable)

def Look(refee: T, label: str, vType: Type[T]) -> T:
	match Scribe.mode:
		case LoadSaveMode.Saving:
			if refee is None:
				Scribe.saver.WriteElement(label, "null")
				return refee
			uniqueLoadId = refee.GetUniqueLoadID()
			Scribe.saver.WriteElement(label, uniqueLoadId, str);
			Scribe.saver.loadIDsErrorsChecker.RegisterReferenced(refee, label)
		case LoadSaveMode.LoadingVars:
			if Scribe.loader.curParent is not None and not isinstance(Scribe.loader.curParent, IExposable):
				Log.Warning(f"Trying to load reference of an object of type {vType} with label {label}, but our current node is a value type. The reference won't be loaded properly. curParent={Scribe.loader.curParent}")
			xmlNode: ET.ElementBase = Scribe.loader.curXmlParent.find(label)
			innerText = None if xmlNode is None else "".join(xmlNode.itertext())
			Scribe.loader.crossRefs.loadIDs.RegisterLoadIDReadFromXmlCurrent(innerText, vType, label)
		case LoadSaveMode.ResolvingCrossRefs:
			refee = Scribe.loader.crossRefs.TakeResolvedRef(label)
	return refee