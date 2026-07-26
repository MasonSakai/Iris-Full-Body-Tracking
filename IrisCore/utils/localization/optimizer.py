from dataclasses import dataclass, field
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares, OptimizeResult

from utils.localization.graph import Graph, TraverseResult
from utils.localization.objects import Detection, SolverIdent
from utils.localization.placement_rules import PlacementRule

@dataclass
class OptimizationResult:
    success: bool

    function_evaluations: int

    initial_cost: float
    final_cost: float

    initial_residual_norm: float
    final_residual_norm: float

    scipy_result: OptimizeResult


@dataclass
class OptimizationState:
    x0: np.ndarray
    index: dict[SolverIdent, int]
    fixed: dict[SolverIdent, np.ndarray]

    def unpack_pose(
        self,
        x: np.ndarray,
        ident: SolverIdent
    ) -> np.ndarray:
        if ident in self.fixed:
            return self.fixed[ident]

        start = self.index[ident] * 6

        t = x[start:start+3]
        r = Rotation.from_rotvec(
            x[start+3:start+6]
        )

        T = np.eye(4)
        T[:3, :3] = r.as_matrix()
        T[:3, 3] = t

        return T

    def validate(self):
        assert len(self.x0) == len(self.index) * 6

        assert not (
            self.fixed.keys() &
            self.index.keys()
        )

def pack_variables(
    graph: Graph,
    traversal: TraverseResult,
):
    x = []
    index = {}
    fixed = {}

    variable_index = 0

    for ident, node in graph.items():

        if ident in traversal.roots:
            fixed[ident] = node.relative_pose
            continue

        index[ident] = variable_index

        x.extend(node.relative_pose[:3,3])
        x.extend(
            Rotation.from_matrix(
                node.relative_pose[:3,:3]
            ).as_rotvec()
        )

        variable_index += 1
        
    assert len(x) == len(index) * 6

    return OptimizationState(
        x0=np.asarray(x),
        index=index,
        fixed=fixed,
    )

def unpack_all(state: OptimizationState, x: np.ndarray):
    return {
        ident: state.unpack_pose(x, ident)
        for ident in state.fixed.keys() | state.index.keys()
    }


def optimize_relative(
    graph: Graph,
    detections: list[Detection],
    traversal: TraverseResult
) -> OptimizationResult:
    """
    Refine the propagated poses using nonlinear least-squares.

    The graph should already contain an initial estimate for every node
    from the traversal stage.
    """

    state = pack_variables(graph, traversal)
    state.validate()

    def residual(x: np.ndarray):
        poses = unpack_all(state, x)
        errors = []

        #
        # Detection constraints
        #

        for det in detections:
            cam = poses[det.camera]
            tag = poses[det.tag]

            predicted = np.linalg.inv(cam) @ tag

            #
            # Translation error
            #
            translation_error = (
                predicted[:3, 3]
                - det.transform[:3, 3]
            )

            #
            # Rotation error
            #
            delta = (
                Rotation.from_matrix(predicted[:3, :3])
                * Rotation.from_matrix(det.transform[:3, :3]).inv()
            )

            rotation_error = delta.as_rotvec()

            errors.extend(det.weight * translation_error)
            errors.extend(det.weight * rotation_error)

        return np.asarray(errors)

    initial_residual = residual(state.x0)
    initial_cost = 0.5 * np.dot(initial_residual, initial_residual)

    result: OptimizeResult = least_squares(
        residual,
        state.x0,
        method="trf",
    )

    #
    # Copy optimized poses back into graph
    #

    poses = unpack_all(state, result.x)

    for ident, pose in poses.items():
        graph[ident].relative_pose = pose

    return OptimizationResult(
        success=result.success,
        function_evaluations=result.nfev,

        initial_cost=initial_cost,
        final_cost=result.cost,

        initial_residual_norm=np.linalg.norm(initial_residual),
        final_residual_norm=np.linalg.norm(result.fun),

        scipy_result=result
    )
