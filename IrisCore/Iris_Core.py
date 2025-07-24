from flask import flash
from config import Config
from app import create_app, start_app, db
from app.IrisModules import imported_modules, IrisModule
from app.apriltag.models import AprilTagDetector
from app.main.models import Camera, CVUndistortableCamera
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
import numpy as np

app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'np': np,
            'imported_modules': imported_modules, 'IrisModule': IrisModule,
            'Camera': Camera, 'CVUndistortableCamera': CVUndistortableCamera}


@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()
        if db.session.scalars(sqla.select(AprilTagDetector)).first() is None:
            db.session.add(AprilTagDetector(families="tag36h11"))
            flash('Auto-created april tag detector for family tag36h11')

        try:
            cams: list[CVUndistortableCamera] = db.session.scalars(sqla.select(CVUndistortableCamera)).all()
            for cam in cams:
                if cam.calib_res_width > 0:
                    continue

                print('fixing', cam)

                cam.calib_res_width = 640
                cam.calib_res_height = 480
            
                cam.set_camera_params(
                    np.array([
                        [ 239.88769520166855,   0.0,              328.05049792214913 ],
                        [   0.0,              240.17084283097014, 198.87224716815462 ],
                        [   0.0,                0.0,                1.0              ]
                    ]),
                    np.array([
                         0.013031624243773052,
                        -0.028433912783647892,
                        -0.0010503130874263626,
                        -0.0008006911517726126,
                         0.004664156567676642
                    ]))
        except:
            pass

        db.session.commit()


if __name__ == "__main__":
    start_app(app, Config)
