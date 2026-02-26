

from enum import Enum
from threading import RLock
import traceback
from typing import Type

class LogLevel(Enum):
	Off = 0
	Critical = 1
	Error = 2
	Warning = 3
	Minimal = 4
	Info = 5
	Verbose = 6
	
from utils.debug import DebugViewSettings

__logLock = RLock()
__usedKeys = set()

def Message(messageLevel: LogLevel, msg: str) -> None:
	if DebugViewSettings.logLoadLevel.value < messageLevel.value: return
	with __logLock:
		print(msg)

def Warning(messageLevel: LogLevel, msg: str) -> None:
	if DebugViewSettings.logLoadLevel.value < messageLevel.value: return
	with __logLock:
		print(msg)

def Error(messageLevel: LogLevel, msg: str) -> None:
	if DebugViewSettings.logLoadLevel.value < messageLevel.value: return
	with __logLock:
		print(msg, traceback.format_exc(), sep='\n\n')
	
def ErrorOnce(messageLevel: LogLevel, msg: str, key: int) -> None:
	if DebugViewSettings.logLoadLevel.value < messageLevel.value: return
	with __logLock:
		if key in __usedKeys: return
		__usedKeys.add(key)
		Error(messageLevel, msg)


def ToStringSafe[T](obj: T, vtype: Type[T]) -> str:
	if obj is None:
		return 'None'
	try:
		return str(obj)
	except Exception as ex:
		gotHash = False
		hashNum = 0
		try:
			hashNum = hash(obj)
			gotHash = True
		except:
			pass
		if gotHash:
			ErrorOnce(LogLevel.Error, f"Exception in str(): {ex}", hashNum ^ 1857461521)
		else:
			Error(LogLevel.Error, f"Exception in str(): {ex}")
	return 'error'
