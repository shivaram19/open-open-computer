# src/security/identity.py
"""
Identity management for ACN.

Every actor — human user, service, or agent — has an Identity.
Identities are the foundation of authentication, authorization, and audit.

[CITATION: NIST800-207]
Zero Trust requires every request to be authenticated and authorized,
regardless of network location.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from shared.utils.citations import cite


@cite(
    key="IDENTITY-TYPE",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Identity Types",
    rationale="Different actor types require different authentication and lifecycle policies",
    confidence="CERTAIN",
)
class IdentityType(Enum):
    """Kinds of actors in the ACN system."""
    HUMAN = "human"           # Authenticated via OIDC
    SERVICE = "service"       # Authenticated via API key or mTLS
    AGENT = "agent"           # Authenticated via API key or mTLS
    SYSTEM = "system"         # Internal system processes


@cite(
    key="IDENTITY",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Identity Model",
    rationale="Immutable identity carries authentication metadata and tenant context",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class Identity:
    """
    A verified identity in the ACN system.

    Identities are created after successful authentication. They are
    immutable and carry the minimal context needed for authorization
    and audit decisions.
    """
    id: str
    type: IdentityType
    name: str
    tenant_id: str
    roles: List[str] = field(default_factory=list)
    claims: Dict[str, Any] = field(default_factory=dict)
    auth_method: str = "unknown"  # e.g., "oidc", "api_key", "mTLS"
    session_id: Optional[str] = None

    def is_human(self) -> bool:
        return self.type == IdentityType.HUMAN

    def is_service(self) -> bool:
        return self.type == IdentityType.SERVICE

    def is_agent(self) -> bool:
        return self.type == IdentityType.AGENT

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def to_audit_dict(self) -> Dict[str, Any]:
        return {
            "identity_id": self.id,
            "identity_type": self.type.value,
            "identity_name": self.name,
            "tenant_id": self.tenant_id,
            "roles": self.roles,
            "auth_method": self.auth_method,
            "session_id": self.session_id,
        }
