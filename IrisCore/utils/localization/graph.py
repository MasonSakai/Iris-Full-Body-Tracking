from collections import deque
from dataclasses import dataclass, field
import heapq
import numpy as np

from utils.localization.objects import Detection, Pose, SolverIdent, SolverObject
from utils.localization.placement_rules import PlacementRule

@dataclass(slots=True)
class GraphEdge:
    target: SolverIdent          # Neighbor node ID
    transform: np.ndarray        # This node -> target
    weight: float

@dataclass(slots=True)
class PoseEstimate:
    pose: np.ndarray
    weight: float
    path_cost: float

    from_node: SolverIdent
    to_node: SolverIdent

@dataclass(slots=True)
class GraphNode:
    ident: SolverIdent
    previous_pose: np.ndarray | None
    static: bool
    
    relative_pose: np.ndarray | None = field(default=None)
    world_pose: Pose = field(default=None)

    estimates: list[PoseEstimate] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)

@dataclass
class ConnectedComponent:
    id: int
    members: set[SolverIdent]
    root: SolverIdent = None
    
    has_detections: bool = False
    has_rules: bool = False

    relative_solved: bool = False
    

@dataclass
class TraverseResult:
    roots: set[SolverIdent] = field(default_factory=set)
    components: list[ConnectedComponent] = field(default_factory=list)
    path_costs: dict[SolverIdent, float] = field(default_factory=dict)

type Graph = dict[SolverIdent, GraphNode]

"""def from_detections(detections: list[Detection]) -> Graph:
    graph: dict[SolverIdent, GraphNode] = {}

    def get_node(ident: SolverIdent) -> GraphNode:
        if ident not in graph:
            graph[ident] = GraphNode(ident=ident)
        return graph[ident]

    for det in detections:
        cam = get_node(det.camera)
        tag = get_node(det.tag)

        cam.edges.append(
            GraphEdge(
                target=tag.ident,
                transform=det.transform,
                weight=det.weight,
            )
        )

        tag.edges.append(
            GraphEdge(
                target=cam.ident,
                transform=np.linalg.inv(det.transform),
                weight=det.weight,
            )
        )

    return graph"""

def build_scene_graph(objects: list[SolverObject], detections: list[Detection]) -> Graph:
    graph: Graph = {}

    # 1. Add all configured objects
    for obj in objects:
        graph[obj.ident] = GraphNode(
            ident=obj.ident,
            previous_pose=obj.previous_pose,
            static=obj.static
        )

    # 2. Add detection relationships
    for det in detections:
        cam = graph[det.camera]
        tag = graph[det.tag]

        cam.edges.append(
            GraphEdge(
                target=tag.ident,
                transform=det.transform,
                weight=det.weight,
            )
        )

        tag.edges.append(
            GraphEdge(
                target=cam.ident,
                transform=np.linalg.inv(det.transform),
                weight=det.weight,
            )
        )

    return graph

def connected_components(graph: Graph) -> list[ConnectedComponent]:
    objs = set(graph.keys())
    connections: list[ConnectedComponent] = []

    while len(objs):
        queue = deque([objs.pop()])
        conns = set()
        has_detections = False

        while queue:
            obj = queue.popleft()
            node = graph[obj]
            conns.add(obj)
            if len(node.edges):
                has_detections = True
            
            for edge in node.edges:
                if edge.target in objs:
                    objs.remove(edge.target)
                    queue.append(edge.target)

        connections.append(ConnectedComponent(
            id=len(connections),
            members=conns,
            has_detections=has_detections
        ))
    return connections

def annotate_components(
    components: list[ConnectedComponent],
    rules: list[PlacementRule],
):
    for component in components:
        component.has_rules = any(
            rule.target in component.members
            for rule in rules
        )

def choose_graph_root(graph: Graph, connected: ConnectedComponent) -> SolverIdent:
    def score(ident: SolverIdent):
        return sum(edge.weight for edge in graph[ident].edges)
    return max(connected.members, key=score)

def traverse(graph: Graph, connections: list[ConnectedComponent]):

    results = TraverseResult()

    for conn in connections:
        conn.root = choose_graph_root(graph, conn)
        best_cost = { conn.root: 0.0 }
        best_pose = { conn.root: np.eye(4) }
        pq = [(0.0, conn.root)]
        while pq:
            cost, current = heapq.heappop(pq)
            if cost > best_cost[current]:
                continue

            for edge in graph[current].edges:
                new_cost = cost + 1.0 / edge.weight
                new_pose = best_pose[current] @ edge.transform
                graph[edge.target].estimates.append(PoseEstimate(pose=new_pose, weight=edge.weight, path_cost=new_cost, to_node=edge.target, from_node=current))

                if (
                    edge.target not in best_cost
                    or
                    new_cost < best_cost[edge.target]
                ):
                    best_cost[edge.target] = new_cost
                    best_pose[edge.target] = new_pose
                    heapq.heappush(pq, (new_cost, edge.target))

        for ident, pose in best_pose.items():
            graph[ident].relative_pose = pose

        results.roots.add(conn.root)
        results.path_costs.update(best_cost)
        results.components.append(conn)

    return results

