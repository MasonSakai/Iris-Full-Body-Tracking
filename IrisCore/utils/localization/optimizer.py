from dataclasses import dataclass, field
import numpy as np
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares, OptimizeResult

from utils.localization.graph import ConnectedComponent, Graph, TraverseResult
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
    component: ConnectedComponent,
):
    x = []
    index = {}
    fixed = {}

    variable_index = 0

    for ident in component.members:
        node = graph[ident]

        if ident == component.root:
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

def optimize_relative_component(graph: Graph, component: ConnectedComponent, detections: list[Detection]):
    state = pack_variables(graph, component)
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

    component.relative_solved = True

    return OptimizationResult(
        success=result.success,
        function_evaluations=result.nfev,

        initial_cost=initial_cost,
        final_cost=result.cost,

        initial_residual_norm=np.linalg.norm(initial_residual),
        final_residual_norm=np.linalg.norm(result.fun),

        scipy_result=result
    )

def optimize_relative(
    graph: Graph,
    traversal: TraverseResult,
    detections: list[Detection]
) -> dict[int, OptimizationResult]:
    """
    Refine the propagated poses using nonlinear least-squares.

    The graph should already contain an initial estimate for every node
    from the traversal stage.
    """

    results = {}

    for component in traversal.components:

        if not component.has_detections:
            continue

        results[component.id] = optimize_relative_component(graph, component, detections)

    return results


@dataclass
class WorldOptimizationState:
    x0: np.ndarray

    # Component index -> optimizer variable index
    index: dict[int, int]

    # Fixed relative poses
    relative_poses: dict[SolverIdent, np.ndarray]

def pack_world_variables(
    graph: Graph,
    traversal: TraverseResult,
) -> WorldOptimizationState:

    x = []
    index = {}

    relative = {
        ident: node.relative_pose
        for ident, node in graph.items()
    }

    for i, component in enumerate(
        traversal.components
    ):
        index[i] = i

        x.extend([
            0, 0, 0,   # translation
            0, 0, 0,   # rotation
        ])

    return WorldOptimizationState(
        x0=np.asarray(x),
        index=index,
        relative_poses=relative,
    )

def unpack_component(
    x: np.ndarray,
    index: int,
    component_id: int,
):
    start = index[component_id] * 6

    t = x[start:start+3]
    r = Rotation.from_rotvec(
        x[start+3:start+6]
    )

    T = np.eye(4)
    T[:3,:3] = r.as_matrix()
    T[:3,3] = t

    return T

def get_world_poses(
    state: WorldOptimizationState,
    x: np.ndarray,
    traversal: TraverseResult,
):
    poses: dict[SolverIdent, np.ndarray] = {}

    for component_id, component in enumerate(traversal.components):
        C = unpack_component(x, state.index, component_id)
        for ident in component.members:
            poses[ident] = C @ state.relative_poses[ident]

    return poses

def optimize_world(
    graph: Graph,
    traversal: TraverseResult,
    rules: list[PlacementRule]
):

    state = pack_world_variables(graph, traversal)

    def residual(x: np.ndarray):
        world_poses = get_world_poses(state, x, traversal)

        errors = []

        for rule in rules:
            errors.extend(
                rule.residual(
                    world_poses[rule.target]
                )
            )

        return np.asarray(errors)
    
    initial_residual = residual(state.x0)
    initial_cost = 0.5 * np.dot(initial_residual, initial_residual)

    result = least_squares(
        residual,
        state.x0
    )

    poses = get_world_poses(
        state,
        result.x,
        traversal,
    )

    return OptimizationResult(
        success=result.success,
        function_evaluations=result.nfev,

        initial_cost=initial_cost,
        final_cost=result.cost,

        initial_residual_norm=np.linalg.norm(initial_residual),
        final_residual_norm=np.linalg.norm(result.fun),

        scipy_result=result
    ), poses