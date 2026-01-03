from flask import flash
from config import Config
from utils.scribe import Scribe
from app import create_app, start_app
from utils.modulemanager.IrisModules import imported_modules, IrisModule
from app.cameras.models import Camera, CVUndistortableCamera
from app.apriltag import AprilTag
import numpy as np

print("DO: https://youtube.com/shorts/SUOEgaPL6xM")
app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {'scribe': Scribe, 'np': np,
            'imported_modules': imported_modules, 'IrisModule': IrisModule,
            'Camera': Camera, 'CVUndistortableCamera': CVUndistortableCamera,
            'AprilTag': AprilTag}


# @app.before_request
# def initDB(*args, **kwargs):
#     if app._got_first_request:
#         db.create_all()
#         if db.session.scalars(sqla.select(AprilTagDetector)).first() is None:
#             db.session.add(AprilTagDetector(families="tag36h11"))
#             flash('Auto-created april tag detector for family tag36h11')

#         db.session.commit()


if __name__ == "__main__":
    start_app(app, Config)
