# ADR-004 PROPOSAL: Memory Architecture — Temporal Knowledge Graphs vs Stream Forest

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Depends On:** ADR-001 (Consensus), ADR-003 (Temporal Consistency)  
**Scope:** Knowledge & Topology Node (primary), all blocks (secondary)  
**Affected Components:** Persistent storage, retrieval, graph evolution, unlearning

---

## 1. Context

The Knowledge & Topology Node must store the "world state" of the autonomous cognitive network. This includes:
- **4D scene graphs** from video understanding (objects, relations, attributes, 3D coordinates, timestamps)
- **Conversational temporal graphs** from voice interactions (utterances, intents, emotions, causal chains)
- **Generation decision graphs** from video/content creation (templates, parameters, outcomes, brand compliance)
- **Trust graphs** from cross-block interactions (block reputation, confidence history, violation records)
- **Causal event graphs** from temporal orchestration (happens-before relationships, litigation chains)

**Total estimated scale:** 1M+ concurrent sessions × 1000+ graph nodes per session × hours of operation = billions of nodes and edges.

**The critical research finding:** Temporal GNNs must unlearn trust as fast as they learn it. A static knowledge graph that accumulates forever becomes a liability — old incorrect beliefs compound, stale relationships dominate retrieval, and the graph's own size becomes an attack vector (poisoning via historical injection).

---

## 2. Problem Statement

How should the network store, retrieve, and evolve knowledge when:
1. Knowledge is inherently temporal ("the cup was on the table at T1, moved at T2")
2. Knowledge must be forgettable (incorrect beliefs, stale trust, revoked permissions)
3. Retrieval must be fast (<100ms for real-time decisions)
4. The graph must support causal reasoning ("why did X happen?" requires traversing temporal edges)
5. Cross-modal queries must work ("show me the video segment where the user said Y")
6. The system must scale to billions of nodes without degradation

---

## 3. Options Considered

### Option A: PTKG (Periodic Temporal Knowledge Graph)
**Source:** AAAI 2026, "ViG-RAG: Video-aware Graph Retrieval-Augmented Generation"

**Mechanism:** Knowledge is stored as a temporal knowledge graph where each fact has an associated time interval [start, end] and confidence score. Facts are versioned: when a belief changes, the old fact is marked with an end time and a new fact is inserted. Retrieval queries specify a timestamp and receive the graph state at that time.

**Pros:**
- Native temporal versioning — query "what did we believe at T?" directly
- Confidence scores enable probabilistic reasoning
- Well-suited to video understanding (ViG-RAG demonstrated retrieval over hours of video)
- Supports temporal validity intervals ("this fact was true from T1 to T2")

**Cons:**
- Versioning creates graph bloat (every update doubles nodes)
- No native unlearning — old facts persist with low confidence
- Temporal indexing overhead (must index on time + entity + relation)
- Complex query language (need to specify time context)

**Researcher Voice:** ViG-RAG authors would argue that temporal validity is intrinsic to knowledge, not an annotation. "A fact without a time is not a fact — it's a fiction."

---

### Option B: StreamForest / StreamMem / HERMES
**Source:** Multiple papers, 2025–2026

**Mechanism:** Instead of a single persistent graph, maintain a forest of streaming graph snapshots. Each snapshot captures the graph state at a given time window. Old snapshots are compressed, merged, or discarded based on relevance. Retrieval traverses the most recent snapshot and selectively dips into historical snapshots.

**Pros:**
- Natural streaming semantics — matches our real-time processing model
- Old snapshots can be aggressively compressed or deleted (true unlearning)
- Parallelizable — different sessions operate on different snapshot trees
- Matches StreamingVLM and Venus architectures

**Cons:**
- Causal reasoning across snapshots is expensive (must merge or traverse multiple trees)
- Snapshot granularity is a tuning parameter (too fine = overhead, too coarse = lost detail)
- No unified query interface across the forest
- Complex consistency model (when do snapshots commit?)

**Researcher Voice:** Streaming cognition researchers would argue that memory should mirror perception — continuous, bounded, and forgetful. "A system that never forgets is a system that never learns."

---

### Option C: Selective Amnesia with Tiered Storage (Smṛti Model)
**Source:** ADR-010 Sanskrit Architecture + Neuromorphic Computing Principles

**Mechanism:** Three memory tiers inspired by human memory:
- **Working Memory (Saṃvedana):** Recent graph state (last 5 minutes), fully materialized, fast access
- **Episodic Memory (Smṛti):** Compressed event summaries (last 24 hours), lossy but queryable
- **Semantic Memory (Śruti):** Long-term distilled knowledge (indefinite), highly compressed, slow to update

Unlearning is tier-dependent:
- Working: immediate eviction
- Episodic: gradual decay (exponential forgetting curve)
- Semantic: requires explicit re-consolidation (new evidence must outweigh old)

**Pros:**
- Matches human cognitive architecture (well-studied, well-understood)
- Each tier optimized for its access pattern
- Natural unlearning through decay and re-consolidation
- The Sanskrit terms map directly to our existing architecture (ADR-010)

**Cons:**
- Compression between tiers is lossy — some detail is irretrievably lost
- Re-consolidation requires consensus (which block decides what counts as "long-term knowledge?")
- No direct precedent in production AI systems (research concept)
- Complex to implement and tune (three tiers + transition rules + decay functions)

**Researcher Voice:** The Sanskrit architecture (ADR-010) treats memory as selective amnesia — Śruti (that which is remembered) is not total recall but distilled wisdom. "What you choose to forget is as important as what you choose to remember."

---

### Option D: World Scene Graph with Object Permanence (WSGG + PWG)
**Source:** Peddi et al., "WSGG," arXiv:2603.13185, 2026

**Mechanism:** A persistent 3D world scene graph that maintains object permanence — objects that leave the field of view are not deleted but marked as "occluded" with predicted location. The graph evolves continuously as new observations arrive, with old observations updated rather than versioned.

**Pros:**
- Object permanence is critical for embodied reasoning (robotics, AR)
- Single unified graph (no versioning, no snapshots)
- Physical consistency enforced (objects cannot teleport without cause)
- Directly applicable to video understanding and generation

**Cons:**
- No native temporal querying ("what did we believe at T?" requires reconstruction)
- Object prediction errors compound over time (drift)
- No formal unlearning mechanism (old observations are overwritten, not forgotten)
- Designed for single-session scenes, not multi-session persistent knowledge

**Researcher Voice:** Rohith Peddi would argue that frame-centric memory is wrong — the world persists when you look away. "True understanding requires reasoning about what you cannot see."

---

## 4. Evaluation Criteria

| Criterion | Weight | PTKG | StreamForest | Tiered Smṛti | WSGG |
|-----------|--------|------|-------------|--------------|------|
| Temporal Query Support | Critical | ✅ Native | ⚠️ Across snapshots | ⚠️ Tier-dependent | ❌ Reconstruct |
| Unlearning Capability | Critical | ⚠️ Low confidence | ✅ Delete snapshots | ✅ Decay + re-consolidation | ⚠️ Overwrite |
| Retrieval Speed (<100ms) | Critical | ⚠️ Index overhead | ✅ Recent snapshot | ✅ Working memory | ✅ Single graph |
| Causal Reasoning | High | ✅ Temporal edges | ⚠️ Cross-snapshot | ⚠️ Episodic chains | ✅ Physical causality |
| Cross-Modal Retrieval | High | ✅ PTKG supports | ⚠️ Per-snapshot | ⚠️ Tier-dependent | ⚠️ Visual only |
| Scalability (billions) | High | ⚠️ Bloat | ✅ Forest parallel | ⚠️ Three tiers | ⚠️ Single graph |
| Implementation Maturity | Medium | ⚠️ Research | ⚠️ Research | ❌ Conceptual | ⚠️ Research |
| Integration with Graph Memory Block | High | ✅ ViG-RAG | ⚠️ Streaming | ✅ Sanskrit mapping | ✅ WSGG native |

---

## 5. Tentative Recommendation

**Proposed:** **Hybrid: Tiered Smṛti as the conceptual model + PTKG as the physical storage layer + StreamForest for session isolation**

**Rationale:**

1. **Tiered Smṛti as the conceptual model:**
   - Working Memory: Last 5 minutes of graph state, fully materialized in memory (Redis/Dragonfly)
   - Episodic Memory: Last 24 hours, stored as PTKG with temporal validity intervals
   - Semantic Memory: Indefinite, distilled knowledge graph with confidence-weighted facts
   - Unlearning: Working = immediate, Episodic = exponential decay (half-life 6 hours), Semantic = requires consensus-weighted re-consolidation

2. **PTKG as the physical storage for Episodic and Semantic tiers:**
   - All facts stored as (entity, relation, entity, start_time, end_time, confidence)
   - Temporal indexing: B-tree on time range + inverted index on entities
   - Query: "What relationships existed for entity E during [T1, T2] with confidence > θ?"
   - Graph database: Neo4j with temporal extension or custom PTKG implementation

3. **StreamForest for session isolation:**
   - Each of the 1M+ sessions has its own snapshot tree
   - Session trees are rooted in the shared Semantic Memory (common knowledge)
   - Session-specific beliefs branch from the shared root
   - Session termination triggers snapshot archival or deletion (configurable)

4. **WSGG integration for Perception Block:**
   - The Perception Block (video understanding) maintains a real-time WSGG for the current scene
   - WSGG snapshots are periodically compressed and stored as PTKG entries
   - Object permanence transitions from WSGG (active) → PTKG (archived) → Smṛti (semantic)

5. **Unlearning protocol:**
   - **Working:** LRU eviction + explicit delete API
   - **Episodic:** Exponential decay function: confidence(t) = confidence(0) × e^(-λt). When confidence < threshold, fact is archived.
   - **Semantic:** Requires a "re-consolidation consensus" — three blocks must agree that new evidence overrides old belief. Old belief is not deleted but marked "superseded" with a pointer to the replacement.

---

## 6. Integration with Other ADRs

| ADR | Integration Point |
|-----|-------------------|
| ADR-001 (Consensus) | Re-consolidation of semantic memory requires cross-block consensus |
| ADR-002 (Topology) | Session trees mirror communication topology — active sessions have active spokes |
| ADR-003 (Temporal) | All PTKG entries carry HLC timestamps for causal ordering |
| ADR-005 (Omni-Modal) | Cross-modal facts stored as typed entities in PTKG |
| ADR-010 (Bad Actor) | Trust graph is a first-class PTKG subgraph with accelerated decay for suspicious blocks |

---

## 7. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PTKG bloat from versioning | High | High | Aggressive compression of old versions; archive to cold storage |
| StreamForest inconsistency | Medium | High | Commit protocol: session snapshot only commits after Temporal Auditor validates causal ordering |
| Smṛti tier transitions lose critical info | Medium | Critical | Safety-critical facts (brand violations, safety incidents) bypass decay and go directly to Semantic |
| Re-consolidation consensus deadlock | Low | High | Timeout with fallback: if consensus fails, old belief persists and alert is raised |
| Cross-session query performance | Medium | High | Shared Semantic Memory pre-materializes common queries; session-specific queries are parallelized |

---

## 8. Open Questions for Council Deliberation

1. **What is the decay rate λ for Episodic Memory?** Too fast = lost context; too slow = bloat.

2. **Should safety-critical facts ever decay?** A safety violation from a year ago might still be relevant.

3. **How do we handle contradictory beliefs across sessions?** Session A believes X, Session B believes not-X. Which goes into Semantic Memory?

4. **What is the physical storage backend?** Neo4j, TigerGraph, custom implementation, or something else?

5. **How do we query across all three tiers in a single request?** Working + Episodic + Semantic may each have relevant information.

---

## 9. References

- ViG-RAG, "Video-aware Graph Retrieval-Augmented Generation," AAAI 2026
- Peddi et al., "WSGG: World Scene Graph Generation," arXiv:2603.13185, 2026
- StreamForest / StreamMem / HERMES, 2025–2026
- PTKG (Periodic Temporal Knowledge Graph) literature
- Human Memory Research: Working Memory (Baddeley), Episodic Memory (Tulving), Memory Reconsolidation (Nader)
- ADR-010: Sanskrit Architecture (Śruti → Saṃvedana → Smṛti)

---

*This is a PROPOSAL, not a final decision. No code shall be written until the Council of Ten reaches documented consensus on this ADR.*
