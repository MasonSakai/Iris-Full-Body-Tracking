from config import Config
from app import create_app, start_app, db
from app.IrisModules import imported_modules, IrisModule
from app.apriltag.models import AprilTagDetector
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db,
            'imported_modules': imported_modules, 'IrisModule': IrisModule }


@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()
        if db.session.scalars(sqla.select(AprilTagDetector)).first() is None:
            db.session.add(AprilTagDetector(families="tag36h11"))
        db.session.commit()


if __name__ == "__main__":
    start_app(app, Config)
