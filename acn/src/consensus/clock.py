# src/consensus/clock.py
"""
Clock Protocol — Dependency Inversion for Time Services.

Decouples consensus, memory, and agent layers from the concrete
HybridLogicalClock implementation. Enables:
- Testability: inject MockClock for deterministic tests
- Extensibility: add VectorClock, LamportClock without editing callers
- Swappability: replace HLC with a different timestamp strategy

Research basis:
- Martin (1996): DIP — "High-level modules should not depend on
  low-level modules. Both should depend on abstractions."
- Meyer (1988): Design by Contract — Clock declares what it guarantees.

[CITATION: Kulkarni2014]
[CITATION: ADR-003]
"""

from typing import Protocol, Dict, Any
from dataclasses import dataclass

from shared.utils.citations import cite


@cite(
    key="CLOCK-PROTOCOL",
    paper="Clock Protocol: Decoupled Time Abstraction for Distributed Consensus",
    venue="ACN Architecture Document",
    section="Temporal Consistency",
    rationale="Protocol decouples callers from HybridLogicalClock, enabling testability and extensibility",
    confidence="CERTAIN",
)
class Timestamp(Protocol):
    """A logical or hybrid logical timestamp."""

    def compare(self, other: "Timestamp") -> int: ...
    def to_dict(self) -> Dict[str, Any]: ...
    def __str__(self) -> str: ...


@cite(
    key="CLOCK-PROTOCOL",
    paper="Clock Protocol: Decoupled Time Abstraction for Distributed Consensus",
    venue="ACN Architecture Document",
    section="Temporal Consistency",
    rationale="Protocol decouples callers from HybridLogicalClock, enabling testability and extensibility",
    confidence="CERTAIN",
)
class Clock(Protocol):
    """
    Abstract clock for timestamp generation and causality tracking.

    Contract:
    - now() returns the current timestamp
    - send() returns a timestamp safe to send to another node
    - receive(timestamp) merges an external timestamp, advancing local time
    - reset() returns the clock to its initial state
    """

    def now(self) -> Timestamp: ...
    def send(self) -> Timestamp: ...
    def receive(self, timestamp: Timestamp) -> Timestamp: ...
    def reset(self) -> None: ...
