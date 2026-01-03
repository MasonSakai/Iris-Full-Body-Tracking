


import random
from typing import Generic, Iterable, Type, TypeVar

from utils import Log
from utils.registry import IThing
from utils.scribe import IExposable, LoadSaveMode, Scribe, Scribe_Collections, Scribe_Values

T = TypeVar('T_Thing', bound=IThing)

class ThingDatabaseInternal(Generic[T], IExposable):
	"""
	Rimworld-style database for global storage of things of a specific type
	"""
	
	__thingList: list[T] = []
	__thingsByName: dict[str, T] = {}
	__my_type: type[T]

	def __init__(self, t: T):
		super().__init__()
		self.__my_type = t

	def ExposeData(self):
		if Scribe.mode == LoadSaveMode.PostLoadInit:
			for index in range(len(self.__thingList)):
				thing = self.__thingList[index]
				self.__thingsByName[thing.ThingName()] = thing
				thing._index = index

		self.__thingList = Scribe_Collections.LookList(self.__thingList, 'ThingList', self.__my_type, Scribe_Collections.LookMode.Deep)

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

	#def AddAll

	def Add(self, *things: T) -> None:
		for thing in things:
			if not isinstance(thing, self.__my_type):
				Log.Error(Log.LogLevel.Error, f"ThingDatabase failed to add {thing.ThingName()} because {type(thing)} is not {self.__my_type}")
				continue
			self.__thingList.append(thing)
			self.__thingsByName[thing.ThingName()] = thing
			thing._index = len(self.__thingList) - 1

	def Remove(self, *things: T) -> None:
		for thing in things:
			self.__thingList.remove(thing)
			del self.__thingsByName[thing.ThingName]

	def SetIndices(self) -> None:
		for index in range(len(self.__thingList)):
			self.__thingList[index]._index = index
		for thing in self.__thingList:
			thing.PostSetIndices()

	def Clear(self) -> None:
		self.__thingList.clear()
		self.__thingsByName.clear()

	def GetNamed(self, name: str, errorOnFail: bool = True) -> T:
		if name not in self.__thingsByName:
			if errorOnFail:
				Log.Error(Log.LogLevel.Error, f"Failed to find {self.__my_type} named {name}. There are {self.ThingCount} defs of this type loaded.")
			return None
		return self.__thingsByName[name]

	def GetRandom(self) -> T:
		return random.choice(self.__thingsByName)
