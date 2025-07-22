from flask import render_template
import sqlalchemy as sqla

from app import db
from app.apriltag import apriltag_blueprint as bp_aptg
from app.apriltag.models import AprilTag, AprilTagDetector

@bp_aptg.route('/')
def index():
    tags = db.session.scalars(sqla.select(AprilTag)).all()
    detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()

    return render_template('apriltag.html', title='April Tag Manager',
                           known_tags=tags, detectors=detectors, found_tags=[])



@bp_aptg.route('/detectors/<id>')
def view_detector(id):
    pass

@bp_aptg.route('/tags/<id>')
def view_tag(id):
    pass

@bp_aptg.route('/tags/found/<family>:<id>')
def view_found_tag(family, id):
    pass