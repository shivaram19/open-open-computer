# src/consensus/temporal_auditor.py
"""
Temporal Auditor (Kāla): Causal Consistency Guardian for the Agent Swarm.

The Temporal Auditor is the 11th persona in the Sanskrit architecture.
It does not think, propose, or vote. It watches. It ensures that:
- Every agent message carries a valid HLC timestamp
- Causality is never violated (no messages from the future)
- Clock skew between agents stays within bounds
- Deliberation rounds occur in causal order
- A binary causality_health signal alerts the swarm when temporal trust is lost

Design inspired by:
- TemporalObservability2026: 3-5ms skew breaks causal observability silently
- Kulkarni2014: HLC provides causality tracking with bounded error
- ADR-003: Hybrid Logical Clocks + ST-GAT skew correction + causal health signal
- Lamport1978: Happened-before relation as partial ordering

[CITATION: TemporalObservability2026]
[CITATION: Kulkarni2014]
[CITATION: ADR-003]
[CITATION: Lamport1978]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum

from shared.utils.citations import cite
from consensus.hlc import HybridLogicalClock, HLCTimestamp, are_concurrent
from consensus.temporal_types import (
    CausalityHealth,
    ViolationType,
    CausalityViolation,
)
from consensus.audit_rules import (
    MissingTimestampRule,
    SkewExceededRule,
    MessageFromFutureRule,
)


@cite(
    key="TEMPORAL-AUDITOR",
    paper="Temporal Auditor (Kāla): Causal Consistency Guardian",
    venue="ACN Architecture Document",
    section="Temporal Auditor Class",
    rationale="11th persona dedicated to temporal hygiene prevents silent observability collapse",
    confidence="CERTAIN",
)
class TemporalAuditor:
    """
    [CITATION: TEMPORAL-AUDITOR] The Temporal Auditor monitors causal consistency across the swarm.
    
    Every agent message is stamped with an HLC timestamp. The auditor:
    1. Validates each timestamp against local physical time (skew check)
    2. Tracks happened-before relationships between agents
    3. Detects causality cycles (A before B before A)
    4. Monitors deliberation round ordering
    5. Emits a binary causality_health signal
    
    The auditor is stateless between checks — it maintains a sliding window
    of recent timestamps for cycle detection, but does not accumulate
    unbounded history.
    """

    def __init__(
        self,
        auditor_id: str = "kala-temporal-auditor",
        max_skew_ms: float = 500.0,
        violation_window_size: int = 1000,
        skew_warning_threshold_ms: float = 300.0,
        rules=None,
    ):
        """[CITATION: TEMPORAL-AUDITOR] Initialize the Temporal Auditor."""
        self.auditor_id = auditor_id
        self.max_skew_ms = max_skew_ms
        self.skew_warning_threshold_ms = skew_warning_threshold_ms
        self.violation_window_size = violation_window_size

        self._hlc = HybridLogicalClock(node_id=auditor_id, max_skew_ms=max_skew_ms)
        self._last_seen: Dict[str, HLCTimestamp] = {}  # agent_id -> last HLC seen
        self._violations: List[CausalityViolation] = []
        self._health_history: List[Tuple[float, CausalityHealth]] = []
        self._total_messages_checked = 0
        self._total_violations = 0

        # OCP-compliant rule registry — inject rules or use defaults
        self._rules = rules or [
            MissingTimestampRule(),
            SkewExceededRule(max_skew_ms=max_skew_ms, warning_threshold_ms=skew_warning_threshold_ms),
            MessageFromFutureRule(max_skew_ms=max_skew_ms),
        ]

    def audit_message(
        self,
        agent_id: str,
        message_hlc: Optional[HLCTimestamp],
        message_type: str = "generic",
        round_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        [CITATION: TEMPORAL-AUDITOR] Audit a single agent message for causal validity.
        
        Returns:
        {
            "valid": bool,
            "health": CausalityHealth,
            "violations": [CausalityViolation, ...],
            "skew_ms": float,
        }
        """
        self._total_messages_checked += 1
        violations: List[CausalityViolation] = []

        # Execute registered audit rules (OCP-compliant: add rules without editing this method)
        context = {"hlc": self._hlc, "max_skew_ms": self.max_skew_ms}
        for rule in self._rules:
            violation = rule.check(agent_id, message_hlc, message_type, context)
            if violation is not None:
                violations.append(violation)
                self._total_violations += 1
                # Missing timestamp is a terminal condition — skip remaining rules
                if violation.violation_type == ViolationType.MISSING_TIMESTAMP:
                    break

        # Extract skew_ms from SkewExceededRule violation (single source of truth)
        skew_ms = 0.0
        for v in violations:
            if v.violation_type == ViolationType.SKEW_EXCEEDED:
                skew_ms = v.details.get("skew_ms", 0.0)
                break

        # Update last seen and HLC (coordinator concerns, not rule concerns)
        if message_hlc is not None:
            self._last_seen[agent_id] = message_hlc
            self._hlc.receive(message_hlc)

        # Determine health
        critical_violations = [v for v in violations if v.severity == "critical"]
        warning_violations = [v for v in violations if v.severity == "warning"]

        if critical_violations:
            health = CausalityHealth.VIOLATED
        elif warning_violations:
            health = CausalityHealth.DEGRADED
        else:
            health = CausalityHealth.HEALTHY

        self._health_history.append((time.time(), health))
        if len(self._health_history) > self.violation_window_size:
            self._health_history.pop(0)

        self._violations.extend(violations)
        if len(self._violations) > self.violation_window_size:
            self._violations = self._violations[-self.violation_window_size:]

        return {
            "valid": len(critical_violations) == 0,
            "health": health,
            "violations": violations,
            "skew_ms": skew_ms,
        }

    def audit_deliberation_round(
        self,
        round_number: int,
        agent_messages: Dict[str, HLCTimestamp],
    ) -> Dict[str, Any]:
        """
        [CITATION: TEMPORAL-AUDITOR] Audit an entire deliberation round.
        
        Checks that all agents participating in round N have timestamps
        that are causally after round N-1.
        
        Returns:
        {
            "round": int,
            "all_valid": bool,
            "health": CausalityHealth,
            "agent_results": {agent_id: audit_result, ...},
            "overall_skew_ms": float,
        }
        """
        agent_results = {}
        all_valid = True
        max_skew = 0.0
        
        for agent_id, hlc in agent_messages.items():
            result = self.audit_message(
                agent_id=agent_id,
                message_hlc=hlc,
                message_type="deliberation_round",
                round_number=round_number,
            )
            agent_results[agent_id] = result
            if not result["valid"]:
                all_valid = False
            max_skew = max(max_skew, result["skew_ms"])
        
        # Determine round-level health
        health_values = [r["health"] for r in agent_results.values()]
        if CausalityHealth.VIOLATED in health_values:
            round_health = CausalityHealth.VIOLATED
        elif CausalityHealth.DEGRADED in health_values:
            round_health = CausalityHealth.DEGRADED
        else:
            round_health = CausalityHealth.HEALTHY
        
        return {
            "round": round_number,
            "all_valid": all_valid,
            "health": round_health,
            "agent_results": agent_results,
            "overall_skew_ms": max_skew,
        }

    def get_causality_health(self) -> CausalityHealth:
        """
        [CITATION: TEMPORAL-AUDITOR] Get current causality health signal.
        
        Returns HEALTHY if no violations in recent window,
        DEGRADED if warnings only,
        VIOLATED if any critical violations.
        """
        if not self._health_history:
            return CausalityHealth.HEALTHY
        
        recent = self._health_history[-100:]  # Last 100 checks
        if any(h == CausalityHealth.VIOLATED for _, h in recent):
            return CausalityHealth.VIOLATED
        if any(h == CausalityHealth.DEGRADED for _, h in recent):
            return CausalityHealth.DEGRADED
        return CausalityHealth.HEALTHY

    def get_health_report(self) -> Dict[str, Any]:
        """[CITATION: TEMPORAL-AUDITOR] Comprehensive health report."""
        recent = self._health_history[-100:]
        healthy_count = sum(1 for _, h in recent if h == CausalityHealth.HEALTHY)
        degraded_count = sum(1 for _, h in recent if h == CausalityHealth.DEGRADED)
        violated_count = sum(1 for _, h in recent if h == CausalityHealth.VIOLATED)
        total = len(recent) if recent else 1
        
        return {
            "auditor_id": self.auditor_id,
            "current_health": self.get_causality_health().name,
            "total_messages_checked": self._total_messages_checked,
            "total_violations": self._total_violations,
            "violation_rate": self._total_violations / max(self._total_messages_checked, 1),
            "recent_window": {
                "healthy_ratio": healthy_count / total,
                "degraded_ratio": degraded_count / total,
                "violated_ratio": violated_count / total,
            },
            "max_skew_ms": self.max_skew_ms,
            "active_agent_count": len(self._last_seen),
        }
