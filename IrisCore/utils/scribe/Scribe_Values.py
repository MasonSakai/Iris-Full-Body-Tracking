
from typing import Callable, Type
from utils import Log
from utils.scribe import IExposable, Scribe, LoadSaveMode
from utils.scribe.internal import ParseHelper, ScribeExtractor


def Look[T](value: T, label: str, vType: Type[T], defaultValue: T = None, forceSave: bool = False) -> T:
	match Scribe.mode:
		case LoadSaveMode.Saving:
			if issubclass(vType, IExposable):
				Log.Error(f"Using Scribe_Values with a IExposable reference {label}. Use Scribe_References or Scribe_Deep instead.");
				return value
			if (not forceSave) and (value is not None or defaultValue is None) and (value is None or value is defaultValue):
				return value
			if value is None:
				if not Scribe.EnterNode(label):
					return value
				try:
					Scribe.saver.WriteAttribute("IsNull", "True");
				finally:
					Scribe.ExitNode();
			else:
				Scribe.saver.WriteElement(label, value, vType)
		case LoadSaveMode.LoadingVars:
			value = ScribeExtractor.ValueFromNode(Scribe.loader.curXmlParent.find(label), vType, defaultValue);
	return value


def HasParsers(t: Type) -> bool:
	try:
		ParseHelper._find_parser(t, ParseHelper.parsers_ToString)
		ParseHelper._find_parser(t, ParseHelper.parsers_FromString)
		return True
	except:
		return False
def AddParsers[T](t: Type[T],
				  toString: Callable[[T], str | tuple[str, list[tuple[str, str]]]],
				  fromString: Callable[[str, dict[str, str]], T]):
	if toString and fromString:
		ParseHelper.parsers_ToString[t] = toString
		ParseHelper.parsers_FromString[t] = fromString