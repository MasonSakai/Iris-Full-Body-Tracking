from app.main.math_worker import MathWorker
import numpy as np

from app.posehelpers import vec_reject, write_pose

#+x left, -y up, -z forward
# len +y, norm +x, rem +z
# norm: upper x lower
# rem: norm x len

def do_leg_rotation(worker: MathWorker, key_hip: str, key_knee: str, key_ankle: str, key_ref: str):
    b_hip = key_hip in worker.pose_data
    b_knee = key_knee in worker.pose_data
    b_ankle = key_ankle in worker.pose_data

    if b_hip and b_knee and b_ankle:
        _do_full(worker, key_hip, key_knee, key_ankle, key_ref)

        
def _do_full(worker: MathWorker, key_hip: str, key_knee: str, key_ankle: str, key_ref: str):
    pos_hip = worker.pose_data[key_hip]
    pos_knee = worker.pose_data[key_knee]
    pos_ankle = worker.pose_data[key_ankle]

    d_upper = pos_knee - pos_hip
    d_upper /= np.linalg.norm(d_upper)
    d_lower = pos_ankle - pos_knee
    d_lower /= np.linalg.norm(d_lower)

    d_norm = None
    if abs(np.dot(d_upper, d_lower)) > 0.96 and key_ref in worker.pose_data and worker.pose_data[key_ref].size > 3:
        R_ref = worker.pose_data[key_ref][:3, :3]

        d_leg = pos_ankle - pos_hip
        d_leg /= np.linalg.norm(d_leg)
        if np.dot(d_upper, d_lower) < 0:
            d_leg = d_upper
            
        d_left = R_ref[:, 0]
        d_down = R_ref[:, 1]

        if abs(np.dot(d_leg, d_left)) > 0.99:
            d_norm = vec_reject(d_down, d_leg)
            d_norm /= np.linalg.norm(d_norm)
            if np.dot(d_leg, d_left) > 0:
                d_norm *= -1
        else:
            d_norm = vec_reject(d_left, d_leg)
            d_norm /= np.linalg.norm(d_norm)
            if np.dot(d_leg, d_down) < 0:
                d_norm *= -1


    else:
        d_norm = np.cross(d_upper, d_lower)
        d_norm /= np.linalg.norm(d_norm)

    write_pose(worker, key_hip, d_norm, d_upper, np.cross(d_norm, d_upper))
    write_pose(worker, key_knee, d_norm, d_lower, np.cross(d_norm, d_lower))
    write_pose(worker, key_ankle, d_norm, d_lower, np.cross(d_norm, d_lower))