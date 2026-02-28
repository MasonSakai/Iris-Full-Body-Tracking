from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, request, abort

from modules.WebAI.models import WebAICameraReference
from modules.WebAI.WebAISocket import sockets
from app.cameras.models import Camera, CameraReference
from utils.registry import ThingDatabase


bp_webai = Blueprint('WebAI', __name__, static_folder='static', template_folder='templates', url_prefix='/webai')

@bp_webai.route('/')
def index():
	return render_template('webAI.html', title='Web AI Camera')



@bp_webai.route('/cameras')
def get_cameras():
	data = []
	cameraRefs = ThingDatabase(CameraReference).AllThingsListForReading()
	for ref in cameraRefs:
		if isinstance(ref, WebAICameraReference):
			data.append(ref.getConfig())
		
	return jsonify(data)


@bp_webai.route('/cameras/<id>', methods=['GET', 'POST'])
def get_camera(id):
	cameraRef = ThingDatabase(CameraReference).AllThingsListForReading()[int(id)]
	return jsonify(cameraRef.getConfig())


@bp_webai.route('/cameras/<id>/update', methods=['POST'])
def set_config(id):
	cameraRef = ThingDatabase(CameraReference).AllThingsListForReading()[int(id)]
	cameraRef.setConfig(request.json)
	db.session.commit()
	return jsonify(cameraRef.getConfig())


@bp_webai.route('/cameras/<id>/image', methods=['POST'])
def on_image(id):
	if int(id) in sockets:
		sockets[int(id)].on_image(request.get_data().decode('utf-8'))
		return '', 204
	print(id, sockets.keys())
	return 'ID not active', 403


@bp_webai.route('/cameras/new', methods=['POST'])
def new_camera():
	config = request.get_json()
	camera = WebAICameraReference(config)
	db.session.add(camera)
	db.session.commit()
	return jsonify(camera.getConfig())


@bp_webai.route('/cameras/<id>/cam_box')
def get_camera_html(id):
	cameraRef = ThingDatabase(CameraReference).AllThingsListForReading()[int(id)]
	return render_template('_cam_box.html', camera=cameraRef)

@bp_webai.route('/CameraWorker.js')
def get_camera_worker():
	return redirect(url_for('WebAI.static', filename='js/CameraWorker.js'))