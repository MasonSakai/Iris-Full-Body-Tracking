import ast
import binascii
import importlib
from typing import Callable, Type

import numpy as np


def GetQualifiedName(target: type) -> str:
	return f"{target.__module__}:{target.__qualname__}"

def GetTypeFromName(name: str) -> Type:
	module, qualname = name.split(':', 1)
	obj = importlib.import_module(module)
	for attr in qualname.split('.'):
		obj = getattr(obj, attr)
	return obj

def __ParseNPArray(s: str, a: dict[str, str]) -> np.ndarray:
	d = binascii.a2b_base64(s.encode('ascii'))
	dtype = GetTypeFromName(a['dtype'])()
	shape = tuple(map(int, a['shape'][1:-1].split(', ')))
	return np.frombuffer(d, dtype=dtype).reshape(shape)

def __SerializeNPArray(v: np.ndarray) -> tuple[str, list[tuple[str, str]]]:
	return (binascii.b2a_base64(v.tobytes()).decode('ascii'),
			[
				('dtype', GetQualifiedName(type(v.dtype))),
				('shape', str(v.shape))
			])

parsers_FromString: dict[Type, Callable[[str, dict[str, str]], any]] = {}

parsers_FromString[str] = lambda s, a: s.replace('\\n', '\n')
parsers_FromString[int] = lambda s, a: int(s)
parsers_FromString[float] = lambda s, a: float(s)
parsers_FromString[bool] = lambda s, a: bool(s)
parsers_FromString[np.ndarray] = __ParseNPArray
parsers_FromString[type] = lambda s, a: GetTypeFromName(s)


def FromString[T](s: str, a: dict[str, str], t: Type[T]) -> T:
	return parsers_FromString[t](s, a)


parsers_ToString: dict[Type, Callable[[any], str | tuple[str, list[tuple[str, str]]]]] = {}

parsers_ToString[str] = lambda v: v.replace('\n', '\\n')
parsers_ToString[int] = lambda v: str(v)
parsers_ToString[float] = lambda v: str(v)
parsers_ToString[bool] = lambda v: str(v)
parsers_ToString[np.ndarray] = __SerializeNPArray
parsers_ToString[type] = GetQualifiedName

def ToString[T](v: T, t: Type[T]) -> str | tuple[str, list[tuple[str, str]]]:
	return parsers_ToString[t](v)