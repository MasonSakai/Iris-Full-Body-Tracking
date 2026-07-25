
from dataclasses import dataclass

import numpy as np

from utils.localization.objects import SolverObject


@dataclass
class PlacementRule:
    object: SolverObject
    
    def residual(self, poses) -> np.ndarray:
        ...


def parseRule(data):
    return None