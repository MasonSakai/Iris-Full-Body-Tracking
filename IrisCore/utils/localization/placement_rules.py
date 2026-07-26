
from dataclasses import dataclass

import numpy as np

from utils.localization.objects import Pose


@dataclass
class PlacementRule:

    def residual(
        self,
        pose: Pose,
    ) -> np.ndarray:
        ...


def parseRule(data):
    return None