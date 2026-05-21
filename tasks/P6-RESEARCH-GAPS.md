# P6: Research Gaps (Reference As Needed)

**When to open this file:** When you hit a technical question during implementation. Not for systematic reading.

---

## G-1: Omni-Modal Latency Benchmarks

**Question:** Which omni-modal model meets <600ms latency for emotional disclosures?

**Data needed:**
- Qwen3-Omni 30B latency on streaming audio+video
- Gemini 2.5 Pro latency with native audio I/O
- MiniCPM-o 4.5 latency with Omni-Flow TDM
- Measurement: 95th percentile, not average

**Blocker for:** ADR-005, Voice Harness

---

## G-2: Video Generation Cost Model

**Question:** What's the TCO at 100/1,000/10,000 reels/day?

**Data needed:**
- Runway Gen-4.5 cost per reel (credits → dollars)
- Wan 2.6 self-hosted GPU cost per reel
- Veo 3.1 API cost per reel
- Two-tier routing savings vs. single-provider

**Blocker for:** ADR-006, Video Harness

---

## G-3: Dapr Byzantine Overlay Design

**Question:** How to add Byzantine-robust actor resurrection on top of Dapr?

**Data needed:**
- Dapr actor state persistence semantics
- SPIFFE identity verification overhead
- Custom state verification protocol design
- PBFT-backed state commit integration

**Blocker for:** ADR-007, Trust Boundary Model

---

## G-4: Reflection Conformity Protocol

**Question:** How do twins verify each other's reflections are genuine?

**Data needed:**
- Cross-node reflection verification protocol spec
- False positive rate for "reflection is plagiarized/converged"
- Temporal scope: episodic vs. semantic vs. procedural reflection
- MAD-Spear conformity detection on reflection outputs

**Blocker for:** ADR-008, Self-Reflection Mechanism

---

## G-5: Streaming Memory Bounds

**Question:** How does KV-cache grow for infinite streams? What's the eviction policy?

**Data needed:**
- StreamingVLM KV-cache growth rate
- Attention sink stability over hours
- Vision token eviction impact on accuracy
- Memory vs. accuracy tradeoff curve

**Blocker for:** ADR-009, Streaming Architecture

---

## G-6: Containment False Positive Simulation

**Question:** How often do we isolate a good actor that looks bad?

**Data needed:**
- G-Safeguard false positive rate on multi-agent graphs
- MAD-Spear false positive rate on conformity detection
- AgentDropout false positive rate on agent elimination
- Composite system false positive rate

**Blocker for:** ADR-010, Bad Actor Containment

---

## G-7: Cognitive Twin Fidelity Test

**Question:** Can human experts distinguish twin reasoning from real researcher?

**Data needed:**
- Blind A/B test design
- 5 problems per researcher
- Structural similarity metric
- Human expert panel (3+ experts per cluster)

**Blocker for:** P2-COGNITIVE-TWINS validation

---

## G-8: Harness Health Metrics

**Question:** What does "conscious" mean operationally?

**Data needed:**
- Awareness subsystem alert correlation with actual failures
- Health score prediction accuracy
- Direction drift detection precision/recall
- Human evaluation of harness self-reports

**Blocker for:** H-005, Awareness Subsystem Protocol

---

## G-9: Memory Differentiation Validation

**Question:** Do different memory types actually improve performance?

**Data needed:**
- Baseline: uniform memory (all traces stored equally)
- Treatment: differentiated memory (5 types with policies)
- Task: multi-step reasoning with retention test
- Metric: accuracy at 1h, 24h, 7d delays

**Blocker for:** H-006, Memory Protocol

---

## G-10: Outcome-Based Tracking Accuracy

**Question:** Does direction prediction match actual outcomes?

**Data needed:**
- DirectionVector predicted completion vs. actual
- Alignment score correlation with task success
- Drift detection precision/recall
- Course correction effectiveness

**Blocker for:** Awareness Subsystem refinement

---

*This file is a reference. Do not attempt to resolve all gaps at once. Pick the one blocking your current task.*
