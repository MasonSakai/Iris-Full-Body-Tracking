import time
from scipy.spatial.transform import Rotation
from cv2.typing import MatLike
import numpy as np
import cv2 as cv
from pupil_apriltags import Detection

from app.apriltag.registry import FoundTagDetails, TagDetails, clear_tags_for, drawTag, set_found_tags
from app.apriltag.models import AprilTag, AprilTagDetector
from app.cameras.models import Camera, CameraReference
from utils.registry import ThingDatabase


def GetTags(cam: Camera, img: MatLike) -> tuple[list[tuple[float, Detection]], list[tuple[AprilTag, Detection]]]:
	(camera_matrix, dist_coeffs) = cam.get_camera_params()

	#camera_matrix = cam.rescale_camera_matrix(img.shape)
	img, rect = cam.undistortImage(img, camera_matrix, dist_coeffs)
		
	# scale = 3
	# if scale > 1 and img.shape == (480, 640):
	#     kern = np.array([[-1, -1, -1], [-1,  9, -1], [-1, -1, -1]])
	#     img = cv.resize(img, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC)
	#     img = cv.filter2D(img, -1, kern)
	#     camera_matrix = cam.rescale_camera_matrix(img.shape)

	image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

	all_dets: list[tuple[float, Detection]] = []
	all_tags: list[tuple[AprilTag, Detection]] = []
	#clear_tags_for(cam)

	for detector in ThingDatabase(AprilTagDetector).AllThingsListForReading():
		(dets, tags) = detector.detect(image, camera_matrix)
		all_dets.extend([(detector.default_tag_size, d) for d in dets])
		all_tags.extend(tags)
		for r in dets:
			drawTag(img, r, 1)
			#add_found_tag(cam, detector.default_tag_size, r)
		for (tag, r) in tags:
			drawTag(img, r, 1)
			#tag.detections[cam] = r
			
	cv.imwrite('images/{}.png'.format(cam.display_name), img)
	return all_dets, all_tags

def CalculateCameraPose(cam: Camera, img):
	tags = GetTags(cam, img)

	print('CalculateCameraPose', cam.display_name, len(tags), '(todo)')

def TagIdent(det: Detection):
	return (det.tag_family.decode(), det.tag_id)

def ScanTags(num_scans: int = 1, scan_sep: float = 0.25, ref_list: list[CameraReference] = []):
	
	if len(ref_list) == 0:
		ref_list = [ref for cam in ThingDatabase(Camera).AllThingsListForReading() if (ref := cam.ActiveReference())]

	if len(ref_list) == 0:
		return None, None

	images = { ref.parent: [] for ref in ref_list }

	
	for i in range(num_scans - 1, -1, -1):
		start_time = time.time()

		for ref in ref_list:
			if ref.parent in images:
				res, img = ref.RequestImage()
				if res:
					images[ref.parent].append(img)
				else:
					images.pop(ref.parent)

		dt = time.time() - start_time
		if i and (wait_time := scan_sep - dt) > 0:
			time.sleep(wait_time)

	cam_list = list(images.keys())
	
	ref_dets: dict[tuple[str, int], dict[Camera, FoundTagDetails]] = {}
	ref_tags: dict[AprilTag, dict[Camera, TagDetails]] = {}

	for cam in cam_list:

		clear_tags_for(cam)

		all_dets: dict[tuple[str, int], list[tuple[Detection, float]]] = {}
		all_tags: dict[AprilTag, list[Detection]] = {}

		for img in images[cam]:
			dets, tags = GetTags(cam, img)

			for (size, det) in dets:
				ident = TagIdent(det)
				if ident not in all_dets:
					all_dets[ident] = []
				all_dets[ident].append((det, size))

			for (tag, det) in tags:
				if tag not in all_tags:
					all_tags[tag] = []
				all_tags[tag].append(det)

		for ident, dets in all_dets.items():

			base_size = dets[0][1]

			margins: list[float] = [d.decision_margin for d, _ in dets]
			poses: list[np.array] = [d.pose_t * (s / base_size) for d, s in dets]
			q_rots: list[np.array] = [Rotation.from_matrix(d.pose_R).as_quat() for d, _ in dets]

			pos = np.average(poses, axis=0, weights=margins)
			q_rot = np.average(q_rots, axis=0, weights=margins)
			q_rot = q_rot / np.linalg.norm(q_rot)
			rot = Rotation.from_quat(q_rot).as_matrix()
			
			trans = np.eye(4)
			trans[:3, :3] = rot
			trans[:3, 3] = pos.flatten()

			v_pos = float(np.linalg.norm(np.std(poses, axis=0)))
			v_mar = float(np.average(margins))

			if ident not in ref_dets:
				ref_dets[ident] = {}
			ref_dets[ident][cam] = (len(dets), trans, v_pos, v_mar, base_size)

		for tag, dets in all_tags.items():

			margins: list[float] = [d.decision_margin for d in dets]
			poses: list[np.array] = [d.pose_t for d in dets]
			q_rots: list[np.array] = [Rotation.from_matrix(d.pose_R).as_quat() for d in dets]

			pos = np.average(poses, axis=0, weights=margins)
			q_rot = np.average(q_rots, axis=0, weights=margins)
			q_rot = q_rot / np.linalg.norm(q_rot)
			rot = Rotation.from_quat(q_rot).as_matrix()

			trans = np.eye(4)
			trans[:3, :3] = rot
			trans[:3, 3] = pos.flatten()

			v_pos = float(np.linalg.norm(np.std(poses, axis=0)))
			v_mar = float(np.average(margins))

			if tag not in ref_tags:
				ref_tags[tag] = {}
			ref_tags[tag][cam] = (len(dets), trans, v_pos, v_mar)

	set_found_tags(ref_dets)

	for tag, dets in ref_tags.items():
		tag.detections.update(dets)

	return ref_dets, ref_tags
				