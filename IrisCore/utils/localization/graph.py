from collections import deque
from dataclasses import dataclass, field
import heapq
import numpy as np
from scipy.spatial.transform import Rotation

from utils.localization.objects import Detection, Pose, SolverIdent, SolverObject

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
	
	relative_pose: np.ndarray | None = field(default=None)
	world_pose: Pose = field(default=None)

	estimates: list[PoseEstimate] = field(default_factory=list)
	edges: list[GraphEdge] = field(default_factory=list)

@dataclass
class ConnectedComponent:
	id: int
	root: SolverIdent
	members: set[SolverIdent]

@dataclass
class TraverseResult:
	roots: set[SolverIdent] = field(default_factory=set)
	components: list[ConnectedComponent] = field(default_factory=list)
	path_costs: dict[SolverIdent, float] = field(default_factory=dict)

type Graph = dict[SolverIdent, GraphNode]

def from_detections(detections: list[Detection]) -> Graph:
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

	return graph

def connected_components(graph: Graph) -> list[set[SolverIdent]]:
	objs = set(graph.keys())
	connections: list[set[SolverIdent]] = []

	while len(objs):
		queue = deque([objs.pop()])
		conns = set()

		while queue:
			obj = queue.popleft()
			node = graph[obj]
			conns.add(obj)
			
			for edge in node.edges:
				if edge.target in objs:
					objs.remove(edge.target)
					queue.append(edge.target)

		connections.append(conns)
	return connections

def choose_graph_root(graph: Graph, connected: set[SolverIdent]) -> SolverIdent:
	def score(ident: SolverIdent):
		return sum(edge.weight for edge in graph[ident].edges)
	return max(connected, key=score)

def choose_world_anchor(graph: Graph, d_objects: dict[SolverIdent, SolverObject], connected: set[SolverIdent]) -> SolverIdent:
	def score(ident: SolverIdent):
		g_obj = graph[ident]
		d_obj = d_objects[ident]
		return (
			1000 * (len(d_obj.rules) > 0) +
			100 * d_obj.static +
			10 * (d_obj.previous_pose != None) +
			sum(map(lambda e: e.weight, g_obj.edges))
		)

	return max(connected, key=score)

def traverse(graph: Graph, connections: list[set[SolverIdent]]):

	results = TraverseResult()

	for conn in connections:
		root = choose_graph_root(graph, conn)
		best_cost = { root: 0.0 }
		best_pose = { root: np.eye(4) }
		pq = [(0.0, root)]
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

		results.roots.add(root)
		results.path_costs.update(best_cost)
		results.components.append(ConnectedComponent(id=len(results.components), root=root, members=set(best_pose.keys())))

	return results

