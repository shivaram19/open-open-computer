"""
TDD Tests for Phase 4.1 — TemporalAuditor backward-compat skew removal.

Verifies that skew_ms in the audit result comes from SkewExceededRule,
not from redundant inline computation.
"""

import time
import pytest

from consensus.temporal_auditor import TemporalAuditor
from consensus.hlc import HybridLogicalClock, HLCTimestamp
from consensus.temporal_types import CausalityHealth, ViolationType


class TestTemporalAuditorSkewSource:
    """Verify skew_ms comes from rules, not backward-compat computation."""

    def test_skew_ms_zero_when_no_skew(self):
        """When no skew violation occurs, skew_ms should be 0.0."""
        auditor = TemporalAuditor(auditor_id="test", max_skew_ms=10000.0)
        now = auditor._hlc.now()
        result = auditor.audit_message("node-b", now)
        assert result["skew_ms"] == 0.0
        assert result["health"] == CausalityHealth.HEALTHY

    def test_skew_ms_present_when_skew_exceeded(self):
        """When skew is exceeded, skew_ms should be positive in result."""
        auditor = TemporalAuditor(auditor_id="test", max_skew_ms=10.0)
        # Create a timestamp far in the future to trigger skew
        future_ts = HLCTimestamp(pt=time.time() + 10, lc=0, node_id="node-b")

        result = auditor.audit_message("node-b", future_ts)

        assert result["skew_ms"] > 0.0
        assert result["health"] == CausalityHealth.VIOLATED
        skew_violations = [
            v for v in result["violations"]
            if v.violation_type == ViolationType.SKEW_EXCEEDED
        ]
        assert len(skew_violations) == 1
        # The skew_ms in result must match the violation's recorded skew
        assert result["skew_ms"] == skew_violations[0].details["skew_ms"]

    def test_skew_ms_zero_for_missing_timestamp(self):
        """Missing timestamp should yield skew_ms = 0.0 (no skew to measure)."""
        auditor = TemporalAuditor(auditor_id="test", max_skew_ms=1000.0)
        result = auditor.audit_message("node-b", None)
        assert result["skew_ms"] == 0.0
        assert any(
            v.violation_type == ViolationType.MISSING_TIMESTAMP
            for v in result["violations"]
        )
