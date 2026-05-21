# src/memory/causal_chain.py
"""
Causal Chain Tracking across Deliberation Sessions.

Builds and queries causal chains through the PTKG by linking events,
proposals, arguments, and outcomes via CAUSED edges. This enables:
- Root cause analysis: "What argument led to this proposal being rejected?"
- Impact tracing: "Which past decisions influenced the current consensus?"
- Counterfactual queries: "What would have happened if argument X had been addressed?"

Design inspired by:
- SWARP2026: Argument maps track causal relationships between positions
- KGoT2025: Knowledge graph encodes task state evolution
- NSED2026: Quadratic voting outcomes have causal antecedents in argument quality
- GraphMemory2026: Causal links enable structured retrieval

[CITATION: SWARP2026]
[CITATION: KGoT2025]
[CITATION: NSED2026]
[CITATION: GraphMemory2026]
"""

import time
from typing import Dict, List, Optional, Any, Set

from shared.utils.citations import cite
from memory.ptkg import PTKG, PTKGNode, PTKGEdge, NodeType, EdgeType


@cite(
    key="CAUSAL-CHAIN",
    paper="Causal Chain Tracking in Periodic Temporal Knowledge Graphs",
    venue="ACN Architecture Document",
    section="Causal Chain Tracker",
    rationale="Causal edges enable root-cause analysis and impact tracing across deliberation sessions",
    confidence="CERTAIN",
)
class CausalChainTracker:
    """
    [CITATION: PTKG-CAUSAL] Tracks and queries causal chains in the PTKG.
    
    Causal chains are built from CAUSED edges with causal_weight > 0.
    Each link represents: source_event CAUSED target_event with some probability.
    """

    def __init__(self, graph: PTKG, default_causal_weight: float = 0.7):
        """[CITATION: PTKG-CAUSAL] Initialize causal chain tracker."""
        self.graph = graph
        self.default_causal_weight = default_causal_weight

    def record_event(
        self,
        event_label: str,
        event_type: str = "generic",
        properties: Optional[Dict[str, Any]] = None,
        period_id: Optional[str] = None,
        source_agent_id: Optional[str] = None,
    ) -> PTKGNode:
        """[CITATION: PTKG-CAUSAL] Record an event node in the graph."""
        return self.graph.add_node(
            node_type=NodeType.EVENT,
            label=event_label,
            properties={
                "event_type": event_type,
                **(properties or {}),
            },
            period_id=period_id,
            source_agent_id=source_agent_id,
        )

    def record_cause(
        self,
        cause_node_id: str,
        effect_node_id: str,
        causal_weight: Optional[float] = None,
        period_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[PTKGEdge]:
        """
        [CITATION: PTKG-CAUSAL] Record a causal relationship: cause -> effect.
        
        Args:
            cause_node_id: The causing event/node
            effect_node_id: The affected event/node
            causal_weight: Strength of causality (0.0-1.0)
            period_id: Which period this causal link belongs to
            properties: Additional metadata
        """
        weight = causal_weight if causal_weight is not None else self.default_causal_weight
        return self.graph.add_edge(
            source_id=cause_node_id,
            target_id=effect_node_id,
            edge_type=EdgeType.CAUSED,
            causal_weight=weight,
            period_id=period_id,
            properties=properties or {},
        )

    def record_deliberation_causal_chain(
        self,
        period_id: str,
        proposal_node_id: str,
        argument_node_ids: List[str],
        critique_node_ids: List[str],
        outcome: str,
        source_agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        [CITATION: PTKG-CAUSAL] Record the complete causal chain of a deliberation outcome.
        
        Creates:
        - Outcome event node
        - CAUSED edges from arguments to outcome
        - CAUSED edges from critiques to outcome (with negative weight)
        - CAUSED edge from proposal to outcome
        
        Returns the outcome event node_id and recorded edges.
        """
        outcome_label = f"Outcome: {outcome}"
        outcome_node = self.record_event(
            event_label=outcome_label,
            event_type="deliberation_outcome",
            properties={
                "outcome": outcome,
                "proposal_id": proposal_node_id,
                "argument_count": len(argument_node_ids),
                "critique_count": len(critique_node_ids),
            },
            period_id=period_id,
            source_agent_id=source_agent_id,
        )
        
        recorded_edges = []
        
        for arg_id in argument_node_ids:
            edge = self.record_cause(
                cause_node_id=arg_id,
                effect_node_id=outcome_node.node_id,
                causal_weight=0.6,
                period_id=period_id,
                properties={"role": "supporting_argument"},
            )
            if edge:
                recorded_edges.append(edge.edge_id)
        
        for crit_id in critique_node_ids:
            edge = self.record_cause(
                cause_node_id=crit_id,
                effect_node_id=outcome_node.node_id,
                causal_weight=0.4,
                period_id=period_id,
                properties={"role": "opposing_critique"},
            )
            if edge:
                recorded_edges.append(edge.edge_id)
        
        edge = self.record_cause(
            cause_node_id=proposal_node_id,
            effect_node_id=outcome_node.node_id,
            causal_weight=0.8,
            period_id=period_id,
            properties={"role": "source_proposal"},
        )
        if edge:
            recorded_edges.append(edge.edge_id)
        
        return {
            "outcome_node_id": outcome_node.node_id,
            "outcome": outcome,
            "recorded_edges": recorded_edges,
        }

    def find_causes(
        self,
        effect_node_id: str,
        max_depth: int = 3,
        min_causal_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        [CITATION: PTKG-CAUSAL] Find all causes of a given effect (backward causal search).
        
        Returns a list of cause chains, each with:
        - cause_node_id: The causing node
        - depth: Distance from effect
        - cumulative_weight: Product of causal weights along the path
        - path: List of edge IDs traversed
        """
        if effect_node_id not in self.graph._nodes:
            return []
        
        results = []
        visited: Set[str] = set()
        queue: List[Dict[str, Any]] = [
            {"node_id": effect_node_id, "depth": 0, "cumulative_weight": 1.0, "path": []}
        ]
        
        while queue:
            current = queue.pop(0)
            node_id = current["node_id"]
            depth = current["depth"]
            cum_weight = current["cumulative_weight"]
            path = current["path"]
            
            if depth >= max_depth:
                continue
            
            if node_id in visited:
                continue
            visited.add(node_id)
            
            for edge in self.graph.get_incoming_edges(node_id):
                if edge.edge_type != EdgeType.CAUSED:
                    continue
                if edge.causal_weight < min_causal_weight:
                    continue
                
                new_weight = cum_weight * edge.causal_weight
                new_path = path + [edge.edge_id]
                
                results.append({
                    "cause_node_id": edge.source_id,
                    "effect_node_id": node_id,
                    "depth": depth + 1,
                    "cumulative_weight": new_weight,
                    "path": new_path,
                    "edge_id": edge.edge_id,
                })
                
                queue.append({
                    "node_id": edge.source_id,
                    "depth": depth + 1,
                    "cumulative_weight": new_weight,
                    "path": new_path,
                })
        
        results.sort(key=lambda x: x["cumulative_weight"], reverse=True)
        return results

    def find_effects(
        self,
        cause_node_id: str,
        max_depth: int = 3,
        min_causal_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        [CITATION: PTKG-CAUSAL] Find all effects of a given cause (forward causal search).
        """
        if cause_node_id not in self.graph._nodes:
            return []
        
        results = []
        visited: Set[str] = set()
        queue: List[Dict[str, Any]] = [
            {"node_id": cause_node_id, "depth": 0, "cumulative_weight": 1.0, "path": []}
        ]
        
        while queue:
            current = queue.pop(0)
            node_id = current["node_id"]
            depth = current["depth"]
            cum_weight = current["cumulative_weight"]
            path = current["path"]
            
            if depth >= max_depth:
                continue
            
            if node_id in visited:
                continue
            visited.add(node_id)
            
            for edge in self.graph.get_outgoing_edges(node_id):
                if edge.edge_type != EdgeType.CAUSED:
                    continue
                if edge.causal_weight < min_causal_weight:
                    continue
                
                new_weight = cum_weight * edge.causal_weight
                new_path = path + [edge.edge_id]
                
                results.append({
                    "cause_node_id": node_id,
                    "effect_node_id": edge.target_id,
                    "depth": depth + 1,
                    "cumulative_weight": new_weight,
                    "path": new_path,
                    "edge_id": edge.edge_id,
                })
                
                queue.append({
                    "node_id": edge.target_id,
                    "depth": depth + 1,
                    "cumulative_weight": new_weight,
                    "path": new_path,
                })
        
        results.sort(key=lambda x: x["cumulative_weight"], reverse=True)
        return results

    def get_causal_strength(self, cause_node_id: str, effect_node_id: str) -> float:
        """[CITATION: PTKG-CAUSAL] Compute the maximum causal strength between two nodes."""
        effects = self.find_effects(cause_node_id, max_depth=5)
        matching = [e for e in effects if e["effect_node_id"] == effect_node_id]
        if not matching:
            return 0.0
        return max(e["cumulative_weight"] for e in matching)

    def get_cross_session_impact(
        self,
        node_id: str,
        min_causal_weight: float = 0.3,
    ) -> Dict[str, Any]:
        """
        [CITATION: PTKG-CAUSAL] Measure how much impact a node has across sessions.
        
        Returns:
        - direct_effects: Number of nodes directly caused
        - indirect_effects: Number of nodes indirectly caused
        - cross_period_count: Number of distinct periods affected
        - max_causal_depth: Maximum depth of causal influence
        """
        effects = self.find_effects(node_id, max_depth=10, min_causal_weight=min_causal_weight)
        
        direct = [e for e in effects if e["depth"] == 1]
        indirect = [e for e in effects if e["depth"] > 1]
        
        affected_periods = set()
        for e in effects:
            effect_node = self.graph._nodes.get(e["effect_node_id"])
            if effect_node and effect_node.period_id:
                affected_periods.add(effect_node.period_id)
        
        max_depth = max((e["depth"] for e in effects), default=0)
        
        return {
            "node_id": node_id,
            "direct_effects": len(direct),
            "indirect_effects": len(indirect),
            "total_effects": len(effects),
            "cross_period_count": len(affected_periods),
            "max_causal_depth": max_depth,
            "affected_periods": list(affected_periods),
        }

    def find_common_causes(
        self,
        node_ids: List[str],
        max_depth: int = 3,
        min_causal_weight: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        [CITATION: PTKG-CAUSAL] Find common causes shared among multiple effect nodes.
        Useful for identifying shared assumptions or root causes.
        """
        cause_sets: Dict[str, Set[str]] = {}
        
        for nid in node_ids:
            causes = self.find_causes(nid, max_depth, min_causal_weight)
            cause_sets[nid] = set(c["cause_node_id"] for c in causes)
        
        if not cause_sets:
            return []
        
        common = set.intersection(*cause_sets.values()) if cause_sets else set()
        
        results = []
        for cause_id in common:
            cause_node = self.graph._nodes.get(cause_id)
            if cause_node:
                strengths = []
                for nid in node_ids:
                    strength = self.get_causal_strength(cause_id, nid)
                    strengths.append(strength)
                avg_strength = sum(strengths) / len(strengths) if strengths else 0
                
                results.append({
                    "cause_node_id": cause_id,
                    "cause_label": cause_node.label,
                    "affected_nodes": node_ids,
                    "average_causal_strength": avg_strength,
                })
        
        results.sort(key=lambda x: x["average_causal_strength"], reverse=True)
        return results
