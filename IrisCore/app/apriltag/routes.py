from flask import flash, redirect, render_template, request, url_for
from pupil_apriltags import Detector
import sqlalchemy as sqla
import numpy as np

from app import db
from app.apriltag import apriltag_blueprint as bp_aptg, found_tags, seen_tags
from app.apriltag.models import AprilTag, AprilTagDetector
from app.apriltag.forms import DetectorForm, FoundTagForm, EditTagForm
from app.main.models import Camera

@bp_aptg.route('/')
def index(popup_contents=''):
    tags = db.session.scalars(sqla.select(AprilTag)).all()
    detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()

    return render_template('apriltag.html', title='April Tag Manager',
                           known_tags=tags, detectors=detectors, found_tags=found_tags,
                           popup_contents=popup_contents)

@bp_aptg.route('/detectors/<id>', methods=['GET', 'POST'])
def view_detector(id):
    detector = db.session.get(AprilTagDetector, id)
    form = DetectorForm()
    if form.validate_on_submit():
        detector.families = form.families.data
        detector.nthreads = form.nthreads.data
        detector.quad_decimate = form.quad_decimate.data
        detector.quad_sigma = form.quad_sigma.data
        detector.refine_edges = form.refine_edges.data
        detector.decode_sharpening = form.decode_sharpening.data
        detector.default_tag_size = form.default_tag_size.data / 100.

        db.session.commit()
        flash('Detector {} Updated'.format(detector.id))
        return redirect(url_for('apriltag.index'))
    elif request.method == 'GET':
        form.families.data = detector.families
        form.nthreads.data = detector.nthreads
        form.quad_decimate.data = detector.quad_decimate
        form.quad_sigma.data = detector.quad_sigma
        form.refine_edges.data = detector.refine_edges
        form.decode_sharpening.data = detector.decode_sharpening
        form.default_tag_size.data = detector.default_tag_size * 100
        return render_template('_view_detector.html', form=form, detector=detector)

    return index(popup_contents=render_template('_view_detector.html', form=form, detector=detector))

@bp_aptg.route('/detectors/<id>/delete', )
def delete_detector(id):
    detector = db.session.get(AprilTagDetector, id)
    db.session.delete(detector)
    db.session.commit()
    flash('Detector {} Deleted!'.format(id))
    return redirect(url_for('apriltag.index'))


@bp_aptg.route('/tags/<id>', methods=['GET', 'POST'])
def view_tag(id):
    tag: AprilTag = db.session.get(AprilTag, id)
    form = EditTagForm()
    if form.validate_on_submit():

        if tag.id in seen_tags:
            scale = tag.tag_size * 100 / form.tag_size.data



        tag.tag_size = form.tag_size.data / 100
        tag.display_name = form.display_name.data

        db.session.commit()
        flash('Tag {} Updated'.format(tag.display_name))
        return redirect(url_for('apriltag.index'))
    
    seen = seen_tags[tag.id] if tag.id in seen_tags else []
    if request.method == 'GET':

        form.tag_size.data = tag.tag_size * 100
        form.display_name.data = tag.display_name

        return render_template('_view_tag.html', form=form, tag=tag, seen_sources=seen)

    return index(popup_contents=render_template('_view_tag.html', form=form, tag=tag, seen_sources=seen))

@bp_aptg.route('/tags/<id>/delete')
def delete_tag(id):
    tag = db.session.get(AprilTag, id)
    name = tag.display_name
    db.session.delete(tag)
    db.session.commit()
    flash('Tag {} Deleted!'.format(name))
    return redirect(url_for('apriltag.index'))

@bp_aptg.route('/tags/found/<family>:<id>', methods=['GET', 'POST'])
def view_found_tag(family, id):
    id = int(id)

    res: Detector = None
    sources: dict[Camera, list[Detector]] = {}
    index = -1

    for (i, (i_res, i_sources)) in enumerate(found_tags):
        if i_res.tag_family.decode('utf-8') == family and i_res.tag_id == id:
            index = i
            res = i_res
            sources = i_sources
            break

    r_sources = {}
    for source in sources:
        r_sources[source] = (sources[source], np.linalg.norm(sources[source].pose_t))
        
    detector = db.session.scalars(sqla.select(AprilTagDetector).where(AprilTagDetector.families.contains(family))).first()

    form = FoundTagForm()
    if form.validate_on_submit():
        tag = AprilTag(tag_id = id, tag_family=family,
                       tag_size = form.tag_size.data / 100., display_name=form.display_name.data)
        db.session.add(tag)
        db.session.commit()
        found_tags.pop(index)
        flash('Tag {} ({}:{}) Added'.format(tag.display_name, tag.tag_family, tag.tag_id))
        return redirect(url_for('apriltag.index'))

    elif request.method == 'GET':

        form.display_name.data = '{}:{}'.format(family, id)
        form.tag_size.data = detector.default_tag_size * 100.
        return render_template('_add_tag.html', form=form, tag=res, sources=r_sources, detector=detector)

    return index(popup_contents=render_template('_add_tag.html', form=form, tag=res, sources=r_sources, detector=detector))

@bp_aptg.route('/tags/found/clear')
def clear_found_tags():
    found_tags.clear()
    return redirect(url_for('apriltag.index'))

@bp_aptg.route('/tags/found/refresh')
def refresh_found_tags():
    #found_tags.clear()
    #send message to sources
    return redirect(url_for('apriltag.index'))