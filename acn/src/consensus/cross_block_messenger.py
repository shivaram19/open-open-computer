# src/consensus/cross_block_messenger.py
"""
Cross-Block Messenger: Distributed Message Passing with HLC Stamps.

Enables agents to communicate across process boundaries with:
- HLC timestamping on every message
- Causal ordering guarantees
- Async message queues
- Message envelope with routing metadata

This is the bridge between in-memory agent communication and true
distributed execution. Even in single-process mode, it enforces
the same message envelope format that would be used across network.

Design inspired by:
- TemporalObservability2026: Transport-agnostic causality failure
- Kafka/ZeroMQ: Message-oriented middleware patterns
- ADR-002: Hierarchical hub-and-spoke with topology optimization

[CITATION: TemporalObservability2026]
[CITATION: ADR-002]
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque

from shared.utils.citations import cite
from consensus.hlc import HybridLogicalClock, HLCTimestamp


@dataclass
class MessageEnvelope:
    """[CITATION: MESSENGER] A stamped message for cross-agent communication."""
    message_id: str
    sender_id: str
    recipient_id: str
    payload: Dict[str, Any]
    hlc_timestamp: HLCTimestamp
    sent_at: float = field(default_factory=time.time)
    deliver_after: Optional[float] = None  # For simulated delay
    causal_deps: List[str] = field(default_factory=list)  # message_ids this depends on

    def to_dict(self) -> Dict[str, Any]:
        """[CITATION: MESSENGER] Serialize envelope."""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "payload": self.payload,
            "hlc_timestamp": self.hlc_timestamp.to_dict(),
            "sent_at": self.sent_at,
            "causal_deps": self.causal_deps,
        }


@cite(
    key="CROSS-BLOCK-MESSENGER",
    paper="Cross-Block Messenger: Distributed Message Passing with HLC",
    venue="ACN Architecture Document",
    section="Cross-Block Messaging",
    rationale="Transport-agnostic message envelopes with HLC stamps enable causal ordering regardless of underlying transport",
    confidence="CERTAIN",
)
class CrossBlockMessenger:
    """
    [CITATION: MESSENGER] Distributed message passing with HLC causality tracking.
    
    Each agent has a message queue. Messages are stamped with HLC timestamps
    and optionally delayed to simulate network conditions.
    
    The messenger enforces causal delivery: a message is only delivered after
    all its causal dependencies have been delivered.
    """

    def __init__(
        self,
        messenger_id: str = "cross-block-messenger",
        max_queue_size: int = 1000,
        simulate_delay_ms: float = 0.0,
    ):
        """[CITATION: MESSENGER] Initialize messenger."""
        self.messenger_id = messenger_id
        self.max_queue_size = max_queue_size
        self.simulate_delay_ms = simulate_delay_ms
        
        self._queues: Dict[str, deque] = defaultdict(deque)
        self._hlc_clocks: Dict[str, HybridLogicalClock] = {}
        self._delivered: set = set()  # message_ids already delivered
        self._handlers: Dict[str, Callable] = {}  # agent_id -> handler
        self._message_count = 0

    def register_agent(self, agent_id: str, handler: Optional[Callable] = None) -> None:
        """[CITATION: MESSENGER] Register an agent with optional delivery handler."""
        if agent_id not in self._hlc_clocks:
            self._hlc_clocks[agent_id] = HybridLogicalClock(node_id=agent_id)
        if handler:
            self._handlers[agent_id] = handler

    def send(
        self,
        sender_id: str,
        recipient_id: str,
        payload: Dict[str, Any],
        causal_deps: Optional[List[str]] = None,
    ) -> MessageEnvelope:
        """
        [CITATION: MESSENGER] Send a message from sender to recipient.
        
        Generates HLC timestamp, creates envelope, and queues for delivery.
        """
        clock = self._hlc_clocks.get(sender_id)
        if clock is None:
            clock = HybridLogicalClock(node_id=sender_id)
            self._hlc_clocks[sender_id] = clock
        
        hlc = clock.send()
        
        envelope = MessageEnvelope(
            message_id=f"msg-{uuid.uuid4().hex[:12]}",
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            hlc_timestamp=hlc,
            causal_deps=causal_deps or [],
        )
        
        if self.simulate_delay_ms > 0:
            envelope.deliver_after = time.time() + (self.simulate_delay_ms / 1000.0)
        
        queue = self._queues[recipient_id]
        if len(queue) >= self.max_queue_size:
            queue.popleft()  # Drop oldest
        
        queue.append(envelope)
        self._message_count += 1
        
        return envelope

    def broadcast(
        self,
        sender_id: str,
        recipient_ids: List[str],
        payload: Dict[str, Any],
    ) -> List[MessageEnvelope]:
        """[CITATION: MESSENGER] Broadcast a message to multiple recipients."""
        envelopes = []
        for rid in recipient_ids:
            env = self.send(sender_id, rid, payload)
            envelopes.append(env)
        return envelopes

    def poll(self, agent_id: str, max_messages: int = 10) -> List[MessageEnvelope]:
        """
        [CITATION: MESSENGER] Poll for deliverable messages for an agent.
        
        A message is deliverable if:
        1. Its deliver_after time has passed (simulated delay)
        2. All its causal dependencies have been delivered
        """
        queue = self._queues.get(agent_id, deque())
        deliverable = []
        now = time.time()
        
        # Scan queue for deliverable messages
        remaining = deque()
        for envelope in queue:
            if len(deliverable) >= max_messages:
                remaining.append(envelope)
                continue
            
            # Check delay
            if envelope.deliver_after is not None and envelope.deliver_after > now:
                remaining.append(envelope)
                continue
            
            # Check causal dependencies
            deps_satisfied = all(dep in self._delivered for dep in envelope.causal_deps)
            if not deps_satisfied:
                remaining.append(envelope)
                continue
            
            # Update recipient's HLC
            recipient_clock = self._hlc_clocks.get(agent_id)
            if recipient_clock is not None:
                recipient_clock.receive(envelope.hlc_timestamp)
            
            self._delivered.add(envelope.message_id)
            deliverable.append(envelope)
        
        self._queues[agent_id] = remaining
        return deliverable

    def deliver_all(self, agent_id: str) -> List[MessageEnvelope]:
        """[CITATION: MESSENGER] Deliver all pending messages for an agent."""
        return self.poll(agent_id, max_messages=10000)

    def get_pending_count(self, agent_id: str) -> int:
        """[CITATION: MESSENGER] Count pending messages for an agent."""
        return len(self._queues.get(agent_id, deque()))

    def get_message_stats(self) -> Dict[str, Any]:
        """[CITATION: MESSENGER] Messenger statistics."""
        return {
            "messenger_id": self.messenger_id,
            "total_messages_sent": self._message_count,
            "registered_agents": len(self._hlc_clocks),
            "pending_by_agent": {
                aid: len(q) for aid, q in self._queues.items()
            },
            "delivered_count": len(self._delivered),
        }

    def reset(self) -> None:
        """[CITATION: MESSENGER] Clear all queues and state."""
        self._queues.clear()
        self._delivered.clear()
        self._message_count = 0
