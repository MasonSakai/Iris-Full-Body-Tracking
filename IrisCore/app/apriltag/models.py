from __future__ import annotations
import numpy as np
from pupil_apriltags import Detection, Detector

from app.cameras.models import Camera
from utils.registry import IThing, ThingDatabase
from utils.scribe import IExposable, ILoadReferenceable, Scribe_Values

class AprilTag(IThing, IExposable, ILoadReferenceable, ThingName='AprilTag'):
	
	tag_id : int
	tag_family : str
	tag_size : float
	
	display_name : str
	ensure_static : bool

	transform: np.ndarray

	detections: dict[Camera, TagDetails]
	
	def __init__(self):
		super().__init__()
		self.tag_id = None
		self.tag_family = None
		self.tag_size = 0.1125
		self.display_name = None
		self.ensure_static = False
		self.transform = None
		self.detections = {}

	def __repr__(self):
		return '<AprilTag "{}">'.format(self.display_name)
	
	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'name', str)

		self.tag_id = Scribe_Values.Look(self.tag_id, 'TagID', int)
		self.tag_family = Scribe_Values.Look(self.tag_family, 'TagFamily', str)
		self.tag_size = Scribe_Values.Look(self.tag_size, 'TagSize', float)

		self.ensure_static = Scribe_Values.Look(self.ensure_static, 'EnsureStatic', bool, False)
		self.transform = Scribe_Values.Look(self.transform, 'transform', np.ndarray)

	def GetUniqueLoadID(self) -> str:
		return self.ThingID

	def set_transform(self, transform: np.ndarray):
		self.transform = transform

	def get_transform(self) -> np.ndarray:
		return self.transform
	

class AprilTagDetector(IThing, IExposable, ThingName='AprilTagDetector'):
	display_name : str
	families : str

	nthreads : int
	quad_decimate : float
	quad_sigma : float
	refine_edges : bool
	decode_sharpening : float
	default_tag_size : float
	
	_detector: Detector
	
	#functions
	def __init__(self):
		super().__init__()
		self.display_name = None
		self.families = None
		self.nthreads = 1
		self.quad_decimate = 2.0
		self.quad_sigma = 0.0
		self.refine_edges = True
		self.decode_sharpening = 0.25
		self.default_tag_size = 0.173
		self._detector = None

	def __repr__(self):
		return '<AprilTagDetector - {} "{}">'.format(self.display_name, self.families)

	def ExposeData(self):
		super().ExposeData()
		self.display_name = Scribe_Values.Look(self.display_name, 'name', str)
		self.families = Scribe_Values.Look(self.families, 'families', str)

		self.nthreads = Scribe_Values.Look(self.nthreads, 'nthreads', int, 1)
		self.quad_decimate = Scribe_Values.Look(self.quad_decimate, 'QuadDecimate', float, 2.0)
		self.quad_sigma = Scribe_Values.Look(self.quad_sigma, 'QuadSigma', float, 0.0)
		self.refine_edges = Scribe_Values.Look(self.refine_edges, 'RefineEdges', bool, True)
		self.decode_sharpening = Scribe_Values.Look(self.decode_sharpening, 'DecodeSharpening', float, 0.25)
		self.default_tag_size = Scribe_Values.Look(self.default_tag_size, 'DefaultTagSize', float, 0.175)

	def getDetector(self) -> Detector:
		if not self._detector:
			self._detector = Detector(
				families=self.families,
				nthreads=self.nthreads,
				quad_decimate=self.quad_decimate,
				quad_sigma=self.quad_sigma,
				refine_edges=self.refine_edges,
				decode_sharpening=self.decode_sharpening,
				debug=0
			)
		return self._detector

	def detect(self, image, camera_matrix) -> tuple[list[Detection], list[tuple[AprilTag, Detection]]]:
		params = [camera_matrix[0, 0], camera_matrix[1, 1], camera_matrix[0, 2], camera_matrix[1, 2]]

		res = self.getDetector().detect(image, True, params, self.default_tag_size)
		res: list[Detection]
		
		tags: list[tuple[Detection, AprilTag]] = []

		tag_list = ThingDatabase(AprilTag).AllThingsListForReading()
		for i in range(len(res)-1, -1, -1):
			tag = next((tag for tag in tag_list if (tag.tag_id == res[i].tag_id and tag.tag_family == res[i].tag_family.decode())), None)
			if tag:
				r = res.pop(i)
				r.pose_t *= tag.tag_size / self.default_tag_size
				tags.append((tag, r))

		return (res, tags)
	
	
from app.apriltag.registry import TagDetails