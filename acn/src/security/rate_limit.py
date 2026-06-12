# src/security/rate_limit.py
"""
Rate limiting and resource controls for ACN.

Sliding-window counters per identity prevent abuse and resource exhaustion.
Supports burst allowances and per-tenant overrides.

[CITATION: ADR-011]
Enterprise Security Baseline — rate limiting per identity and tenant
prevents abuse and ensures fair resource allocation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Callable
from shared.utils.citations import cite


@cite(
    key="RATE-LIMIT-RESULT",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Rate Limiting",
    rationale="Explicit allow/deny result with retry-after supports clients and gateways",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class RateLimitResult:
    """Result of a rate-limit check."""
    allowed: bool
    remaining: int
    reset_after_seconds: int
    limit: int
    window_seconds: int
    key: str


@cite(
    key="RATE-LIMIT-WINDOW",
    paper="ACN Enterprise Security Baseline",
    venue="ACN Architecture Document",
    section="Rate Limiting",
    rationale="Sliding window provides smooth limits without hard slot boundaries",
    confidence="CERTAIN",
)
class RateLimiter:
    """
    In-memory sliding-window rate limiter.

    Production deployments should back this with Redis or a similar
    distributed store so limits are shared across replicas.
    """

    def __init__(
        self,
        default_limit: int = 100,
        default_window_seconds: int = 60,
        default_burst: int = 10,
        clock: Optional[Callable[[], float]] = None,
    ):
        self._default_limit = default_limit
        self._default_window_seconds = default_window_seconds
        self._default_burst = default_burst
        self._clock = clock or self._default_clock
        # key -> sorted list of timestamps (float seconds)
        self._windows: Dict[str, list[float]] = {}
        # key -> (limit, window_seconds, burst) overrides
        self._overrides: Dict[str, tuple[int, int, int]] = {}

    @staticmethod
    def _default_clock() -> float:
        import time
        return time.monotonic()

    def set_override(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        burst: int = 0,
    ) -> None:
        """Set a per-key rate-limit override."""
        self._overrides[key] = (limit, window_seconds, burst)

    def remove_override(self, key: str) -> None:
        self._overrides.pop(key, None)

    def _config(self, key: str) -> tuple[int, int, int]:
        return self._overrides.get(
            key,
            (self._default_limit, self._default_window_seconds, self._default_burst),
        )

    @cite(
        key="RATE-LIMIT-CHECK",
        paper="ACN Enterprise Security Baseline",
        venue="ACN Architecture Document",
        section="Rate Limiting",
        rationale="Sliding window evicts old events and enforces limit + burst",
        confidence="CERTAIN",
    )
    def check(self, key: str) -> RateLimitResult:
        """Check whether the key is within its rate limit."""
        limit, window_seconds, burst = self._config(key)
        now = self._clock()
        cutoff = now - window_seconds
        window = self._windows.get(key, [])
        # Evict events outside the window.
        window = [t for t in window if t > cutoff]

        effective_limit = limit + burst
        allowed = len(window) < effective_limit

        if allowed:
            window.append(now)

        self._windows[key] = window
        remaining = max(0, effective_limit - len(window))
        reset_after_seconds = max(0, int(window[0] - cutoff)) if window else 0
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_after_seconds=reset_after_seconds,
            limit=limit,
            window_seconds=window_seconds,
            key=key,
        )

    def reset(self, key: str) -> None:
        """Reset the window for a key."""
        self._windows.pop(key, None)

    def status(self, key: str) -> RateLimitResult:
        """Return current status without consuming quota."""
        limit, window_seconds, burst = self._config(key)
        now = self._clock()
        cutoff = now - window_seconds
        window = [t for t in self._windows.get(key, []) if t > cutoff]
        effective_limit = limit + burst
        remaining = max(0, effective_limit - len(window))
        reset_after_seconds = max(0, int(window[0] - cutoff)) if window else 0
        return RateLimitResult(
            allowed=remaining > 0,
            remaining=remaining,
            reset_after_seconds=reset_after_seconds,
            limit=limit,
            window_seconds=window_seconds,
            key=key,
        )
