from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for, Response
from pupil_apriltags import Detector
from moms_apriltag import TagGenerator2
import numpy as np
import cv2 as cv

from app.main.modal import modal_redirect, modal_success
from utils.registry import ThingDatabase
from app.apriltag import found_tags, seen_tags
from app.apriltag.models import AprilTag, AprilTagDetector
from app.apriltag.forms import DetectorForm, CreateDetectorForm, FoundTagForm, EditTagForm
from app.cameras.models import Camera

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
        flash('Detector {} Created'.format(detector.display_name))
        return modal_success(id=detector.ThingID())
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
    form = DetectorForm()
    if form.validate_on_submit():
        detector.families = form.families.data
        detector.nthreads = form.nthreads.data
        detector.quad_decimate = form.quad_decimate.data
        detector.quad_sigma = form.quad_sigma.data
        detector.refine_edges = form.refine_edges.data
        detector.decode_sharpening = form.decode_sharpening.data
        detector.default_tag_size = form.default_tag_size.data / 100.

        flash('Detector {} Updated'.format(detector.display_name))
        return modal_success(id=detector.ThingID())
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
    flash('Detector {} Deleted!'.format(name))
    return redirect(url_for('apriltag.index'))


@bp_aptg.route('/tags/<id>', methods=['GET', 'POST'])
def view_tag(id):
    tag = ThingDatabase(AprilTag).GetByULID(id)
    form = EditTagForm()
    if form.validate_on_submit():

        if tag.id in seen_tags:
            scale = tag.tag_size * 100 / form.tag_size.data
            for src in seen_tags[tag.id]:
                seen_tags[tag.id][src].pose_t *= scale


        tag.tag_size = form.tag_size.data / 100
        tag.display_name = form.display_name.data
        tag.ensure_static = form.ensure_static.data

        flash('Tag {} Updated'.format(tag.display_name))
        return redirect(url_for('apriltag.index'))
    
    seen = seen_tags[tag.id] if tag.id in seen_tags else []
    if request.method == 'GET':

        form.tag_size.data = tag.tag_size * 100
        form.display_name.data = tag.display_name
        form.ensure_static.data = tag.ensure_static

        return render_template('_view_tag.html', form=form, tag=tag, seen_sources=seen)

    return index(popup_contents=render_template('_view_tag.html', form=form, tag=tag, seen_sources=seen))

@bp_aptg.route('/tags/<id>/delete')
def delete_tag(id):
    db = ThingDatabase(AprilTag)
    tag = db.GetByULID(id)
    name = tag.display_name
    db.Remove(tag)
    flash('Tag {} Deleted!'.format(name))
    return redirect(url_for('apriltag.index'))


@bp_aptg.route('/tags/found/<family>:<id>', methods=['GET', 'POST'])
def view_found_tag(family, id):
    id = int(id)

    res: Detector = None
    size = -1
    sources: dict[Camera, list[Detector]] = {}
    index = -1

    for (i, (i_res, i_size, i_sources)) in enumerate(found_tags):
        if i_res.tag_family.decode('utf-8') == family and i_res.tag_id == id:
            index = i
            res = i_res
            size = i_size
            sources = i_sources
            break

    r_sources = {}
    for source in sources:
        r_sources[source] = (sources[source], np.linalg.norm(sources[source].pose_t))

    form = FoundTagForm()
    if form.validate_on_submit():
        tag = AprilTag(tag_id = id, tag_family=family,
                       tag_size = form.tag_size.data / 100., display_name=form.display_name.data)
        ThingDatabase(AprilTag).Add(tag)
        found_tags.pop(index)
        #move tag to seen_tags
        flash('Tag {} ({}:{}) Added'.format(tag.display_name, tag.tag_family, tag.tag_id))
        return redirect(url_for('apriltag.index'))

    elif request.method == 'GET':

        form.display_name.data = '{}:{}'.format(family, id)
        form.tag_size.data = size * 100.
        return render_template('_add_tag.html', form=form, tag=res, sources=r_sources, size=size)

    return index(popup_contents=render_template('_add_tag.html', form=form, tag=res, sources=r_sources, size=size))

@bp_aptg.route('/tags/found/clear')
def clear_found_tags():
    found_tags.clear()
    return redirect(url_for('apriltag.index'))

@bp_aptg.route('/tags/found/refresh')
def refresh_found_tags():
    #found_tags.clear()
    #send message to sources
    return redirect(url_for('apriltag.index'))