# src/memory/reputation_graph.py
"""
Agent Reputation Evolution as a Temporal Graph.

Tracks how each agent's reputation changes over time by storing
reputation snapshots as nodes in the PTKG and linking them via
temporal edges. This enables:
- Historical reputation queries: "What was agent X's reputation during session Y?"
- Reputation trajectory analysis: "Is agent Z becoming more reliable?"
- Reputation-weighted consensus: "Weight votes by current reputation"

Design inspired by:
- NSED2026: Quadratic voting with reputation-weighted aggregation
- DecentLLMs2025: Geometric median aggregation for Byzantine robustness
- ReliableMAM2025: Decentralized feedback architecture
- GraphMemory2026: Agent state tracked in graph memory

[CITATION: NSED2026]
[CITATION: DecentLLMs2025]
[CITATION: ReliableMAM2025]
[CITATION: GraphMemory2026]
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from memory.ptkg import PTKG, PTKGNode, PTKGEdge, NodeType, EdgeType


@cite(
    key="REPUTATION-MODEL",
    paper="Reputation Evolution in Temporal Knowledge Graphs",
    venue="ACN Architecture Document",
    section="Reputation Model",
    rationale="Multi-factor reputation with temporal decay prevents stale reputation from dominating consensus",
    confidence="CERTAIN",
)
@dataclass
class ReputationFactors:
    """[CITATION: PTKG-REPUTATION] Factors contributing to an agent's reputation score."""
    task_success_rate: float = 0.5
    consensus_alignment: float = 0.5
    peer_evaluation: float = 0.5
    deliberation_quality: float = 0.5
    recency_weight: float = 1.0

    def compute_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """[CITATION: PTKG-REPUTATION] Compute weighted reputation score from factors."""
        w = weights or {
            "task_success_rate": 0.25,
            "consensus_alignment": 0.25,
            "peer_evaluation": 0.25,
            "deliberation_quality": 0.25,
        }
        score = (
            self.task_success_rate * w.get("task_success_rate", 0.25) +
            self.consensus_alignment * w.get("consensus_alignment", 0.25) +
            self.peer_evaluation * w.get("peer_evaluation", 0.25) +
            self.deliberation_quality * w.get("deliberation_quality", 0.25)
        ) * self.recency_weight
        return min(1.0, max(0.0, score))


@cite(
    key="REPUTATION-TRACKER",
    paper="Reputation Evolution in Temporal Knowledge Graphs",
    venue="ACN Architecture Document",
    section="Graph-Based Reputation Tracker",
    rationale="Storing reputation as graph nodes enables time-aware queries and trajectory analysis",
    confidence="CERTAIN",
)
class ReputationGraphTracker:
    """
    [CITATION: PTKG-REPUTATION] Tracks agent reputation evolution within a PTKG.
    
    Each reputation update creates a new REPUTATION_SNAPSHOT node
    linked to the agent via HAS_REPUTATION edges. Temporal ordering
    is maintained via TEMPORAL_NEXT edges between snapshots.
    """

    def __init__(self, graph: PTKG, reputation_decay: float = 0.95):
        """[CITATION: PTKG-REPUTATION] Initialize reputation tracker."""
        self.graph = graph
        self.reputation_decay = reputation_decay
        self._agent_latest_snapshot: Dict[str, str] = {}

    def ensure_agent_node(self, agent_id: str, agent_name: str = "", cluster: str = "") -> PTKGNode:
        """[CITATION: PTKG-REPUTATION] Ensure an agent node exists in the graph. Returns the node."""
        for node in self.graph._nodes.values():
            if (node.node_type == NodeType.AGENT and
                node.properties.get("agent_id") == agent_id):
                return node
        
        return self.graph.add_node(
            node_type=NodeType.AGENT,
            label=agent_name or f"Agent {agent_id}",
            properties={
                "agent_id": agent_id,
                "name": agent_name or agent_id,
                "cluster": cluster,
            },
            source_agent_id=agent_id,
        )

    def record_reputation(
        self,
        agent_id: str,
        score: float,
        factors: Optional[ReputationFactors] = None,
        period_id: Optional[str] = None,
        agent_name: str = "",
        cluster: str = "",
    ) -> PTKGNode:
        """
        [CITATION: PTKG-REPUTATION] Record a new reputation snapshot for an agent.
        
        Creates:
        1. Agent node (if not exists)
        2. Reputation snapshot node
        3. HAS_REPUTATION edge from agent to snapshot
        4. TEMPORAL_NEXT edge from previous snapshot (if exists)
        """
        agent_node = self.ensure_agent_node(agent_id, agent_name, cluster)
        
        snapshot = self.graph.add_node(
            node_type=NodeType.REPUTATION_SNAPSHOT,
            label=f"Reputation: {score:.3f}",
            properties={
                "agent_id": agent_id,
                "score": score,
                "factors": factors.__dict__ if factors else {},
                "recorded_at": time.time(),
            },
            confidence=score,
            period_id=period_id,
            source_agent_id=agent_id,
        )
        
        self.graph.add_edge(
            source_id=agent_node.node_id,
            target_id=snapshot.node_id,
            edge_type=EdgeType.HAS_REPUTATION,
            period_id=period_id,
            causal_weight=0.0,
            properties={"score": score},
        )
        
        prev_snapshot_id = self._agent_latest_snapshot.get(agent_id)
        if prev_snapshot_id and prev_snapshot_id in self.graph._nodes:
            self.graph.add_edge(
                source_id=prev_snapshot_id,
                target_id=snapshot.node_id,
                edge_type=EdgeType.TEMPORAL_NEXT,
                period_id=period_id,
                causal_weight=0.0,
            )
        
        self._agent_latest_snapshot[agent_id] = snapshot.node_id
        return snapshot

    def get_reputation_history(self, agent_id: str) -> List[Dict[str, Any]]:
        """[CITATION: PTKG-REPUTATION] Get chronological reputation history for an agent."""
        snapshots = []
        for node in self.graph._nodes.values():
            if (node.node_type == NodeType.REPUTATION_SNAPSHOT and
                node.properties.get("agent_id") == agent_id):
                snapshots.append(node)
        
        snapshots.sort(key=lambda n: n.created_at)
        return [
            {
                "snapshot_id": s.node_id,
                "score": s.properties.get("score", 0.5),
                "recorded_at": s.created_at,
                "period_id": s.period_id,
                "factors": s.properties.get("factors", {}),
            }
            for s in snapshots
        ]

    def get_current_reputation(self, agent_id: str) -> float:
        """[CITATION: PTKG-REPUTATION] Get the most recent reputation score for an agent."""
        history = self.get_reputation_history(agent_id)
        if not history:
            return 0.5
        return history[-1]["score"]

    def get_reputation_at_time(self, agent_id: str, timestamp: float) -> float:
        """[CITATION: PTKG-REPUTATION] Get the agent's reputation at a specific point in time."""
        history = self.get_reputation_history(agent_id)
        if not history:
            return 0.5
        
        applicable = [h for h in history if h["recorded_at"] <= timestamp]
        if not applicable:
            return 0.5
        return applicable[-1]["score"]

    def compute_reputation_from_deliberation(
        self,
        agent_id: str,
        proposals_made: int = 0,
        proposals_accepted: int = 0,
        critiques_received: int = 0,
        critiques_addressed: int = 0,
        peer_ratings: Optional[List[float]] = None,
        period_id: Optional[str] = None,
    ) -> float:
        """
        [CITATION: PTKG-REPUTATION] Compute reputation from deliberation outcomes and record it.
        
        Factors:
        - deliberation_quality: proposals_accepted / proposals_made
        - peer_evaluation: average of peer ratings
        - consensus_alignment: critiques_addressed / critiques_received
        """
        factors = ReputationFactors()
        
        if proposals_made > 0:
            factors.deliberation_quality = proposals_accepted / proposals_made
        
        if critiques_received > 0:
            factors.consensus_alignment = critiques_addressed / critiques_received
        
        if peer_ratings:
            factors.peer_evaluation = sum(peer_ratings) / len(peer_ratings)
        
        score = factors.compute_score()
        self.record_reputation(agent_id, score, factors, period_id)
        return score

    def get_all_agent_reputations(self) -> Dict[str, float]:
        """[CITATION: PTKG-REPUTATION] Get current reputation for all known agents."""
        reps = {}
        for node in self.graph._nodes.values():
            if node.node_type == NodeType.AGENT:
                agent_id = node.properties.get("agent_id")
                if agent_id:
                    reps[agent_id] = self.get_current_reputation(agent_id)
        return reps

    def get_reputation_trend(self, agent_id: str, window: int = 5) -> Dict[str, Any]:
        """
        [CITATION: PTKG-REPUTATION] Analyze reputation trend over the last N snapshots.
        
        Returns:
        - trend: "rising", "falling", or "stable"
        - slope: linear change per snapshot
        - volatility: standard deviation of scores
        """
        history = self.get_reputation_history(agent_id)
        if len(history) < 2:
            return {"trend": "stable", "slope": 0.0, "volatility": 0.0}
        
        recent = history[-window:]
        scores = [h["score"] for h in recent]
        
        n = len(scores)
        slope = (scores[-1] - scores[0]) / max(n - 1, 1)
        
        mean = sum(scores) / n
        variance = sum((s - mean) ** 2 for s in scores) / n
        volatility = variance ** 0.5
        
        if slope > 0.05:
            trend = "rising"
        elif slope < -0.05:
            trend = "falling"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "volatility": volatility,
            "current": scores[-1],
            "previous": scores[0] if len(scores) > 1 else scores[-1],
        }
