from dataclasses import dataclass
from typing import Literal
import numpy as np
from scipy.spatial.transform import Rotation


from utils.localization.graph import Graph, TraverseResult, annotate_components, build_scene_graph, connected_components, traverse
from utils.localization.objects import Detection, SolverIdent, SolverObject
from utils.localization.optimizer import optimize_world
from utils.localization.placement_rules import PlacementRule, PlacementRule_Facing, PlacementRule_Offset
from utils.localization.solver import optimize_relative

class TestScene:
    def __init__(self):
        self._objects: dict[SolverIdent, tuple[np.ndarray, bool]] = {}
        self._detections: list[Detection] = []
        self._rules: list[PlacementRule] = []

    # ------------------------------------------------------------------
    # Transform helper
    # ------------------------------------------------------------------

    @staticmethod
    def T(pos=(0, 0, 0), rot=(0, 0, 0)):
        tf = np.eye(4)
        tf[:3, :3] = Rotation.from_euler(
            "xyz",
            rot,
            degrees=True,
        ).as_matrix()
        tf[:3, 3] = pos
        return tf

    # ------------------------------------------------------------------
    # Object creation
    # ------------------------------------------------------------------

    def add(
        self,
        ident: SolverIdent,
        pose: np.ndarray,
        *,
        static=False,
    ):
        self._objects[ident] = (pose, static)
        return ident

    def camera(self, name, pose=None):
        if pose is None:
            pose = self.T()
        return self.add((name, "camera"), pose)

    def tag(self, name, pose=None, *, static=False):
        if pose is None:
            pose = self.T()
        return self.add((name, "tag"), pose, static=static)

    def found(self, name, pose=None):
        if pose is None:
            pose = self.T()
        return self.add((name, "found"), pose)

    def pinned(self, name, pose=None):
        if pose is None:
            pose = self.T()
        return self.add((name, "pinned"), pose)

    def facing(self, target: SolverIdent, direction: list[float], weight: float = 1):
        self._rules.append(PlacementRule_Facing({
            'target': target,
            'weight': weight,
            'direction': direction,
        }))

    def offset(self, target: SolverIdent, axis: Literal['x'] | Literal['y'] | Literal['z'] | Literal['normal'], distance: float, weight: float = 1):
        self._rules.append(PlacementRule_Offset({
            'weight': weight,
            'target': target,
            'axis': axis,
            'distance': distance
        }))

    # ------------------------------------------------------------------
    # Observation generation
    # ------------------------------------------------------------------

    def observe(
        self,
        camera: SolverIdent,
        tag: SolverIdent,
        *,
        weight=1.0,
    ):
        cam_pose, _ = self._objects[camera]
        tag_pose, _ = self._objects[tag]

        self._detections.append(
            Detection(
                camera=camera,
                tag=tag,
                transform=np.linalg.inv(cam_pose) @ tag_pose,
                weight=weight,
            )
        )

    def observe_all(self, camera: SolverIdent, *tags: SolverIdent, weight=1.0):
        for tag in tags:
            self.observe(camera, tag, weight=weight)

    # ------------------------------------------------------------------
    # Build solver inputs
    # ------------------------------------------------------------------

    def build(self, *, use_previous_poses=False):
        objects = [
            SolverObject(
                ident=ident,
                previous_pose=pose.copy() if use_previous_poses else None,
                static=static,
            )
            for ident, (pose, static) in self._objects.items()
        ]
        return objects, self._detections

    def solve_graph(self):
        objects, detections = self.build()

        graph = build_scene_graph(objects, detections)

        result = traverse(
            graph,
            connected_components(graph),
        )

        return graph, result

    def optimize_relative(self, graph: Graph, traversal: TraverseResult):
        result = optimize_relative(
            graph,
            traversal,
            self._detections
        )

        return graph, result

    def solve_scene(self):
        objects, detections = self.build()
        graph = build_scene_graph(objects, detections)

        components = connected_components(graph)
        annotate_components(components, self._rules)

        traversal = traverse(
            graph,
            components,
        )

        relative = optimize_relative(
            graph,
            traversal,
            detections,
        )

        world, poses = optimize_world(
            graph,
            traversal,
            self._rules,
        )

        return graph, relative, world, poses

    # ------------------------------------------------------------------
    # Expected poses
    # ------------------------------------------------------------------

    @property
    def poses(self):
        return {
            ident: pose.copy()
            for ident, (pose, _) in self._objects.items()
        }
