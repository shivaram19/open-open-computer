# ADR-003 PROPOSAL: Temporal Consistency and Causal Ordering

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Depends On:** ADR-001 (Consensus Protocol), ADR-002 (Communication Topology)  
**Scope:** All time-aware operations across blocks  
**Affected Blocks:** Temporal Orchestration Node (primary), all blocks (secondary)

---

## 1. Context

The autonomous cognitive network processes real-time streams (audio, video, text) across distributed blocks. Each block operates with its own clock, message queue, and processing latency. Without explicit causal ordering, the network can make decisions based on stale or reordered information.

**The critical research finding:** arXiv:2604.21361 (2026), "Time, Causality, and Observability Failures in Distributed AI Inference," showed that **3–5ms clock skew silently breaks causal consistency** in multi-node LLM inference pipelines. When one node processes a message "before" another node that actually sent it (due to clock skew), the resulting decisions are logically incoherent.

**In our network:** The Temporal Orchestration Node must maintain a global causal ordering of events such that:
- "The user said X" (Voice block, timestamp T1)
- "The video showed Y" (Video block, timestamp T2)
- "The knowledge graph updated Z" (Knowledge block, timestamp T3)

...are ordered by **happens-before** relationships, not just wall-clock timestamps.

---

## 2. Problem Statement

How do we maintain causal consistency when:
1. Each block has its own physical clock (no shared hardware clock)
2. Network latency between blocks is variable (10ms–200ms depending on topology)
3. Messages carry structured graph data with temporal edges ("event A caused event B")
4. The 11th Temporal Auditor persona must validate causal consistency in real-time
5. Clock skew as small as 3ms can break causality
6. The network must handle 1M+ concurrent sessions, each with its own causal timeline

---

## 3. Options Considered

### Option A: Lamport Timestamps (Logical Clocks)
**Source:** Lamport, "Time, Clocks, and the Ordering of Events in a Distributed System," 1978

**Mechanism:** Each block maintains a monotonic counter. On send: increment counter, attach to message. On receive: counter = max(local, received) + 1.

**Pros:**
- Simple to implement (one integer per block)
- Captures happens-before relationships (if A → B then timestamp(A) < timestamp(B))
- No clock synchronization needed
- Minimal overhead

**Cons:**
- Only partial ordering — concurrent events have no relative order
- No notion of physical time — cannot detect "this event happened 5 seconds ago"
- Cannot measure clock skew
- The Temporal Auditor cannot validate physical causality

**Verdict:** Insufficient for our needs. We need both logical and physical time.

---

### Option B: Vector Clocks
**Source:** Mattern, "Virtual Time and Global States of Distributed Systems," 1988; Fidge, "Timestamps in Message-Passing Systems," 1988

**Mechanism:** Each block maintains a vector of counters (one per block). On send: increment own entry, attach full vector. On receive: element-wise max with received vector, then increment own entry.

**Pros:**
- Captures full causal history (can detect concurrent events explicitly)
- Can identify causality violations (if message arrives with vector indicating unseen events)
- Well-understood, formally verified

**Cons:**
- O(n) space per message (n = number of blocks)
- Does not capture physical time
- With 4 blocks: manageable; with N blocks: scalability concern
- Still cannot detect clock skew

**Researcher Voice:** Mattern would argue that vector clocks are the gold standard for causal ordering. "If you need to know whether two events are causally related or concurrent, there is no simpler solution."

---

### Option C: Hybrid Logical + Physical Clocks (HLC)
**Source:** Kulkarni et al., "Logical Physical Clocks," 2014

**Mechanism:** Each timestamp has two components: (physical_time, logical_counter). Physical time comes from local clock (e.g., NTP-synchronized). Logical counter increments when physical time hasn't changed. On receive: physical = max(local, received), logical = max(local, received) + 1 if physical ties.

**Pros:**
- Captures both physical time and causal ordering
- One timestamp per message (not a vector)
- Can detect clock skew (physical component diverges)
- Well-tested in production systems (CockroachDB, YugaByte)

**Cons:**
- Still requires NTP or similar for physical time synchronization
- Physical clocks can drift between sync intervals
- The logical counter can overflow in extreme cases
- Does not explicitly track "which blocks have seen which events"

**Researcher Voice:** Kulkarni would argue that HLC is the pragmatic sweet spot. "You need physical time for human reasoning and logical time for machine correctness. HLC gives you both in one timestamp."

---

### Option D: Spatio-Temporal Graph Attention (ST-GAT) with Clock Dynamics
**Source:** Jamshidi et al., "Clock-Dynamics-Aware Spatio-Temporal Graph Attention Network," arXiv:2601.23147, 2026

**Mechanism:** A GNN explicitly models clock dynamics as part of the spatio-temporal graph. Each node (block) has a clock state. Edges carry temporal weights that account for clock skew. The GNN learns to correct for observed skew patterns.

**Pros:**
- Learns to correct clock skew automatically (no manual NTP tuning)
- Integrates temporal consistency into the graph memory layer
- Can model complex temporal patterns (seasonal drift, load-dependent skew)
- Directly applicable to our graph memory architecture

**Cons:**
- Requires training data of clock skew patterns
- GNN inference adds latency to every message
- No formal guarantees — learned corrections can fail on unseen patterns
- Complex to debug ("why did the GNN adjust this timestamp by 7ms?")

**Researcher Voice:** Jamshidi would argue that clock dynamics are a first-class feature of distributed systems, not an implementation detail to be hidden. "If you don't model the clock, the clock will model you."

---

### Option E: Causal Observability Health Signal
**Source:** arXiv:2604.21361, 2026

**Mechanism:** A dedicated health-monitoring subsystem continuously probes the network for causal consistency violations. It injects "heartbeat" messages with known causal chains and verifies they arrive in order. Detected violations trigger alerts and automatic correction.

**Pros:**
- Active monitoring (not passive hope)
- Can detect violations that static timestamping misses
- Provides operational visibility into temporal health
- Can be layered on top of any timestamping scheme

**Cons:**
- Heartbeat traffic adds overhead
- Detection is post-hoc (violation already occurred)
- Cannot prevent violations, only detect them
- Alert fatigue if the network is naturally noisy

---

## 4. Evaluation Criteria

| Criterion | Weight | Lamport | Vector Clocks | HLC | ST-GAT | Health Signal |
|-----------|--------|---------|--------------|-----|--------|---------------|
| Causal Ordering Correctness | Critical | ⚠️ Partial | ✅ Full | ✅ Full | ❌ None |
| Physical Time Capture | High | ❌ No | ❌ No | ✅ Yes | ⚠️ Indirect |
| Clock Skew Detection | High | ❌ No | ❌ No | ⚠️ Partial | ✅ Yes |
| Scalability (N blocks) | High | ✅ O(1) | ⚠️ O(n) | ✅ O(1) | ⚠️ O(n²) probes | ⚠️ O(n) traffic |
| Implementation Complexity | Medium | Low | Low | Medium | High | Medium |
| Formal Guarantees | Medium | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Integration with Graph Memory | Medium | ⚠️ Awkward | ⚠️ Awkward | ⚠️ Awkward | ✅ Native | ⚠️ Separate |
| Real-Time Validation (<500ms) | High | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ GNN latency | ⚠️ Probe delay |

---

## 5. Tentative Recommendation

**Proposed:** **Hybrid: HLC as the base timestamp + ST-GAT for skew correction + Causal Health Signal for monitoring**

**Rationale:**

1. **HLC as the universal timestamp:**
   - Every message carries an HLC timestamp: `(physical_ms, logical_counter)`
   - Physical time from NTP-synchronized local clocks (sync every 100ms)
   - Logical counter handles events within the same millisecond
   - HLC timestamps are compact (8 bytes for physical + 2 bytes for logical)

2. **ST-GAT for learned skew correction:**
   - The Knowledge & Topology Node runs a small ST-GAT that observes message flow patterns
   - Learns per-block clock drift rates (e.g., "Video block's clock runs 2ms fast")
   - Applies learned corrections to HLC physical component
   - Falls back to raw HLC if GNN confidence is low
   - GNN operates on aggregated statistics, not per-message (low latency)

3. **Causal Health Signal for active monitoring:**
   - Temporal Orchestration Node injects heartbeat messages every 10 seconds
   - Each heartbeat has a known causal chain: Temporal → Voice → Video → Knowledge → Temporal
   - If the chain returns out-of-order, alarm triggers
   - Health signal feeds into the Temporal Auditor (11th persona)
   - Health score is a first-class metric in the RL Hub

4. **Temporal Auditor validation layer:**
   - Every cross-block decision is validated against HLC happens-before
   - The Auditor maintains a condensed causal graph (not full vector clocks — too heavy)
   - Violations block the decision and trigger investigation
   - Auditor has read-only access to all block message queues

5. **Per-session causal isolation:**
   - Each of the 1M+ concurrent sessions has its own HLC namespace
   - Sessions are causally independent (no cross-session happens-before except through shared knowledge)
   - This prevents the O(n) vector clock problem from becoming O(n × sessions)

---

## 6. Integration with Other ADRs

| ADR | Integration Point |
|-----|-------------------|
| ADR-001 (Consensus) | Consensus votes carry HLC timestamps; Temporal Auditor validates causal ordering of votes |
| ADR-002 (Topology) | Topology changes are themselves causal events — must be ordered relative to ongoing messages |
| ADR-004 (Memory) | PTKG temporal knowledge graphs store HLC timestamps on all temporal edges |
| ADR-010 (Bad Actor) | Temporal violations are a detection signal — a block that consistently causes violations is suspect |

---

## 7. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| NTP sync fails, physical clocks drift | Medium | Critical | Multiple NTP sources + ST-GAT learned drift correction + health signal alerts |
| HLC logical counter overflows | Very Low | High | 64-bit counter (overflows in ~500M years at 1M events/sec) |
| ST-GAT learns wrong drift correction | Medium | High | Validate against health signal; manual override; gradual trust build-up |
| Health signal adds too much traffic | Medium | Medium | Adaptive frequency: frequent during instability, rare during stability |
| Temporal Auditor becomes bottleneck | Medium | High | Auditor operates on sampled validation (10% of decisions), not all |
| Per-session HLC namespaces leak | Low | Critical | Cryptographic session IDs; namespace isolation enforced at kernel level |

---

## 8. Open Questions for Council Deliberation

1. **NTP vs PTP:** Should we use NTP (millisecond precision) or PTP (microsecond precision) for physical time? PTP requires hardware support but gives us headroom on the 3ms skew threshold.

2. **HLC vs CockroachDB-style HLC:** CockroachDB uses a variant with uncertainty intervals. Do we need uncertainty intervals for our use case?

3. **Should the Temporal Auditor have veto power?** If the Auditor detects a causal violation in a consensus decision, should it block the decision or just log a warning?

4. **ST-GAT training data:** How do we collect labeled clock skew data before deployment? Do we need a simulation phase?

5. **Cross-session causality:** When two sessions interact (e.g., shared knowledge graph update), how do we merge their HLC namespaces?

---

## 9. Sanskrit Connection

The Temporal Auditor (11th persona) maps to **Kāla** (time) in the Sanskrit architecture. In Indian philosophy, Kāla is not merely sequence but the ordering principle that makes causation possible. The HLC captures this duality: physical time (Kāla as duration) and logical time (Kāla as order). The health signal is the **Dṛṣṭi** (watchful gaze) that ensures Kāla does not deceive.

---

## 10. References

- Lamport, "Time, Clocks, and the Ordering of Events in a Distributed System," CACM 1978
- Mattern, "Virtual Time and Global States of Distributed Systems," 1988
- Kulkarni et al., "Logical Physical Clocks and Consistent Snapshotting for Distributed Systems," 2014
- Jamshidi et al., "Clock-Dynamics-Aware ST-GAT," arXiv:2601.23147, 2026
- arXiv:2604.21361, "Time, Causality, and Observability Failures in Distributed AI Inference," 2026
- CockroachDB Technical Documentation: HLC Implementation

---

*This is a PROPOSAL, not a final decision. No code shall be written until the Council of Ten reaches documented consensus on this ADR.*
