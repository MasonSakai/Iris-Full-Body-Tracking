from app.dataproviders import DataSource, TransformedDataSource
import numpy as np


class PositionSource(DataSource):
    
    def get_priority_positions(self):
        return 0

    def get_data_positions(self):
        return {}

    worker_priority_positions: float
    worker_data_positions: dict[str, np.array]
    def update(self):
        with self.source_pose_lock:
            self.worker_priority_positions = self.get_priority_positions()
            self.worker_data_positions = self.get_data_positions()

class RayPositionSource(PositionSource, TransformedDataSource):
    pass

class ScoredPositionSource:
    
    def get_scores_positions(self):
        return {}
    
    worker_scores_positions: dict[str, float]
    def update(self):
        with self.source_pose_lock:
            self.worker_scores_positions = self.get_scores_positions()