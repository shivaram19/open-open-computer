# acn/tests/security/test_api_key.py
"""Tests for API key lifecycle."""

import pytest
from datetime import datetime, timezone, timedelta
from security.api_key import ApiKeyManager, ApiKeyStatus


def test_create_returns_plaintext_and_hash():
    manager = ApiKeyManager()
    raw, credential = manager.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
    )
    assert raw.startswith("acn_")
    assert credential.key_id.startswith("ak_")
    assert credential.hashed_secret
    assert credential.hashed_secret != raw
    assert credential.status == ApiKeyStatus.ACTIVE


def test_validate_active_key():
    manager = ApiKeyManager()
    raw, credential = manager.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
    )
    validated = manager.validate(raw)
    assert validated is not None
    assert validated.key_id == credential.key_id
    assert validated.last_used_at is not None


def test_validate_invalid_key():
    manager = ApiKeyManager()
    manager.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
    )
    assert manager.validate("acn_invalidkey") is None
    assert manager.validate("not_a_key") is None
    assert manager.validate("") is None


def test_revoke_makes_key_invalid():
    manager = ApiKeyManager()
    raw, credential = manager.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
    )
    manager.revoke(credential.key_id, "compromised")
    assert manager.validate(raw) is None
    assert manager.get(credential.key_id).status == ApiKeyStatus.REVOKED


def test_rotate_preserves_grace_period():
    manager = ApiKeyManager()
    raw, old = manager.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
    )
    new_raw, new_cred = manager.rotate(old.key_id)
    assert new_raw.startswith("acn_")
    assert new_cred.key_id != old.key_id
    assert manager.validate(new_raw) is not None
    # Old key is rotated and has a short grace period.
    assert manager.get(old.key_id).status == ApiKeyStatus.ROTATED
    assert manager.validate(raw) is not None  # still valid during grace


def test_key_expires():
    manager = ApiKeyManager()
    raw, credential = manager.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
        ttl_days=1,
    )
    future = datetime.now(timezone.utc) + timedelta(days=2)
    assert manager.validate(raw, now=future) is None


def test_list_for_identity():
    manager = ApiKeyManager()
    manager.create("t-1", "agent-1", "agent", "k1")
    manager.create("t-1", "agent-1", "agent", "k2")
    manager.create("t-1", "agent-2", "agent", "k3")
    assert len(manager.list_for_identity("agent-1")) == 2
    assert len(manager.list_for_identity("agent-2")) == 1
