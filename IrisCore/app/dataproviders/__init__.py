from threading import Lock
import numpy as np

source_registry: list['DataSource'] = []

class DataSource:
    
    source_pose_lock = Lock()

    def init(self):
        pass

    def update(self):
        pass

    def update_rare(self):
        pass

    def provider_flags(self):
        return {}

class TransformedDataSource(DataSource):
    
    worker_source_transform: np.array
    def update(self):
        with self.source_pose_lock:
            self.worker_source_transform = self.get_source_transform()

    def get_source_transform(self):
        return np.identity(4)

#add weighted?