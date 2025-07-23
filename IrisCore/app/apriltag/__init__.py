from flask import Blueprint

apriltag_blueprint = Blueprint('apriltag', __name__, static_folder='static', template_folder='templates', url_prefix='/apriltag')

from app.main.models import Camera
from pupil_apriltags import Detection

found_tags = []

from app.apriltag import models, routes

def add_found_tag(source: Camera, res: Detection):
    for i in range(len(found_tags)):
        det: Detection = found_tags[i][0]
        if det.tag_family == res.tag_family and det.tag_id == res.tag_id:
            found_tags[i][1].append(source)
            return

    found_tags.append((res, [source]))