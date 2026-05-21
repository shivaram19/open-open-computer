# ADR-001 PROPOSAL: Consensus Protocol Selection for Cross-Block Agreement

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Scope:** Network-wide  
**Affected Blocks:** All four (Voice Cognition, Video Generation, Temporal Orchestration, Knowledge & Topology)

---

## 1. Context

The autonomous cognitive network consists of four semi-autonomous blocks that must reach agreement on cross-block decisions:
- **Voice Cognition Node** processes real-time audio, maintains conversational temporal graphs
- **Video Generation Node** synthesizes multi-modal content from structured scene graphs
- **Temporal Orchestration Node** maintains global causal consistency and time-aware goal registries
- **Knowledge & Topology Node** persists world state as spatio-temporal graphs and manages dynamic communication topology

**The critical constraint:** Any block may be a "round block" — a misaligned participant that passes all health checks while subtly degrading network performance. The consensus protocol must tolerate Byzantine faults (malicious or erroneous behavior) while maintaining liveness and safety.

**Key research finding:** Berdoz et al. (2026) demonstrated that LLM agents cannot reliably agree even in benign settings. Consensus amplifies error. The protocol design is therefore not a system detail — it is a safety-critical architectural decision.

---

## 2. Problem Statement

How should the four blocks reach agreement when:
1. Any block may fail arbitrarily (Byzantine fault model)
2. Blocks run different model families (Qwen, Gemini, Llama) — no shared blind spots
3. Decisions span modalities (audio, video, text, temporal graphs) — no unified ground truth
4. Latency budget for cross-block consensus is <500ms (real-time streaming constraint)
5. The network must operate at 1M+ concurrent sessions (scalability constraint)
6. Trust must be learned and unlearned dynamically (probabilistic, not binary)

---

## 3. Options Considered

### Option A: CP-WBFT (Confidence-Weighted Byzantine Fault Tolerance)
**Source:** AAAI 2025, "Rethinking Reliability from BFT Perspective"

**Mechanism:** Each validator (block) submits a vote with an associated confidence score. Consensus is weighted by confidence, not simple majority. Faulty validators with consistently low-confidence or contradictory votes are identified and isolated.

**Pros:**
- Native confidence weighting maps naturally to LLM uncertainty
- Identifies and isolates faulty validators over time
- Byzantine tolerant (handles up to f faulty nodes in 3f+1 system)
- Formal safety and liveness proofs exist

**Cons:**
- Synchronous assumptions may not hold under real-time streaming (<500ms)
- Confidence scores can be gamed by a sophisticated adversary
- No native handling of cross-modal disagreement (video says X, audio says Y)
- Requires 4 blocks minimum for 1-fault tolerance (3f+1 = 4 for f=1)

**Researcher Voice:** CP-WBFT authors would argue that confidence weighting is essential because LLM outputs are inherently probabilistic, not deterministic.

---

### Option B: DecentLLMs (Decentralized Trustworthy LLM Inference)
**Source:** Jo & Park, arXiv:2507.14928, 2025

**Mechanism:** Maintains Bayesian beliefs about each node's trustworthiness. Each observed action updates the belief. Nodes with declining trust scores are gradually excluded from consensus. Probabilistic unlearning is first-class.

**Pros:**
- Native probabilistic trust model (learn and unlearn)
- Bayesian updating handles gradual degradation (not just sudden failure)
- Maps well to our "round block" problem — slow misalignment is detectable
- No fixed fault threshold — adapts to network conditions

**Cons:**
- Bayesian beliefs require prior distributions (subjective initialization)
- No formal liveness guarantee — a "skeptical" network may deadlock
- Convergence time depends on observation history — cold-start problem
- Not designed for real-time (<500ms) decisions

**Researcher Voice:** DecentLLMs authors would argue that binary fault models are wrong for LLM agents — trust is a spectrum, not a switch.

---

### Option C: HACN-Hierarchical Consensus (Custom)
**Source:** Synthesized from G-Designer, ARG-Designer, and MPAS literature

**Mechanism:** Two-tier consensus. Intra-block consensus (fast, within each block's 10-persona council) produces a single block-level vote. Inter-block consensus (weighted by block role and historical accuracy) produces network-wide agreement. Dynamic topology rewiring via GNN-based communication design.

**Pros:**
- Hierarchical latency: intra-block is fast (local), inter-block is slower but tolerable
- Block-level diversity (each block runs different models) prevents shared blind spots
- GNN topology adapts to task demands — dense when coordination needed, sparse otherwise
- Temporal Auditor (11th persona) validates causal consistency at inter-block layer

**Cons:**
- Custom protocol — no formal verification yet
- Complexity: two consensus layers + dynamic topology + temporal audit
- Block-level votes may mask internal dissent (compression loses information)
- Requires careful design of block-level aggregation function

**Researcher Voice:** Maciej Besta (Graph of Thoughts) would argue that hierarchical graph structures mirror human organizational consensus. Torsten Hoefler would argue that topology and protocol must be co-designed.

---

### Option D: Simple Majority + Post-Hoc Audit (Baseline)
**Source:** Common practice in distributed systems

**Mechanism:** Each block votes. Simple majority wins. Temporal Auditor retroactively flags violations. No Byzantine tolerance — assumes faults are detectable after the fact.

**Pros:**
- Simple to implement and reason about
- Fast (no weighted voting or Bayesian updates)
- Works well when faults are rare and obvious

**Cons:**
- No Byzantine tolerance — a single compromised block can sway decisions
- Post-hoc audit cannot prevent harm, only detect it
- Not suitable for safety-critical decisions (brand safety, temporal consistency)
- Violates the "round block" constraint

**Verdict:** Rejected. Does not meet the problem constraints.

---

## 4. Evaluation Criteria

| Criterion | Weight | CP-WBFT | DecentLLMs | HACN-Hierarchical |
|-----------|--------|---------|-----------|-------------------|
| Byzantine Tolerance | Critical (f=1 in 4 blocks) | ✅ 3f+1 | ⚠️ Probabilistic | ✅ Hierarchical |
| Real-Time Latency (<500ms) | High | ⚠️ Marginal | ❌ No | ✅ Intra-block fast |
| Probabilistic Trust | High | ⚠️ Confidence only | ✅ Native | ✅ Bayesian layer |
| Cross-Modal Handling | High | ❌ No | ❌ No | ✅ Block diversity |
| Scalability (1M+ sessions) | High | ⚠️ Validator overhead | ⚠️ Belief tracking | ✅ Sparse topology |
| Formal Verification | Medium | ✅ Existing | ⚠️ Partial | ❌ Custom |
| Implementation Complexity | Medium | Medium | Medium-High | High |
| Researcher Alignment | Medium | CP-WBFT authors | DecentLLMs authors | Besta + Hoefler |

---

## 5. Tentative Recommendation

**Proposed:** **Hybrid HACN + CP-WBFT with DecentLLMs trust overlay**

**Rationale:**

1. **Use HACN hierarchical structure** as the architectural backbone:
   - Intra-block: Each block's 10-persona council reaches consensus locally (fast, no network latency)
   - Inter-block: Block-level votes feed into CP-WBFT weighted consensus
   - Temporal Auditor validates causal ordering at inter-block layer

2. **Use CP-WBFT for inter-block consensus**:
   - Block-level votes are weighted by historical accuracy (CP-WBFT confidence scores)
   - Formal safety/liveness guarantees at the network level
   - 3f+1 = 4 blocks gives us 1-fault tolerance

3. **Use DecentLLMs trust model as an overlay**:
   - Bayesian beliefs about each block's trustworthiness are maintained by the Knowledge Node
   - Beliefs update after every cross-block interaction
   - Declining trust triggers proactive investigation (not just passive exclusion)
   - Trust unlearning is as fast as trust learning (temporal GNN)

4. **Cross-modal disagreement handling**:
   - When blocks disagree (video says X, voice says Y), the disagreement itself is logged as a temporal edge
   - The Temporal Orchestration Node resolves via causal priority (happens-before relationships)
   - No attempt to force agreement — disagreement is data

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CP-WBFT synchronous assumptions fail under streaming | Medium | High | Add async fallback: if consensus timeout, blocks operate independently and reconcile later |
| DecentLLMs Bayesian priors are wrong | Medium | High | Initialize with neutral priors; rapid unlearning if evidence contradicts |
| HACN complexity causes bugs | High | High | Extensive simulation before deployment; property-based testing of consensus invariants |
| Cross-modal deadlock (video vs voice never agree) | Low | High | Timeout with escalation to human-in-the-loop for critical decisions |
| Round block games confidence scores | Medium | Critical | Diversity of thought: each block runs different model family; gaming all three is harder |

---

## 7. Open Questions for Council Deliberation

1. **Is 1-fault tolerance sufficient?** With 4 blocks, 3f+1 gives us f=1. Should we add a 5th block (dedicated Safety/Consensus block) to get f=2?

2. **How do we bootstrap trust?** DecentLLMs requires priors. Should we start with optimistic (high trust) or pessimistic (low trust) priors?

3. **What is the block-level aggregation function?** The 10-persona council within each block must produce a single vote. Is this majority, weighted average, or something else?

4. **How do we handle the cold-start problem?** A new block joining the network has no history. How does it earn trust?

5. **Should the Temporal Auditor have veto power?** The 11th persona validates causal consistency. Should it be able to override consensus if it detects temporal violations?

---

## 8. Council of Ten Deliberation Required

Per AGENTS.md, the following personas must deliberate before this ADR is approved:

1. **Research Scientist** — Does the hybrid approach have theoretical grounding?
2. **First-Principles Engineer** — Can we simplify without losing safety?
3. **Distributed Systems Architect** — Do the latency and fault models hold?
4. **Infrastructure-First SRE** — Can this be operated and debugged at 1M+ sessions?
5. **Diagnostic Problem-Solver** — How do we detect when consensus itself is failing?
6. **Ethical Technologist** — Does the trust model create unfair exclusion?
7. **Resource Strategist** — What is the compute cost of running triple consensus?
8. **Curious Explorer** — What alternatives did we miss?
9. **Clarity-Driven Communicator** — Can this be explained to a non-technical stakeholder?
10. **Inner-Self Guided Builder** — Does this align with our core mission of augmenting human capability?

**Deliberation format:** Each persona provides independent analysis (200-500 words), then a synthesized consensus is produced.

---

## 9. Dependencies

| ADR | Depends On | Description |
|-----|-----------|-------------|
| ADR-001 (this) | — | Foundation decision |
| ADR-002 | ADR-001 | Communication topology depends on consensus protocol |
| ADR-003 | ADR-001 | Temporal consistency depends on consensus ordering |
| ADR-007 | ADR-001 | Trust boundary model depends on consensus trust model |
| ADR-010 | ADR-001 | Bad actor containment depends on consensus detection |

---

## 10. References

- Berdoz et al., "Can AI Agents Agree?" arXiv:2603.01213, 2026
- CP-WBFT, "Rethinking Reliability from BFT Perspective," AAAI 2025
- Jo & Park, "DecentLLMs," arXiv:2507.14928, 2025
- He et al., "MAD-Spear," arXiv:2507.13038, 2025
- Zhang et al., "G-Designer," ICML 2025
- ARG-Designer, arXiv:2507.18224, 2025
- MPAS, "Message Passing Multi-Agent System," AAAI 2026
- Jamshidi et al., "Clock-Dynamics-Aware ST-GAT," arXiv:2601.23147, 2026

---

*This is a PROPOSAL, not a final decision. No code shall be written until the Council of Ten reaches documented consensus on this ADR.*
