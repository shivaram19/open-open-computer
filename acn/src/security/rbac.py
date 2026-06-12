# src/security/rbac.py
"""
Role-based access control (RBAC) for ACN.

Permissions describe what actions can be performed.
Roles are named collections of permissions.
Access decisions are made by checking whether an identity's roles
grant the required permission.

[CITATION: ADR-011]
Enterprise Security Baseline — RBAC for authorization,
principle of least privilege, deny-by-default.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Set, Optional, Any
from shared.utils.citations import cite


@cite(
    key="RBAC-PERMISSION",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Authorization Model",
    rationale="Fine-grained action:resource permissions enforce least privilege",
    confidence="CERTAIN",
)
class Permission(Enum):
    """Granular permissions for ACN resources and operations."""
    # Agent permissions
    AGENT_READ = "agent:read"
    AGENT_CREATE = "agent:create"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"
    AGENT_MEMORY_READ = "agent:memory:read"
    AGENT_MEMORY_WRITE = "agent:memory:write"

    # Twin permissions
    TWIN_READ = "twin:read"
    TWIN_CREATE = "twin:create"
    TWIN_DELETE = "twin:delete"
    TWIN_DEPLOY = "twin:deploy"

    # Memory permissions
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    MEMORY_DELETE = "memory:delete"
    MEMORY_EXPORT = "memory:export"

    # Graph permissions
    GRAPH_READ = "graph:read"
    GRAPH_WRITE = "graph:write"
    GRAPH_QUERY = "graph:query"

    # Audit permissions
    AUDIT_READ = "audit:read"
    AUDIT_EXPORT = "audit:export"

    # Security admin permissions
    SECURITY_MANAGE = "security:manage"
    POLICY_MANAGE = "policy:manage"
    API_KEY_MANAGE = "api_key:manage"
    IDENTITY_MANAGE = "identity:manage"

    # Infrastructure permissions
    INFRA_READ = "infra:read"
    INFRA_MODIFY = "infra:modify"
    CONFIG_READ = "config:read"
    CONFIG_WRITE = "config:write"


@cite(
    key="RBAC-ROLE",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Authorization Model",
    rationale="Named role bundles permissions for common enterprise personas",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class Role:
    """A named role bundling permissions."""
    name: str
    description: str
    permissions: Set[Permission]
    tenant_scoped: bool = True
    is_system_role: bool = False

    def grants(self, permission: Permission) -> bool:
        return permission in self.permissions


@cite(
    key="RBAC-DECISION",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Authorization Model",
    rationale="Explicit allow/deny decision with reason supports audit and policy debugging",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class AuthorizationDecision:
    """Result of an authorization check."""
    allowed: bool
    reason: str
    identity_id: str
    permission: Permission
    tenant_id: str

    def to_audit_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "identity_id": self.identity_id,
            "permission": self.permission.value,
            "tenant_id": self.tenant_id,
        }


# Predefined enterprise roles
@cite(
    key="RBAC-PREDEFINED-ROLES",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Predefined Roles",
    rationale="Standard enterprise roles map to common access patterns",
    confidence="CERTAIN",
)
class PredefinedRoles:
    """Built-in enterprise roles."""

    ADMIN = Role(
        name="admin",
        description="Full system administration",
        permissions=set(Permission),
        is_system_role=True,
    )

    OPERATOR = Role(
        name="operator",
        description="Run and monitor agents and twins",
        permissions={
            Permission.AGENT_READ,
            Permission.AGENT_EXECUTE,
            Permission.AGENT_MEMORY_READ,
            Permission.TWIN_READ,
            Permission.TWIN_DEPLOY,
            Permission.MEMORY_READ,
            Permission.GRAPH_READ,
            Permission.GRAPH_QUERY,
            Permission.AUDIT_READ,
            Permission.INFRA_READ,
            Permission.CONFIG_READ,
        },
        is_system_role=True,
    )

    DEVELOPER = Role(
        name="developer",
        description="Build and configure agents",
        permissions={
            Permission.AGENT_READ,
            Permission.AGENT_CREATE,
            Permission.AGENT_MEMORY_READ,
            Permission.AGENT_MEMORY_WRITE,
            Permission.TWIN_READ,
            Permission.TWIN_CREATE,
            Permission.MEMORY_READ,
            Permission.MEMORY_WRITE,
            Permission.GRAPH_READ,
            Permission.GRAPH_QUERY,
            Permission.CONFIG_READ,
            Permission.CONFIG_WRITE,
        },
        is_system_role=True,
    )

    AUDITOR = Role(
        name="auditor",
        description="Read-only access for compliance and security review",
        permissions={
            Permission.AGENT_READ,
            Permission.AGENT_MEMORY_READ,
            Permission.TWIN_READ,
            Permission.MEMORY_READ,
            Permission.MEMORY_EXPORT,
            Permission.GRAPH_READ,
            Permission.GRAPH_QUERY,
            Permission.AUDIT_READ,
            Permission.AUDIT_EXPORT,
            Permission.INFRA_READ,
            Permission.CONFIG_READ,
        },
        is_system_role=True,
    )

    SERVICE = Role(
        name="service",
        description="Default role for service accounts and agents",
        permissions={
            Permission.AGENT_READ,
            Permission.AGENT_EXECUTE,
            Permission.AGENT_MEMORY_READ,
            Permission.AGENT_MEMORY_WRITE,
            Permission.MEMORY_READ,
            Permission.MEMORY_WRITE,
            Permission.GRAPH_READ,
            Permission.GRAPH_QUERY,
        },
        is_system_role=True,
    )

    READONLY = Role(
        name="readonly",
        description="Minimal read-only access",
        permissions={
            Permission.AGENT_READ,
            Permission.TWIN_READ,
            Permission.MEMORY_READ,
            Permission.GRAPH_READ,
            Permission.GRAPH_QUERY,
            Permission.CONFIG_READ,
        },
        is_system_role=True,
    )


# Named lookup for predefined roles
BY_NAME: Dict[str, Role] = {
    PredefinedRoles.ADMIN.name: PredefinedRoles.ADMIN,
    PredefinedRoles.OPERATOR.name: PredefinedRoles.OPERATOR,
    PredefinedRoles.DEVELOPER.name: PredefinedRoles.DEVELOPER,
    PredefinedRoles.AUDITOR.name: PredefinedRoles.AUDITOR,
    PredefinedRoles.SERVICE.name: PredefinedRoles.SERVICE,
    PredefinedRoles.READONLY.name: PredefinedRoles.READONLY,
}


@cite(
    key="RBAC-AUTHORIZER",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Authorization Model",
    rationale="Central authorizer evaluates identity roles against required permission",
    confidence="CERTAIN",
)
class RBACAuthorizer:
    """Evaluates authorization requests against identity roles."""

    def __init__(self, role_registry: Optional[Dict[str, Role]] = None):
        self._roles = role_registry or BY_NAME

    def authorize(
        self,
        identity_id: str,
        roles: List[str],
        permission: Permission,
        tenant_id: str,
        resource_tenant_id: Optional[str] = None,
    ) -> AuthorizationDecision:
        """
        Decide whether the identity is allowed to perform `permission`.

        Deny-by-default. Tenant-scoped roles restrict access to resources
        in the same tenant unless the role is not tenant-scoped.
        """
        target_tenant = resource_tenant_id or tenant_id

        if not roles:
            return AuthorizationDecision(
                allowed=False,
                reason="Identity has no assigned roles",
                identity_id=identity_id,
                permission=permission,
                tenant_id=tenant_id,
            )

        for role_name in roles:
            role = self._roles.get(role_name)
            if role is None:
                continue

            if role.tenant_scoped and tenant_id != target_tenant:
                return AuthorizationDecision(
                    allowed=False,
                    reason=f"Role '{role_name}' is tenant-scoped; cross-tenant access denied",
                    identity_id=identity_id,
                    permission=permission,
                    tenant_id=tenant_id,
                )

            if role.grants(permission):
                return AuthorizationDecision(
                    allowed=True,
                    reason=f"Granted by role '{role_name}'",
                    identity_id=identity_id,
                    permission=permission,
                    tenant_id=tenant_id,
                )

        return AuthorizationDecision(
            allowed=False,
            reason=f"No assigned role grants permission '{permission.value}'",
            identity_id=identity_id,
            permission=permission,
            tenant_id=tenant_id,
        )
