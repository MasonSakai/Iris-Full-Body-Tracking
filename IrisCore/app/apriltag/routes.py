from flask import flash, redirect, render_template, request, url_for
import sqlalchemy as sqla

from app import db
from app.apriltag import apriltag_blueprint as bp_aptg, found_tags
from app.apriltag.models import AprilTag, AprilTagDetector
from app.apriltag.forms import DetectorForm

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
        detector.default_tag_size = form.default_tag_size.data / 100

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


@bp_aptg.route('/tags/<id>')
def view_tag(id):
    pass

@bp_aptg.route('/tags/found/<family>:<id>')
def view_found_tag(family, id):
    pass

@bp_aptg.route('/tags/found/clear')
def clear_found_tags():
    found_tags.clear()
    return redirect(url_for('apriltag.index'))

@bp_aptg.route('/tags/found/refresh')
def refresh_found_tags():
    #found_tags.clear()
    #send message to sources
    return redirect(url_for('apriltag.index'))