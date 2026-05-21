# src/consensus/hlc.py
"""
Hybrid Logical Clocks (HLC) for Distributed Agent Consensus.

HLC combines physical wall-clock time with a logical counter to provide:
- Causality tracking: if event A happened-before event B, HLC(A) < HLC(B)
- Near-physical accuracy: timestamps approximate real time (within NTP skew bounds)
- Monotonicity: timestamps never go backward on a single node
- Bounded logical counter: lc resets when physical time advances

Used by CockroachDB, MongoDB, YugabyteDB for distributed transaction ordering.
In ACN, HLC timestamps every agent message, enabling the Temporal Auditor
to detect causality violations even under clock skew.

Design inspired by:
- Kulkarni et al. 2014: Hybrid Logical Clocks
- CockroachDB/YugabyteDB: HLC for distributed snapshot isolation
- TemporalObservability2026: Even 3-5ms skew breaks causal observability

[CITATION: Kulkarni2014]
[CITATION: CockroachDB2022]
[CITATION: TemporalObservability2026]
"""

import time
from dataclasses import dataclass
from typing import Optional, Tuple

from shared.utils.citations import cite


@cite(
    key="HLC-TIMESTAMP",
    paper="Hybrid Logical Clocks for Distributed Agent Consensus",
    venue="ACN Architecture Document",
    section="HLC Timestamp Dataclass",
    rationale="Tuple of (physical_time, logical_counter, node_id) provides causality + near-physical accuracy",
    confidence="CERTAIN",
)
@dataclass(frozen=True)
class HLCTimestamp:
    """
    [CITATION: HLC-CORE] An immutable Hybrid Logical Clock timestamp.
    
    Fields:
    - pt: physical time component (microsecond-precision wall clock)
    - lc: logical counter for events at the same physical time
    - node_id: originating node for tie-breaking and debugging
    """
    pt: float
    lc: int
    node_id: str

    def __lt__(self, other: "HLCTimestamp") -> bool:
        """[CITATION: HLC-CORE] Causal ordering: self happened-before other."""
        if self.pt < other.pt:
            return True
        if self.pt > other.pt:
            return False
        if self.lc < other.lc:
            return True
        if self.lc > other.lc:
            return False
        return self.node_id < other.node_id

    def __le__(self, other: "HLCTimestamp") -> bool:
        """[CITATION: HLC-CORE] self happened-before or is concurrent with other."""
        return self == other or self < other

    def __gt__(self, other: "HLCTimestamp") -> bool:
        return other < self

    def __ge__(self, other: "HLCTimestamp") -> bool:
        return other <= self

    def to_dict(self) -> dict:
        """[CITATION: HLC-CORE] Serialize to dictionary."""
        return {"pt": self.pt, "lc": self.lc, "node_id": self.node_id}

    @classmethod
    def from_dict(cls, data: dict) -> "HLCTimestamp":
        """[CITATION: HLC-CORE] Deserialize from dictionary."""
        return cls(pt=data["pt"], lc=data["lc"], node_id=data["node_id"])

    def __str__(self) -> str:
        return f"HLC({self.pt:.6f}|{self.lc}|{self.node_id})"

    def compare(self, other: "HLCTimestamp") -> int:
        """
        Three-way comparison for protocol compliance.
        Returns -1 if self < other, 0 if equal, 1 if self > other.
        """
        if self < other:
            return -1
        if self.pt == other.pt and self.lc == other.lc:
            return 0
        return 1


@cite(
    key="HYBRID-LOGICAL-CLOCK",
    paper="Hybrid Logical Clocks for Distributed Agent Consensus",
    venue="ACN Architecture Document",
    section="HLC Implementation",
    rationale="Per-node HLC with send/receive/now operations ensures causality tracking across agent swarm",
    confidence="CERTAIN",
)
class HybridLogicalClock:
    """
    [CITATION: HLC-CORE] Per-node Hybrid Logical Clock.
    
    Algorithm (Kulkarni et al. 2014):
    
    Local event:
    1. now = physical_time()
    2. if now > pt: pt = now, lc = 0
    3. elif now == pt: lc += 1
    4. else (clock behind): lc += 1  # still monotonic
    
    Send event:
    1. Update HLC per local event rules
    2. Attach timestamp to outgoing message
    
    Receive event (remote timestamp = (pt_m, lc_m)):
    1. now = physical_time()
    2. pt = max(now, self.pt, pt_m)
    3. if pt == self.pt == pt_m: lc = max(self.lc, lc_m) + 1
    4. elif pt == self.pt: lc = self.lc + 1
    5. elif pt == pt_m: lc = lc_m + 1
    6. else: lc = 0
    """

    def __init__(self, node_id: str, max_skew_ms: float = 500.0):
        """[CITATION: HLC-CORE] Initialize HLC for a node."""
        self.node_id = node_id
        self._pt = 0.0
        self._lc = 0
        self.max_skew_ms = max_skew_ms
        self._event_count = 0

    def now(self) -> HLCTimestamp:
        """
        [CITATION: HLC-CORE] Generate timestamp for a local event.
        
        Updates internal state and returns the new timestamp.
        """
        now_physical = time.time()
        
        if now_physical > self._pt:
            self._pt = now_physical
            self._lc = 0
        elif now_physical == self._pt:
            self._lc += 1
        else:
            # Local clock is behind our HLC — increment logical counter
            self._lc += 1
        
        self._event_count += 1
        return HLCTimestamp(pt=self._pt, lc=self._lc, node_id=self.node_id)

    def send(self) -> HLCTimestamp:
        """[CITATION: HLC-CORE] Generate timestamp for an outgoing message."""
        return self.now()

    def receive(self, remote_ts: HLCTimestamp) -> HLCTimestamp:
        """
        [CITATION: HLC-CORE] Merge a remote timestamp and generate local timestamp.
        
        This is the core causal synchronization primitive.
        """
        now_physical = time.time()
        old_pt = self._pt
        old_lc = self._lc
        
        self._pt = max(now_physical, old_pt, remote_ts.pt)
        
        if self._pt == old_pt == remote_ts.pt:
            self._lc = max(old_lc, remote_ts.lc) + 1
        elif self._pt == old_pt:
            self._lc = old_lc + 1
        elif self._pt == remote_ts.pt:
            self._lc = remote_ts.lc + 1
        else:
            self._lc = 0
        
        self._event_count += 1
        return HLCTimestamp(pt=self._pt, lc=self._lc, node_id=self.node_id)

    def get_current(self) -> HLCTimestamp:
        """[CITATION: HLC-CORE] Get current HLC value without incrementing."""
        return HLCTimestamp(pt=self._pt, lc=self._lc, node_id=self.node_id)

    def get_event_count(self) -> int:
        """[CITATION: HLC-CORE] Total events processed by this clock."""
        return self._event_count

    def detect_skew(self, remote_ts: HLCTimestamp) -> Tuple[bool, float]:
        """
        [CITATION: HLC-CORE] Detect if remote timestamp indicates clock skew.
        
        Returns:
        - (is_skewed, skew_ms): True if skew exceeds threshold, with magnitude
        """
        now_physical = time.time()
        skew = abs(now_physical - remote_ts.pt) * 1000  # ms
        return skew > self.max_skew_ms, skew

    def reset(self) -> None:
        """[CITATION: HLC-CORE] Reset clock to current physical time."""
        self._pt = time.time()
        self._lc = 0


def hlc_max(ts1: HLCTimestamp, ts2: HLCTimestamp) -> HLCTimestamp:
    """[CITATION: HLC-CORE] Return the later of two HLC timestamps."""
    return ts1 if ts1 >= ts2 else ts2


def are_concurrent(ts1: HLCTimestamp, ts2: HLCTimestamp) -> bool:
    """
    [CITATION: HLC-CORE] Check if two timestamps are concurrent (neither happened-before the other).
    
    Concurrent events cannot be causally ordered — they represent independent operations.
    """
    return not (ts1 < ts2 or ts2 < ts1)
