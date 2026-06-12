# src/security/encryption.py
"""
Encryption primitives for data at rest and in transit.

Uses Fernet (AES-128-CBC + HMAC-SHA256) for symmetric data encryption.
Provides envelope encryption with data encryption keys (DEKs) wrapped
by a master key.

[CITATION: ADR-011]
Enterprise Security Baseline — encrypt secrets and PII at rest,
TLS 1.3 for data in transit, envelope encryption for key rotation.
"""

import base64
import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from shared.utils.citations import cite

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback path
    _CRYPTO_AVAILABLE = False
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore
    PBKDF2HMAC = None  # type: ignore
    hashes = None  # type: ignore


@cite(
    key="DEK",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Encryption",
    rationale="Envelope encryption separates per-tenant DEK from master key",
    confidence="CERTAIN",
)
@dataclass
class DataEncryptionKey:
    """A data encryption key used for envelope encryption."""
    key_id: str
    tenant_id: str
    algorithm: str
    encrypted_key: bytes
    created_at: str
    rotated_at: Optional[str]
    metadata: Dict[str, Any]


@cite(
    key="ENCRYPTION-MANAGER",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Encryption",
    rationale="Central manager handles key derivation, envelope encryption, and rotation",
    confidence="CERTAIN",
)
class EncryptionManager:
    """
    Symmetric encryption manager with envelope encryption support.

    In production the master key lives in an HSM or external KMS.
    This implementation derives a master key from an environment-provided
    base64 secret or a passphrase + salt for test/development use.
    """

    def __init__(
        self,
        master_key: Optional[bytes] = None,
        master_key_env_var: str = "ACN_MASTER_KEY",
    ):
        raw = master_key or os.environ.get(master_key_env_var, "").encode()
        if not raw:
            raise RuntimeError(
                "Master key is required. Set ACN_MASTER_KEY to a base64-encoded 32-byte secret."
            )
        self._master_key = self._normalize_master_key(raw)
        self._master_fernet = self._fernet(self._master_key)
        self._dek_store: Dict[str, DataEncryptionKey] = {}

    @staticmethod
    def _normalize_master_key(raw: bytes) -> bytes:
        """Accept base64-encoded 32-byte key or derive one from a passphrase."""
        try:
            decoded = base64.urlsafe_b64decode(raw)
            if len(decoded) == 32:
                return base64.urlsafe_b64encode(decoded)
        except Exception:
            pass
        # Derive 32-byte key from passphrase using PBKDF2.
        salt = hashlib.sha256(b"acn-default-salt-v1").digest()
        if _CRYPTO_AVAILABLE and PBKDF2HMAC and hashes:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=600000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(raw))
        else:
            key = base64.urlsafe_b64encode(
                hashlib.pbkdf2_hmac("sha256", raw, salt, 600000)
            )
        return key

    @staticmethod
    def _fernet(key: bytes) -> "Fernet":
        if not _CRYPTO_AVAILABLE:
            raise RuntimeError("cryptography package is required for encryption")
        return Fernet(key)

    @cite(
        key="ENCRYPTION-DEK-GENERATE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Encryption",
        rationale="Per-tenant DEK limits blast radius of key compromise",
        confidence="CERTAIN",
    )
    def generate_dek(self, tenant_id: str, key_id: Optional[str] = None) -> DataEncryptionKey:
        """Generate a new DEK for a tenant and encrypt it under the master key."""
        dek = Fernet.generate_key()
        key_id = key_id or f"dek_{secrets.token_hex(8)}"
        encrypted_dek = self._master_fernet.encrypt(dek)
        dek_record = DataEncryptionKey(
            key_id=key_id,
            tenant_id=tenant_id,
            algorithm="fernet-aes128-cbc-hmac",
            encrypted_key=encrypted_dek,
            created_at=EncryptionManager._now(),
            rotated_at=None,
            metadata={},
        )
        self._dek_store[key_id] = dek_record
        return dek_record

    def _get_or_create_active_dek(self, tenant_id: str) -> DataEncryptionKey:
        """Get or create the active DEK record for a tenant."""
        for dek in self._dek_store.values():
            if dek.tenant_id == tenant_id and dek.rotated_at is None:
                return dek
        return self.generate_dek(tenant_id)

    @cite(
        key="ENCRYPTION-ENCRYPT",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Encryption",
        rationale="Envelope encryption: data encrypted with DEK, DEK encrypted with master key",
        confidence="CERTAIN",
    )
    def encrypt(
        self,
        tenant_id: str,
        plaintext: bytes,
        associated_data: Optional[Dict[str, Any]] = None,
        key_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Encrypt plaintext using envelope encryption."""
        if key_id:
            dek_record = self._dek_store.get(key_id)
            if dek_record is None or dek_record.tenant_id != tenant_id:
                raise ValueError(f"DEK {key_id} not available for tenant {tenant_id}")
        else:
            dek_record = self._get_or_create_active_dek(tenant_id)
        dek = self._master_fernet.decrypt(dek_record.encrypted_key)
        fernet = self._fernet(dek)
        ciphertext = fernet.encrypt(plaintext)
        return {
            "version": 1,
            "algorithm": "fernet-envelope",
            "tenant_id": tenant_id,
            "key_id": dek_record.key_id,
            "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),
            "associated_data": associated_data or {},
        }

    @cite(
        key="ENCRYPTION-DECRYPT",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Encryption",
        rationale="Decrypt envelope-encrypted data and verify key binding",
        confidence="CERTAIN",
    )
    def decrypt(self, envelope: Dict[str, Any]) -> bytes:
        """Decrypt an envelope produced by `encrypt`."""
        key_id = envelope["key_id"]
        tenant_id = envelope.get("tenant_id")
        dek_record = self._dek_store.get(key_id)
        if dek_record is None:
            raise ValueError(f"DEK {key_id} not found")
        if tenant_id and dek_record.tenant_id != tenant_id:
            raise ValueError("Tenant mismatch: envelope tenant does not match DEK tenant")
        dek = self._master_fernet.decrypt(dek_record.encrypted_key)
        fernet = self._fernet(dek)
        ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"].encode("ascii"))
        return fernet.decrypt(ciphertext)

    @cite(
        key="ENCRYPTION-ROTATE-DEK",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Encryption",
        rationale="Rotate tenant DEK and re-encrypt under master key",
        confidence="CERTAIN",
    )
    def rotate_dek(self, key_id: str) -> DataEncryptionKey:
        """Rotate a DEK in place. Old data must be re-encrypted separately."""
        old = self._dek_store.get(key_id)
        if not old:
            raise ValueError(f"DEK {key_id} not found")
        new_dek = Fernet.generate_key()
        new_record = DataEncryptionKey(
            key_id=f"dek_{secrets.token_hex(8)}",
            tenant_id=old.tenant_id,
            algorithm=old.algorithm,
            encrypted_key=self._master_fernet.encrypt(new_dek),
            created_at=old.created_at,
            rotated_at=EncryptionManager._now(),
            metadata={**old.metadata, "rotated_from": old.key_id},
        )
        old.rotated_at = EncryptionManager._now()
        old.metadata["rotated_to"] = new_record.key_id
        self._dek_store[new_record.key_id] = new_record
        return new_record

    @staticmethod
    def _now() -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    @cite(
        key="ENCRYPTION-HASH",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Encryption",
        rationale="SHA-256 used for integrity fingerprints; not for password hashing",
        confidence="CERTAIN",
    )
    @staticmethod
    def fingerprint(data: bytes) -> str:
        """Return a SHA-256 fingerprint for non-secret data."""
        return hashlib.sha256(data).hexdigest()
