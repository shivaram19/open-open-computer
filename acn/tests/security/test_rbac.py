# acn/tests/security/test_rbac.py
"""Tests for RBAC authorization."""

import pytest
from security.rbac import (
    Permission,
    Role,
    RBACAuthorizer,
    BY_NAME,
    PredefinedRoles,
)


def test_predefined_roles_loaded():
    assert "admin" in BY_NAME
    assert "operator" in BY_NAME
    assert "developer" in BY_NAME
    assert "auditor" in BY_NAME
    assert "service" in BY_NAME
    assert "readonly" in BY_NAME


def test_admin_grants_all_permissions():
    admin = BY_NAME["admin"]
    for perm in Permission:
        assert admin.grants(perm), f"admin should grant {perm}"


def test_readonly_does_not_grant_write():
    readonly = BY_NAME["readonly"]
    assert readonly.grants(Permission.AGENT_READ)
    assert not readonly.grants(Permission.AGENT_CREATE)
    assert not readonly.grants(Permission.MEMORY_WRITE)


def test_authorizer_allows_granted_permission():
    authorizer = RBACAuthorizer()
    decision = authorizer.authorize(
        identity_id="dev-1",
        roles=["developer"],
        permission=Permission.AGENT_CREATE,
        tenant_id="t-1",
    )
    assert decision.allowed
    assert "developer" in decision.reason


def test_authorizer_denies_missing_permission():
    authorizer = RBACAuthorizer()
    decision = authorizer.authorize(
        identity_id="ro-1",
        roles=["readonly"],
        permission=Permission.AGENT_CREATE,
        tenant_id="t-1",
    )
    assert not decision.allowed
    assert "does not grant" in decision.reason or "grants permission" in decision.reason


def test_authorizer_denies_cross_tenant():
    authorizer = RBACAuthorizer()
    decision = authorizer.authorize(
        identity_id="dev-1",
        roles=["developer"],
        permission=Permission.AGENT_READ,
        tenant_id="t-1",
        resource_tenant_id="t-2",
    )
    assert not decision.allowed
    assert "cross-tenant" in decision.reason


def test_authorizer_denies_no_roles():
    authorizer = RBACAuthorizer()
    decision = authorizer.authorize(
        identity_id="unknown",
        roles=[],
        permission=Permission.AGENT_READ,
        tenant_id="t-1",
    )
    assert not decision.allowed
    assert "no assigned roles" in decision.reason


def test_custom_role():
    custom = Role(
        name="memory-curator",
        description="Can read and write semantic memory only",
        permissions={Permission.MEMORY_READ, Permission.MEMORY_WRITE},
    )
    registry = {"memory-curator": custom}
    authorizer = RBACAuthorizer(registry)
    assert authorizer.authorize("mc-1", ["memory-curator"], Permission.MEMORY_READ, "t-1").allowed
    assert not authorizer.authorize("mc-1", ["memory-curator"], Permission.AGENT_READ, "t-1").allowed
