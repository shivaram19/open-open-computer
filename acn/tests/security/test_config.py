# acn/tests/security/test_config.py
"""Tests for security configuration."""

import os
import pytest
from security.config import SecurityConfig


def test_default_config():
    config = SecurityConfig()
    assert config.api_key_enabled is True
    assert config.oidc_enabled is False
    assert config.rate_limit_enabled is True
    assert config.audit_enabled is True
    assert config.tls_min_version == "1.3"


def test_from_env(monkeypatch):
    monkeypatch.setenv("ACN_OIDC_ENABLED", "true")
    monkeypatch.setenv("ACN_API_KEY_ENABLED", "false")
    monkeypatch.setenv("ACN_RATE_LIMIT_DEFAULT", "200")
    monkeypatch.setenv("ACN_DATA_RETENTION_DAYS", "30")
    monkeypatch.setenv("ACN_ALLOWED_ORIGINS", "https://app.example.com,https://admin.example.com")

    config = SecurityConfig.from_env()
    assert config.oidc_enabled is True
    assert config.api_key_enabled is False
    assert config.rate_limit_default == 200
    assert config.data_retention_days == 30
    assert config.allowed_origins == ["https://app.example.com", "https://admin.example.com"]


def test_from_env_invalid_int_uses_default(monkeypatch):
    monkeypatch.setenv("ACN_RATE_LIMIT_DEFAULT", "not-a-number")
    config = SecurityConfig.from_env()
    assert config.rate_limit_default == 100


def test_config_audit_dict():
    config = SecurityConfig()
    audit = config.to_audit_dict()
    assert "tls_min_version" in audit
    assert "enforce_mfa_for_admin" in audit
