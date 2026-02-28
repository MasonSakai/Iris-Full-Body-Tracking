from abc import abstractmethod
from threading import RLock
import time
from utils.registry import IThing, CreateThingDatabase

class IDataSource(IThing):
	
	source_data_lock: RLock

	def __init__(self):
		super().__init__()
		self.source_data_lock = RLock()
		
	@abstractmethod
	def HasUpdate(self) -> bool:
		pass
	
	@abstractmethod
	def GetData(self):
		pass

	def _GetTimestamp(self):
		return time.time()

CreateThingDatabase(IDataSource)