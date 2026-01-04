from abc import ABC, abstractmethod
from typing import Callable, Type, TypeVar, cast

from utils import Log

class IThing(ABC):
    """
    Interface for ThingDatabase
    """
    _index: int
    """
    internal database index
    NOT PERSISTENT
    """

    def __init__(self):
        super().__init__()
        self._index = -1

    @abstractmethod
    def ThingName(self) -> str:
        """
        Unique name for this item in the database
        """

    def PostSetIndices(self) -> None:
        """
        callback by ThingDatabase when indices are recalculated
        """
    
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
        return None
    if t not in _internal_databases:
        try:
            _internal_databases[t] = db_factory(t)
        except Exception as ex:
            Log.Error(Log.LogLevel.Error, f'Failed to create ThingDatabase with type {t}\n{ex}')
            return None
    return _internal_databases[t]