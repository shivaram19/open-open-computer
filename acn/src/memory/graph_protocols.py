# src/memory/graph_protocols.py
"""
Graph Protocols — Interface Segregation for PTKG.

Splits the monolithic PTKG interface (20+ public methods) into
six role-specific protocols. Clients depend only on the methods
they actually use.

Research basis:
- Martin (1996): ISP — "Clients should not be forced to depend on
  interfaces they do not use."
- Xerox story: The Job class caused 1-hour redeploy cycles because
  every client depended on every method.
- Martin (2017): Dependency Rule — inner circles declare abstractions.

[CITATION: PTKG-GRAPH]
[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Protocol, Dict, List, Optional, Any
from abc import abstractmethod

from shared.utils.citations import cite


# ── Core Storage Protocol ──────────────────────────────────────────────

class GraphStorage(Protocol):
    """Core node/edge CRUD — needed by all graph clients."""

    def add_node(self, node_id: str, node_type: str, **kwargs) -> None: ...
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]: ...
    def add_edge(
        self, source: str, target: str, edge_type: str, **kwargs
    ) -> None: ...
    def get_edge(self, edge_id: str) -> Optional[Dict[str, Any]]: ...
    def has_node(self, node_id: str) -> bool: ...
    def has_edge(self, edge_id: str) -> bool: ...


# ── Traversal Protocol ─────────────────────────────────────────────────

class GraphTraversal(Protocol):
    """Graph traversal — needed by reasoning clients."""

    def bfs_traversal(
        self, start: str, max_depth: int = 3
    ) -> List[str]: ...
    def get_neighbors(self, node_id: str) -> List[str]: ...
    def get_incoming_edges(self, node_id: str) -> List[Dict[str, Any]]: ...
    def get_outgoing_edges(self, node_id: str) -> List[Dict[str, Any]]: ...


# ── Temporal Protocol ──────────────────────────────────────────────────

class TemporalGraph(Protocol):
    """Time-aware queries — needed by temporal clients."""

    def start_period(self, period_id: str, timestamp: float) -> None: ...
    def end_period(self, period_id: str, timestamp: float) -> None: ...
    def get_nodes_valid_at(self, timestamp: float) -> List[Dict[str, Any]]: ...
    def get_edges_in_period(self, period_id: str) -> List[Dict[str, Any]]: ...


# ── Causal Protocol ────────────────────────────────────────────────────

class CausalGraph(Protocol):
    """Causal path finding — needed by causal chain tracker."""

    def find_causal_paths(
        self, source: str, target: str, max_depth: int = 3
    ) -> List[List[str]]: ...


# ── Serialization Protocol ─────────────────────────────────────────────

class GraphSerializer(Protocol):
    """Serialization — needed by persistence clients."""

    def to_dict(self) -> Dict[str, Any]: ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphSerializer": ...


# ── Statistics Protocol ────────────────────────────────────────────────

class GraphStatistics(Protocol):
    """Metrics — needed by diagnostics."""

    def get_graph_stats(self) -> Dict[str, Any]: ...
