


import random
from typing import Generic, Iterable, Type, TypeVar

from utils.scribe import ILoadReferenceable
from utils import Log
from utils.registry import IThing

T = TypeVar('T_Thing', bound=IThing)

class ThingDatabaseInternal(Generic[T]):
	"""
	ThingDatabaseInternal is a mutable, runtime-global registry.
	"""
	
	__thingList: list[T]
	__thingsByID: dict[str, T]
	__my_type: type[T]

	def __init__(self, t: T):
		super().__init__()
		self.__my_type = t
		self.__thingList = []
		self.__thingsByID = {}

	def AllThings(self) -> Iterable[T]:
		"""
		Gives an iterable with all contained things
		"""
		for thing in self.__thingList:
			yield thing

	def AllThingsListForReading(self) -> list[T]:
		"""
		(NOT RECOMMENDED) Returns direct reference to internal thing list
		"""
		return self.__thingList

	def ThingCount(self) -> int:
		return len(self.__thingList)

	def Add(self, *things: T) -> None: #add conflict check?
		for thing in things:
			if not isinstance(thing, self.__my_type):
				Log.Error(Log.LogLevel.Error, f"ThingDatabase failed to add {thing.ThingID} because {type(thing)} is not {self.__my_type}")
				continue
			self.__thingList.append(thing)
			self.__thingsByID[thing.ThingID] = thing

	def Remove(self, *things: T) -> None:
		for thing in things:
			self.__thingList.remove(thing)
			del self.__thingsByID[thing.ThingID]

	def Clear(self) -> None:
		self.__thingList.clear()
		self.__thingsByID.clear()

	def Get(self, id: str, errorOnFail: bool = True) -> T:
		if id not in self.__thingsByID:
			if errorOnFail:
				Log.Error(Log.LogLevel.Error, f"Failed to find {self.__my_type} with ID {id}. There are {self.ThingCount()} things of this type loaded.")
			return None
		return self.__thingsByID[id]

	def GetRandom(self) -> T:
		return random.choice(self.__thingList)
