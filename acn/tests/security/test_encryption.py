# acn/tests/security/test_encryption.py
"""Tests for encryption manager."""

import pytest
import base64
from security.encryption import EncryptionManager


def _master_key() -> bytes:
    return base64.urlsafe_b64encode(b"x" * 32)


def test_encrypt_decrypt_roundtrip():
    manager = EncryptionManager(master_key=_master_key())
    plaintext = b"sensitive agent memory"
    envelope = manager.encrypt("t-1", plaintext, associated_data={"type": "memory"})
    assert envelope["algorithm"] == "fernet-envelope"
    assert envelope["key_id"].startswith("dek_")
    decrypted = manager.decrypt(envelope)
    assert decrypted == plaintext


def test_tenant_mismatch_raises():
    manager = EncryptionManager(master_key=_master_key())
    envelope = manager.encrypt("t-1", b"data")
    envelope["tenant_id"] = "t-2"
    with pytest.raises(ValueError, match="Tenant mismatch"):
        manager.decrypt(envelope)


def test_missing_dek_raises():
    manager = EncryptionManager(master_key=_master_key())
    envelope = manager.encrypt("t-1", b"data")
    del manager._dek_store[envelope["key_id"]]
    with pytest.raises(ValueError, match="not found"):
        manager.decrypt(envelope)


def test_same_manager_reuses_active_dek():
    manager = EncryptionManager(master_key=_master_key())
    e1 = manager.encrypt("t-1", b"a")
    e2 = manager.encrypt("t-1", b"b")
    assert e1["key_id"] == e2["key_id"]


def test_different_tenants_have_different_deks():
    manager = EncryptionManager(master_key=_master_key())
    e1 = manager.encrypt("t-1", b"a")
    e2 = manager.encrypt("t-2", b"b")
    assert e1["key_id"] != e2["key_id"]


def test_rotate_dek():
    manager = EncryptionManager(master_key=_master_key())
    envelope = manager.encrypt("t-1", b"data")
    old_key_id = envelope["key_id"]
    new_dek = manager.rotate_dek(old_key_id)
    assert new_dek.key_id != old_key_id
    assert manager._dek_store[old_key_id].rotated_at is not None
    # After rotation, the old envelope still decrypts with the old DEK.
    decrypted = manager.decrypt(envelope)
    assert decrypted == b"data"


def test_fingerprint():
    assert EncryptionManager.fingerprint(b"hello") == EncryptionManager.fingerprint(b"hello")
    assert EncryptionManager.fingerprint(b"hello") != EncryptionManager.fingerprint(b"world")
