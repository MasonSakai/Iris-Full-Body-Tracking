from __future__ import annotations
import random



class ThingIDManager:

	_type_names: dict[type, str] = {}
	_allocated_ids: dict[type, set[str]] = {}

	@classmethod
	def get_class(cls, thing_type: type[IThing]) -> type[IThing]:
		for base in thing_type.__mro__:
			if base in cls._type_names:
				return base

		raise RuntimeError(
			f"{thing_type.__qualname__} does not define a ThingName "
			"and inherits none from its bases."
		)

	@classmethod
	def next(cls, thing_type: type) -> str:
		t = cls.get_class(thing_type)
		name = cls._type_names[t]
		while (ident := f"{name}{random.randint(1000, 9999)}") and ident in cls._allocated_ids[t]: pass
		cls._allocated_ids[t].add(ident)
		return ident

	@classmethod
	def register(cls, thing: IThing):
		cls._allocated_ids[cls.get_class(type(thing))].add(thing._thing_id)

	@classmethod
	def register_class(cls, thing_type: type[IThing], thing_name: str | None):
		if thing_name is None: return
		cls._type_names[thing_type] = thing_name
		cls._allocated_ids[thing_type] = set()


from utils.registry import IThing