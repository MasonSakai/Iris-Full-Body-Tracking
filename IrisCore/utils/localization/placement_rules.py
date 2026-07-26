
from dataclasses import dataclass
from enum import Enum

import numpy as np
from scipy.spatial.transform import Rotation

from utils.localization.objects import SolverIdent


def pose_error(actual: np.ndarray, target: np.ndarray) -> np.ndarray:
    """
    Returns the residual between two poses.

    Translation is meters.
    Rotation is axis-angle radians.
    """

    # Translation error
    t_error = actual[:3, 3] - target[:3, 3]

    # Rotation error
    r_actual = Rotation.from_matrix(actual[:3, :3])

    r_target = Rotation.from_matrix(target[:3, :3])

    r_error = (r_target.inv() * r_actual).as_rotvec()

    return np.concatenate([ t_error, r_error ])


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

    def weighted_residual(
        self,
        world_pose: np.ndarray,
    ) -> np.ndarray:
        residual = self.residual(world_pose)

        return (
            self.weight
            / np.sqrt(len(residual))
            * residual
        )

    def constrained_dofs(self) -> set[str]:
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
        return facing - self.direction

    def constrained_dofs(self) -> set[str]:
        return { 'pitch', 'yaw' }
    
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

        return np.asarray([ projection - self.distance ])

    def constrained_dofs(self) -> set[str]:
        return {f'translation_{ self.axis }'}
    
#@dataclass(init=False)
#class PoseRule_Previous(PlacementRule):
#
#    def residual(self, world_pose):
#        return pose_error(world_pose, self.previous_pose)


def parseRule(data: dict[str, any]) -> PlacementRule:
    match data['rule_type']:
        case 'facing':
            return PlacementRule_Facing(data)
        case 'offset':
            return PlacementRule_Offset(data)
        case _:
            raise ValueError('Invalid Placement Rule rule_type', data)