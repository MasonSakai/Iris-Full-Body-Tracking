from app.main.math_worker import MathWorker
import numpy as np

from app.posehelpers import vec_reject, write_pose

#+x left, -y up, -z forward
#left:  len +x, norm +y, rem +z
#right: len -x, norm -y, rem +z
# norm: upper x lower
# rem: norm x len

def do_arm_rotation(worker: MathWorker, key_shoulder: str, key_elbow: str, key_wrist: str, key_ref: str, is_right: bool):
    b_shoulder = key_shoulder in worker.pose_data
    b_elbow = key_elbow in worker.pose_data
    b_wrist = key_wrist in worker.pose_data

    if b_shoulder and b_elbow and b_wrist:
        _do_full(worker, key_shoulder, key_elbow, key_wrist, key_ref, is_right)

        
def _do_full(worker: MathWorker, key_shoulder: str, key_elbow: str, key_wrist: str, key_ref: str, is_right: bool):
    pos_shoulder = worker.pose_data[key_shoulder]
    pos_elbow = worker.pose_data[key_elbow]
    pos_wrist = worker.pose_data[key_wrist]

    d_upper = pos_elbow - pos_shoulder
    d_upper /= np.linalg.norm(d_upper)
    d_lower = pos_wrist - pos_elbow
    d_lower /= np.linalg.norm(d_lower)

    d_norm = None
    if abs(np.dot(d_upper, d_lower)) > 0.95 and key_ref in worker.pose_data and worker.pose_data[key_ref].size > 3:
        R_ref = worker.pose_data[key_ref][:3, :3]

        d_arm = pos_wrist - pos_shoulder
        d_arm /= np.linalg.norm(d_arm)
        if np.dot(d_upper, d_lower) < 0:
            d_arm = d_upper
            
        d_left = R_ref[:, 0]
        d_down = R_ref[:, 1]
        d_back = R_ref[:, 2]

        if abs(np.dot(d_arm, d_back)) > 0.99:
            d_norm = d_left
            d_norm /= np.linalg.norm(d_norm)
        else:
            d_norm = np.cross(d_back, d_arm)
            d_norm /= np.linalg.norm(d_norm)
            if np.dot(d_arm, d_down) < 0:
                d_norm *= -1

    else:
        d_norm = np.cross(d_upper, d_lower)
        d_norm /= np.linalg.norm(d_norm)

    if is_right:
        d_norm *= -1
        d_upper *= -1
        d_lower *= -1

    write_pose(worker, key_shoulder, d_upper, d_norm, np.cross(d_upper, d_norm))
    write_pose(worker, key_elbow, d_lower, d_norm, np.cross(d_lower, d_norm))
    write_pose(worker, key_wrist, d_lower, d_norm, np.cross(d_lower, d_norm))