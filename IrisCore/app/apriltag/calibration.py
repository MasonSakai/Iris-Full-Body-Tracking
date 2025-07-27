from app import db
import sqlalchemy as sqla
import numpy as np
import cv2 as cv

from app.apriltag import add_found_tag, add_seen_tags, clear_tags_for, drawTag
from app.apriltag.models import AprilTagDetector
from app.main.models import CVUndistortableCamera


def GetTags(cam: CVUndistortableCamera, img):
    (_, dist_coeffs) = cam.get_camera_params()

    camera_matrix = cam.rescale_camera_matrix(img.shape)
    img = cam.undistortImage(img, camera_matrix, dist_coeffs)
        
    scale = 3
    if scale > 1 and img.shape == (480, 640):
        kern = np.array([[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]])
        img = cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)
        img = cv.filter2D(img, -1, kern)
            
    camera_matrix = cam.rescale_camera_matrix(img.shape)

    image = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

    all_tags = []
    clear_tags_for(cam)

    detectors = db.session.scalars(sqla.select(AprilTagDetector)).all()
    for detector in detectors:
        (res, tags) = detector.detect(img, camera_matrix)
        all_tags.extend(tags)
        for r in res:
            drawTag(image, r, scale)
            add_found_tag(cam, detector.default_tag_size, r)
        for (r, tag) in tags:
            drawTag(image, r, scale)
            add_seen_tags(tag, cam, r)

    cv.imwrite('images/{}-{}.png'.format(cam.id, scale), image)

    return all_tags

def CalculateCameraPose(cam: CVUndistortableCamera, img):
    tags = GetTags(cam, img)

    print('CalculateCameraPose', cam.display_name, len(tags), '(todo)')