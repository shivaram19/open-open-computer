# src/consensus/temporal_types.py
"""
Shared temporal types for consensus and audit layers.

Extracted from temporal_auditor.py to break circular imports between
TemporalAuditor and AuditRule implementations.

Research basis:
- Martin (2017): Dependency Rule — shared types belong in the inner layer
- Martin (1996): ISP — clients depend on minimal interfaces

[CITATION: ADR-003]
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="CAUSALITY-HEALTH",
    paper="Temporal Auditor: Causal Consistency Guardian",
    venue="ACN Architecture Document",
    section="Causality Health Signal",
    rationale="Binary health signal surfaces silent observability failures before they become system failures",
    confidence="CERTAIN",
)
class CausalityHealth(Enum):
    """Binary causality health signal."""
    HEALTHY = 1
    VIOLATED = 0
    DEGRADED = -1


@cite(
    key="CAUSALITY-VIOLATION",
    paper="Temporal Auditor: Causal Consistency Guardian",
    venue="ACN Architecture Document",
    section="Violation Types",
    rationale="Explicit violation taxonomy enables targeted remediation",
    confidence="CERTAIN",
)
class ViolationType(Enum):
    """Types of causal violations the auditor detects."""
    MESSAGE_FROM_FUTURE = "message_from_future"
    HAPPENED_BEFORE_CYCLE = "happened_before_cycle"
    SKEW_EXCEEDED = "skew_exceeded"
    MISSING_TIMESTAMP = "missing_timestamp"
    ROUND_ORDER_INVERSION = "round_order_inversion"


@dataclass
class CausalityViolation:
    """A single detected causality violation."""
    violation_type: ViolationType
    agent_id: str
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "warning"
