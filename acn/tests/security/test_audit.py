# acn/tests/security/test_audit.py
"""Tests for tamper-evident audit logging."""

import pytest
from security.audit import AuditLogger, AuditCategory, AuditSeverity


def test_log_event():
    logger = AuditLogger()
    event = logger.log(
        category=AuditCategory.AUTHENTICATION,
        severity=AuditSeverity.INFO,
        action="login",
        actor_id="user-1",
        actor_type="human",
        tenant_id="t-1",
        outcome="success",
        resource_type="session",
        resource_id="sess-1",
    )
    assert event.event_id
    assert event.category == "authentication"
    assert event.outcome == "success"
    assert event.chain_hash


def test_chain_integrity():
    logger = AuditLogger()
    logger.log(
        category=AuditCategory.AUTHENTICATION,
        severity=AuditSeverity.INFO,
        action="login",
        actor_id="user-1",
        actor_type="human",
        tenant_id="t-1",
        outcome="success",
        resource_type="session",
        resource_id="sess-1",
    )
    logger.log(
        category=AuditCategory.AUTHORIZATION,
        severity=AuditSeverity.INFO,
        action="access_agent",
        actor_id="user-1",
        actor_type="human",
        tenant_id="t-1",
        outcome="allowed",
        resource_type="agent",
        resource_id="agent-1",
    )
    result = logger.verify_chain()
    assert result["valid"]
    assert result["records"] == 2


def test_chain_detects_tampering():
    logger = AuditLogger()
    logger.log(
        category=AuditCategory.AUTHENTICATION,
        severity=AuditSeverity.INFO,
        action="login",
        actor_id="user-1",
        actor_type="human",
        tenant_id="t-1",
        outcome="success",
        resource_type="session",
        resource_id="sess-1",
    )
    # Tamper with the stored record.
    logger._records[0].details["evil"] = True
    result = logger.verify_chain()
    assert not result["valid"]


def test_filter_records():
    logger = AuditLogger()
    logger.log(
        category=AuditCategory.AUTHENTICATION,
        severity=AuditSeverity.INFO,
        action="login",
        actor_id="user-1",
        actor_type="human",
        tenant_id="t-1",
        outcome="success",
        resource_type="session",
        resource_id="sess-1",
    )
    logger.log(
        category=AuditCategory.AUTHORIZATION,
        severity=AuditSeverity.INFO,
        action="deny",
        actor_id="user-2",
        actor_type="human",
        tenant_id="t-2",
        outcome="denied",
        resource_type="agent",
        resource_id="agent-1",
    )
    assert len(logger.get_records(category=AuditCategory.AUTHENTICATION)) == 1
    assert len(logger.get_records(actor_id="user-1")) == 1
    assert len(logger.get_records(tenant_id="t-2")) == 1
    assert len(logger.get_records()) == 2


def test_sink_called():
    sink_events = []
    logger = AuditLogger(sink=sink_events.append)
    logger.log(
        category=AuditCategory.SYSTEM,
        severity=AuditSeverity.WARNING,
        action="test",
        actor_id="system",
        actor_type="system",
        tenant_id="t-1",
        outcome="success",
        resource_type="system",
        resource_id="system",
    )
    assert len(sink_events) == 1
    assert sink_events[0].action == "test"
