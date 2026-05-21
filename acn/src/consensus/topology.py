# src/consensus/topology.py
"""
Communication Topology Optimization for Multi-Agent Swarms.

Implements task-adaptive communication topologies inspired by G-Designer:
- Simpler tasks → simpler topologies (fewer edges, lower token cost)
- Complex tasks → richer topologies (more edges, higher connectivity)
- Token-economical: minimize communication overhead while maximizing consensus quality

Supported topologies:
- COMPLETE: All-to-all (highest consensus, highest cost)
- STAR: Central hub (fast, single point of failure)
- CHAIN: Linear pipeline (sequential, low parallelism)
- TREE: Hierarchical (good for decomposition)
- RANDOM: Erdős-Rényi random graph (balanced)
- LAYERED: Clustered hierarchy (cross-cluster sparingly)
- ADAPTIVE: Task-difficulty-based selection (G-Designer inspired)

Design inspired by:
- G-Designer2025: Variational graph auto-encoder for topology optimization
- CP-WBFT2025: Topology affects Byzantine fault tolerance
- ReliableMAM2025: Network topology impacts reliability

[CITATION: G-Designer2025]
[CITATION: CP-WBFT2025]
[CITATION: ReliableMAM2025]
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple

from shared.utils.citations import cite
from consensus.topology_builders import (
    CompleteTopologyBuilder,
    StarTopologyBuilder,
    ChainTopologyBuilder,
    TreeTopologyBuilder,
    RandomTopologyBuilder,
    LayeredTopologyBuilder,
    AdaptiveTopologyBuilder,
)


@cite(
    key="TOPOLOGY-TYPE",
    paper="Communication Topology Optimization for Multi-Agent Swarms",
    venue="ACN Architecture Document",
    section="Topology Type Enumeration",
    rationale="Different topologies trade off consensus quality, cost, and fault tolerance",
    confidence="CERTAIN",
)
class TopologyType(Enum):
    """[CITATION: TOPOLOGY] Communication topology types."""
    COMPLETE = "complete"
    STAR = "star"
    CHAIN = "chain"
    TREE = "tree"
    RANDOM = "random"
    LAYERED = "layered"
    ADAPTIVE = "adaptive"


# OCP-compliant registry: add a new topology by adding an entry here.
# Built in two phases to inject the registry into AdaptiveTopologyBuilder (DIP).
TOPOLOGY_BUILDERS = {
    TopologyType.COMPLETE: CompleteTopologyBuilder(),
    TopologyType.STAR: StarTopologyBuilder(),
    TopologyType.CHAIN: ChainTopologyBuilder(),
    TopologyType.TREE: TreeTopologyBuilder(),
    TopologyType.RANDOM: RandomTopologyBuilder(),
    TopologyType.LAYERED: LayeredTopologyBuilder(),
}
TOPOLOGY_BUILDERS[TopologyType.ADAPTIVE] = AdaptiveTopologyBuilder(
    registry=TOPOLOGY_BUILDERS
)


@dataclass
class TopologyMetrics:
    """[CITATION: TOPOLOGY] Metrics for a communication topology."""
    topology_type: TopologyType
    node_count: int
    edge_count: int
    diameter: int          # Longest shortest path
    avg_degree: float
    clustering_coefficient: float
    estimated_token_cost: float  # Relative communication cost
    fault_tolerance_score: float  # 0-1, higher = more resilient


@cite(
    key="TOPOLOGY-OPTIMIZER",
    paper="Communication Topology Optimization for Multi-Agent Swarms",
    venue="ACN Architecture Document",
    section="Topology Optimizer",
    rationale="Task-adaptive topology selection balances performance and cost per G-Designer",
    confidence="CERTAIN",
)
class TopologyOptimizer:
    """
    [CITATION: TOPOLOGY] Optimizes agent communication topologies.
    
    G-Designer insight: Not all multi-agent topologies outperform single-agent.
    Task-appropriate topology design is crucial for collective intelligence.
    
    Usage:
        optimizer = TopologyOptimizer()
        graph = optimizer.build_topology(agent_ids, TopologyType.ADAPTIVE, task_difficulty=0.7)
    """

    def __init__(self, random_seed: Optional[int] = None):
        """[CITATION: TOPOLOGY] Initialize topology optimizer."""
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)

    def build_topology(
        self,
        agent_ids: List[str],
        topology_type: TopologyType,
        task_difficulty: float = 0.5,
        hub_agent: Optional[str] = None,
        cluster_map: Optional[Dict[str, str]] = None,
        random_edge_prob: float = 0.3,
    ) -> Dict[str, List[str]]:
        """
        [CITATION: TOPOLOGY] Build a communication topology for given agents.
        
        Args:
            agent_ids: List of agent IDs
            topology_type: Type of topology to build
            task_difficulty: 0.0-1.0, used by ADAPTIVE to select topology
            hub_agent: Central node for STAR topology
            cluster_map: agent_id -> cluster_name for LAYERED topology
            random_edge_prob: Edge probability for RANDOM topology
        
        Returns:
            Adjacency list: {agent_id: [neighbor_id, ...], ...}
        """
        builder = TOPOLOGY_BUILDERS.get(topology_type)
        if builder is None:
            builder = TOPOLOGY_BUILDERS[TopologyType.COMPLETE]

        kwargs = {}
        if hub_agent is not None:
            kwargs["hub"] = hub_agent
        if cluster_map is not None:
            kwargs["cluster_map"] = cluster_map
        if random_edge_prob != 0.3:
            kwargs["random_edge_prob"] = random_edge_prob
        if self.random_seed is not None:
            kwargs["random_seed"] = self.random_seed
        if task_difficulty != 0.5:
            kwargs["task_difficulty"] = task_difficulty

        return builder.build(agent_ids, **kwargs)



    def compute_metrics(
        self,
        graph: Dict[str, List[str]],
        topology_type: TopologyType,
    ) -> TopologyMetrics:
        """[CITATION: TOPOLOGY] Compute metrics for a topology."""
        node_count = len(graph)
        if node_count == 0:
            return TopologyMetrics(
                topology_type=topology_type,
                node_count=0, edge_count=0, diameter=0,
                avg_degree=0.0, clustering_coefficient=0.0,
                estimated_token_cost=0.0, fault_tolerance_score=0.0,
            )
        
        edges = set()
        for src, targets in graph.items():
            for tgt in targets:
                edge = tuple(sorted([src, tgt]))
                edges.add(edge)
        edge_count = len(edges)
        
        avg_degree = sum(len(neighbors) for neighbors in graph.values()) / node_count
        
        # Diameter via BFS from each node
        diameter = 0
        for start in graph:
            visited = {start: 0}
            queue = [start]
            while queue:
                node = queue.pop(0)
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        visited[neighbor] = visited[node] + 1
                        queue.append(neighbor)
            if visited:
                diameter = max(diameter, max(visited.values()))
        
        # Token cost: proportional to edge count (more edges = more messages)
        # Complete graph has cost 1.0, chain has cost ~2/n
        max_edges = node_count * (node_count - 1) // 2
        token_cost = edge_count / max_edges if max_edges > 0 else 0.0
        
        # Fault tolerance: related to connectivity and diameter
        # Complete = 1.0, chain = low, star = medium (hub is single point)
        if topology_type == TopologyType.COMPLETE:
            fault_tol = 1.0
        elif topology_type == TopologyType.LAYERED:
            fault_tol = 0.75
        elif topology_type == TopologyType.RANDOM:
            fault_tol = 0.6
        elif topology_type == TopologyType.TREE:
            fault_tol = 0.4
        elif topology_type == TopologyType.STAR:
            fault_tol = 0.3
        elif topology_type == TopologyType.CHAIN:
            fault_tol = 0.2
        else:
            fault_tol = 0.5
        
        return TopologyMetrics(
            topology_type=topology_type,
            node_count=node_count,
            edge_count=edge_count,
            diameter=diameter,
            avg_degree=avg_degree,
            clustering_coefficient=0.0,  # Simplified
            estimated_token_cost=token_cost,
            fault_tolerance_score=fault_tol,
        )

    def optimize_for_task(
        self,
        agent_ids: List[str],
        task_complexity: float,
        max_token_budget: float = 1.0,
        min_fault_tolerance: float = 0.3,
    ) -> Tuple[TopologyType, Dict[str, List[str]], TopologyMetrics]:
        """
        [CITATION: TOPOLOGY] Select optimal topology for a task given constraints.
        
        Tries ADAPTIVE first, then falls back to simpler topologies if constraints violated.
        """
        candidates = [
            TopologyType.ADAPTIVE,
            TopologyType.LAYERED,
            TopologyType.RANDOM,
            TopologyType.TREE,
            TopologyType.STAR,
            TopologyType.CHAIN,
        ]
        
        for topo_type in candidates:
            graph = self.build_topology(
                agent_ids, topo_type, task_difficulty=task_complexity
            )
            metrics = self.compute_metrics(graph, topo_type)
            if (metrics.estimated_token_cost <= max_token_budget and
                    metrics.fault_tolerance_score >= min_fault_tolerance):
                return topo_type, graph, metrics

        # Fallback: complete graph (always satisfies fault tolerance, may exceed budget)
        graph = self.build_topology(agent_ids, TopologyType.COMPLETE)
        metrics = self.compute_metrics(graph, TopologyType.COMPLETE)
        return TopologyType.COMPLETE, graph, metrics
