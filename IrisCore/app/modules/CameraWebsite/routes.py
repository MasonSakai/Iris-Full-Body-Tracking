from flask import render_template, flash, redirect, url_for, jsonify, request, abort
import sqlalchemy as sqla

from app import db
from CameraWebsite.models import WebsiteCamera
from CameraWebsite import cam_web_blueprint as bp_cam


@bp_cam.route('/')
def index():
    return render_template('index.html', title='Remote Camera Process')


@bp_cam.route('/cameras')
def get_cameras():
    data = []
    cameras = db.session.scalars(sqla.select(WebsiteCamera)).all()
    for camera in cameras:
        data.append(camera.getConfig())
        
    return jsonify(data)


@bp_cam.route('/cameras/<id>', methods=['GET', 'POST'])
def get_camera(cam_id):
    camera = db.session.scalars(
        sqla.select(WebsiteCamera)
        .where(WebsiteCamera.camera_id == cam_id)
    ).first()
    return jsonify(camera.getConfig())


@bp_cam.route('/cameras/new', methods=['POST'])
def new_camera():
    config = request.get_json()
    camera = WebsiteCamera(config)
    db.session.add(camera)
    db.session.commit()
    return jsonify(camera.getConfig())


@bp_cam.route('/cameras/<cam_id>/cam_box')
def get_camera_html(cam_id):
    camera = db.session.scalars(
        sqla.select(WebsiteCamera)
        .where(WebsiteCamera.camera_id == cam_id)
    ).first()
    return render_template('_cam_box.html', camera=camera)


#@bp_main.route('/fields/list')
#def rf_list():
#    data = []
#    
#    fields = db.session.scalars(sqla.select(ResearchField)).all()
#    for field in fields:
#        data.append({
#            'id': field.id,
#            'title': field.title,
#            'position_count': len(db.session.scalars(field.positions.select()).all()),
#            'student_count': len(db.session.scalars(field.students.select()).all())
#        })

#    return jsonify(data)


#@bp_main.route('/positions/<pos_id>')
#def view_position(pos_id):
#    return render_template('_research.html',
#                           research_pos=db.session.get(ResearchPosition, pos_id))