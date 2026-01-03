from abc import ABC, abstractmethod
from typing import Callable, Type, TypeVar, cast

from utils import Log

class IThing(ABC):
    """
    Interface for ThingDatabase
    """
    _index: int = -1
    """
    internal database index
    NOT PERSISTENT
    """

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
    db = _internal_databases.get(t)
    if db is None:
        raise KeyError(f"No database registered for {t}")
    return cast(ThingDatabaseInternal[T], db)

def HasThingDatabase(t: Type[T]) -> bool:
    """
    Returns true if a database exists EXPLICITLY for a given type
    """
    return t in _internal_databases

def CreateThingDatabase(t: Type[T], db_factory: Callable[[Type[T]], ThingDatabaseInternal[T]] = ThingDatabaseInternal[T]) -> bool:
    """
    Creates a thing database
    Returns True if the database was created or already exists, false if it failed to create or T is not an IThing
    """
    if not issubclass(t, IThing):
        return False
    if t in _internal_databases:
        return True
    try:
        _internal_databases[t] = db_factory(T)
        return True
    except Exception as ex:
        Log.Error(Log.LogLevel.Error, f'Failed to create ThingDatabase with type {t}\n{ex}')
        return False