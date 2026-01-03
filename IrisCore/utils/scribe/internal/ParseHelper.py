import importlib
from typing import Callable, Type

import numpy as np


def GetQualifiedName(target) -> str:
	return f"{target.__module__}:{target.__qualname__}"

def GetTypeFromName(name) -> Type:
	s = name.split(':')
	return getattr(importlib.import_module(s[0]), s[1])


parsers: dict[Type, Callable[[str], any]] = {}

parsers[str] = lambda s: s.replace('\\n', '\n')
parsers[int] = lambda s: int(s)
parsers[float] = lambda s: float(s)
parsers[bool] = lambda s: bool(s)
parsers[np.ndarray] = lambda s: np.fromstring(s)
parsers[Type] = GetTypeFromName

def FromString[T](s: str, t: Type[T]) -> T:
	return parsers[t](s)