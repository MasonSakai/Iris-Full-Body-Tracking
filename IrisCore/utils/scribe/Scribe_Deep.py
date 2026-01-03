from lxml import etree as ET
from typing import Type, TypeVar
from utils import Log
from utils.scribe import IExposable, LoadSaveMode, Scribe
from utils.scribe.internal import ParseHelper, ScribeExtractor

T = TypeVar('T_Expo', bound=IExposable)

def Look(target: T, label: str, vType: Type[T], *args, **kwargs) -> T:
	match Scribe.mode:
		case LoadSaveMode.Saving:
			if not isinstance(target, IExposable):
				Log.Error(f"Cannot use LookDeep to save non-IExposable non-null {label} of type {vType}")
				return target
			if target is None:
				if Scribe.EnterNode(label):
					try:
						Scribe.saver.WriteAttribute("IsNull", "True")
					finally:
						Scribe.ExitNode()
			elif Scribe.EnterNode(label):
				try:
					if type(target) != vType:
						Scribe.saver.WriteAttribute("Class", ParseHelper.GetQualifiedName(target));
					target.ExposeData()
				except Exception as ex:
					Log.Error(f"Exception while saving {Log.ToStringSafe(target, IExposable)}: {ex}");
				finally:
					Scribe.ExitNode()
			Scribe.saver.loadIDsErrorsChecker.RegisterDeepSaved(target, label)
		case LoadSaveMode.LoadingVars:
			try:
				#if isinstance(target, IDisposable):
				#	target.Dispose()
				target = ScribeExtractor.SaveableFromNode(Scribe.loader.curXmlParent[label], vType, *args, **kwargs)
			except Exception as ex:
				Log.Error(f"Exception while loading {Log.ToStringSafe(Scribe.loader.curXmlParent[label], ET.ElementBase)}: {ex}")
				target = vType()
	return target