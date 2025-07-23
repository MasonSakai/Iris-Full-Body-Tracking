import numpy as np
from sqlalchemy import event
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.context import QueryContext

class DataSource:

	def init():
		pass

	def update(self):
		pass

	def update_rare(self):
		pass

	def provider_flags(self):
		return {}

class TransformedDataSource(DataSource):
	
	def get_source_transform(self):
		return np.identity(4, np.float64)

#add weighted?