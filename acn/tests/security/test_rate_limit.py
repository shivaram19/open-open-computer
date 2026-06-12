# acn/tests/security/test_rate_limit.py
"""Tests for rate limiter."""

import pytest
from security.rate_limit import RateLimiter


def test_allowed_within_limit():
    limiter = RateLimiter(default_limit=3, default_window_seconds=60, default_burst=0)
    for _ in range(3):
        result = limiter.check("alice")
        assert result.allowed
    result = limiter.check("alice")
    assert not result.allowed


def test_burst_allows_extra():
    limiter = RateLimiter(default_limit=2, default_window_seconds=60, default_burst=1)
    assert limiter.check("bob").allowed
    assert limiter.check("bob").allowed
    assert limiter.check("bob").allowed  # burst
    assert not limiter.check("bob").allowed


def test_keys_are_isolated():
    limiter = RateLimiter(default_limit=1, default_window_seconds=60)
    assert limiter.check("alice").allowed
    assert limiter.check("bob").allowed


def test_status_does_not_consume():
    limiter = RateLimiter(default_limit=2, default_window_seconds=60, default_burst=0)
    limiter.check("carol")
    status = limiter.status("carol")
    assert status.remaining == 1
    status2 = limiter.status("carol")
    assert status2.remaining == 1


def test_override():
    limiter = RateLimiter(default_limit=1, default_window_seconds=60)
    limiter.set_override("premium", 10, 60, burst=0)
    for _ in range(10):
        assert limiter.check("premium").allowed
    assert not limiter.check("premium").allowed


def test_reset():
    limiter = RateLimiter(default_limit=1, default_window_seconds=60, default_burst=0)
    assert limiter.check("dave").allowed
    assert not limiter.check("dave").allowed
    limiter.reset("dave")
    assert limiter.check("dave").allowed
