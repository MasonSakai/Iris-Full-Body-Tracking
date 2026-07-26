from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.spatial.transform import Rotation


type SolverIdent = tuple[str, Literal["camera", "tag", "found", "pinned"]]

@dataclass(frozen=True)
class Pose:
    matrix: np.ndarray

    @property
    def rotation(self):
        return self.matrix[:3, :3]

    @property
    def translation(self):
        return self.matrix[:3, 3]

    @property
    def scipy_rotation(self):
        return Rotation.from_matrix(self.rotation)

    @staticmethod
    def from_parts(rotation: Rotation, translation: np.ndarray):
        m = np.eye(4)
        m[:3, :3] = rotation.as_matrix()
        m[:3, 3] = translation
        return Pose(m)


@dataclass
class SolverObject:
    ident: SolverIdent
    previous_pose: np.ndarray | None
    static: bool

@dataclass
class Detection:
    camera: SolverIdent
    tag: SolverIdent

    # Camera -> Tag
    transform: np.ndarray

    # Quality
    weight: float