from flask import Blueprint, render_template, flash, redirect, session, url_for, jsonify, request, abort

from app.cameras.forms import CameraForm, NewLocalReferenceForm
from app.cameras.models import Camera, LocalCameraReference
from app.main.modal import modal_redirect, modal_success
from utils.registry import ThingDatabase

bp_cam = Blueprint('cameras', __name__, static_folder='static', template_folder='templates', url_prefix='/cameras')

import app.cameras.calibration

@bp_cam.route('/', methods=['GET', 'POST'])
def index():
	return render_template('cam_manager.html',
		cams = ThingDatabase(Camera).AllThingsListForReading()
	)

@bp_cam.route('/list')
def get_cameras():
	return jsonify([{ 'name': d.display_name, 'id': d.ThingID(), 'transform': d.transform.tolist() if d.transform else None } for d in ThingDatabase(Camera).AllThingsListForReading()])

@bp_cam.route('/new', methods=['GET', 'POST'])
def new_camera():
	form = CameraForm()
	if form.validate_on_submit():
		cam = Camera()
		cam.display_name = form.display_name.data
		ThingDatabase(Camera).Add(cam)
		return redirect(url_for('cameras.view_camera', cam_id=cam.ThingID()))
	return render_template('_new_cam.html', form=form)

@bp_cam.route('/<cam_id>', methods=['GET', 'POST'])
def view_camera(cam_id):
	cam = ThingDatabase(Camera).Get(cam_id)
	form = CameraForm(existing_cam=cam)
	if form.validate_on_submit():
		if cam.display_name != form.display_name.data:
			cam.Rename(form.display_name.data)
		return modal_success(cam_id=cam.ThingID())
	elif request.method == 'GET':
		form.display_name.data = cam.display_name
	return render_template('_view_cam.html', form=form, camera=cam)

@bp_cam.route('/<cam_id>/delete', methods=['GET', 'POST'])
def delete_camera(cam_id):
	db = ThingDatabase(Camera)
	cam = db.Get(cam_id)
	name = cam.display_name
	db.Remove(cam)
	return modal_success(name=name)


@bp_cam.route('/<cam_id>/references/new/local', methods=['GET', 'POST'])
def new_lref(cam_id: str):
	cam = ThingDatabase(Camera).Get(cam_id)
	found_cams, new_cams = LocalCameraReference.EnumerateCameras()
	form = NewLocalReferenceForm(new_cams, cam)

	if form.validate_on_submit():
		ref = LocalCameraReference()
		ref.parent = cam
		ref.display_name = form.display_name.data
		ref.autostart = form.autostart.data

		[ref.name, ref.vid, ref.pid] = form.ident.data.split(':')
		cam.references.append(ref)
		return modal_success()
	elif request.method == 'GET':
		form.display_name.data = f"Local Reference { len(cam.references) }"
	return render_template('_new_lref.html', form=form, camera=cam)


@bp_cam.route('/<cam_id>/references/<ref_id>', methods=['GET', 'POST'])
def view_ref(cam_id: str, ref_id: str):
	cam = ThingDatabase(Camera).Get(cam_id)
	ref = next(filter(lambda r: r.ThingID() == ref_id, cam.references), None)
	return ref.RenderView()

@bp_cam.route('/<cam_id>/references/<ref_id>/delete')
def delete_ref(cam_id: str, ref_id: str):
	cam = ThingDatabase(Camera).Get(cam_id)
	ref = next(filter(lambda r: r.ThingID() == ref_id, cam.references), None)
	name = ref.display_name
	cam.references.remove(ref)
	return modal_success(name=name)