from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

import numpy as np


type SolverIdent = tuple[str, Literal["camera", "tag", "found", "pinned"]]

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
