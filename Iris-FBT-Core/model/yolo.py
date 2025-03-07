import os
import cv2 as cv
from config import Config
from ultralytics import YOLO
from model import Model, ModelConfig


class YoloModelConfig(ModelConfig):
    MODEL_PATH = 'Models\\yolo11n-pose.onnx'
    MODEL_CUTOFF = 0.8
    MODEL_INDEXES = {
            'nose':            0,
            'left_eye':        1,
            'right_eye':       2,
            'left_ear':        3,
            'right_ear':       4,
            'left_shoulder':   5,
            'right_shoulder':  6,
            'left_elbow':      7,
            'right_elbow':     8,
            'left_wrist':      9,
            'right_wrist':    10,
            'left_hip':       11,
            'right_hip':      12,
            'left_knee':      13,
            'right_knee':     14,
            'left_foot':      15,
            'right_foot':     16,
        }

class YOLOModel(Model):
    
    def __init__(self, base_config=Config, model_config=YoloModelConfig):
        super().__init__(base_config, model_config)
        path = os.path.join(base_config.ROOT_PATH, model_config.MODEL_PATH)
        self.model = YOLO(path)
        print(path)

    
    def forward(self, img, point_correction=lambda x: x, stream=False, **values):
        res = self.model.track(img, stream=stream)
        
        poses = []

        for r in res:
            points = r.keypoints
            for data in points.data:
                poses.append(self.To_Pose(data, point_correction))

        return poses

    
    def To_Pose(self, data, point_correction):
        pose = {}
        for key in self.model_config.MODEL_INDEXES:
            pdata = data[self.model_config.MODEL_INDEXES[key]]
            if pdata[2] >= self.model_config.MODEL_CUTOFF:
                pose[key] = Model.To_Point(pdata, point_correction)
                
        return pose