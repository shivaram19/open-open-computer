# acn/tests/security/test_identity.py
"""Tests for identity model."""

import pytest
from security.identity import Identity, IdentityType


def test_identity_human():
    identity = Identity(
        id="user-1",
        type=IdentityType.HUMAN,
        name="Ada Lovelace",
        tenant_id="tenant-42",
        roles=["developer"],
        auth_method="oidc",
        session_id="sess-123",
    )
    assert identity.is_human()
    assert not identity.is_service()
    assert not identity.is_agent()
    assert identity.has_role("developer")
    assert not identity.has_role("admin")
    audit = identity.to_audit_dict()
    assert audit["identity_id"] == "user-1"
    assert audit["identity_type"] == "human"
    assert audit["auth_method"] == "oidc"


def test_identity_service():
    identity = Identity(
        id="svc-1",
        type=IdentityType.SERVICE,
        name="memory-service",
        tenant_id="tenant-42",
        roles=["service"],
        auth_method="api_key",
    )
    assert identity.is_service()
    assert identity.to_audit_dict()["identity_type"] == "service"
