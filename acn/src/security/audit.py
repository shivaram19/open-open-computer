# src/security/audit.py
"""
Tamper-evident audit logging for ACN.

Every security-relevant event is appended to an immutable chain of
audit records. Each record hashes the previous record's hash,
forming a simple hash chain that makes undetected tampering hard.

[CITATION: ADR-011]
Enterprise Security Baseline — append-only, structured audit logs
for compliance, forensics, and trust-but-verify operations.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from shared.utils.citations import cite


@cite(
    key="AUDIT-SEVERITY",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Audit Logging",
    rationale="Severity levels map to SIEM alerting and retention policies",
    confidence="CERTAIN",
)
class AuditSeverity(Enum):
    """Severity classification for audit events."""
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"


@cite(
    key="AUDIT-CATEGORY",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Audit Logging",
    rationale="Categories group events for compliance reporting",
    confidence="CERTAIN",
)
class AuditCategory(Enum):
    """Categories of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    API_KEY = "api_key"
    IDENTITY = "identity"
    POLICY = "policy"
    ENCRYPTION = "encryption"
    AGENT = "agent"
    MEMORY = "memory"
    GRAPH = "graph"
    INFRA = "infra"
    CONFIG = "config"
    SYSTEM = "system"


@cite(
    key="AUDIT-EVENT",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Audit Logging",
    rationale="Structured immutable event captures who, what, when, where, and outcome",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class AuditEvent:
    """A single immutable audit event."""
    event_id: str
    timestamp: str  # ISO 8601 UTC
    category: str
    severity: str
    action: str
    actor_id: str
    actor_type: str
    tenant_id: str
    outcome: str  # "success" | "failure" | "denied" | "error"
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    previous_hash: str
    event_hash: str
    chain_hash: str


@cite(
    key="AUDIT-LOGGER",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Audit Logging",
    rationale="Hash-chained logger makes tampering detectable and supports retention",
    confidence="CERTAIN",
)
class AuditLogger:
    """Append-only tamper-evident audit logger."""

    def __init__(
        self,
        sink: Optional[Callable[[AuditEvent], None]] = None,
        initial_hash: str = "0" * 64,
    ):
        self._records: List[AuditEvent] = []
        self._sink = sink
        self._previous_hash = initial_hash

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _hash(data: Dict[str, Any]) -> str:
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @cite(
        key="AUDIT-LOG",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Audit Logging",
        rationale="Every event is hashed and chained to previous event",
        confidence="CERTAIN",
    )
    def log(
        self,
        category: AuditCategory,
        severity: AuditSeverity,
        action: str,
        actor_id: str,
        actor_type: str,
        tenant_id: str,
        outcome: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """Append a new audit event to the chain."""
        event_id = str(uuid.uuid4())
        timestamp = self._now()
        payload = {
            "event_id": event_id,
            "timestamp": timestamp,
            "category": category.value,
            "severity": severity.value,
            "action": action,
            "actor_id": actor_id,
            "actor_type": actor_type,
            "tenant_id": tenant_id,
            "outcome": outcome,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "previous_hash": self._previous_hash,
        }
        event_hash = self._hash(payload)
        chain_hash = self._hash({"previous": self._previous_hash, "event": event_hash})

        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            category=category.value,
            severity=severity.value,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            tenant_id=tenant_id,
            outcome=outcome,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            previous_hash=self._previous_hash,
            event_hash=event_hash,
            chain_hash=chain_hash,
        )
        self._records.append(event)
        self._previous_hash = chain_hash
        if self._sink:
            self._sink(event)
        return event

    def log_identity(
        self,
        action: str,
        actor_id: str,
        actor_type: str,
        tenant_id: str,
        outcome: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
    ) -> AuditEvent:
        return self.log(
            category=AuditCategory.IDENTITY,
            severity=severity,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            tenant_id=tenant_id,
            outcome=outcome,
            resource_type="identity",
            resource_id=resource_id,
            details=details,
        )

    def log_authn(
        self,
        action: str,
        actor_id: str,
        actor_type: str,
        tenant_id: str,
        outcome: str,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
    ) -> AuditEvent:
        return self.log(
            category=AuditCategory.AUTHENTICATION,
            severity=severity,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            tenant_id=tenant_id,
            outcome=outcome,
            resource_type="session",
            resource_id=actor_id,
            details=details,
        )

    def log_authz(
        self,
        action: str,
        actor_id: str,
        actor_type: str,
        tenant_id: str,
        outcome: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
    ) -> AuditEvent:
        return self.log(
            category=AuditCategory.AUTHORIZATION,
            severity=severity,
            action=action,
            actor_id=actor_id,
            actor_type=actor_type,
            tenant_id=tenant_id,
            outcome=outcome,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
        )

    def get_records(
        self,
        category: Optional[AuditCategory] = None,
        severity: Optional[AuditSeverity] = None,
        actor_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AuditEvent]:
        """Filter records. Does not mutate the chain."""
        results = list(self._records)
        if category:
            results = [r for r in results if r.category == category.value]
        if severity:
            results = [r for r in results if r.severity == severity.value]
        if actor_id:
            results = [r for r in results if r.actor_id == actor_id]
        if tenant_id:
            results = [r for r in results if r.tenant_id == tenant_id]
        return results

    def verify_chain(self) -> Dict[str, Any]:
        """Verify the integrity of the hash chain."""
        if not self._records:
            return {"valid": True, "records": 0, "first_hash": None, "last_hash": None}

        previous_hash = self._records[0].previous_hash
        for idx, record in enumerate(self._records):
            if record.previous_hash != previous_hash:
                return {
                    "valid": False,
                    "broken_at_index": idx,
                    "expected_previous": previous_hash,
                    "actual_previous": record.previous_hash,
                }
            payload = {
                "event_id": record.event_id,
                "timestamp": record.timestamp,
                "category": record.category,
                "severity": record.severity,
                "action": record.action,
                "actor_id": record.actor_id,
                "actor_type": record.actor_type,
                "tenant_id": record.tenant_id,
                "outcome": record.outcome,
                "resource_type": record.resource_type,
                "resource_id": record.resource_id,
                "details": record.details,
                "previous_hash": record.previous_hash,
            }
            expected_event_hash = self._hash(payload)
            if record.event_hash != expected_event_hash:
                return {
                    "valid": False,
                    "broken_at_index": idx,
                    "reason": "event_hash_mismatch",
                    "expected": expected_event_hash,
                    "actual": record.event_hash,
                }
            expected_chain_hash = self._hash({"previous": previous_hash, "event": record.event_hash})
            if record.chain_hash != expected_chain_hash:
                return {
                    "valid": False,
                    "broken_at_index": idx,
                    "reason": "chain_hash_mismatch",
                    "expected": expected_chain_hash,
                    "actual": record.chain_hash,
                }
            previous_hash = record.chain_hash

        return {
            "valid": True,
            "records": len(self._records),
            "first_hash": self._records[0].previous_hash,
            "last_hash": self._records[-1].chain_hash,
        }
