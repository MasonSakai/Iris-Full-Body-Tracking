import numpy as np

class RollingAverageFilter:
    
    filter_window: int
    filter_i = 0
    filter_data: np.array
    reduc: float
    reduc_div: float

    def __init__(self, dims: tuple | int, window: int, r: float = 1):
        self.filter_window = window
        self.filter_data = np.zeros(shape=((window,) + dims) if isinstance(dims, tuple) else (window, dims))
        self.reduc = r
        self.reduc_div = self.filter_window if self.reduc == 1 else ((pow(self.reduc, self.filter_window) - 1) / (self.reduc - 1))

    def apply(self, data):
        self.filter_data *= self.reduc
        self.filter_data[self.filter_i] = data
        self.filter_i += 1
        if self.filter_i >= self.filter_window: self.filter_i = 0

        return np.sum(self.filter_data, axis=0) / self.reduc_div



