
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np

from utils.localization.objects import SolverIdent


@dataclass(init=False)
class PlacementRule:
    target: SolverIdent
    weight: float
    
    def __init__(self, data: dict[str, any]):
        super().__init__()
        self.target = tuple(data['target'])
        self.weight = float(data['weight'])

    def residual(
        self,
        world_pose: np.ndarray,
    ) -> np.ndarray:
        ...

        
@dataclass(init=False)
class PlacementRule_Facing(PlacementRule):
    direction: np.ndarray
    
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.direction = np.array(data['direction'], dtype=np.float64)
        self.direction /= np.linalg.norm(self.direction)

    def residual(self, world_pose):
        facing = world_pose[:3, :3] @ np.array([0., 0., 1.])
        facing /= np.linalg.norm(facing)
        return self.weight * (facing - self.direction)
    
class OffsetAxis(Enum):
    X = 'x'
    Y = 'y'
    Z = 'z'
    NORMAL = 'normal'

@dataclass(init=False)
class PlacementRule_Offset(PlacementRule):
    axis: OffsetAxis
    distance: float
    
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.axis = OffsetAxis(data['axis'])
        self.distance = np.array(data['distance'], dtype=np.float64)

    def residual(self, world_pose):

        match self.axis:
            case OffsetAxis.X:
                direction = np.array([1., 0., 0.])
            case OffsetAxis.Y:
                direction = np.array([0., 1., 0.])
            case OffsetAxis.Z:
                direction = np.array([0., 0., 1.])
            case OffsetAxis.NORMAL:
                direction = world_pose[:3, :3] @ np.array([0., 0., 1.])
                direction /= np.linalg.norm(direction)
        
        position = world_pose[:3, 3]
        projection: float = np.dot(position, direction)

        return np.asarray([
            self.weight * (projection - self.distance)
        ])


def parseRule(data: dict[str, any]) -> PlacementRule:
    match data['rule_type']:
        case 'facing':
            return PlacementRule_Facing(data)
        case 'offset':
            return PlacementRule_Offset(data)
        case _:
            raise ValueError('Invalid Placement Rule rule_type', data)