

from utils.localization.objects import Detection, SolverObject
from utils.localization.graph import connected_components, from_detections, traverse


def Solve(objects: list[SolverObject], detections: list[Detection]):
    
    d_objects = { obj.ident: obj for obj in objects }

    graph = from_detections(detections)

    print(graph)

    connections = connected_components(graph)

    print(connections)

    results = traverse(graph, connections)

    print(results)
    print(graph)
