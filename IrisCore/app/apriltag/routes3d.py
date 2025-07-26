from flask import flash, redirect, render_template, request, url_for, Response
from pupil_apriltags import Detector
from moms_apriltag import TagGenerator2
import sqlalchemy as sqla
import numpy as np
import cv2 as cv

from app import db
from app.apriltag import apriltag_blueprint as bp_aptg, found_tags, seen_tags
from app.apriltag.models import AprilTag, AprilTagDetector
from app.apriltag.forms import DetectorForm, FoundTagForm, EditTagForm
from app.main.models import Camera


@bp_aptg.route('/3D')
def index3d():
    return render_template('apriltag3D.html', title='April Tag 3D Manager')

@bp_aptg.route('/tags/image/<family>:<id>.<fileType>')
def generate_tag_image(family, id, fileType):
    tag_image = TagGenerator2(family).generate(int(id))
    _, encoded_image = cv.imencode('.{}'.format(fileType), cv.cvtColor(tag_image, cv.COLOR_GRAY2BGR))
    return Response(encoded_image.tobytes())
