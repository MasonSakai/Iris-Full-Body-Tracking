from flask import Blueprint, render_template, flash, redirect, session, url_for, jsonify, request, abort

from app.cameras.forms import CameraForm
from app.cameras.models import Camera
from app.main.modal import modal_redirect, modal_success
from utils.registry import ThingDatabase

bp_cam = Blueprint('cameras', __name__, static_folder='static', template_folder='templates', url_prefix='/cameras')

import app.cameras.calibration

@bp_cam.route('/', methods=['GET', 'POST'])
def index():
    return render_template('cam_manager.html',
        cams = ThingDatabase(Camera).AllThingsListForReading()
    )

@bp_cam.route('/new', methods=['GET', 'POST'])
def new_camera():
    form = CameraForm()
    if form.validate_on_submit():
        cam = Camera()
        cam.display_name = form.display_name.data
        ThingDatabase(Camera).Add(cam)
        return redirect(url_for('cameras.view_camera', id=cam.ThingID()))
    return render_template('_new_cam.html', form=form)

@bp_cam.route('/<id>', methods=['GET', 'POST'])
def view_camera(id):
    cam = ThingDatabase(Camera).Get(id)
    form = CameraForm(existing_cam=cam)
    if form.validate_on_submit():
        if cam.display_name != form.display_name.data:
            cam.Rename(form.display_name.data)
        return modal_success(id=cam.ThingID())
    elif request.method == 'GET':
        form.display_name.data = cam.display_name
    return render_template('_view_cam.html', form=form, camera=cam)

@bp_cam.route('/<id>/delete', methods=['GET', 'POST'])
def delete_camera(id):
    db = ThingDatabase(Camera)
    cam = db.Get(id)
    name = cam.display_name
    db.Remove(cam)
    flash('Camera {} Deleted!'.format(name))
    return redirect(url_for('cameras.index'))
