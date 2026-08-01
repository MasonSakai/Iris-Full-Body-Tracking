

import time
from utils.localization.objects import Detection, SolverObject
from utils.localization.graph import annotate_components, build_scene_graph, connected_components, traverse
from utils.localization.optimizer import optimize_relative, optimize_world
from utils.localization.placement_rules import PlacementRule


def Solve(objects: list[SolverObject], detections: list[Detection], rules: list[PlacementRule]):
    start_time = time.perf_counter()

    graph = build_scene_graph(objects, detections)
    components = connected_components(graph)
    annotate_components(components, rules)

    traversal = traverse(graph, components)

    relative = optimize_relative(graph, traversal, detections)
    world, poses = optimize_world(graph, traversal, rules)

    run_time = time.perf_counter() - start_time
    return graph, traversal, relative, world, poses, run_time


