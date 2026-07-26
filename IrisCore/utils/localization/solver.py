

from utils.localization.objects import Detection, SolverObject
from utils.localization.graph import connected_components, from_detections, traverse
from utils.localization.optimizer import optimize_relative
from utils.localization.placement_rules import PlacementRule


def Solve(objects: list[SolverObject], detections: list[Detection], rules: list[PlacementRule]):
    
    graph = from_detections(detections)
    #print(graph)

    connections = connected_components(graph)
    #print(connections)

    traversal = traverse(graph, connections)
    #print(traversal)

    optimization = optimize_relative(graph, detections, traversal)
    print(optimization)

