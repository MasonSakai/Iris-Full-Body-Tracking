import pickle
from typing import Optional
from cv2.typing import MatLike
from app import db
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import numpy as np
import cv2 as cv


class Camera(db.Model):
    __tablename__ = "camera"
    
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    display_name : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True, index=True)
    transform: sqlo.Mapped[sqla.LargeBinary] = sqlo.mapped_column(sqla.LargeBinary, default=pickle.dumps(np.empty(0)))
    
    camera_type : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'camera',
        'polymorphic_on': camera_type}

    
    #functions
    def __init__(self, config):
        self.setConfig(config)
        super().__init__()

    def __repr__(self):
        return '<Camera - {} "{}">'.format(self.id, self.display_name)
    

    def set_transform(self, transform: np.array):
        self.transform = pickle.dumps(transform)
        db.session.commit()

    def get_transform(self):
        return pickle.loads(self.transform)

    def getConfig(self):
        return {
            'id': self.id,
            'name': self.display_name
        }
    
    def setConfig(self, config):
        if 'name' in config:
            self.display_name = config['name']

class CVUndistortableCamera(Camera):
    __tablename__ = "cv_undistortable_camera"
    id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey("camera.id"), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'cv_undistortable_camera'}

    calib_res_width: sqlo.Mapped[int] = sqlo.mapped_column(default=0)
    calib_res_height: sqlo.Mapped[int] = sqlo.mapped_column(default=0)
    camera_matrix: sqlo.Mapped[sqla.LargeBinary] = sqlo.mapped_column(sqla.LargeBinary, default=pickle.dumps(np.empty(0)))
    dist_coeffs: sqlo.Mapped[sqla.LargeBinary] = sqlo.mapped_column(sqla.LargeBinary, default=pickle.dumps(np.empty(0)))

    def set_camera_params(self, camera_matrix: np.array, dist_coeffs: np.array):
        self.camera_matrix = pickle.dumps(camera_matrix)
        self.dist_coeffs = pickle.dumps(dist_coeffs)
        db.session.commit()

    def get_camera_params(self):
        return (pickle.loads(self.camera_matrix), pickle.loads(self.dist_coeffs))

    def rescale_camera_matrix(self, shape):
        sy = shape[0] / self.calib_res_height
        
        mat = pickle.loads(self.camera_matrix)
        mat *= sy
        mat[0, 2] += (shape[1] - sy * self.calib_res_width) / 2
        mat[2, 2] = 1

        return mat

    def undistortImage(self, image: MatLike):
        (camera_matrix, dist_coeffs) = self.get_camera_params()
        return self.undistortImage(image, camera_matrix, dist_coeffs)
        
    def undistortImage(self, image: MatLike, camera_matrix: np.array, dist_coeffs: np.array):
        return cv.undistort(image, camera_matrix, dist_coeffs)

    def undistortPoints(self, data: np.array):
        (camera_matrix, dist_coeffs) = self.get_camera_params()
        return self.undistortPoints(data, camera_matrix, dist_coeffs)

        
    def undistortPoints(self, data: np.array, camera_matrix: np.array, dist_coeffs: np.array):
        if data is not np.array:
            data = np.array(data)

        return np.squeeze(cv.undistortPoints(data, camera_matrix, dist_coeffs))
