from dataclasses import dataclass, field
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares, OptimizeResult

from utils.localization.graph import Graph
from utils.localization.objects import Detection, SolverIdent
from utils.localization.placement_rules import PlacementRule


def pack_variables(graph: Graph, roots: set[SolverIdent]):
    x = []
    index: dict[SolverIdent, int] = {}

    for i, (ident, node) in enumerate(graph.items()):
        
        if ident in roots:
            continue

        pose = node.relative_pose

        t = pose[:3, 3]
        r = Rotation.from_matrix(pose[:3, :3]).as_rotvec()

        index[ident] = i

        x.extend(t)
        x.extend(r)

    return np.asarray(x), index

def unpack_pose(graph: Graph, x: np.ndarray, index: dict[SolverIdent, int], ident: SolverIdent):
    if ident not in index:
        return graph[ident].relative_pose

    start = index[ident] * 6

    t = x[start:start+3]

    r = Rotation.from_rotvec(
        x[start+3:start+6]
    )

    T = np.eye(4)
    T[:3, :3] = r.as_matrix()
    T[:3, 3] = t

    return T


@dataclass
class OptimizationResult:
    success: bool

    function_evaluations: int

    initial_cost: float
    final_cost: float

    initial_residual_norm: float
    final_residual_norm: float

    scipy_result: OptimizeResult


def optimize_relative(
    graph: Graph,
    detections: list[Detection],
    roots: set[SolverIdent],
) -> OptimizationResult:
    """
    Refine the propagated poses using nonlinear least-squares.

    The graph should already contain an initial estimate for every node
    from the traversal stage.
    """

    x0, index = pack_variables(graph, roots)

    def unpack_all(x: np.ndarray):
        return {
            ident: unpack_pose(graph, x, index, ident)
            for ident in index
        }

    def residual(x: np.ndarray):
        poses = unpack_all(x)
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

    initial_residual = residual(x0)
    initial_cost = 0.5 * np.dot(initial_residual, initial_residual)

    result: OptimizeResult = least_squares(
        residual,
        x0,
        method="trf",
    )

    #
    # Copy optimized poses back into graph
    #

    poses = unpack_all(result.x)

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