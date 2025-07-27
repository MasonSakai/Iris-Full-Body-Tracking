from flask import flash, redirect, render_template, request, url_for, Response
from pupil_apriltags import Detector
import sqlalchemy as sqla
import numpy as np
import cv2 as cv

from app import db, socketio
from app.apriltag import apriltag_blueprint as bp_aptg, found_tags, seen_tags
from app.apriltag.models import AprilTag, AprilTagDetector
from app.apriltag.forms import DetectorForm, FoundTagForm, EditTagForm
from app.main.models import Camera

def update_from(src: Camera | AprilTag):
    
    ignore = []
    queue = [src]

    while len(queue) > 0:
        src = queue.pop(0)
        ignore.append(src)
        s_mat = src.get_transform()

        if isinstance(src, AprilTag):
            cams = seen_tags[src.id]
            for cam_id, det in cams.items():
                cam = db.session.get(Camera, cam_id)
                if cam in queue or cam in ignore:
                    continue
                queue.append(cam)
                
                mat = np.identity(4)
                mat[:3, :3] = det.pose_R
                mat[:3, 3] = np.array(det.pose_t).flatten()
                mat = np.linalg.inv(mat)

                cam.set_transform(np.linalg.matmul(
                    s_mat,
                    mat))
        else:
            for tag_id, cams in seen_tags.items():
                if src.id not in cams:
                    continue
                tag = db.session.get(AprilTag, tag_id)
                if tag in queue or tag in ignore:
                    continue
                queue.append(tag)

                det = seen_tags[tag_id][src.id]
                
                mat = np.identity(4)
                mat[:3, :3] = det.pose_R
                mat[:3, 3] = np.array(det.pose_t).flatten()

                tag.set_transform(np.linalg.matmul(s_mat, mat))


    db.session.commit()
    get_tags()
    get_found_tags()
    get_cams()
  
def update_global(mat: np.array):
    def update(src: AprilTag | Camera):
        trans = src.get_transform()
        if (trans.size > 0):
            src.set_transform(np.linalg.matmul(mat, trans))

    for src in db.session.scalars(sqla.select(AprilTag)).all(): update(src)
    for src in db.session.scalars(sqla.select(Camera)).all(): update(src)

    db.session.commit()
    get_tags()
    get_found_tags()
    get_cams()
        
def get_by_ident(ident) -> Camera | AprilTag:
    if isinstance(ident, str):
        [family, tag_id] = ident.split(':')
        tag_id = int(tag_id)
        return db.session.scalar(sqla.select(AprilTag).where(AprilTag.tag_family == family).where(AprilTag.tag_id == tag_id))
    else:
        return db.session.get(Camera, ident)

@socketio.on('set-position', namespace='/apriltag') #0 1.334 -1.60
def set_position(ident, pos, upd_glob):
    src = get_by_ident(ident)
    
    trans: np.array[float] = src.get_transform()
    if trans.size == 0:
        trans = np.identity(4)
        src.set_transform(trans)

    trans[:3, 3] = pos

    if (upd_glob):
        s_mat = np.linalg.inv(src.get_transform())
        trans = np.linalg.matmul(trans, s_mat)
        update_global(trans)
    else:
        src.set_transform(trans)
        update_from(src)
        
@socketio.on('set-position-axis', namespace='/apriltag')
def set_position(ident, axis_index, pos, upd_glob):
    if (pos == None): return
    src = get_by_ident(ident)
    
    trans: np.array[float] = src.get_transform()
    if trans.size == 0:
        trans = np.identity(4)
        src.set_transform(trans)

    trans[axis_index, 3] = pos

    if (upd_glob):
        s_mat = np.linalg.inv(src.get_transform())
        trans = np.linalg.matmul(trans, s_mat)
        update_global(trans)
    else:
        src.set_transform(trans)
        update_from(src)
    

@socketio.on('tags', namespace='/apriltag')
def get_tags(sid = None):
    db_tags = db.session.scalars(sqla.select(AprilTag)).all()

    tags = []
    for tag in db_tags:
        data = []
        if tag.id in seen_tags:
            for i in seen_tags[tag.id]:
                data.append(i)
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

    socketio.emit('tags', tags, namespace='/apriltag', to=(sid if sid != None else request.sid))
    
@socketio.on('found_tags', namespace='/apriltag')
def get_found_tags(sid = None):
    detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()
    sizes = {}
    for detector in detectors:
        for family in detector.families.split():
            sizes[family] = detector.default_tag_size

    tags = {}
    for (tag, sources) in found_tags:
        data = []
        for source in sources:
            data.append(source.id)
        tags['{}:{}'.format(tag.tag_family.decode('utf-8'), tag.tag_id)] = {
            'size': sizes[tag.tag_family.decode('utf-8')],
            'cams': data
        }
        
    socketio.emit('found_tags', tags, namespace='/apriltag', to=(sid if sid != None else request.sid))
    
@socketio.on('cams', namespace='/apriltag')
def get_cams(sid = None):
    db_cams = db.session.scalars(sqla.select(Camera)).all()

    cams = []
    for cam in db_cams:
        cams.append({
            'id': cam.id,
            'name': cam.display_name,
            'transform': cam.get_transform().tolist()
        })
        
    socketio.emit('cams', cams, namespace='/apriltag', to=(sid if sid != None else request.sid))