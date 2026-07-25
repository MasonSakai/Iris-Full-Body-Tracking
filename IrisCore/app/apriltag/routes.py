from statistics import mode
from flask import Blueprint, jsonify, redirect, render_template, request, url_for, Response
from pupil_apriltags import Detector
from moms_apriltag import TagGenerator2
import numpy as np
import cv2 as cv

from app.apriltag.localization import ScanTags
from app.main.modal import modal_redirect, modal_success
from utils.registry import ThingDatabase
from app.apriltag.registry import found_tags, jsonify_FoundTagDetails, jsonify_TagDetails
from app.apriltag.models import AprilTag, AprilTagDetector
from app.apriltag.forms import DetectorForm, CreateDetectorForm, TagForm, EditTagForm
from utils.localization.objects import Detection, SolverObject
from utils.localization.placement_rules import parseRule
from utils.localization.solver import Solve

bp_aptg = Blueprint('apriltag', __name__, static_folder='static', template_folder='templates', url_prefix='/apriltag')

@bp_aptg.route('/')
def index():
	tags = ThingDatabase(AprilTag).AllThingsListForReading()
	detectors = ThingDatabase(AprilTagDetector).AllThingsListForReading()

	return render_template('apriltag.html', title='April Tag Manager',
						   known_tags=tags, detectors=detectors, found_tags=found_tags)

@bp_aptg.route('/3D')
def index3d():
	return render_template('apriltag3D.html', title='April Tag 3D Manager')


@bp_aptg.route('/tags/image/<family>:<id>.<fileType>')
def generate_tag_image(family, id, fileType):
	tag_image = TagGenerator2(family).generate(int(id))
	_, encoded_image = cv.imencode('.{}'.format(fileType), cv.cvtColor(tag_image, cv.COLOR_GRAY2BGR))
	return Response(encoded_image.tobytes())

@bp_aptg.route('/detectors')
def get_detectors():
	return jsonify([{ 'name': d.display_name, 'id': d.ThingID } for d in ThingDatabase(AprilTagDetector).AllThingsListForReading()])

@bp_aptg.route('/detectors/new', methods=['GET', 'POST'])
def create_detector():
	detector = AprilTagDetector()
	form = CreateDetectorForm()
	if form.validate_on_submit():
		detector.display_name = form.display_name.data
		detector.families = form.families.data
		detector.nthreads = form.nthreads.data
		detector.quad_decimate = form.quad_decimate.data
		detector.quad_sigma = form.quad_sigma.data
		detector.refine_edges = form.refine_edges.data
		detector.decode_sharpening = form.decode_sharpening.data
		detector.default_tag_size = form.default_tag_size.data / 100.

		ThingDatabase(AprilTagDetector).Add(detector)
		return modal_success(id=detector.ThingID)
	elif request.method == 'GET':
		form.display_name.data = 'tag36h11'
		form.families.data = 'tag36h11'
		form.nthreads.data = detector.nthreads
		form.quad_decimate.data = detector.quad_decimate
		form.quad_sigma.data = detector.quad_sigma
		form.refine_edges.data = detector.refine_edges
		form.decode_sharpening.data = detector.decode_sharpening
		form.default_tag_size.data = detector.default_tag_size * 100.

	return render_template('_create_detector.html', form=form)

@bp_aptg.route('/detectors/<id>', methods=['GET', 'POST'])
def view_detector(id):
	detector = ThingDatabase(AprilTagDetector).Get(id)
	form = DetectorForm(existing_detector=detector)
	if form.validate_on_submit():
		detector.families = form.families.data
		detector.nthreads = form.nthreads.data
		detector.quad_decimate = form.quad_decimate.data
		detector.quad_sigma = form.quad_sigma.data
		detector.refine_edges = form.refine_edges.data
		detector.decode_sharpening = form.decode_sharpening.data
		detector.default_tag_size = form.default_tag_size.data / 100.

		return modal_success(id=detector.ThingID)
	elif request.method == 'GET':
		form.families.data = detector.families
		form.nthreads.data = detector.nthreads
		form.quad_decimate.data = detector.quad_decimate
		form.quad_sigma.data = detector.quad_sigma
		form.refine_edges.data = detector.refine_edges
		form.decode_sharpening.data = detector.decode_sharpening
		form.default_tag_size.data = detector.default_tag_size * 100

	return render_template('_view_detector.html', form=form, detector=detector)

@bp_aptg.route('/detectors/<id>/delete')
def delete_detector(id):
	db = ThingDatabase(AprilTagDetector)
	detector = db.Get(id)
	name = detector.display_name
	db.Remove(detector)
	return modal_success(name=name)


@bp_aptg.route('/tags/scan')
def scan_tags():
	dets, tags = ScanTags(10)

	if ('noreturn' in request.args) and (request.args['noreturn'].lower() in ['', 'true']):
		return "{}"

	if tags is None:
		return jsonify({ 'known': { }, 'found': { } })
	
	return jsonify({
		'known': {
			tag.ThingID: {
				'name': tag.display_name,
				'size': tag.tag_size,
				'static': tag.ensure_static,
				'ident': f"{ tag.tag_family }:{ tag.tag_id }",
				'transform': tag.transform.tolist() if tag.transform else None,
				'detections': {
					cam.ThingID: jsonify_TagDetails(det)
					for cam, det in cams.items()
				}
			} for tag, cams in tags.items()
		},
		'found': {
			f"{family}:{id}": {
				cam.ThingID: jsonify_FoundTagDetails(det)
				for cam, det in cams.items()
			} for (family, id), cams in dets.items()
		}
	})


@bp_aptg.route('/tags')
def get_tags():
	return jsonify({
		tag.ThingID: {
			'name': tag.display_name,
			'size': tag.tag_size,
			'static': tag.ensure_static,
			'ident': f"{ tag.tag_family }:{ tag.tag_id }",
			'transform': tag.transform.tolist() if tag.transform else None,
			'detections': {
				cam.ThingID: jsonify_TagDetails(det)
				for cam, det in tag.detections.items()
			}
		} for tag in ThingDatabase(AprilTag).AllThingsListForReading()
	})

@bp_aptg.route('/tags/<id>', methods=['GET', 'POST'])
def view_tag(id):
	tag = ThingDatabase(AprilTag).Get(id)
	form = EditTagForm(existing_tag=tag)
	if form.validate_on_submit():

		#if tag.id in seen_tags:
		#    scale = tag.tag_size * 100 / form.tag_size.data
		#    for src in seen_tags[tag.id]:
		#        seen_tags[tag.id][src].pose_t *= scale


		tag.tag_size = form.tag_size.data / 100.
		tag.display_name = form.display_name.data
		tag.ensure_static = form.ensure_static.data

		return modal_success(id=tag.ThingID)
	
	if request.method == 'GET':
		form.tag_size.data = tag.tag_size * 100.
		form.display_name.data = tag.display_name
		form.ensure_static.data = tag.ensure_static
		
	return render_template('_view_tag.html', form=form, tag=tag)

@bp_aptg.route('/tags/<id>/delete')
def delete_tag(id):
	db = ThingDatabase(AprilTag)
	tag = db.Get(id)
	name = tag.display_name
	db.Remove(tag)
	# have this move to found tag if it has detections?
	return modal_success(name=name, id=id)


@bp_aptg.route('/tags/found')
def get_found_tags():
	return jsonify({
		f"{family}:{id}": {
			cam.ThingID: jsonify_FoundTagDetails(det)
			for cam, det in cams.items()
		} for (family, id), cams in found_tags.items()
	})

@bp_aptg.route('/tags/found/clear')
def clear_found_tags():
	found_tags.clear()
	return modal_success()

@bp_aptg.route('/tags/found/<family>:<id>', methods=['GET', 'POST'])
def view_found_tag(family, id):
	id = int(id)

	data = found_tags.get((family, id), None)

	if data is None:
		return


	form = TagForm()
	if form.validate_on_submit():
		tag = AprilTag()
		tag.tag_id = id
		tag.tag_family = family
		tag.tag_size = form.tag_size.data / 100.
		tag.display_name=form.display_name.data

		tag.detections = { cam: (num, pos * tag.tag_size / size, rot, v_pos * tag.tag_size / size, v_mar) for cam, (num, pos, rot, v_pos, v_mar, size) in data.items() }

		ThingDatabase(AprilTag).Add(tag)
		found_tags.pop((family, id))
		return modal_success(id=tag.ThingID)

	elif request.method == 'GET':

		form.display_name.data = '{}:{}'.format(family, id)
		form.tag_size.data = mode([v[5] for v in data.values()]) * 100.

	return render_template('_add_tag.html', form=form, tag_family=family, tag_id=id, cams=data)

@bp_aptg.route('/tags/found/<family>:<id>/clear')
def clear_found_tag(family, id):
	id = int(id)

	if (family, id) in found_tags:
		found_tags.pop((family, id))

	return modal_success()


@bp_aptg.route('/localizer', methods=['POST'])
def localize():

	data = request.get_json()
	
	objects = [
		SolverObject(
			ident=tuple(obj['ident']),
			previous_pose=np.array(obj['previous_pose']) if obj['previous_pose'] else None,
			static=obj['static'],
			rules=[parseRule(rule) for rule in obj['rules']]
		) for obj in data['objects']
	]
	
	detections = [
		Detection(
			tag=tuple(det['tag']),
			camera=tuple(det['camera']),
			transform=np.array(det['transform']) if det['transform'] else None,
			weight=det['weight']
		) for det in data['detections']
	]

	Solve(objects, detections)

	return jsonify()