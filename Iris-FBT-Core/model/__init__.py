import threading

class Point2DC:
    def __init__(self, x, y, conf):
        self.x = x
        self.y = y
        self.conf = conf

    def __repr__(self):
        return f'<Point2DC: {self.__str__()}>'
    
    def __str__(self):
        return f'({self.x} {self.y}) - {self.conf}'


class ModelConfig(object):
    MODEL_PATH = ''
    MODEL_CUTOFF = 0.8
    MODEL_INDEXES = {}


class Model:
    
    model_lock = threading.Lock()

    def __init__(self, base_config, model_config=ModelConfig):
        self.base_config = base_config
        self.model_config = model_config

    def __enter__(self):
        self.model_lock.acquire()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model_lock.release()
    

    def forward(self, img, point_correction=lambda x: x, **values):
        pass
    
    def To_Pose(self, data, point_correction):
        pass
    
    @staticmethod
    def To_Point(data, point_correction):
        return point_correction(Point2DC(data[0], data[1], data[2]))

                    
class ModelGenerator:
    pass