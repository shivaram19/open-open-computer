# src/memory/graph_retrieval.py
"""
Graph Retrieval Strategies for the Periodic Temporal Knowledge Graph.

Implements multiple retrieval strategies that operate over the PTKG:
- NEIGHBOR: Direct neighbors of a node
- MULTI_HOP_BFS: Breadth-first traversal with depth limit
- TEMPORAL_RANGE: Nodes/edges within a time window
- CAUSAL_CHAIN: Follow CAUSED edges to trace outcomes
- REPUTATION_WEIGHTED: Rank results by source agent reputation
- HYBRID: Combine multiple strategies with configurable weights

Design inspired by:
- GraphMemory2026: Retrieval must precede reasoning
- LiCoMemory2025: Temporal and hierarchy-aware search with reranking
- Zep2025: Time-aware retrieval over temporal knowledge graph
- KGoT2025: Graph queries extract task-relevant subgraphs

[CITATION: GraphMemory2026]
[CITATION: LiCoMemory2025]
[CITATION: Zep2025]
[CITATION: KGoT2025]
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from memory.ptkg import PTKG, PTKGNode, PTKGEdge, NodeType, EdgeType


@cite(
    key="RETRIEVAL-STRATEGY",
    paper="Graph Retrieval Strategies for PTKG",
    venue="ACN Architecture Document",
    section="Retrieval Strategy Enumeration",
    rationale="Different retrieval strategies match different cognitive needs: local vs global, temporal vs causal",
    confidence="CERTAIN",
)
class GraphRetrievalStrategy(Enum):
    """[CITATION: PTKG-RETRIEVAL] Different retrieval strategies match different cognitive needs."""
    NEIGHBOR = "neighbor"
    MULTI_HOP_BFS = "multi_hop_bfs"
    TEMPORAL_RANGE = "temporal_range"
    CAUSAL_CHAIN = "causal_chain"
    REPUTATION_WEIGHTED = "reputation_weighted"
    HYBRID = "hybrid"


@dataclass
class RetrievalResult:
    """[CITATION: PTKG-RETRIEVAL] Result of a graph retrieval operation."""
    nodes: List[PTKGNode]
    edges: List[PTKGEdge]
    score: float = 0.0
    strategy: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """[CITATION: PTKG-RETRIEVAL] Initialize default metadata."""
        if self.metadata is None:
            self.metadata = {}


@cite(
    key="GRAPH-RETRIEVER",
    paper="Graph Retrieval Strategies for PTKG",
    venue="ACN Architecture Document",
    section="Graph Retriever",
    rationale="Strategy-dispatched retrieval enables flexible context construction for agent reasoning",
    confidence="CERTAIN",
)
class GraphRetriever:
    """
    [CITATION: PTKG-RETRIEVAL] Retrieves context from a PTKG using configurable strategies.
    
    The retriever is the bridge between the persistent graph memory
    and the agent's reasoning process. Per GraphMemory2026, retrieval
    MUST precede reasoning.
    """

    def __init__(self, graph: PTKG):
        """[CITATION: PTKG-RETRIEVAL] Initialize retriever with a graph."""
        self.graph = graph
        self._agent_reputation: Dict[str, float] = {}

    def set_agent_reputation(self, agent_id: str, reputation: float) -> None:
        """[CITATION: PTKG-RETRIEVAL] Set the reputation score for an agent (0.0-1.0)."""
        self._agent_reputation[agent_id] = reputation

    def get_agent_reputation(self, agent_id: str) -> float:
        """[CITATION: PTKG-RETRIEVAL] Get the reputation score for an agent."""
        return self._agent_reputation.get(agent_id, 0.5)

    def retrieve(
        self,
        strategy: GraphRetrievalStrategy,
        query_node_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        """
        [CITATION: PTKG-RETRIEVAL] Execute a retrieval strategy.
        
        Args:
            strategy: The retrieval strategy to use
            query_node_id: The starting node for traversal-based strategies
            params: Strategy-specific parameters
        
        Returns:
            RetrievalResult with nodes, edges, and score
        """
        params = params or {}
        
        if strategy == GraphRetrievalStrategy.NEIGHBOR:
            return self._retrieve_neighbor(query_node_id, params)
        elif strategy == GraphRetrievalStrategy.MULTI_HOP_BFS:
            return self._retrieve_multi_hop_bfs(query_node_id, params)
        elif strategy == GraphRetrievalStrategy.TEMPORAL_RANGE:
            return self._retrieve_temporal_range(params)
        elif strategy == GraphRetrievalStrategy.CAUSAL_CHAIN:
            return self._retrieve_causal_chain(query_node_id, params)
        elif strategy == GraphRetrievalStrategy.REPUTATION_WEIGHTED:
            return self._retrieve_reputation_weighted(query_node_id, params)
        elif strategy == GraphRetrievalStrategy.HYBRID:
            return self._retrieve_hybrid(query_node_id, params)
        
        return RetrievalResult(nodes=[], edges=[], score=0.0, strategy=strategy.value)

    def _retrieve_neighbor(
        self, query_node_id: Optional[str], params: Dict[str, Any]
    ) -> RetrievalResult:
        """Retrieve direct neighbors (1-hop) of a node."""
        if not query_node_id or query_node_id not in self.graph._nodes:
            return RetrievalResult(nodes=[], edges=[], score=0.0, strategy="neighbor")
        
        outgoing = self.graph.get_outgoing_edges(query_node_id)
        incoming = self.graph.get_incoming_edges(query_node_id)
        all_edges = outgoing + incoming
        
        edge_types = params.get("edge_types")
        if edge_types:
            type_values = [et.value if isinstance(et, EdgeType) else et for et in edge_types]
            all_edges = [e for e in all_edges if e.edge_type.value in type_values]
        
        neighbor_ids = set()
        for edge in all_edges:
            neighbor_ids.add(edge.source_id)
            neighbor_ids.add(edge.target_id)
        neighbor_ids.discard(query_node_id)
        
        nodes = [self.graph._nodes[nid] for nid in neighbor_ids if nid in self.graph._nodes]
        
        return RetrievalResult(
            nodes=nodes,
            edges=all_edges,
            score=len(nodes) / max(len(all_edges), 1),
            strategy="neighbor",
            metadata={"center_node": query_node_id, "hop": 1},
        )

    def _retrieve_multi_hop_bfs(
        self, query_node_id: Optional[str], params: Dict[str, Any]
    ) -> RetrievalResult:
        """Multi-hop BFS traversal from a starting node."""
        if not query_node_id or query_node_id not in self.graph._nodes:
            return RetrievalResult(nodes=[], edges=[], score=0.0, strategy="multi_hop_bfs")
        
        depth = params.get("depth", 2)
        edge_types = params.get("edge_types")
        min_confidence = params.get("min_confidence", 0.0)
        valid_at = params.get("valid_at")
        
        results = self.graph.bfs_traversal(
            start_node_id=query_node_id,
            max_depth=depth,
            edge_types=edge_types,
            min_confidence=min_confidence,
            valid_at=valid_at,
        )
        
        node_ids = set()
        edge_ids = set()
        node_ids.add(query_node_id)
        
        for result in results:
            for step in result["path"]:
                node_ids.add(step["from"])
                node_ids.add(step["to"])
                edge_ids.add(step["edge"])
        
        nodes = [self.graph._nodes[nid] for nid in node_ids if nid in self.graph._nodes]
        edges = [self.graph._edges[eid] for eid in edge_ids if eid in self.graph._edges]
        
        return RetrievalResult(
            nodes=nodes,
            edges=edges,
            score=len(results) / max(depth * 5, 1),
            strategy="multi_hop_bfs",
            metadata={"start_node": query_node_id, "depth": depth, "paths_found": len(results)},
        )

    def _retrieve_temporal_range(self, params: Dict[str, Any]) -> RetrievalResult:
        """Retrieve nodes and edges within a time window."""
        start_time = params.get("start_time", 0)
        end_time = params.get("end_time", time.time())
        node_type = params.get("node_type")
        edge_type = params.get("edge_type")
        
        nodes = []
        for node in self.graph._nodes.values():
            if node.valid_from <= end_time:
                if node.valid_until is None or node.valid_until >= start_time:
                    if node_type is None or node.node_type == node_type:
                        nodes.append(node)
        
        edges = []
        for edge in self.graph._edges.values():
            if start_time <= edge.timestamp <= end_time:
                if edge_type is None or edge.edge_type == edge_type:
                    edges.append(edge)
        
        return RetrievalResult(
            nodes=nodes,
            edges=edges,
            score=len(nodes) / max(len(self.graph._nodes), 1),
            strategy="temporal_range",
            metadata={"start_time": start_time, "end_time": end_time},
        )

    def _retrieve_causal_chain(
        self, query_node_id: Optional[str], params: Dict[str, Any]
    ) -> RetrievalResult:
        """Follow causal chains from a starting node."""
        if not query_node_id or query_node_id not in self.graph._nodes:
            return RetrievalResult(nodes=[], edges=[], score=0.0, strategy="causal_chain")
        
        max_depth = params.get("max_depth", 5)
        min_causal_weight = params.get("min_causal_weight", 0.5)
        
        paths = self.graph.find_causal_paths(
            start_node_id=query_node_id,
            max_depth=max_depth,
            min_causal_weight=min_causal_weight,
        )
        
        node_ids = set()
        edge_ids = set()
        node_ids.add(query_node_id)
        
        for path in paths:
            for step in path:
                node_ids.add(step["from"])
                node_ids.add(step["to"])
                edge_ids.add(step["edge"])
        
        nodes = [self.graph._nodes[nid] for nid in node_ids if nid in self.graph._nodes]
        edges = [self.graph._edges[eid] for eid in edge_ids if eid in self.graph._edges]
        
        return RetrievalResult(
            nodes=nodes,
            edges=edges,
            score=len(paths) / max(max_depth, 1),
            strategy="causal_chain",
            metadata={"start_node": query_node_id, "paths_found": len(paths)},
        )

    def _retrieve_reputation_weighted(
        self, query_node_id: Optional[str], params: Dict[str, Any]
    ) -> RetrievalResult:
        """Retrieve neighbors ranked by source agent reputation."""
        base_result = self._retrieve_neighbor(query_node_id, params)
        if not base_result.nodes:
            return base_result
        
        scored_nodes = []
        for node in base_result.nodes:
            rep = self.get_agent_reputation(node.source_agent_id or "unknown")
            scored_nodes.append((node, rep * node.confidence))
        
        scored_nodes.sort(key=lambda x: x[1], reverse=True)
        limit = params.get("limit", len(scored_nodes))
        
        return RetrievalResult(
            nodes=[n for n, _ in scored_nodes[:limit]],
            edges=base_result.edges,
            score=sum(s for _, s in scored_nodes[:limit]) / max(limit, 1),
            strategy="reputation_weighted",
            metadata={"reputation_weighted": True, "limit": limit},
        )

    def _retrieve_hybrid(
        self, query_node_id: Optional[str], params: Dict[str, Any]
    ) -> RetrievalResult:
        """
        Hybrid retrieval combining multi-hop BFS with temporal and reputation filtering.
        
        This is the default strategy for agent reasoning context construction.
        It balances:
        - Structural relevance (multi-hop BFS)
        - Temporal recency (time-window filtering)
        - Source reliability (reputation weighting)
        """
        bfs_params = {
            "depth": params.get("depth", 2),
            "edge_types": params.get("edge_types"),
            "min_confidence": params.get("min_confidence", 0.0),
        }
        bfs_result = self._retrieve_multi_hop_bfs(query_node_id, bfs_params)
        
        if not bfs_result.nodes:
            return bfs_result
        
        time_window = params.get("time_window_seconds")
        if time_window is not None:
            now = time.time()
            bfs_result.nodes = [
                n for n in bfs_result.nodes
                if n.valid_from >= now - time_window or n.created_at >= now - time_window
            ]
            bfs_result.edges = [
                e for e in bfs_result.edges
                if e.timestamp >= now - time_window
            ]
        
        if params.get("reputation_boost", True):
            scored = []
            for node in bfs_result.nodes:
                rep = self.get_agent_reputation(node.source_agent_id or "unknown")
                age_factor = 1.0
                if time_window:
                    age = now - max(node.created_at, node.valid_from)
                    age_factor = max(0.1, 1.0 - (age / (time_window * 2)))
                scored.append((node, rep * node.confidence * age_factor))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            bfs_result.nodes = [n for n, _ in scored]
            bfs_result.score = sum(s for _, s in scored) / max(len(scored), 1)
        
        bfs_result.strategy = "hybrid"
        bfs_result.metadata.update({
            "time_window": time_window,
            "reputation_boost": params.get("reputation_boost", True),
        })
        
        return bfs_result

    def build_reasoning_context(
        self,
        agent_id: str,
        goal_description: str,
        max_nodes: int = 10,
    ) -> Dict[str, Any]:
        """
        [CITATION: PTKG-RETRIEVAL] Build a reasoning context for an agent from the PTKG.
        
        This is the primary integration point with ConsciousAgent.think().
        It retrieves the most relevant graph context given an agent's identity
        and current goal.
        
        Returns a dict with:
        - relevant_nodes: List of PTKGNode dicts
        - relevant_edges: List of PTKGEdge dicts
        - agent_reputation: Current reputation of this agent
        - similar_past_tasks: Past tasks related to the goal
        - peer_proposals: Recent proposals from other agents
        """
        agent_nodes = [
            n for n in self.graph._nodes.values()
            if n.node_type == NodeType.AGENT and n.properties.get("agent_id") == agent_id
        ]
        
        query_node_id = agent_nodes[0].node_id if agent_nodes else None
        
        result = self.retrieve(
            strategy=GraphRetrievalStrategy.HYBRID,
            query_node_id=query_node_id,
            params={
                "depth": 2,
                "time_window_seconds": 86400 * 7,
                "reputation_boost": True,
                "edge_types": [
                    EdgeType.PROPOSED,
                    EdgeType.PARTICIPATED_IN,
                    EdgeType.HAS_REPUTATION,
                    EdgeType.SUPPORTED,
                    EdgeType.CRITIQUED,
                ],
            },
        )
        
        nodes = result.nodes[:max_nodes]
        
        task_nodes = [n for n in self.graph._nodes.values() if n.node_type == NodeType.TASK]
        similar_tasks = [
            n for n in task_nodes
            if goal_description.lower() in n.label.lower() or any(
                goal_description.lower() in str(v).lower() for v in n.properties.values()
            )
        ][:5]
        
        peer_proposals = [n for n in result.nodes if n.node_type == NodeType.PROPOSAL and n.source_agent_id != agent_id]
        
        return {
            "relevant_nodes": [n.to_dict() for n in nodes],
            "relevant_edges": [e.to_dict() for e in result.edges[:max_nodes * 2]],
            "agent_reputation": self.get_agent_reputation(agent_id),
            "similar_past_tasks": [n.to_dict() for n in similar_tasks],
            "peer_proposals": [n.to_dict() for n in peer_proposals],
            "retrieval_score": result.score,
            "strategy": result.strategy,
        }
