# src/security/__init__.py
"""
Enterprise security baseline for ACN.

Provides:
- Identity management (users, services, agents)
- Role-based access control (RBAC)
- API key lifecycle (create, hash, validate, rotate, revoke)
- Audit logging (tamper-evident structured logs)
- Encryption utilities (at-rest and in-transit primitives)
- Rate limiting and resource controls

[CITATION: ADR-011]
Enterprise Security Baseline — OIDC/OAuth2 for humans,
API keys for services/agents, mTLS encouraged for service mesh.
"""

from security.identity import Identity, IdentityType
from security.rbac import Role, Permission, AuthorizationDecision
from security.api_key import ApiKeyManager, ApiKeyCredential
from security.audit import AuditLogger, AuditEvent
from security.encryption import EncryptionManager, DataEncryptionKey
from security.rate_limit import RateLimiter, RateLimitResult
from security.config import SecurityConfig
from security.manager import SecurityManager

__all__ = [
    "Identity",
    "IdentityType",
    "Role",
    "Permission",
    "AuthorizationDecision",
    "ApiKeyManager",
    "ApiKeyCredential",
    "AuditLogger",
    "AuditEvent",
    "EncryptionManager",
    "DataEncryptionKey",
    "RateLimiter",
    "RateLimitResult",
    "SecurityConfig",
    "SecurityManager",
]
