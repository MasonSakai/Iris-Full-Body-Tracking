from dataclasses import dataclass
import cv2 as cv
import numpy as np

from app.cameras.models import Camera
from pupil_apriltags import Detection
from app.apriltag.models import AprilTag
from utils.registry import ThingDatabase


type TagDetails = tuple[int, np.ndarray, np.ndarray, float, float]
type FoundTagDetails = tuple[*TagDetails, float]
    
found_tags: dict[tuple[str, int], dict[Camera, FoundTagDetails]] = {}


def drawTag(image, r: Detection, scale):
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


def clear_tags_for(source: Camera):
    
    for tag in ThingDatabase(AprilTag).AllThingsListForReading():
        if source in tag.detections:
            tag.detections.pop(source)

    
    for i in range(len(found_tags) - 1, -1, -1):
        if source in found_tags[i][2]:
            found_tags[i][2].pop(source)
            if len(found_tags[i][2]) == 0:
                found_tags.pop(i)
