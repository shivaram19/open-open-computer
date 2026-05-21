# src/consensus/audit_rules.py
"""
AuditRule Protocol and Implementations.

Extracts hardcoded checks from TemporalAuditor.audit_message() into
self-contained, polymorphic rule classes registered in a list.

Research basis:
- Meyer (1988): OCP — open for extension, closed for modification
- Martin (1996): SRP — each rule has one reason to change
- Feathers (2004): Seam model — rules are seams where behavior can vary

[CITATION: Kulkarni2014]
[CITATION: TemporalObservability2026]
"""

import time
from typing import Protocol, Dict, List, Optional, Any

from shared.utils.citations import cite
from consensus.temporal_types import CausalityViolation, ViolationType


class AuditRule(Protocol):
    """
    Protocol for a single temporal-audit rule.

    Each rule checks one specific causality concern. Rules are stateless
    and re-entrant — the TemporalAuditor holds all mutable state.
    """

    def check(
        self,
        agent_id: str,
        message_hlc: Optional[Any],
        message_type: str,
        context: Dict[str, Any],
    ) -> Optional[CausalityViolation]: ...


@cite(
    key="AUDIT-MISSING-TIMESTAMP",
    paper="Temporal Auditor: Missing Timestamp Rule",
    venue="ACN Architecture Document",
    section="Temporal Consistency",
    rationale="Every message must carry an HLC timestamp for causality tracking",
    confidence="CERTAIN",
)
class MissingTimestampRule:
    """Rule 1: Every message must carry a timestamp."""

    def check(self, agent_id, message_hlc, message_type, context):
        if message_hlc is None:
            return CausalityViolation(
                violation_type=ViolationType.MISSING_TIMESTAMP,
                agent_id=agent_id,
                timestamp=time.time(),
                details={"message_type": message_type},
                severity="critical",
            )
        return None


@cite(
    key="AUDIT-SKEW-EXCEEDED",
    paper="Temporal Auditor: Clock Skew Rule",
    venue="ACN Architecture Document",
    section="Temporal Consistency",
    rationale="Clock skew beyond threshold breaks causal observability silently",
    confidence="CERTAIN",
)
class SkewExceededRule:
    """Rule 2: Clock skew between sender and receiver must be bounded."""

    def __init__(self, max_skew_ms: float = 500.0, warning_threshold_ms: float = 250.0):
        self.max_skew_ms = max_skew_ms
        self.warning_threshold_ms = warning_threshold_ms

    def check(self, agent_id, message_hlc, message_type, context):
        if message_hlc is None:
            return None

        hlc = context.get("hlc")
        if hlc is None:
            return None

        is_skewed, skew_ms = hlc.detect_skew(message_hlc)
        if is_skewed:
            return CausalityViolation(
                violation_type=ViolationType.SKEW_EXCEEDED,
                agent_id=agent_id,
                timestamp=time.time(),
                details={
                    "skew_ms": skew_ms,
                    "max_skew_ms": self.max_skew_ms,
                    "message_hlc": str(message_hlc),
                },
                severity="critical",
            )
        elif skew_ms > self.warning_threshold_ms:
            return CausalityViolation(
                violation_type=ViolationType.SKEW_EXCEEDED,
                agent_id=agent_id,
                timestamp=time.time(),
                details={
                    "skew_ms": skew_ms,
                    "threshold_ms": self.warning_threshold_ms,
                    "message_hlc": str(message_hlc),
                },
                severity="warning",
            )
        return None


@cite(
    key="AUDIT-MESSAGE-FROM-FUTURE",
    paper="Temporal Auditor: Message From Future Rule",
    venue="ACN Architecture Document",
    section="Temporal Consistency",
    rationale="Messages with timestamps in the future violate causality",
    confidence="CERTAIN",
)
class MessageFromFutureRule:
    """Rule 3: A message cannot originate from the future."""

    def __init__(self, max_skew_ms: float = 500.0):
        self.max_skew_ms = max_skew_ms

    def check(self, agent_id, message_hlc, message_type, context):
        if message_hlc is None:
            return None

        local_now = time.time()
        if message_hlc.pt > local_now + (self.max_skew_ms / 1000.0):
            return CausalityViolation(
                violation_type=ViolationType.MESSAGE_FROM_FUTURE,
                agent_id=agent_id,
                timestamp=time.time(),
                details={
                    "message_pt": message_hlc.pt,
                    "local_now": local_now,
                    "delta_s": message_hlc.pt - local_now,
                },
                severity="critical",
            )
        return None
