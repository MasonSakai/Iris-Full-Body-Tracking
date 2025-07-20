from app.dataproviders import DataSource, TransformedDataSource
import numpy as np


class PositionSource(DataSource):
	
	def get_priority_positions(self):
		return 0

	def get_data_positions(self):
		return {}

class RayPositionSource(PositionSource, TransformedDataSource):
	pass

class ScoredPositionSource:
	
	def get_scores_positions(self):
		return {}