from __future__ import annotations
from typing import Callable, Type, TypeVar, cast, final

from utils import Log
from utils.scribe import LoadSaveMode, Scribe, Scribe_Values

class IThing:
	"""
	Interface for ThingDatabase
	"""

	def __init_subclass__(cls, ThingName: str | None = None, **kwargs):
		super().__init_subclass__(**kwargs)
		ThingIDManager.register_class(cls, ThingName)

	_thing_id: str | None

	def __init__(self):
		super().__init__()
		self._thing_id = None

	def ExposeData(self):
		super().ExposeData()
		self._thing_id = Scribe_Values.Look(self._thing_id, 'ThingID', str)

		match Scribe.mode:
			case LoadSaveMode.LoadingVars:
				ThingIDManager.register(self)
			case LoadSaveMode.PostLoadInit:
				self.ThingID

	@final
	@property
	def ThingID(self) -> str:
		"""
		Unique id for this item in the database
		"""
		if self._thing_id is None:
			self._thing_id = ThingIDManager.next(type(self))
		return self._thing_id
	
from utils.registry.ThingIDManager import ThingIDManager
from utils.registry.ThingDatabaseInternal import ThingDatabaseInternal

T = TypeVar('T_Thing', bound=IThing)

_internal_databases: dict[Type[T], ThingDatabaseInternal[T]] = {}

def ThingDatabase(t: Type[T]) -> ThingDatabaseInternal[T]:
	"""
	Rimworld-style database for global storage of things of a specific type
	This function gives an existing database
	"""
	if not isinstance(t, type):
		t = type(t)
	db = _internal_databases.get(t)
	if db is None:
		raise KeyError(f"No database registered for {t}")
	return cast(ThingDatabaseInternal[T], db)

def HasThingDatabase(t: Type[T]) -> bool:
	"""
	Returns true if a database exists EXPLICITLY for a given type
	"""
	if not isinstance(t, type):
		t = type(t)
	return t in _internal_databases

def CreateThingDatabase(t: Type[T], db_factory: Callable[[Type[T]], ThingDatabaseInternal[T]] = ThingDatabaseInternal[T]) -> ThingDatabaseInternal[T]:
	"""
	Creates a thing database
	Returns database if the database was created or already exists, None if it failed to create or T is not an IThing
	"""
	if not isinstance(t, type):
		t = type(t)
	if not issubclass(t, IThing):
		Log.Error(Log.LogLevel.Error, f'Failed to create ThingDatabase, {t} is not IThing')
		return None
	if t not in _internal_databases:
		try:
			_internal_databases[t] = db_factory(t)
		except Exception as ex:
			Log.Error(Log.LogLevel.Error, f'Failed to create ThingDatabase with type {t}\n{ex}')
			return None
	return _internal_databases[t]

def ClearAllThingDatabases():
	for db in _internal_databases.values():
		db.Clear()
