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

@bp_aptg.route('/tags/list')
def get_tags():
    db_tags = db.session.scalars(sqla.select(AprilTag)).all()

    tags = []
    for tag in db_tags:
        data = []
        if tag.id in seen_tags:
            for i, det in seen_tags[tag.id].items():
                source = db.session.get(Camera, i)
                data.append({
                    'cam': source.id,
                    'pose_t': det.pose_t.tolist(),
                    'pose_r': det.pose_R.tolist(),
                    'pose_err': det.pose_err
                })
        tags.append({
            'tag':
            {
                'id': tag.id,
                'size': tag.tag_size,
                'name': tag.display_name,
                'ident': '{}:{}'.format(tag.tag_family, tag.tag_id),
                'transform': tag.get_transform().tolist(),
                'static': tag.ensure_static,
            },
            'cams': data
        })

    return tags

@bp_aptg.route('/tags/found/list')
def get_found_tags():
    detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()
    sizes = {}
    for detector in detectors:
        for family in detector.families.split():
            sizes[family] = detector.default_tag_size

    tags = {}
    for (tag, sources) in found_tags:
        data = []
        for source, det in sources.items():
            data.append({
                'cam': source.id,
                'pose_t': det.pose_t.tolist(),
                'pose_r': det.pose_R.tolist(),
                'pose_err': det.pose_err
            })
        tags['{}:{}'.format(tag.tag_family.decode('utf-8'), tag.tag_id)] = {
            'size': sizes[tag.tag_family.decode('utf-8')],
            'cams': data
        }

    return tags

@bp_aptg.route('/cameras/list')
def get_cams():
    db_cams = db.session.scalars(sqla.select(Camera)).all()

    cams = []
    for cam in db_cams:
        cams.append({
            'id': cam.id,
            'name': cam.display_name,
            'transform': cam.get_transform().tolist()
        })

    return cams