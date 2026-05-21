# ADR-002 PROPOSAL: Communication Topology for Cross-Block Messaging

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Depends On:** ADR-001 (Consensus Protocol Selection)  
**Scope:** Network-wide message routing and agent-to-agent protocol  
**Affected Blocks:** All four + inter-block edges

---

## 1. Context

The autonomous cognitive network requires a communication topology that determines:
- Which blocks can message which other blocks
- How messages are routed, serialized, and validated
- How the topology itself adapts to changing task demands
- What protocol carries the messages (A2A, MCP, custom graph protocol)

**The critical insight from research:** Topology is destiny — and also a security choice. NetSafe (Yu et al., ACL 2025) showed that fully-connected multi-agent networks are more vulnerable to conformity attacks than sparsely-connected ones. G-Designer (Zhang et al., ICML 2025) demonstrated that GNN-based topology design can improve task performance by 15-40% by routing messages through structurally optimal paths.

**The tension:** Dense connectivity enables rich information sharing (good for emergent capabilities) but increases attack surface (bad for Byzantine tolerance). Sparse connectivity limits information flow but contains fault propagation.

---

## 2. Problem Statement

How should the four blocks be connected when:
1. Different tasks require different coordination patterns (video generation needs tight Voice↔Video coupling; litigation graph needs Temporal↔Knowledge coupling)
2. The topology must adapt without human intervention as task demands shift
3. A compromised block should be containable — its influence limited by network distance
4. Messages carry structured graph data (EVSG, PTKG, 4DSG) — not just text
5. The network must scale from 4 blocks to N blocks as new capabilities are added
6. Cross-block latency must stay under 500ms for real-time decisions

---

## 3. Options Considered

### Option A: Static Fully-Connected Graph (Baseline)
**Mechanism:** Every block can message every other block directly. Fixed edges. Simple pub/sub or direct RPC.

**Pros:**
- Maximum information sharing
- Simple to implement and reason about
- No topology management overhead

**Cons:**
- O(n²) message complexity — does not scale
- Single compromised block can influence all others directly
- No task-specific optimization
- Violates NetSafe principles (fully-connected = vulnerable)

**Verdict:** Rejected. Violates security constraints.

---

### Option B: G-Designer Adaptive GNN Topology
**Source:** Zhang et al., ICML 2025

**Mechanism:** A GNN learns optimal communication topologies for each task type. Given a task embedding, the GNN outputs a sparse adjacency matrix specifying which blocks should communicate. Topology rewires dynamically per task.

**Pros:**
- Task-optimal routing (15-40% performance improvement demonstrated)
- Sparse by design — limits attack surface
- Formalized as a learning problem with trainable parameters
- Can incorporate block capabilities as node features

**Cons:**
- GNN training requires labeled task-topology pairs (expensive)
- Topology changes introduce latency (rewiring cost)
- No formal safety guarantees — a learned topology might create unexpected bottlenecks
- Cold-start: new task types have no learned topology

**Researcher Voice:** Zhang et al. would argue that topology should be a learned parameter, not a human-designed constant. "The network should discover its own optimal communication structure."

---

### Option C: ARG-Designer Autoregressive Topology Generation
**Source:** arXiv:2507.18224, 2025

**Mechanism:** An autoregressive model generates the topology one edge at a time, conditioned on task requirements and current network state. Each generated edge is validated against safety constraints before being added.

**Pros:**
- More expressive than GNN — can generate arbitrary graph structures
- Constraint-aware generation (safety rules baked into the generative model)
- Handles novel task types better than GNN (generalizes via autoregressive prior)

**Cons:**
- Autoregressive generation is slow (sequential edge generation)
- More complex than GNN — harder to debug
- No published large-scale deployment evidence
- Constraint validation adds per-edge latency

**Researcher Voice:** ARG-Designer authors would argue that autoregressive generation is the natural choice for graph-structured outputs, mirroring the success of autoregressive models in other domains.

---

### Option D: Hierarchical Hub-and-Spoke with Dynamic Spokes
**Source:** Synthesized from CrewAI crew/process model + Dapr Agents durable execution

**Mechanism:**
- A central "orchestrator hub" (Temporal Orchestration Node) manages all cross-block communication
- Blocks register capabilities with the hub
- For each task, the hub dynamically creates a temporary "spoke" subgraph connecting only the relevant blocks
- Spokes are torn down after task completion
- Hub maintains persistent state across tasks (via Dapr-style durable execution)

**Pros:**
- Centralized visibility — the hub sees all cross-block traffic (good for audit)
- Dynamic spokes contain fault propagation (compromised block only affects its current spoke)
- Maps naturally to CrewAI's crew/process/task hierarchy
- Durable execution ensures message delivery even during block failures

**Cons:**
- Hub is a single point of failure (mitigated by hot standby)
- All cross-block traffic flows through hub — potential bottleneck
- Latency: hub adds one hop to every message
- Centralization may conflict with decentralized consensus (ADR-001)

**Researcher Voice:** João Moura (CrewAI) would argue that organizational hierarchy is a proven pattern for coordinating complex work. The hub is not a bottleneck — it's a conductor.

---

### Option E: Protocol-Layer Abstraction (A2A + MCP + Custom Graph Protocol)
**Source:** Google ADK, Anthropic MCP, OpenAI Agents SDK

**Mechanism:** Rather than fixing the topology, fix the protocol. Blocks communicate via standardized messages that carry structured graph data. The topology is an implementation detail — blocks discover each other via a capability registry and establish direct connections as needed.

**Pros:**
- Protocol interoperability — new blocks can join without topology changes
- Decouples message format from routing
- A2A supports rich structured data (not just text)
- MCP enables tool-calling between blocks

**Cons:**
- Protocol abstraction doesn't solve the topology problem — it defers it
- Discovery and capability matching adds overhead
- Three protocols (A2A, MCP, custom) may create fragmentation

**Researcher Voice:** Google ADK team would argue that agent-to-agent communication should be standardized at the protocol layer, not the topology layer.

---

## 4. Evaluation Criteria

| Criterion | Weight | G-Designer | ARG-Designer | Hub-and-Spoke | Protocol Abstraction |
|-----------|--------|-----------|--------------|---------------|---------------------|
| Security (attack containment) | Critical | ✅ Sparse | ✅ Sparse | ✅ Spoke isolation | ⚠️ Depends on impl |
| Task Optimization | High | ✅ 15-40% | ⚠️ Theoretical | ⚠️ Manual | ❌ No |
| Scalability (N blocks) | High | ✅ O(edges) | ⚠️ Slow gen | ⚠️ Hub bottleneck | ✅ O(connections) |
| Latency (<500ms) | High | ✅ Fast | ❌ Slow gen | ⚠️ Hub hop | ✅ Direct |
| Formal Safety | Medium | ❌ No | ❌ No | ⚠️ Dapr provides some | ❌ No |
| Implementation Complexity | Medium | Medium | High | Medium | Low |
| Cold-Start Handling | Medium | ❌ Needs data | ✅ Better | ✅ Always works | ✅ Always works |
| Auditability | Medium | ⚠️ Black box | ⚠️ Black box | ✅ Hub sees all | ⚠️ Distributed |

---

## 5. Tentative Recommendation

**Proposed:** **Hybrid: Hierarchical Hub-and-Spoke with G-Designer topology optimization within spokes**

**Rationale:**

1. **Hub-and-spoke as the architectural backbone:**
   - Temporal Orchestration Node serves as the hub — already responsible for causal consistency and time-aware goal registries
   - Hub maintains durable execution state (Dapr-style) — messages survive block failures
   - Hub creates task-specific spokes: for video generation tasks, spoke connects Voice↔Video↔Knowledge; for litigation tasks, spoke connects Temporal↔Knowledge↔Video

2. **G-Designer optimizes within spokes:**
   - Within each spoke (3-4 blocks), G-Designer learns optimal message routing
   - GNN operates on small graphs (fast inference)
   - Training data: historical task-topology-performance triples
   - Fallback: if GNN unavailable, use fully-connected within spoke (small enough to be safe)

3. **Protocol abstraction at the message layer:**
   - Blocks communicate via A2A protocol for agent-to-agent messages
   - MCP used for tool-calling (one block calling another block's capability as a tool)
   - Custom graph protocol for structured data (EVSG, PTKG, 4DSG embeddings)
   - Protocol is orthogonal to topology — blocks can speak any protocol over any spoke connection

4. **Safety constraints hard-coded:**
   - Voice block cannot directly message Generation block without Temporal hub validation (prevents off-brand audio injection)
   - Knowledge block maintains read-only access to all spokes (audit trail)
   - Spoke maximum size: 4 blocks (prevents fully-connected large subgraphs)

---

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Hub becomes bottleneck | Medium | High | Hot standby hub; spoke-to-spoke direct connections for high-bandwidth streams |
| G-Designer generates unsafe topology | Medium | Critical | Safety constraints validated before any topology change; manual override available |
| Protocol fragmentation (A2A + MCP + custom) | High | Medium | Define clear protocol selection rules per message type; unify where possible |
| Hub compromise = total network compromise | Low | Critical | Hub runs triple-redundant consensus internally; Temporal Auditor validates all hub decisions |
| Spoke creation latency exceeds budget | Medium | High | Pre-warm common spoke patterns; cache topology decisions |

---

## 7. Open Questions for Council Deliberation

1. **Should the hub be a separate block or a capability of the Temporal Orchestration Node?** A separate block adds redundancy but increases complexity.

2. **How do we handle cross-spoke communication?** If a task requires two spokes to coordinate, does the hub bridge them or do spokes merge?

3. **What is the G-Designer training pipeline?** We need historical data of task-topology-performance. How do we collect this before deployment?

4. **Should topology changes require consensus?** If G-Designer proposes a new topology, do all blocks vote (per ADR-001) or does the hub decide unilaterally?

5. **How do we prevent the hub from becoming a round block?** The hub has extraordinary power. What checks and balances exist?

---

## 8. Integration with ADR-001

The proposed consensus protocol (ADR-001: Hybrid HACN + CP-WBFT + DecentLLMs trust overlay) interacts with topology as follows:

- **Intra-spoke consensus:** Blocks within a spoke use CP-WBFT weighted voting for local decisions
- **Inter-spoke consensus:** Hub mediates cross-spoke consensus using the same protocol
- **Trust overlay:** DecentLLMs Bayesian beliefs about each block are maintained by the Knowledge Node and influence spoke membership (low-trust blocks are excluded from sensitive spokes)
- **Temporal audit:** The 11th Temporal Auditor validates that topology changes preserve causal ordering

---

## 9. References

- Zhang et al., "G-Designer: Topology Design for Multi-Agent Reinforcement Learning via Graph Neural Networks," ICML 2025
- ARG-Designer, "Autoregressive Graph Generation for Multi-Agent Communication Topology," arXiv:2507.18224, 2025
- Yu et al., "NetSafe: Network Safety for Multi-Agent Systems," ACL 2025
- Google ADK (Agent Development Kit), 2025
- Anthropic MCP (Model Context Protocol), 2025
- Dapr Agents & Durable Execution, Microsoft, 2025
- CrewAI Documentation: Hierarchical Process and Memory Architecture

---

## 10. Council of Ten Deliberation Required

Per AGENTS.md, all ten personas must deliberate on:
- Whether hub-and-spoke is the right backbone or if a pure peer-to-peer approach is preferable
- Whether G-Designer adds justified complexity or if simpler heuristics suffice
- Whether the protocol fragmentation risk (A2A + MCP + custom) is acceptable
- How the hub's single-point-of-failure risk is mitigated in practice

---

*This is a PROPOSAL, not a final decision. No code shall be written until the Council of Ten reaches documented consensus on this ADR.*
