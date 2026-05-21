"""
TDD Tests for AuditRule Protocol and Registry.

Drives the extraction of hardcoded checks from TemporalAuditor.audit_message()
into polymorphic AuditRule classes.

Research basis:
- Meyer (1988): OCP — open for extension, closed for modification
- Feathers (2004): Seam model — alter behavior without editing in place
"""

import time
import pytest

from consensus.temporal_auditor import (
    TemporalAuditor,
    CausalityViolation,
    ViolationType,
    CausalityHealth,
)
from consensus.hlc import HybridLogicalClock, HLCTimestamp


class TestAuditRuleProtocol:
    """Tests for the AuditRule abstraction."""

    def test_audit_rule_protocol_exists(self):
        """An AuditRule protocol must exist."""
        from consensus.audit_rules import AuditRule
        assert AuditRule is not None

    def test_missing_timestamp_rule_exists(self):
        """MissingTimestampRule must detect missing timestamps."""
        from consensus.audit_rules import MissingTimestampRule
        rule = MissingTimestampRule()
        violation = rule.check(agent_id="a1", message_hlc=None, message_type="test", context={})
        assert violation is not None
        assert violation.violation_type == ViolationType.MISSING_TIMESTAMP
        assert violation.severity == "critical"

    def test_missing_timestamp_rule_passes_when_timestamp_present(self):
        """MissingTimestampRule must return None when timestamp exists."""
        from consensus.audit_rules import MissingTimestampRule
        rule = MissingTimestampRule()
        hlc = HybridLogicalClock(node_id="a1").now()
        violation = rule.check(agent_id="a1", message_hlc=hlc, message_type="test", context={})
        assert violation is None

    def test_skew_exceeded_rule_exists(self):
        """SkewExceededRule must detect clock skew."""
        from consensus.audit_rules import SkewExceededRule
        from consensus.hlc import HybridLogicalClock
        rule = SkewExceededRule(max_skew_ms=1000)
        # Create a timestamp with huge skew relative to a local HLC
        hlc = HybridLogicalClock(node_id="local")
        hlc_now = hlc.now()
        future_hlc = HLCTimestamp(pt=hlc_now.pt + 10, lc=0, node_id="a1")
        violation = rule.check(agent_id="a1", message_hlc=future_hlc, message_type="test", context={"hlc": hlc})
        assert violation is not None
        assert violation.violation_type == ViolationType.SKEW_EXCEEDED

    def test_message_from_future_rule_exists(self):
        """MessageFromFutureRule must detect messages from the future."""
        from consensus.audit_rules import MessageFromFutureRule
        rule = MessageFromFutureRule(max_skew_ms=1000)
        future_hlc = HLCTimestamp(pt=time.time() + 10, lc=0, node_id="a1")
        violation = rule.check(agent_id="a1", message_hlc=future_hlc, message_type="test", context={})
        assert violation is not None
        assert violation.violation_type == ViolationType.MESSAGE_FROM_FUTURE


class TestTemporalAuditorUsesRules:
    """Tests that TemporalAudit delegates to registered AuditRules."""

    def test_auditor_has_default_rules(self):
        """TemporalAuditor must initialize with default rules."""
        from consensus.audit_rules import MissingTimestampRule
        auditor = TemporalAuditor(auditor_id="test")
        assert len(auditor._rules) > 0
        assert any(isinstance(r, MissingTimestampRule) for r in auditor._rules)

    def test_auditor_delegates_to_rules(self):
        """TemporalAuditor.audit_message must execute registered rules."""
        spy_called = False

        class SpyRule:
            def check(self, agent_id, message_hlc, message_type, context):
                nonlocal spy_called
                spy_called = True
                return None

        auditor = TemporalAuditor(auditor_id="test")
        auditor._rules = [SpyRule()]
        hlc = HybridLogicalClock(node_id="a1").now()
        auditor.audit_message("a1", hlc)
        assert spy_called, "TemporalAuditor did NOT execute registered rules"
