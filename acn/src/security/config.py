# src/security/config.py
"""
Security configuration loader for ACN.

Loads settings from environment variables with sensible defaults.
Centralizes feature flags, timeouts, and cryptographic parameters.

[CITATION: ADR-011]
Enterprise Security Baseline — configuration must be explicit,
environment-driven, and fail-closed.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from shared.utils.citations import cite


@cite(
    key="SECURITY-CONFIG",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Configuration",
    rationale="Central immutable config prevents scattered security defaults",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class SecurityConfig:
    """Security configuration for the ACN runtime."""

    # Master key
    master_key: Optional[str] = None
    master_key_env_var: str = "ACN_MASTER_KEY"

    # Authentication
    oidc_issuer: Optional[str] = None
    oidc_audience: Optional[str] = "acn"
    oidc_enabled: bool = False
    api_key_enabled: bool = True
    mtls_enabled: bool = False

    # Audit
    audit_enabled: bool = True
    audit_sink: Optional[str] = None  # e.g., stdout, file path, http endpoint
    audit_min_severity: str = "INFO"

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_default: int = 100
    rate_limit_window_seconds: int = 60
    rate_limit_burst: int = 10

    # Cryptographic defaults
    password_hash_algorithm: str = "argon2id"
    password_hash_time_cost: int = 3
    password_hash_memory_cost: int = 65536
    password_hash_parallelism: int = 4

    # Defaults for API keys
    api_key_ttl_days: int = 90
    api_key_max_per_identity: int = 10

    # TLS
    tls_min_version: str = "1.3"
    tls_cipher_suites: List[str] = field(default_factory=lambda: [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256",
    ])

    # CORS / CSP
    allowed_origins: List[str] = field(default_factory=list)
    content_security_policy: str = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    # Feature flags
    enforce_mfa_for_admin: bool = False
    require_approval_for_high_risk: bool = True
    data_retention_days: int = 365

    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Load security config from environment variables."""
        def _bool(name: str, default: bool) -> bool:
            val = os.environ.get(name, "").lower()
            if val in ("1", "true", "yes", "on"):
                return True
            if val in ("0", "false", "no", "off"):
                return False
            return default

        def _int(name: str, default: int) -> int:
            try:
                return int(os.environ.get(name, str(default)))
            except ValueError:
                return default

        def _list(name: str) -> List[str]:
            raw = os.environ.get(name, "")
            return [x.strip() for x in raw.split(",") if x.strip()]

        return cls(
            master_key=os.environ.get("ACN_MASTER_KEY"),
            master_key_env_var=os.environ.get("ACN_MASTER_KEY_ENV_VAR", "ACN_MASTER_KEY"),
            oidc_issuer=os.environ.get("ACN_OIDC_ISSUER"),
            oidc_audience=os.environ.get("ACN_OIDC_AUDIENCE", "acn"),
            oidc_enabled=_bool("ACN_OIDC_ENABLED", False),
            api_key_enabled=_bool("ACN_API_KEY_ENABLED", True),
            mtls_enabled=_bool("ACN_MTLS_ENABLED", False),
            audit_enabled=_bool("ACN_AUDIT_ENABLED", True),
            audit_sink=os.environ.get("ACN_AUDIT_SINK"),
            audit_min_severity=os.environ.get("ACN_AUDIT_MIN_SEVERITY", "INFO"),
            rate_limit_enabled=_bool("ACN_RATE_LIMIT_ENABLED", True),
            rate_limit_default=_int("ACN_RATE_LIMIT_DEFAULT", 100),
            rate_limit_window_seconds=_int("ACN_RATE_LIMIT_WINDOW_SECONDS", 60),
            rate_limit_burst=_int("ACN_RATE_LIMIT_BURST", 10),
            password_hash_algorithm=os.environ.get("ACN_PASSWORD_HASH_ALGORITHM", "argon2id"),
            password_hash_time_cost=_int("ACN_PASSWORD_HASH_TIME_COST", 3),
            password_hash_memory_cost=_int("ACN_PASSWORD_HASH_MEMORY_COST", 65536),
            password_hash_parallelism=_int("ACN_PASSWORD_HASH_PARALLELISM", 4),
            api_key_ttl_days=_int("ACN_API_KEY_TTL_DAYS", 90),
            api_key_max_per_identity=_int("ACN_API_KEY_MAX_PER_IDENTITY", 10),
            tls_min_version=os.environ.get("ACN_TLS_MIN_VERSION", "1.3"),
            tls_cipher_suites=_list("ACN_TLS_CIPHER_SUITES") or [
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_AES_128_GCM_SHA256",
            ],
            allowed_origins=_list("ACN_ALLOWED_ORIGINS"),
            content_security_policy=os.environ.get(
                "ACN_CONTENT_SECURITY_POLICY",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'; "
                "base-uri 'self'; form-action 'self';",
            ),
            enforce_mfa_for_admin=_bool("ACN_ENFORCE_MFA_FOR_ADMIN", False),
            require_approval_for_high_risk=_bool("ACN_REQUIRE_APPROVAL_FOR_HIGH_RISK", True),
            data_retention_days=_int("ACN_DATA_RETENTION_DAYS", 365),
        )

    def to_audit_dict(self) -> Dict[str, Any]:
        return {
            "oidc_enabled": self.oidc_enabled,
            "api_key_enabled": self.api_key_enabled,
            "mtls_enabled": self.mtls_enabled,
            "audit_enabled": self.audit_enabled,
            "rate_limit_enabled": self.rate_limit_enabled,
            "tls_min_version": self.tls_min_version,
            "enforce_mfa_for_admin": self.enforce_mfa_for_admin,
            "require_approval_for_high_risk": self.require_approval_for_high_risk,
            "data_retention_days": self.data_retention_days,
        }
