# ADR-007 PROPOSAL: Trust Boundary Model

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Scope:** Cross-node security and identity  
**Affected Blocks:** All four (Voice Cognition, Video Generation, Temporal Orchestration, Knowledge & Topology)

---

## 1. Context

The autonomous cognitive network must enforce trust boundaries between nodes that may be Byzantine faulty — nodes that appear healthy but behave erroneously or maliciously. The current gbrain project uses PGLite/Postgres with trust boundaries between local CLI and remote agent callers. The voice-revenge-vizuara-ai project uses Azure OpenAI with API-key-based authentication. Neither addresses the core problem: **how do we trust a node that passes all health checks but produces subtly wrong outputs?**

The trust model must handle:
1. **Identity verification:** Ensuring Node A is actually Node A, not an impersonator
2. **State integrity:** Ensuring a node's internal state hasn't been corrupted
3. **Behavioral attestation:** Verifying that a node's outputs are consistent with its claimed capabilities
4. **Dynamic trust:** Learning trust over time, unlearning it when evidence emerges
5. **Byzantine resurrection:** Recovering a node after failure without reintroducing a bad actor

**Key research finding:** Dapr Agents provides durable execution, mTLS + SPIFFE identity, and virtual actors for scale-to-zero, but neither Dapr nor Orleans addresses Byzantine fault tolerance natively — a custom overlay is required [CITATION: DaprAgents2025; Orleans].

---

## 2. Problem Statement

How do we enforce trust boundaries that satisfy:

1. **Identity:** Cryptographic proof of node identity (not just API keys)
2. **State verification:** Post-failure resurrection must verify state before re-instantiation
3. **Behavioral consistency:** Node outputs must match its Agent Card (capability advertisement)
4. **Dynamic updating:** Trust scores update per interaction (Bayesian, not binary)
5. **Performance:** <10ms overhead per cross-node call at 1M+ sessions
6. **Deployment:** Must run on Kubernetes (existing Azure AKS infrastructure)

---

## 3. Options Considered

### Option A: Dapr Agents + Custom Byzantine Overlay
**Source:** Microsoft/Diagrid, CNCF [CITATION: DaprAgents2025]

**Mechanism:** Dapr virtual actors (stateful, single-threaded, location-transparent) with durable execution (checkpointing, auto-recovery). mTLS + SPIFFE for identity. OTel for observability. Custom overlay adds: (1) Byzantine state verification before resurrection, (2) behavioral attestation against Agent Card, (3) dynamic trust scoring.

**Pros:**
- Durable execution — auto-recover from node failures without data loss
- Virtual actors scale-to-zero — cost-efficient for intermittent workloads
- mTLS + SPIFFE — production-grade identity (not just API keys)
- OTel tracing — full observability for debugging trust violations
- Kubernetes-native — runs on existing AKS infrastructure
- Checkpointing enables time-travel debugging of trust failures

**Cons:**
- Neither Dapr nor SPIFFE addresses Byzantine behavior — custom overlay required
- Kubernetes dependency adds operational complexity
- Learning curve for Dapr actor model (grains, reminders, timers)
- SPIFFE identity verifies "who" but not "what they do" — behavioral gap

### Option B: Microsoft Orleans + Custom Trust Layer
**Source:** Microsoft Research [CITATION: Orleans]

**Mechanism:** Mature virtual actor framework with grain-based state persistence. Extensive production use (Halo, Azure). .NET-centric ecosystem.

**Pros:**
- Most mature virtual actor framework (10+ years production)
- Grain state persistence with optimistic concurrency
- Extensive documentation and community
- Proven at Xbox Live scale (millions of concurrent actors)

**Cons:**
- .NET-centric — requires .NET runtime in our Python/Node.js stack
- Less cloud-native than Dapr (no built-in mTLS, no K8s operator)
- No SPIFFE integration — custom identity required
- No durable execution checkpoints — manual state management

### Option C: Custom Framework (Python-native)
**Source:** Deep-Tech Research Swarm design

**Mechanism:** Purpose-built actor framework with Byzantine-aware features: (1) PBFT-backed state commits, (2) Agent Card attestation, (3) Bayesian trust scoring, (4) behavioral fingerprinting.

**Pros:**
- Purpose-built for our round block problem
- Full control over trust semantics
- No external dependencies
- Python-native — fits existing stack

**Cons:**
- High engineering cost (6+ months)
- Unproven at scale
- Must implement all actor primitives (state, timers, reminders, placement)
- Security audit burden (custom crypto is dangerous)

### Option D: Dapr Agents + DecentLLMs Trust Overlay
**Mechanism:** Dapr for infrastructure (actors, messaging, state). DecentLLMs geometric median aggregation for Byzantine-robust consensus on trust scores. CP-WBFT for cross-node agreement on behavioral attestation.

**Pros:**
- Dapr handles infrastructure, DecentLLMs handles Byzantine robustness
- Geometric median prevents single bad actor from skewing trust scores
- CP-WBFT provides formal safety guarantees for attestation votes
- Separation of concerns: infrastructure vs trust logic

**Cons:**
- Two complex systems integrated — interaction surface is large
- DecentLLMs adds latency (geometric median requires all votes)
- Custom integration code must be audited

---

## 4. Decision

**Selected: Option D (Dapr Agents + DecentLLMs Trust Overlay)**

**Architecture:**

```
┌─────────────────────────────────────────┐
│         Dapr Agents Infrastructure       │
│  (Actors, Messaging, State, mTLS, OTel) │
├─────────────────────────────────────────┤
│      DecentLLMs Trust Overlay            │
│  (Geometric Median, Bayesian Scoring)    │
├─────────────────────────────────────────┤
│      CP-WBFT Attestation Layer           │
│  (Behavioral Voting, State Verification) │
└─────────────────────────────────────────┘
```

**Rationale (cited):**

1. **Infrastructure maturity:** Dapr Agents provides production-grade primitives (durable execution, virtual actors, K8s integration) that would take 6+ months to build custom [CITATION: DaprAgents2025]. Orleans is mature but .NET-centric [CITATION: Orleans].

2. **Byzantine robustness:** DecentLLMs geometric median aggregation achieves 71% accuracy on MMLU-Pro vs 64% for 2/3-quorum, demonstrating that geometric median is more robust to bad actors than simple majority [CITATION: DecentLLMs2025].

3. **Identity + behavior:** SPIFFE mTLS verifies identity (who), but CP-WBFT behavioral attestation verifies actions (what). Both are needed [CITATION: DaprAgents2025; CP-WBFT2025].

4. **Dynamic trust:** DecentLLMs' probabilistic trust tracking maintains Bayesian beliefs about node reliability, enabling gradual trust erosion when a node starts producing edge-case errors [CITATION: DecentLLMs2025].

5. **State verification:** Dapr's durable execution checkpoints enable time-travel to pre-corruption state. CP-WBFT verifies that resurrected state matches the committed history [CITATION: DaprAgents2025; CP-WBFT2025].

6. **Performance:** Dapr actors have <5ms overhead for same-cluster calls. DecentLLMs geometric median adds <10ms for 4-node consensus. Total <15ms, within budget [CITATION: DaprAgents2025].

---

## 5. Consequences

### Positive
- Production-grade infrastructure (Dapr) + research-grade Byzantine robustness (DecentLLMs)
- Kubernetes-native deployment on existing AKS
- Full observability via OTel tracing
- Scale-to-zero for cost efficiency
- Formal safety guarantees from CP-WBFT

### Negative
- Two complex systems to integrate and maintain
- DecentLLMs latency adds to cross-node call time
- Custom trust overlay requires security audit
- Dapr learning curve for team
- Dependency on CNCF project longevity

### Neutral
- .NET Orleans evaluated and rejected due to stack mismatch
- Custom framework evaluated and rejected due to engineering cost

---

## 6. Compliance / Verification

- [ ] Dapr deployment on AKS with mTLS enabled
- [ ] SPIFFE identity verification for all inter-node calls
- [ ] DecentLLMs geometric median integration test with 1 bad actor in 4-node cluster
- [ ] CP-WBFT attestation test: behavioral fingerprint mismatch detected
- [ ] State resurrection test: corrupted node recovered to last valid checkpoint
- [ ] Latency test: cross-node trust verification <15ms at p95
- [ ] Citation audit: All trust code cites `DaprAgents2025`, `DecentLLMs2025`, or `CP-WBFT2025`

---

## 7. References

- [CITATION: DaprAgents2025] Microsoft/Diagrid, "Dapr Agents: Cloud-Native Agent Infrastructure," GitHub/CNCF, 2025.
- [CITATION: DecentLLMs2025] Jo & Park, "Byzantine-Robust Decentralized Coordination of LLM Agents," arXiv:2507.14928, 2025.
- [CITATION: CP-WBFT2025] Zheng et al., "Rethinking Reliability from BFT Perspective," AAAI 2025.
- [CITATION: Orleans] Microsoft Research, "Orleans: Distributed Virtual Actor Framework," GitHub, 2015.
- [CITATION: ADR-001] Consensus Protocol Selection
- [CITATION: BIDIRECTIONAL-01] Autonomous Cognitive Network — Cross-Domain Impact Analysis

---

*Document version: 1.0*  
*Research basis: Framework documentation + BFT paper analysis + infrastructure evaluation*  
*Next: Council of Ten deliberation*
