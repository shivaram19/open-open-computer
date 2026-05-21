# acn/dashboard/data_collector.py
"""
DashboardDataCollector: Export L0-L3 memory state for real-time visualization.

Collects layered memory data from TwinMemoryProfile instances and writes
a JSON snapshot that the Streamlit dashboard reads.

Usage:
    collector = DashboardDataCollector(".acn_dashboard_state.json")
    collector.collect_from_swarm(orchestrator)
    collector.save()

[CITATION: LAYERED-MEMORY]
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from shared.utils.citations import cite


@cite(
    key="DASHBOARD-COLLECTOR",
    paper="ACN Dashboard: Real-Time Layered Memory Observability",
    venue="ACN Architecture Document",
    section="Dashboard Data Pipeline",
    rationale="JSON snapshot bridge between runtime memory and Streamlit visualization",
    confidence="HIGH",
)
class DashboardDataCollector:
    """
    Collects layered memory state from twins and exports for dashboard rendering.
    """

    def __init__(self, state_path: Optional[str] = None):
        self.state_path = Path(state_path) if state_path else Path(".acn_dashboard_state.json")
        self._state: Dict[str, Any] = {
            "version": "1.0",
            "last_updated": 0.0,
            "twins": {},
            "swarm": {
                "total_twins": 0,
                "total_l0_traces": 0,
                "total_l1_atoms": 0,
                "total_l2_scenarios": 0,
                "total_l3_personas": 0,
            },
            "consensus": {
                "score": 0.0,
                "round": 0,
                "academic_support": 0.0,
                "dissent_detected": False,
            },
            "recent_events": [],
        }

    def collect_from_swarm(self, orchestrator) -> None:
        """Collect L0-L3 data from all agents in a SwarmOrchestrator."""
        for agent_id, agent in orchestrator.agents.items():
            if hasattr(agent, "layered_memory") and agent.layered_memory is not None:
                self._collect_from_twin(agent_id, agent)
            elif hasattr(agent, "memory"):
                # Fallback: collect flat memory stats
                self._collect_flat_memory(agent_id, agent)

        # Update swarm aggregates
        self._update_swarm_aggregates()

    def collect_from_executor(self, executor) -> None:
        """Collect data from an AutonomousExecutor's orchestrator."""
        if hasattr(executor, "orchestrator"):
            self.collect_from_swarm(executor.orchestrator)

    def collect_vm_stats(self, vm_cluster) -> None:
        """Collect VM cluster health and hibernation stats."""
        stats = vm_cluster.get_swarm_stats()
        self._state["vm_cluster"] = {
            "total_twins": stats.get("total_twins", 0),
            "active": stats.get("active", 0),
            "hibernated": stats.get("hibernated", 0),
            "destroyed": stats.get("destroyed", 0),
            "total_thinks": stats.get("total_thinks", 0),
            "total_hibernates": stats.get("total_hibernates", 0),
            "total_checkpoints": stats.get("total_checkpoints", 0),
            "total_compute_time_ms": stats.get("total_compute_time_ms", 0.0),
            "twins": stats.get("twins", []),
        }

    def _collect_from_twin(self, agent_id: str, agent) -> None:
        """Extract L0-L3 data from a single TwinAgent."""
        profile = agent.layered_memory
        stats = profile.get_stats()

        # L0: Recent conversation traces
        l0_ctx = profile.layered.retrieve_context("", limit_per_layer=5)
        l0_traces = [
            {
                "trace_id": t.get("trace_id", ""),
                "timestamp": t.get("timestamp", 0),
                "content_preview": str(t.get("content", ""))[:200],
            }
            for t in l0_ctx.l0_traces
        ]

        # L1-L3: Retrieve context once
        l1_ctx = profile.layered.retrieve_context("", limit_per_layer=10)
        l1_atoms = [
            {
                "atom_id": a.get("atom_id", ""),
                "atom_type": a.get("atom_type", ""),
                "content": a.get("content", ""),
                "confidence": a.get("confidence", 0),
                "tags": a.get("tags", []),
            }
            for a in l1_ctx.l1_atoms[:10]
        ]

        # L2: Scenarios
        l2_scenarios = [
            {
                "pattern_id": s.get("pattern_id", ""),
                "template": s.get("template", ""),
                "support_count": s.get("support_count", 0),
                "confidence": s.get("confidence", 0),
                "context_keywords": s.get("context_keywords", []),
            }
            for s in l1_ctx.l2_scenarios[:10]
        ]

        # L3: Persona
        l3_persona = None
        if l1_ctx.l3_persona:
            p = l1_ctx.l3_persona
            l3_persona = {
                "persona_id": p.get("persona_id", ""),
                "version": p.get("version", 1),
                "confidence_map": p.get("confidence_map", {}),
                "heuristic_evidence": p.get("heuristic_evidence", {}),
                "bias_manifestations": p.get("bias_manifestations", {}),
                "expertise_boundaries": p.get("expertise_boundaries", {}),
            }

        self._state["twins"][agent_id] = {
            "agent_id": agent_id,
            "name": getattr(agent, "name", agent_id),
            "cluster": getattr(agent, "cluster", "unknown"),
            "twin_id": getattr(agent, "twin", None) and getattr(agent.twin, "TWIN_ID", ""),
            "twin_name": getattr(agent, "twin", None) and getattr(agent.twin, "NAME", ""),
            "stats": stats,
            "l0_traces": l0_traces,
            "l1_atoms": l1_atoms,
            "l2_scenarios": l2_scenarios,
            "l3_persona": l3_persona,
            "layer_counts": {
                "l0": stats.get("l0_conversation", 0),
                "l1": stats.get("l1_atoms", 0),
                "l2": stats.get("l2_scenarios", 0),
                "l3": stats.get("l3_personas", 0),
            },
        }

    def _collect_flat_memory(self, agent_id: str, agent) -> None:
        """Fallback: collect flat memory stats when layered memory is unavailable."""
        memory_stats = agent.memory.get_memory_stats() if hasattr(agent, "memory") else {}
        self._state["twins"][agent_id] = {
            "agent_id": agent_id,
            "name": getattr(agent, "name", agent_id),
            "cluster": getattr(agent, "cluster", "unknown"),
            "stats": memory_stats,
            "l0_traces": [],
            "l1_atoms": [],
            "l2_scenarios": [],
            "l3_persona": None,
            "layer_counts": {
                "l0": memory_stats.get("episodic_count", 0),
                "l1": 0,
                "l2": 0,
                "l3": 0,
            },
            "flat_memory": True,
        }

    def _update_swarm_aggregates(self) -> None:
        """Compute swarm-level aggregates from individual twin data."""
        twins = self._state["twins"]
        self._state["swarm"] = {
            "total_twins": len(twins),
            "total_l0_traces": sum(t.get("layer_counts", {}).get("l0", 0) for t in twins.values()),
            "total_l1_atoms": sum(t.get("layer_counts", {}).get("l1", 0) for t in twins.values()),
            "total_l2_scenarios": sum(t.get("layer_counts", {}).get("l2", 0) for t in twins.values()),
            "total_l3_personas": sum(t.get("layer_counts", {}).get("l3", 0) for t in twins.values()),
        }

    def record_consensus(self, score: float, round_num: int, academic_support: float = 0.0, dissent: bool = False) -> None:
        """Record a consensus event."""
        self._state["consensus"] = {
            "score": score,
            "round": round_num,
            "academic_support": academic_support,
            "dissent_detected": dissent,
        }
        self._state["recent_events"].append({
            "type": "consensus",
            "timestamp": time.time(),
            "score": score,
            "round": round_num,
        })
        # Keep only last 50 events
        self._state["recent_events"] = self._state["recent_events"][-50:]

    def record_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record a generic event."""
        self._state["recent_events"].append({
            "type": event_type,
            "timestamp": time.time(),
            **data,
        })
        self._state["recent_events"] = self._state["recent_events"][-50:]

    def save(self) -> None:
        """Write state to disk."""
        self._state["last_updated"] = time.time()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2, default=str)

    def load(self) -> Dict[str, Any]:
        """Load state from disk (for dashboard use)."""
        if self.state_path.exists():
            with open(self.state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._state

    @staticmethod
    def load_for_dashboard(state_path: Optional[str] = None) -> Dict[str, Any]:
        """Static helper for dashboard to load state without instantiating collector."""
        path = Path(state_path) if state_path else Path(".acn_dashboard_state.json")
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "version": "1.0",
            "last_updated": 0.0,
            "twins": {},
            "swarm": {"total_twins": 0, "total_l0_traces": 0, "total_l1_atoms": 0, "total_l2_scenarios": 0, "total_l3_personas": 0},
            "consensus": {"score": 0.0, "round": 0, "academic_support": 0.0, "dissent_detected": False},
            "recent_events": [],
        }
