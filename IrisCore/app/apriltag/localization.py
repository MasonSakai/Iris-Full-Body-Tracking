from cv2.typing import MatLike
import numpy as np
import cv2 as cv
from pupil_apriltags import Detection

from app.apriltag.registry import add_found_tag, clear_tags_for, drawTag
from app.apriltag.models import AprilTag, AprilTagDetector
from app.cameras.models import Camera
from utils.registry import ThingDatabase


def GetTags(cam: Camera, img: MatLike) -> tuple[list[Detection], list[tuple[Detection, AprilTag]]]:
    (_, dist_coeffs) = cam.get_camera_params()

    camera_matrix = cam.rescale_camera_matrix(img.shape)
    img, rect = cam.undistortImage(img, camera_matrix, dist_coeffs)
        
    # scale = 3
    # if scale > 1 and img.shape == (480, 640):
    #     kern = np.array([[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]])
    #     img = cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)
    #     img = cv.filter2D(img, -1, kern)
    #     camera_matrix = cam.rescale_camera_matrix(img.shape)

    image = cv.cvtColor(img, cv.COLOR_GRAY2BGR)

    all_dets = []
    all_tags = []
    clear_tags_for(cam)

    for detector in ThingDatabase(AprilTagDetector).AllThingsListForReading():
        (dets, tags) = detector.detect(img, camera_matrix)
        all_dets.extend(dets)
        all_tags.extend(tags)
        for r in dets:
            drawTag(image, r, 1)
            add_found_tag(cam, detector.default_tag_size, r)
        for (r, tag) in tags:
            drawTag(image, r, 1)
            tag.detections[cam] = r
            
    cv.imwrite('images/{}.png'.format(cam.display_name), image)
    return all_dets, all_tags

def CalculateCameraPose(cam: Camera, img):
    tags = GetTags(cam, img)

    print('CalculateCameraPose', cam.display_name, len(tags), '(todo)')