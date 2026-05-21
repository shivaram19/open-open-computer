# src/consensus/topology_builders.py
"""
TopologyBuilder Protocol and Registry.

Extracts the if-elif chain from TopologyOptimizer.build_topology() into
polymorphic builders registered by TopologyType.

Research basis:
- Meyer (1988): OCP — open for extension, closed for modification
- Fowler (1999): Replace Conditional with Polymorphism

[CITATION: G-Designer2025]
"""

import random
from typing import Protocol, Dict, List, Optional, Any

from shared.utils.citations import cite


class TopologyBuilder(Protocol):
    """Protocol for building a communication topology."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]: ...


class CompleteTopologyBuilder:
    """All-to-all connections."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        return {aid: [x for x in agent_ids if x != aid] for aid in agent_ids}


class StarTopologyBuilder:
    """Star topology with central hub."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        hub = kwargs.get("hub") or (agent_ids[0] if agent_ids else None)
        if not agent_ids:
            return {}
        graph = {}
        for aid in agent_ids:
            if aid == hub:
                graph[aid] = [x for x in agent_ids if x != hub]
            else:
                graph[aid] = [hub]
        return graph


class ChainTopologyBuilder:
    """Linear chain topology."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        graph = {}
        for i, aid in enumerate(agent_ids):
            neighbors = []
            if i > 0:
                neighbors.append(agent_ids[i - 1])
            if i < len(agent_ids) - 1:
                neighbors.append(agent_ids[i + 1])
            graph[aid] = neighbors
        return graph


class TreeTopologyBuilder:
    """Hierarchical tree topology."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        if not agent_ids:
            return {}
        graph = {aid: [] for aid in agent_ids}
        for i, aid in enumerate(agent_ids):
            parent_idx = (i - 1) // 2
            if parent_idx >= 0 and parent_idx < len(agent_ids):
                parent = agent_ids[parent_idx]
                if parent != aid:
                    graph[aid].append(parent)
                    graph[parent].append(aid)
        return graph


class RandomTopologyBuilder:
    """Erdős-Rényi random graph."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        prob = kwargs.get("random_edge_prob", 0.3)
        seed = kwargs.get("random_seed")
        rng = random.Random(seed)
        graph = {aid: [] for aid in agent_ids}
        for i, a1 in enumerate(agent_ids):
            for a2 in agent_ids[i + 1 :]:
                if rng.random() < prob:
                    graph[a1].append(a2)
                    graph[a2].append(a1)
        return graph


class LayeredTopologyBuilder:
    """Clustered layered topology."""

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        cluster_map = kwargs.get("cluster_map", {})
        graph = {aid: [] for aid in agent_ids}
        clusters: Dict[str, List[str]] = {}
        for aid in agent_ids:
            cluster = cluster_map.get(aid, "default")
            clusters.setdefault(cluster, []).append(aid)
        # Intra-cluster: complete
        for cluster_agents in clusters.values():
            for i, a1 in enumerate(cluster_agents):
                for a2 in cluster_agents[i + 1 :]:
                    graph[a1].append(a2)
                    graph[a2].append(a1)
        # Inter-cluster: one representative per cluster
        reps = [agents[0] for agents in clusters.values() if agents]
        for i, r1 in enumerate(reps):
            for r2 in reps[i + 1 :]:
                graph[r1].append(r2)
                graph[r2].append(r1)
        return graph


class AdaptiveTopologyBuilder:
    """
    Task-difficulty-based adaptive selection (G-Designer inspired).

    DIP-compliant: depends on registry abstraction, not concrete builders.
    Adding a new topology to the registry is automatically available
    for adaptive selection by updating the selection map.
    """

    def __init__(self, registry=None):
        self._registry = registry

    def build(self, agent_ids: List[str], **kwargs) -> Dict[str, List[str]]:
        difficulty = kwargs.get("task_difficulty", 0.5)

        # Selection logic maps (difficulty, agent_count) → TopologyType.
        # This map can be extended without modifying builder classes.
        selected_type = self._select_topology_type(difficulty, len(agent_ids))

        if self._registry is not None and selected_type in self._registry:
            return self._registry[selected_type].build(agent_ids, **kwargs)

        # Fallback: direct instantiation (only when registry not injected)
        return self._fallback_build(agent_ids, selected_type, **kwargs)

    def _select_topology_type(self, difficulty: float, agent_count: int):
        """Select topology type based on task difficulty and agent count."""
        # These imports are local to avoid circular dependency at module load.
        from consensus.topology import TopologyType

        if difficulty < 0.3:
            return TopologyType.CHAIN if agent_count <= 3 else TopologyType.STAR
        elif difficulty < 0.6:
            return TopologyType.TREE if agent_count <= 4 else TopologyType.RANDOM
        elif difficulty < 0.8:
            return TopologyType.COMPLETE if agent_count <= 6 else TopologyType.LAYERED
        else:
            return TopologyType.COMPLETE

    def _fallback_build(self, agent_ids, selected_type, **kwargs):
        """Direct fallback — avoids circular imports when registry unavailable."""
        from consensus.topology import TopologyType

        if selected_type == TopologyType.CHAIN:
            return ChainTopologyBuilder().build(agent_ids, **kwargs)
        elif selected_type == TopologyType.STAR:
            return StarTopologyBuilder().build(agent_ids, **kwargs)
        elif selected_type == TopologyType.TREE:
            return TreeTopologyBuilder().build(agent_ids, **kwargs)
        elif selected_type == TopologyType.RANDOM:
            return RandomTopologyBuilder().build(agent_ids, random_edge_prob=0.4, **kwargs)
        elif selected_type == TopologyType.COMPLETE:
            return CompleteTopologyBuilder().build(agent_ids, **kwargs)
        elif selected_type == TopologyType.LAYERED:
            return LayeredTopologyBuilder().build(agent_ids, **kwargs)
        return CompleteTopologyBuilder().build(agent_ids, **kwargs)



