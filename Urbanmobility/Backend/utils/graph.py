from typing import Dict, List, Tuple, Any
from .priority_queue import MinHeapPriorityQueue


class Graph:
    """Weighted directed graph with Dijkstra shortest path.

    Nodes are arbitrary hashable values; edges stored as adjacency list:
    {u: [(v, weight), ...], ...}
    """

    def __init__(self) -> None:
        self.adj: Dict[Any, List[Tuple[Any, float]]] = {}

    def add_edge(self, u: Any, v: Any, w: float) -> None:
        self.adj.setdefault(u, []).append((v, w))
        self.adj.setdefault(v, [])  # ensure v appears in adjacency

    def dijkstra(self, source: Any) -> Dict[Any, float]:
        """Compute shortest path distances from source to all nodes."""
        dist: Dict[Any, float] = {node: float('inf') for node in self.adj}
        dist[source] = 0.0
        pq = MinHeapPriorityQueue[Any]()
        pq.push(0.0, source)

        while len(pq) > 0:
            d, u = pq.pop()
            if d > dist[u]:
                continue
            for v, w in self.adj.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    pq.push(nd, v)
        return dist


