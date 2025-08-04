from flask import request, render_template, flash, redirect, url_for, jsonify, request, abort
import sqlalchemy as sqla

from app import db
from CameraWebsite.models import WebsiteCamera
from CameraWebsite import cam_web_blueprint as bp_cam
from CamWebSocket import sockets


@bp_cam.route('/')
def index():
    return render_template('camsite.html', title='Remote Camera Process')



@bp_cam.route('/cameras')
def get_cameras():
    data = []
    cameras = db.session.scalars(sqla.select(WebsiteCamera)).all()
    for camera in cameras:
        data.append(camera.getConfig())
        
    return jsonify(data)


@bp_cam.route('/cameras/<id>', methods=['GET', 'POST'])
def get_camera(id):
    camera = db.session.get(WebsiteCamera, id)
    return jsonify(camera.getConfig())


@bp_cam.route('/cameras/<id>/update', methods=['POST'])
def set_config(id):
    camera = db.session.get(WebsiteCamera, id)
    camera.setConfig(request.json)
    db.session.commit()
    return jsonify(camera.getConfig())


@bp_cam.route('/cameras/<id>/image', methods=['POST'])
def on_image(id):
    if int(id) in sockets:
        sockets[int(id)].on_image(request.get_data().decode('utf-8'))
        return '', 204
    print(id, sockets.keys())
    return 'ID not active', 403


@bp_cam.route('/cameras/new', methods=['POST'])
def new_camera():
    config = request.get_json()
    camera = WebsiteCamera(config)
    db.session.add(camera)
    db.session.commit()
    return jsonify(camera.getConfig())


@bp_cam.route('/cameras/<id>/cam_box')
def get_camera_html(id):
    return render_template('_cam_box.html', camera=db.session.get(WebsiteCamera, id))

@bp_cam.route('/CameraWorker.js')
def get_camera_worker():
    return redirect(url_for('CameraWebsite.static', filename='js/CameraWorker.js'))