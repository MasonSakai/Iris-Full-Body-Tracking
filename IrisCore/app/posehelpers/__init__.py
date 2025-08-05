from app.main.math_worker import MathWorker
import numpy as np

def write_pose(worker: MathWorker, key: str, x: np.array, y: np.array, z: np.array):
    pose = worker.pose_data[key]
    if pose.size == 3:
        pose = np.eye(4)
        pose[:3, 3] = worker.pose_data[key]

    pose[:3, 0] = x
    pose[:3, 1] = y
    pose[:3, 2] = z

    worker.pose_data[key] = pose

def vec_project(a: np.ndarray, b: np.ndarray) -> np.ndarray :
    return (np.dot(a, b) / np.dot(b, b)) * b

def vec_reject(a: np.ndarray, b: np.ndarray) -> np.ndarray :
    return a - vec_project(a, b)