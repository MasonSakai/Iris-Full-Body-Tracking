

from utils.localization.objects import Detection, SolverObject
from utils.localization.graph import annotate_components, build_scene_graph, connected_components, traverse
from utils.localization.optimizer import optimize_relative, optimize_world
from utils.localization.placement_rules import PlacementRule


def Solve(objects: list[SolverObject], detections: list[Detection], rules: list[PlacementRule]):
    
    graph = build_scene_graph(objects, detections)
    #print(graph)

    connections = connected_components(graph)
    annotate_components(connections, rules)
    #print(connections)

    traversal = traverse(graph, connections)
    #print(traversal)

    relative = optimize_relative(graph, traversal, detections)
    print(relative)

    world, poses = optimize_world(graph, traversal, rules)
    print(world)
    print(poses)

