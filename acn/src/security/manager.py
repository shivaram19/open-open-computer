# src/security/manager.py
"""
Security manager — composes identity, RBAC, API keys, audit, encryption,
and rate limiting into a single enterprise-facing entry point.

[CITATION: ADR-011]
Enterprise Security Baseline — unified security context for
authentication, authorization, audit, and encryption.
"""

from typing import Any, Dict, List, Optional

from security.identity import Identity, IdentityType
from security.rbac import Permission, RBACAuthorizer, AuthorizationDecision, BY_NAME
from security.api_key import ApiKeyManager, ApiKeyCredential
from security.audit import AuditLogger, AuditCategory, AuditSeverity
from security.encryption import EncryptionManager
from security.rate_limit import RateLimiter
from security.config import SecurityConfig
from shared.utils.citations import cite


@cite(
    key="SECURITY-MANAGER",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Security Manager",
    rationale="Single composition point prevents services from wiring security primitives ad-hoc",
    confidence="CERTAIN",
)
class SecurityManager:
    """Composed security facade for ACN services and agents."""

    def __init__(
        self,
        config: Optional[SecurityConfig] = None,
        api_key_manager: Optional[ApiKeyManager] = None,
        audit_logger: Optional[AuditLogger] = None,
        encryption_manager: Optional[EncryptionManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        self.config = config or SecurityConfig.from_env()
        self.api_keys = api_key_manager or ApiKeyManager()
        self.audit = audit_logger or AuditLogger()
        self.encryption = encryption_manager
        if self.encryption is None and self.config.master_key:
            self.encryption = EncryptionManager(master_key=self.config.master_key.encode())
        self.rate_limiter = rate_limiter or RateLimiter(
            default_limit=self.config.rate_limit_default,
            default_window_seconds=self.config.rate_limit_window_seconds,
            default_burst=self.config.rate_limit_burst,
        )
        self.authorizer = RBACAuthorizer(BY_NAME)

    @cite(
        key="SECURITY-AUTHENTICATE-API-KEY",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Authentication",
        rationale="API key authentication maps a validated credential to an Identity",
        confidence="CERTAIN",
    )
    def authenticate_api_key(self, raw_key: str) -> Optional[Identity]:
        """Authenticate a raw API key and return an Identity."""
        credential = self.api_keys.validate(raw_key)
        if credential is None:
            self.audit.log_authn(
                action="api_key_auth",
                actor_id="unknown",
                actor_type="unknown",
                tenant_id="unknown",
                outcome="failure",
                severity=AuditSeverity.WARNING,
            )
            return None

        identity_type = IdentityType(credential.identity_type) if credential.identity_type in {t.value for t in IdentityType} else IdentityType.SERVICE
        identity = Identity(
            id=credential.identity_id,
            type=identity_type,
            name=credential.name,
            tenant_id=credential.tenant_id,
            roles=["service"] if identity_type in (IdentityType.SERVICE, IdentityType.AGENT) else [],
            auth_method="api_key",
        )
        self.audit.log_authn(
            action="api_key_auth",
            actor_id=identity.id,
            actor_type=identity.type.value,
            tenant_id=identity.tenant_id,
            outcome="success",
            details={"key_id": credential.key_id, "masked": credential.mask()},
        )
        return identity

    @cite(
        key="SECURITY-AUTHORIZE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Authorization",
        rationale="Services call one method to enforce RBAC and emit audit events",
        confidence="CERTAIN",
    )
    def authorize(
        self,
        identity: Identity,
        permission: Permission,
        resource_type: str,
        resource_id: str,
        resource_tenant_id: Optional[str] = None,
    ) -> AuthorizationDecision:
        """Authorize an identity and log the decision."""
        decision = self.authorizer.authorize(
            identity_id=identity.id,
            roles=identity.roles,
            permission=permission,
            tenant_id=identity.tenant_id,
            resource_tenant_id=resource_tenant_id,
        )
        self.audit.log_authz(
            action="authorize",
            actor_id=identity.id,
            actor_type=identity.type.value,
            tenant_id=identity.tenant_id,
            outcome="allowed" if decision.allowed else "denied",
            resource_type=resource_type,
            resource_id=resource_id,
            details=decision.to_audit_dict(),
            severity=AuditSeverity.INFO if decision.allowed else AuditSeverity.WARNING,
        )
        return decision

    def check_rate_limit(self, key: str) -> bool:
        """Check whether the key is within its rate limit."""
        if not self.config.rate_limit_enabled:
            return True
        return self.rate_limiter.check(key).allowed

    def encrypt(self, tenant_id: str, plaintext: bytes, **kwargs) -> Optional[Dict[str, Any]]:
        """Encrypt data if encryption is configured."""
        if self.encryption is None:
            return None
        return self.encryption.encrypt(tenant_id, plaintext, **kwargs)

    def decrypt(self, envelope: Dict[str, Any]) -> Optional[bytes]:
        """Decrypt an envelope if encryption is configured."""
        if self.encryption is None:
            return None
        return self.encryption.decrypt(envelope)
