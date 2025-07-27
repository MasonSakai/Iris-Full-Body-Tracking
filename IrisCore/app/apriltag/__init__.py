from flask import Blueprint
import cv2 as cv
import numpy as np

apriltag_blueprint = Blueprint('apriltag', __name__, static_folder='static', template_folder='templates', url_prefix='/apriltag')

from app.main.models import Camera
from pupil_apriltags import Detection

found_tags: list[tuple[Detection, float, dict[Camera, Detection]]] = []
seen_tags: dict[int, dict[int, Detection]] = {}

from app.apriltag.models import AprilTag
from app.apriltag import routes, AprilTag3DSocket


def drawTag(image, r, scale):
    # extract the bounding box (x, y)-coordinates for the AprilTag
    # and convert each of the (x, y)-coordinate pairs to integers
    (ptA, ptB, ptC, ptD) = r.corners
    ptB = (int(ptB[0]), int(ptB[1]))
    ptC = (int(ptC[0]), int(ptC[1]))
    ptD = (int(ptD[0]), int(ptD[1]))
    ptA = (int(ptA[0]), int(ptA[1]))
    # draw the bounding box of the AprilTag detection
    cv.line(image, ptA, ptB, (0, 255, 0), 2)
    cv.line(image, ptB, ptC, (0, 255, 0), 2)
    cv.line(image, ptC, ptD, (0, 255, 0), 2)
    cv.line(image, ptD, ptA, (0, 255, 0), 2)
    # draw the center (x, y)-coordinates of the AprilTag
    (cX, cY) = (int(r.center[0]), int(r.center[1]))
    cv.circle(image, (cX, cY), 5, (0, 0, 255), -1)
    # draw the tag family on the image
    dist = np.linalg.norm(r.pose_t)
    cv.putText(image, '{}:{} @ {}'.format(r.tag_family.decode("utf-8"), r.tag_id, dist),
        (ptA[0], ptA[1] - 15), cv.FONT_HERSHEY_SIMPLEX, 0.25 * scale, (255, 0, 0), scale)

def add_found_tag(source: Camera, size: float, res: Detection):
    for i in range(len(found_tags)):
        det: Detection = found_tags[i][0]
        if det.tag_family == res.tag_family and det.tag_id == res.tag_id:
            found_tags[i][2][source] = res
            return

    found_tags.append((res, size, {source: res}))

def add_seen_tags(tag: AprilTag, source: Camera, res: Detection):
    if not tag.id in seen_tags:
        seen_tags[tag.id] = {}

    seen_tags[tag.id][source.id] = res