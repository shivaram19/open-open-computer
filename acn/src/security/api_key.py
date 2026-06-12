# src/security/api_key.py
"""
API key lifecycle management for ACN services and agents.

Raw API keys are generated once, shown once, and never stored in plaintext.
Only argon2id hashes are retained. Validation uses constant-time comparison.

[CITATION: ADR-011]
Enterprise Security Baseline — API keys for service-to-service
and agent authentication, with automatic rotation and revocation.
"""

import re
import secrets
import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite

try:
    import argon2
    _ARGON2_AVAILABLE = True
except ImportError:  # pragma: no cover - fallback path
    _ARGON2_AVAILABLE = False


# [CITATION: API-KEY-PREFIX]
# Distinct prefix prevents key from being committed as random hex.
API_KEY_PREFIX = "acn_"

# [CITATION: API-KEY-LENGTH]
# 48 bytes of CSPRNG entropy gives ~384 bits of randomness.
API_KEY_ENTROPY_BYTES = 48


class ApiKeyStatus(Enum):
    """Lifecycle status of an API key."""
    ACTIVE = "active"
    ROTATED = "rotated"
    REVOKED = "revoked"
    EXPIRED = "expired"


@cite(
    key="API-KEY-CREDENTIAL",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="API Key Lifecycle",
    rationale="Stored credential keeps only hash and metadata, never plaintext",
    confidence="CERTAIN",
)
@dataclass
class ApiKeyCredential:
    """Stored representation of an API key."""
    key_id: str
    tenant_id: str
    identity_id: str
    identity_type: str
    name: str
    hashed_secret: str
    status: ApiKeyStatus
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    scopes: List[str]
    rotated_to_id: Optional[str] = None
    revoked_reason: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def is_active(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(timezone.utc)
        if self.status == ApiKeyStatus.REVOKED:
            return False
        if self.status == ApiKeyStatus.EXPIRED:
            return False
        if self.expires_at and now >= self.expires_at:
            return False
        return True

    def mask(self) -> str:
        return f"{API_KEY_PREFIX}****{self.key_id[-8:]}"

    def to_audit_dict(self) -> Dict[str, Any]:
        return {
            "key_id": self.key_id,
            "tenant_id": self.tenant_id,
            "identity_id": self.identity_id,
            "identity_type": self.identity_type,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "scopes": self.scopes,
            "masked": self.mask(),
        }


@cite(
    key="API-KEY-MANAGER",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="API Key Lifecycle",
    rationale="Central manager enforces secure generation, hashing, rotation, and validation",
    confidence="CERTAIN",
)
class ApiKeyManager:
    """Creates, hashes, rotates, and validates API keys."""

    def __init__(self, backend_store: Optional[Dict[str, ApiKeyCredential]] = None):
        # In production this is backed by a database; in-memory default for tests.
        self._store: Dict[str, ApiKeyCredential] = backend_store or {}
        self._argon2_hasher = self._build_hasher()

    @staticmethod
    def _build_hasher():
        if _ARGON2_AVAILABLE:
            return argon2.PasswordHasher(
                time_cost=3,
                memory_cost=65536,
                parallelism=4,
                hash_len=32,
                salt_len=16,
            )
        return None

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    @cite(
        key="API-KEY-GENERATE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="API Key Format",
        rationale="CSPRNG + checksum digit reduces transcription errors",
        confidence="CERTAIN",
    )
    def generate_key(self, identity_id: str) -> str:
        """Generate a new raw API key. Returned once and never stored."""
        random_bytes = secrets.token_bytes(API_KEY_ENTROPY_BYTES)
        base = f"{API_KEY_PREFIX}{random_bytes.hex()}"
        # Append a truncated SHA-256 checksum as a readability/transcription guard.
        checksum = hashlib.sha256(base.encode()).hexdigest()[:8]
        return f"{base}{checksum}"

    def _hash_secret(self, secret: str) -> str:
        if self._argon2_hasher:
            return self._argon2_hasher.hash(secret)
        # Fallback only when argon2-cffi is unavailable.
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), 600000)
        return f"$pbkdf2-sha256$600000${salt}${digest.hex()}"

    @cite(
        key="API-KEY-CREATE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="API Key Lifecycle",
        rationale="Create returns plaintext once; only hash is persisted",
        confidence="CERTAIN",
    )
    def create(
        self,
        tenant_id: str,
        identity_id: str,
        identity_type: str,
        name: str,
        ttl_days: Optional[int] = 90,
        scopes: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, ApiKeyCredential]:
        """
        Create a new API key.

        Returns:
            (plaintext_key, credential): plaintext_key MUST be shown once.
        """
        key_id = f"ak_{uuid.uuid4().hex}"
        raw_key = self.generate_key(identity_id)
        hashed = self._hash_secret(raw_key)
        now = self._now()
        expires_at = now + timedelta(days=ttl_days) if ttl_days else None

        credential = ApiKeyCredential(
            key_id=key_id,
            tenant_id=tenant_id,
            identity_id=identity_id,
            identity_type=identity_type,
            name=name,
            hashed_secret=hashed,
            status=ApiKeyStatus.ACTIVE,
            created_at=now,
            expires_at=expires_at,
            last_used_at=None,
            scopes=scopes or [],
            metadata=metadata or {},
        )
        self._store[key_id] = credential
        return raw_key, credential

    @cite(
        key="API-KEY-VALIDATE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="API Key Validation",
        rationale="Constant-time hashing prevents timing attacks",
        confidence="CERTAIN",
    )
    def validate(self, raw_key: str, now: Optional[datetime] = None) -> Optional[ApiKeyCredential]:
        """Validate a raw API key and return its credential if valid."""
        if not raw_key.startswith(API_KEY_PREFIX):
            return None

        # Extract key_id from storage hash for fast lookup is impossible with argon2,
        # so we attempt verification against keys in the same tenant heuristically.
        # In production, embed a key id in the raw key prefix (acn_<key_id>_<secret>).
        # Here we perform a bounded scan for correctness in tests.
        for credential in self._store.values():
            if not credential.is_active(now):
                continue
            if self._verify(raw_key, credential.hashed_secret):
                credential.last_used_at = now or self._now()
                return credential
        return None

    def _verify(self, raw_key: str, hashed_secret: str) -> bool:
        try:
            if self._argon2_hasher and hashed_secret.startswith("$argon2"):
                self._argon2_hasher.verify(hashed_secret, raw_key)
                return True
        except Exception:
            # argon2 raises VerifyMismatchError or similar on mismatch.
            return False

        # Fallback PBKDF2 verification using constant-time comparison.
        if hashed_secret.startswith("$pbkdf2-sha256$"):
            parts = hashed_secret.split("$")
            if len(parts) != 5:
                return False
            _, _, iterations, salt, stored_digest = parts
            digest = hashlib.pbkdf2_hmac(
                "sha256", raw_key.encode(), salt.encode(), int(iterations)
            )
            return secrets.compare_digest(digest.hex(), stored_digest)
        return False

    @cite(
        key="API-KEY-ROTATE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="API Key Lifecycle",
        rationale="Rotation creates a new key before old one expires, preserving uptime",
        confidence="CERTAIN",
    )
    def rotate(self, key_id: str, ttl_days: Optional[int] = 90) -> tuple[str, ApiKeyCredential]:
        """Rotate an active key. Old key becomes ROTATED for a grace period."""
        old = self._store.get(key_id)
        if not old or old.status != ApiKeyStatus.ACTIVE:
            raise ValueError(f"Key {key_id} is not active or does not exist")

        new_plaintext, new_credential = self.create(
            tenant_id=old.tenant_id,
            identity_id=old.identity_id,
            identity_type=old.identity_type,
            name=f"{old.name} (rotated)",
            ttl_days=ttl_days,
            scopes=old.scopes,
            metadata={**old.metadata, "rotated_from": old.key_id},
        )

        old.status = ApiKeyStatus.ROTATED
        old.rotated_to_id = new_credential.key_id
        old.expires_at = self._now() + timedelta(hours=1)  # 1-hour grace
        return new_plaintext, new_credential

    @cite(
        key="API-KEY-REVOKE",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="API Key Lifecycle",
        rationale="Revocation immediately invalidates a key with an auditable reason",
        confidence="CERTAIN",
    )
    def revoke(self, key_id: str, reason: str) -> ApiKeyCredential:
        """Revoke a key immediately."""
        credential = self._store.get(key_id)
        if not credential:
            raise ValueError(f"Key {key_id} does not exist")
        credential.status = ApiKeyStatus.REVOKED
        credential.revoked_reason = reason
        credential.expires_at = None
        return credential

    def get(self, key_id: str) -> Optional[ApiKeyCredential]:
        return self._store.get(key_id)

    def list_for_identity(self, identity_id: str) -> List[ApiKeyCredential]:
        return [c for c in self._store.values() if c.identity_id == identity_id]
