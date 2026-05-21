# src/memory/ptkg.py
"""
Periodic Temporal Knowledge Graph (PTKG) for Cross-Session Agent Memory.

A PTKG stores facts as quintuples (entity, relation, entity, timestamp, confidence)
with explicit temporal validity windows and periodic consolidation. This enables:
- Temporal reasoning: "What did agent X believe at time T?"
- Causal tracing: "Which argument caused proposal Y to be revised?"
- Reputation evolution: "How has agent Z's reliability changed over sessions?"
- Multi-hop retrieval: "Find all agents who supported proposals derived from concept C"

Design inspired by:
- ViG-RAG2026: Probabilistic temporal knowledge graph with plausibility scores
- Zep2025: Temporal knowledge graph with fact validity periods
- TSM2026: Episodic-to-durative memory consolidation
- KGoT2025: Dynamic knowledge graph evolving with task state
- LiCoMemory2025: Hierarchical graph with temporal and hierarchy-aware search

Principle: Memory is not a database. It is a time-evolving graph of causal relationships.

[CITATION: ViG-RAG2026]
[CITATION: Zep2025]
[CITATION: TSM2026]
[CITATION: KGoT2025]
[CITATION: LiCoMemory2025]
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="PTKG-NODE-TYPE",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Node Type Enumeration",
    rationale="Typed nodes enable domain-specific retrieval and semantic indexing",
    confidence="CERTAIN",
)
class NodeType(Enum):
    """[CITATION: PTKG-CORE] Types of entities in the PTKG."""
    AGENT = "agent"
    TASK = "task"
    PROPOSAL = "proposal"
    ARGUMENT = "argument"
    CONCEPT = "concept"
    EVENT = "event"
    REPUTATION_SNAPSHOT = "reputation_snapshot"
    DURATIVE_SUMMARY = "durative_summary"


@cite(
    key="PTKG-EDGE-TYPE",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Edge Type Enumeration",
    rationale="Typed relations enable causal and semantic graph traversal",
    confidence="CERTAIN",
)
class EdgeType(Enum):
    """[CITATION: PTKG-CORE] Types of relations in the PTKG."""
    PROPOSED = "proposed"
    CRITIQUED = "critiqued"
    SUPPORTED = "supported"
    CAUSED = "caused"
    DERIVED_FROM = "derived_from"
    TEMPORAL_NEXT = "temporal_next"
    HAS_REPUTATION = "has_reputation"
    PARTICIPATED_IN = "participated_in"
    CONSOLIDATED_INTO = "consolidated_into"
    BELONGS_TO_PERIOD = "belongs_to_period"
    ADDRESSED = "addressed"


@cite(
    key="PTKG-NODE",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Node Dataclass",
    rationale="Nodes carry temporal validity, confidence, and period metadata for time-aware retrieval",
    confidence="CERTAIN",
)
@dataclass
class PTKGNode:
    """
    [CITATION: PTKG-CORE] A node in the Periodic Temporal Knowledge Graph.
    
    Temporal fields:
    - created_at: when the node was first created
    - valid_from: when the fact described by this node became true
    - valid_until: when the fact ceased to be true (None = still valid)
    - period_id: which time period this node belongs to
    """
    node_id: str
    node_type: NodeType
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    valid_from: Optional[float] = None
    valid_until: Optional[float] = None
    confidence: float = 1.0
    period_id: Optional[str] = None
    source_agent_id: Optional[str] = None

    def __post_init__(self):
        """[CITATION: PTKG-CORE] Initialize default valid_from."""
        if self.valid_from is None:
            self.valid_from = self.created_at

    def is_valid_at(self, timestamp: float) -> bool:
        """[CITATION: PTKG-CORE] Check if this node represents a valid fact at the given time."""
        if timestamp < self.valid_from:
            return False
        if self.valid_until is not None and timestamp > self.valid_until:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """[CITATION: PTKG-CORE] Serialize node to dictionary."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "confidence": self.confidence,
            "period_id": self.period_id,
            "source_agent_id": self.source_agent_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PTKGNode":
        """[CITATION: PTKG-CORE] Deserialize node from dictionary."""
        return cls(
            node_id=data["node_id"],
            node_type=NodeType(data["node_type"]),
            label=data["label"],
            properties=data.get("properties", {}),
            created_at=data["created_at"],
            valid_from=data.get("valid_from"),
            valid_until=data.get("valid_until"),
            confidence=data.get("confidence", 1.0),
            period_id=data.get("period_id"),
            source_agent_id=data.get("source_agent_id"),
        )


@cite(
    key="PTKG-EDGE",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Edge Dataclass",
    rationale="Edges carry causal weight and temporal metadata for weighted traversal",
    confidence="CERTAIN",
)
@dataclass
class PTKGEdge:
    """
    [CITATION: PTKG-CORE] A directed, typed edge in the PTKG.
    
    The causal_weight field enables probabilistic causal reasoning:
    - 1.0 = deterministic cause
    - 0.5 = contributory factor
    - 0.0 = no causal influence (purely correlational)
    """
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0
    causal_weight: float = 0.5
    period_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """[CITATION: PTKG-CORE] Serialize edge to dictionary."""
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "causal_weight": self.causal_weight,
            "period_id": self.period_id,
            "properties": self.properties,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PTKGEdge":
        """[CITATION: PTKG-CORE] Deserialize edge from dictionary."""
        return cls(
            edge_id=data["edge_id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=EdgeType(data["edge_type"]),
            timestamp=data["timestamp"],
            confidence=data.get("confidence", 1.0),
            causal_weight=data.get("causal_weight", 0.5),
            period_id=data.get("period_id"),
            properties=data.get("properties", {}),
        )


@cite(
    key="PTKG-PERIOD",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Period Dataclass",
    rationale="Periods group nodes/edges into discrete time windows that can be consolidated",
    confidence="CERTAIN",
)
@dataclass
class PTKGPeriod:
    """
    [CITATION: PTKG-CORE] A discrete time period in the PTKG.
    
    Periods enable the "periodic" aspect of PTKG:
    - Each session/deliberation creates a new period
    - Old periods are periodically consolidated into durative summaries
    - Queries can target specific periods or span across them
    """
    period_id: str
    start_time: float
    end_time: Optional[float] = None
    label: str = ""
    description: str = ""
    consolidated_into: Optional[str] = None
    node_count: int = 0
    edge_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """[CITATION: PTKG-CORE] Serialize period to dictionary."""
        return {
            "period_id": self.period_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "label": self.label,
            "description": self.description,
            "consolidated_into": self.consolidated_into,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PTKGPeriod":
        """[CITATION: PTKG-CORE] Deserialize period from dictionary."""
        return cls(
            period_id=data["period_id"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            label=data.get("label", ""),
            description=data.get("description", ""),
            consolidated_into=data.get("consolidated_into"),
            node_count=data.get("node_count", 0),
            edge_count=data.get("edge_count", 0),
        )


@cite(
    key="PTKG",
    paper="Periodic Temporal Knowledge Graph for Agent Memory",
    venue="ACN Architecture Document",
    section="Core Graph Class",
    rationale="In-memory graph with temporal indices enables fast time-aware multi-hop queries",
    confidence="CERTAIN",
)
class PTKG:
    """
    [CITATION: PTKG-CORE] The Periodic Temporal Knowledge Graph.
    
    Stores entities and relations with explicit temporal validity,
    supports multi-hop traversal with temporal filtering,
    and provides periodic consolidation of old periods into durative summaries.
    
    Architecture:
    - nodes: Dict[node_id -> PTKGNode]
    - edges: Dict[edge_id -> PTKGEdge]
    - periods: Dict[period_id -> PTKGPeriod]
    - adjacency: Dict[source_id -> List[edge_id]] (outgoing edges)
    - reverse_adjacency: Dict[target_id -> List[edge_id]] (incoming edges)
    - temporal_index: List[(timestamp, node_id)] sorted by timestamp
    """

    def __init__(self, graph_id: Optional[str] = None):
        """[CITATION: PTKG-CORE] Initialize a new PTKG instance."""
        self.graph_id = graph_id or f"ptkg-{uuid.uuid4().hex[:8]}"
        self.created_at = time.time()
        
        # Core storage
        self._nodes: Dict[str, PTKGNode] = {}
        self._edges: Dict[str, PTKGEdge] = {}
        self._periods: Dict[str, PTKGPeriod] = {}
        
        # Indexes
        self._adjacency: Dict[str, List[str]] = {}
        self._reverse_adjacency: Dict[str, List[str]] = {}
        self._node_type_index: Dict[NodeType, List[str]] = {}
        self._period_node_index: Dict[str, List[str]] = {}
        self._period_edge_index: Dict[str, List[str]] = {}

    def add_node(
        self,
        node_type: NodeType,
        label: str,
        node_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        valid_from: Optional[float] = None,
        valid_until: Optional[float] = None,
        confidence: float = 1.0,
        period_id: Optional[str] = None,
        source_agent_id: Optional[str] = None,
    ) -> PTKGNode:
        """[CITATION: PTKG-CORE] Add a node to the graph. Returns the created node."""
        node = PTKGNode(
            node_id=node_id or f"node-{uuid.uuid4().hex[:12]}",
            node_type=node_type,
            label=label,
            properties=properties or {},
            valid_from=valid_from,
            valid_until=valid_until,
            confidence=confidence,
            period_id=period_id,
            source_agent_id=source_agent_id,
        )
        self._nodes[node.node_id] = node
        
        if node.node_type not in self._node_type_index:
            self._node_type_index[node.node_type] = []
        self._node_type_index[node.node_type].append(node.node_id)
        
        if node.period_id:
            if node.period_id not in self._period_node_index:
                self._period_node_index[node.period_id] = []
            self._period_node_index[node.period_id].append(node.node_id)
            if node.period_id in self._periods:
                self._periods[node.period_id].node_count += 1
        
        return node

    def get_node(self, node_id: str) -> Optional[PTKGNode]:
        """[CITATION: PTKG-CORE] Retrieve a node by ID."""
        return self._nodes.get(node_id)

    def has_node(self, node_id: str) -> bool:
        """[CITATION: PTKG-CORE] Check if a node exists."""
        return node_id in self._nodes

    def get_nodes_by_type(self, node_type: NodeType) -> List[PTKGNode]:
        """[CITATION: PTKG-CORE] Retrieve all nodes of a given type."""
        return [self._nodes[nid] for nid in self._node_type_index.get(node_type, [])
                if nid in self._nodes]

    def invalidate_node(self, node_id: str, timestamp: Optional[float] = None) -> bool:
        """[CITATION: PTKG-CORE] Mark a node as no longer valid (fact has been superseded)."""
        node = self._nodes.get(node_id)
        if not node:
            return False
        node.valid_until = timestamp or time.time()
        return True

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: EdgeType,
        edge_id: Optional[str] = None,
        confidence: float = 1.0,
        causal_weight: float = 0.5,
        period_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[PTKGEdge]:
        """[CITATION: PTKG-CORE] Add a directed edge between two nodes. Returns None if nodes missing."""
        if source_id not in self._nodes or target_id not in self._nodes:
            return None
        
        edge = PTKGEdge(
            edge_id=edge_id or f"edge-{uuid.uuid4().hex[:12]}",
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            confidence=confidence,
            causal_weight=causal_weight,
            period_id=period_id,
            properties=properties or {},
        )
        self._edges[edge.edge_id] = edge
        
        if source_id not in self._adjacency:
            self._adjacency[source_id] = []
        self._adjacency[source_id].append(edge.edge_id)
        
        if target_id not in self._reverse_adjacency:
            self._reverse_adjacency[target_id] = []
        self._reverse_adjacency[target_id].append(edge.edge_id)
        
        if period_id:
            if period_id not in self._period_edge_index:
                self._period_edge_index[period_id] = []
            self._period_edge_index[period_id].append(edge.edge_id)
            if period_id in self._periods:
                self._periods[period_id].edge_count += 1
        
        return edge

    def get_edge(self, edge_id: str) -> Optional[PTKGEdge]:
        """[CITATION: PTKG-CORE] Retrieve an edge by ID."""
        return self._edges.get(edge_id)

    def has_edge(self, edge_id: str) -> bool:
        """[CITATION: PTKG-CORE] Check if an edge exists."""
        return edge_id in self._edges

    def get_outgoing_edges(self, node_id: str) -> List[PTKGEdge]:
        """[CITATION: PTKG-CORE] Get all outgoing edges from a node."""
        return [self._edges[eid] for eid in self._adjacency.get(node_id, [])
                if eid in self._edges]

    def get_incoming_edges(self, node_id: str) -> List[PTKGEdge]:
        """[CITATION: PTKG-CORE] Get all incoming edges to a node."""
        return [self._edges[eid] for eid in self._reverse_adjacency.get(node_id, [])
                if eid in self._edges]

    def start_period(self, label: str = "", description: str = "", period_id: Optional[str] = None) -> PTKGPeriod:
        """[CITATION: PTKG-CORE] Start a new time period."""
        period = PTKGPeriod(
            period_id=period_id or f"period-{uuid.uuid4().hex[:8]}",
            start_time=time.time(),
            label=label,
            description=description,
        )
        self._periods[period.period_id] = period
        return period

    def end_period(self, period_id: str) -> bool:
        """[CITATION: PTKG-CORE] End a time period."""
        period = self._periods.get(period_id)
        if not period:
            return False
        period.end_time = time.time()
        return True

    def get_period(self, period_id: str) -> Optional[PTKGPeriod]:
        """[CITATION: PTKG-CORE] Retrieve a period by ID."""
        return self._periods.get(period_id)

    def get_current_periods(self) -> List[PTKGPeriod]:
        """[CITATION: PTKG-CORE] Get all periods that have not been ended."""
        return [p for p in self._periods.values() if p.end_time is None]

    def get_nodes_valid_at(self, timestamp: float, node_type: Optional[NodeType] = None) -> List[PTKGNode]:
        """[CITATION: PTKG-CORE] Retrieve nodes that were valid at a specific point in time."""
        candidates = self._nodes.values()
        if node_type:
            candidates = [self._nodes[nid] for nid in self._node_type_index.get(node_type, [])
                         if nid in self._nodes]
        return [n for n in candidates if n.is_valid_at(timestamp)]

    def get_edges_in_period(self, period_id: str, edge_type: Optional[EdgeType] = None) -> List[PTKGEdge]:
        """[CITATION: PTKG-CORE] Retrieve edges belonging to a specific period."""
        edge_ids = self._period_edge_index.get(period_id, [])
        edges = [self._edges[eid] for eid in edge_ids if eid in self._edges]
        if edge_type:
            edges = [e for e in edges if e.edge_type == edge_type]
        return edges

    def get_nodes_in_period(self, period_id: str, node_type: Optional[NodeType] = None) -> List[PTKGNode]:
        """[CITATION: PTKG-CORE] Retrieve nodes belonging to a specific period."""
        node_ids = self._period_node_index.get(period_id, [])
        nodes = [self._nodes[nid] for nid in node_ids if nid in self._nodes]
        if node_type:
            nodes = [n for n in nodes if n.node_type == node_type]
        return nodes

    @cite(
        key="PTKG-BFS",
        paper="Periodic Temporal Knowledge Graph for Agent Memory",
        venue="ACN Architecture Document",
        section="Multi-Hop Traversal",
        rationale="BFS with edge-type and temporal filtering enables structured multi-hop reasoning",
        confidence="CERTAIN",
    )
    def bfs_traversal(
        self,
        start_node_id: str,
        max_depth: int = 3,
        edge_types: Optional[List[EdgeType]] = None,
        min_confidence: float = 0.0,
        min_causal_weight: float = 0.0,
        valid_at: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        [CITATION: PTKG-CORE] Breadth-first traversal from a start node with filters.
        
        Returns a list of paths, each path is a list of node-edge-node dicts.
        """
        if start_node_id not in self._nodes:
            return []
        
        results: List[Dict[str, Any]] = []
        visited: Set[Tuple[str, int]] = set()
        queue: List[Dict[str, Any]] = [{"node_id": start_node_id, "depth": 0, "path": []}]
        
        while queue:
            current = queue.pop(0)
            node_id = current["node_id"]
            depth = current["depth"]
            path = current["path"]
            
            if depth >= max_depth:
                continue
            
            state_key = (node_id, depth)
            if state_key in visited:
                continue
            visited.add(state_key)
            
            for edge in self.get_outgoing_edges(node_id):
                if edge_types and edge.edge_type not in edge_types:
                    continue
                if edge.confidence < min_confidence:
                    continue
                if edge.causal_weight < min_causal_weight:
                    continue
                if valid_at is not None and not self._nodes[edge.target_id].is_valid_at(valid_at):
                    continue
                
                new_path = path + [{
                    "from": node_id,
                    "edge": edge.edge_id,
                    "edge_type": edge.edge_type.value,
                    "to": edge.target_id,
                    "confidence": edge.confidence,
                    "causal_weight": edge.causal_weight,
                }]
                results.append({
                    "target_node": edge.target_id,
                    "depth": depth + 1,
                    "path": new_path,
                })
                queue.append({
                    "node_id": edge.target_id,
                    "depth": depth + 1,
                    "path": new_path,
                })
        
        return results

    @cite(
        key="PTKG-CAUSAL-PATH",
        paper="Periodic Temporal Knowledge Graph for Agent Memory",
        venue="ACN Architecture Document",
        section="Causal Chain Following",
        rationale="Following CAUSED edges with high causal_weight traces argument-to-outcome chains",
        confidence="CERTAIN",
    )
    def find_causal_paths(
        self,
        start_node_id: str,
        max_depth: int = 5,
        min_causal_weight: float = 0.5,
    ) -> List[List[Dict[str, Any]]]:
        """
        [CITATION: PTKG-CORE] Find all causal paths from a start node following CAUSED edges.
        Returns a list of paths (each path is a list of step dicts).
        """
        paths = self.bfs_traversal(
            start_node_id=start_node_id,
            max_depth=max_depth,
            edge_types=[EdgeType.CAUSED],
            min_causal_weight=min_causal_weight,
        )
        return [p["path"] for p in paths]

    @cite(
        key="PTKG-CONSOLIDATE",
        paper="Periodic Temporal Knowledge Graph for Agent Memory",
        venue="ACN Architecture Document",
        section="Period Consolidation",
        rationale="Episodic periods are consolidated into durative summaries, mirroring TSM2026 episodic-to-semantic consolidation",
        confidence="CERTAIN",
    )
    def consolidate_period(self, period_id: str, summary_label: Optional[str] = None) -> Optional[PTKGNode]:
        """
        [CITATION: PTKG-CORE] Consolidate a completed period into a durative summary node.
        
        Creates a DURATIVE_SUMMARY node containing aggregated information
        from all nodes in the period, marks the period as consolidated,
        and creates CONSOLIDATED_INTO edges from period nodes.
        """
        period = self._periods.get(period_id)
        if not period:
            return None
        if period.end_time is None:
            self.end_period(period_id)
        
        period_nodes = self.get_nodes_in_period(period_id)
        period_edges = self.get_edges_in_period(period_id)
        
        agent_ids = list({n.source_agent_id for n in period_nodes if n.source_agent_id})
        node_type_counts = {}
        for n in period_nodes:
            node_type_counts[n.node_type.value] = node_type_counts.get(n.node_type.value, 0) + 1
        
        summary = PTKGNode(
            node_id=f"summary-{period_id}",
            node_type=NodeType.DURATIVE_SUMMARY,
            label=summary_label or f"Summary of {period.label or period_id}",
            properties={
                "period_id": period_id,
                "node_count": len(period_nodes),
                "edge_count": len(period_edges),
                "agent_ids": agent_ids,
                "node_type_counts": node_type_counts,
                "consolidated_at": time.time(),
            },
            valid_from=period.start_time,
            period_id=period_id,
        )
        self._nodes[summary.node_id] = summary
        
        if summary.node_type not in self._node_type_index:
            self._node_type_index[summary.node_type] = []
        self._node_type_index[summary.node_type].append(summary.node_id)
        
        for node in period_nodes:
            self.add_edge(
                source_id=node.node_id,
                target_id=summary.node_id,
                edge_type=EdgeType.CONSOLIDATED_INTO,
                period_id=period_id,
                causal_weight=0.0,
            )
        
        period.consolidated_into = summary.node_id
        return summary

    def get_graph_stats(self) -> Dict[str, Any]:
        """[CITATION: PTKG-CORE] Return statistics about the graph."""
        return {
            "graph_id": self.graph_id,
            "node_count": len(self._nodes),
            "edge_count": len(self._edges),
            "period_count": len(self._periods),
            "node_type_distribution": {
                nt.value: len(nids) for nt, nids in self._node_type_index.items()
            },
            "consolidated_periods": sum(
                1 for p in self._periods.values() if p.consolidated_into is not None
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        """[CITATION: PTKG-CORE] Serialize the entire graph to a dictionary."""
        return {
            "graph_id": self.graph_id,
            "created_at": self.created_at,
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
            "edges": {eid: e.to_dict() for eid, e in self._edges.items()},
            "periods": {pid: p.to_dict() for pid, p in self._periods.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PTKG":
        """[CITATION: PTKG-CORE] Deserialize a graph from a dictionary."""
        graph = cls(graph_id=data.get("graph_id", "restored"))
        graph.created_at = data.get("created_at", time.time())
        
        for nid, ndata in data.get("nodes", {}).items():
            node = PTKGNode.from_dict(ndata)
            graph._nodes[node.node_id] = node
            if node.node_type not in graph._node_type_index:
                graph._node_type_index[node.node_type] = []
            graph._node_type_index[node.node_type].append(node.node_id)
            if node.period_id:
                if node.period_id not in graph._period_node_index:
                    graph._period_node_index[node.period_id] = []
                graph._period_node_index[node.period_id].append(node.node_id)
        
        for eid, edata in data.get("edges", {}).items():
            edge = PTKGEdge.from_dict(edata)
            graph._edges[edge.edge_id] = edge
            if edge.source_id not in graph._adjacency:
                graph._adjacency[edge.source_id] = []
            graph._adjacency[edge.source_id].append(edge.edge_id)
            if edge.target_id not in graph._reverse_adjacency:
                graph._reverse_adjacency[edge.target_id] = []
            graph._reverse_adjacency[edge.target_id].append(edge.edge_id)
            if edge.period_id:
                if edge.period_id not in graph._period_edge_index:
                    graph._period_edge_index[edge.period_id] = []
                graph._period_edge_index[edge.period_id].append(edge.edge_id)
        
        for pid, pdata in data.get("periods", {}).items():
            period = PTKGPeriod.from_dict(pdata)
            graph._periods[period.period_id] = period
        
        return graph
