# acn/tests/security/test_manager.py
"""Tests for the composed SecurityManager."""

import base64
import pytest
from security import SecurityManager
from security.config import SecurityConfig
from security.rbac import Permission


def _master_key() -> str:
    return base64.urlsafe_b64encode(b"k" * 32).decode()


def test_authenticate_api_key_success():
    manager = SecurityManager(config=SecurityConfig(rate_limit_enabled=False))
    raw, _ = manager.api_keys.create(
        tenant_id="t-1",
        identity_id="agent-1",
        identity_type="agent",
        name="agent-1-key",
    )
    identity = manager.authenticate_api_key(raw)
    assert identity is not None
    assert identity.id == "agent-1"
    assert identity.tenant_id == "t-1"
    assert identity.auth_method == "api_key"


def test_authenticate_api_key_failure():
    manager = SecurityManager(config=SecurityConfig(rate_limit_enabled=False))
    identity = manager.authenticate_api_key("acn_invalid")
    assert identity is None


def test_authorize_and_audit():
    manager = SecurityManager(config=SecurityConfig(rate_limit_enabled=False))
    raw, _ = manager.api_keys.create(
        tenant_id="t-1",
        identity_id="svc-1",
        identity_type="service",
        name="svc-1-key",
    )
    identity = manager.authenticate_api_key(raw)
    # Service role does not have AGENT_DELETE.
    decision = manager.authorize(
        identity,
        Permission.AGENT_DELETE,
        resource_type="agent",
        resource_id="agent-1",
    )
    assert not decision.allowed
    assert len(manager.audit.get_records()) == 2  # authn + authz


def test_encrypt_decrypt_with_manager():
    config = SecurityConfig(master_key=_master_key(), rate_limit_enabled=False)
    manager = SecurityManager(config=config)
    envelope = manager.encrypt("t-1", b"classified")
    assert envelope is not None
    assert manager.decrypt(envelope) == b"classified"


def test_rate_limit():
    config = SecurityConfig(rate_limit_enabled=True, rate_limit_default=1, rate_limit_burst=0)
    manager = SecurityManager(config=config)
    assert manager.check_rate_limit("x")
    assert not manager.check_rate_limit("x")


def test_rate_limit_disabled():
    config = SecurityConfig(rate_limit_enabled=False)
    manager = SecurityManager(config=config)
    assert manager.check_rate_limit("x")
    assert manager.check_rate_limit("x")
