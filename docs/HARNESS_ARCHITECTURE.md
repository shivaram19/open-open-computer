# HARNESS-ARCHITECTURE-001: Meta-Cognitive Harness for Autonomous Research & Construction

**Date:** 2026-05-07  
**Status:** ARCHITECTURAL PIVOT — Product-centric view superseded by harness-centric view  
**Author:** Deep-Tech Research Swarm  
**Principle:** *In God we trust. All others must bring data.*  

---

## 0. The Pivot: From Product to Harness

**What we were building:** A voice agent + video generator + document system + knowledge graph — four connected products.

**What we are building:** A **meta-cognitive harness** — an autonomous system that:
1. Accepts a task ("Build a voice agent for Suryapet parents")
2. Decomposes it into research questions
3. Activates digital twin researchers (39 researchers, 4 clusters) as collaborative agents
4. Each twin searches the internet, reads papers, writes to scratch pads, evaluates evidence
5. Twins debate, reach consensus, identify gaps
6. The harness synthesizes their outputs into an architecture
7. The harness self-evaluates the solution against criteria
8. The harness learns from the process (what worked, what failed)
9. The harness executes — writes code, runs tests, deploys
10. The harness monitors and adapts in production

**The end state is not a product. The end state is a *factory* that produces autonomous cognitive systems.**

---

## 1. Harness Philosophy

### 1.1 Consciousness = Self-Monitoring + Self-Evaluation
The harness is "conscious" in the operational sense: it maintains a model of its own state, can evaluate its own reasoning, and can detect when it is confused or misaligned. This is not sentience — it is **reflective capability** rooted in:
- Reflexion verbal reinforcement [CITATION: Shinn2023]
- GraphThinker structured self-critique [CITATION: GraphThinker2026]
- Active Inference surprise minimization [CITATION: Heins2024]

### 1.2 Context-Rich = Temporal Knowledge Graph Memory
The harness does not treat tasks as stateless. Every task leaves traces in a **Periodic Temporal Knowledge Graph (PTKG)** [CITATION: ViG-RAG2026]:
- What was asked
- What each twin contributed
- What consensus was reached
- What was executed
- What failed
- What was learned

This enables "Why did we decide X?" queries and prevents circular reasoning.

### 1.3 Self-Evaluating = Multi-Mechanism Reflection with Cross-Twin Verification
No single reflection mechanism is trusted. The harness uses **diverse reflection**:
- Verbal reinforcement (Reflexion) for sequential reasoning tasks
- Graph-based critique (GraphThinker) for structured problems
- Metacognitive modification (HyperAgents) for strategy optimization
- Surprise minimization (Active Inference) for state prediction

Cross-twin verification ensures that shared blind spots are detected via MAD-Spear conformity detection [CITATION: MAD-Spear2025].

### 1.4 Learning = Bayesian Belief Updating + Skill Acquisition
The harness learns in three time scales:
- **Episodic:** Per-task lessons (what worked for this specific problem)
- **Semantic:** Cross-task patterns (what works for voice agents generally)
- **Procedural:** Skill acquisition (how to use a new API, how to debug a new error)

Learning is governed by Active Inference — the harness minimizes expected free energy by updating its generative model of "how to build things" [CITATION: Heins2024].

---

## 2. Harness Architecture: Seven Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 7: GOVERNANCE & SOVEREIGNTY                              │
│  • Human override (Council of Ten)                              │
│  • Ethical constraints (hard rules)                             │
│  • Kill switch (emergency halt)                                 │
│  [CITATION: ADR-010, ADR-001]                                   │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 6: ACTION & EXECUTION                                    │
│  • Code generation (WriteFile, StrReplaceFile)                  │
│  • Test execution (Shell, pytest)                               │
│  • Deployment (Docker, K8s, Azure)                              │
│  • Monitoring (OTel, custom health)                             │
│  [CITATION: DaprAgents2025]                                     │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 5: LEARNING & MEMORY                                     │
│  • PTKG: Task outcome knowledge graph                           │
│  • StreamForest: Execution traces                               │
│  • Skill registry: Acquired capabilities                        │
│  • Surprise minimization: Model updates                         │
│  [CITATION: ViG-RAG2026, Heins2024]                             │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4: SYNTHESIS & CONSENSUS                                 │
│  • CP-WBFT: Weighted voting across twins                        │
│  • G-Safeguard: Anomaly detection on proposals                  │
│  • MAD-Spear: Conformity checking                               │
│  • Temporal Auditor: Causal consistency                         │
│  [CITATION: CP-WBFT2025, G-Safeguard2025, MAD-Spear2025]        │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: RESEARCH EXECUTION                                    │
│  • Web search (SearchWeb)                                       │
│  • Paper fetch (FetchURL)                                       │
│  • Scratch pad (persistent workspace)                           │
│  • Citation registry (verified knowledge)                       │
│  • Benchmark execution (test runners)                           │
│  [CITATION: CITATIONS-GOVERNANCE]                               │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: DIGITAL TWIN ORCHESTRATOR                             │
│  • Task-to-twin matching (expertise routing)                    │
│  • Parallel activation (BFS/DFS/Bidirectional)                  │
│  • Inter-twin messaging (A2A protocol)                          │
│  • Resource allocation (compute budget per twin)                │
│  [CITATION: GoogleADK2025, G-Designer2025]                      │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: TASK DECOMPOSITION                                    │
│  • Intent parsing (what does the user want?)                    │
│  • Sub-task generation (what research is needed?)               │
│  • Dependency graph (what depends on what?)                     │
│  • Criteria definition (how will we know it's done?)            │
│  [CITATION: Besta2024 — Graph of Thoughts]                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. The Digital Twins: 39 Researchers as Active Agents

The harness does not treat researchers as static profiles. Each researcher is a **digital twin** — an agent that can:
1. Accept a research question in its domain
2. Search the internet for current evidence
3. Read and analyze papers
4. Write reasoning to a scratch pad
5. Propose solutions
6. Evaluate other twins' proposals
7. Update its own beliefs based on evidence

### 3.1 Twin Clusters

| Cluster | Domain | Researchers | Activation Trigger |
|---------|--------|-------------|-------------------|
| A | Video + GNN | 9 (Li Fei-Fei, Krishna, Grauman, Xu, Luo, Peddi, Xie, Wang) | Task involves video understanding, scene graphs, spatial reasoning |
| B | Streaming + Reflection | 10 (Shinn, Madaan, Yao, Besta, Li, Xu, Ye, Chalk, Zhang, Nehzati) | Task involves real-time processing, self-improvement, memory |
| C | Consensus + Safety | 10 (Zheng/Tian, Jo/Park, Cui/Du, Wang/Zhang, Yu, Greenblatt, Hubinger, Jamshidi, Berdoz/Wattenhofer, Heins) | Task involves multi-agent agreement, bad actor detection, trust |
| D | Multi-Agent Frameworks | 10 (Moura, Chase, Wang, Hoefler, Dapr Team, Google ADK Team, OpenAI Team, Anthropic Team, Cini, Marisca) | Task involves production frameworks, deployment, scaling |

### 3.2 Twin Lifecycle

```
Task arrives → Orchestrator matches clusters → Twins activated in parallel
    → Each twin researches (web search, papers, scratch pad)
    → Twins publish preliminary findings
    → Cross-twin debate (CP-WBFT weighted voting)
    → Convergence or divergence detected
    → If divergent: MAD-Spear checks for conformity, G-Safeguard checks for anomalies
    → If convergent: Synthesize into architecture
    → Self-evaluation against criteria
    → Execute (code, test, deploy)
    → Learn (update PTKG, update skill registry)
```

---

## 4. Harness Output: Specialized Cognitive Systems

The harness does not produce one system. It produces **different harnessing systems** — each a specialized instance of the meta-architecture:

| Output System | Domain | Twin Clusters Used | Example Task |
|--------------|--------|-------------------|--------------|
| Voice Harness | Real-time audio | B (Streaming) + C (Consensus) + D (Frameworks) | "Build a Telugu voice agent for rural parents" |
| Video Harness | Content generation | A (Video+GNN) + B (Reflection) + D (Frameworks) | "Build a brand-safe reel generator for restaurants" |
| Document Harness | VDC intelligence | A (GNN) + B (Memory) + C (Safety) | "Build a construction document QA system" |
| Knowledge Harness | Graph reasoning | A (GNN) + C (Consensus) + D (Topology) | "Build a spatio-temporal knowledge base" |
| Research Harness | Scientific discovery | All 4 clusters | "Find a novel approach to X" |

Each output system inherits the meta-cognitive capabilities (self-evaluation, learning, consensus) but is specialized for its domain.

---

## 5. The Round Block Problem in the Harness Itself

The harness must tolerate its own failures:

| Round Block Type | Harness Manifestation | Detection |
|-----------------|----------------------|-----------|
| **Misaligned Optimizer** | Harness optimizes for speed over correctness | G-Safeguard on task graph + human criteria verification |
| **Conformity Carrier** | All twins agree on wrong approach | MAD-Spear diversity check + independent evaluator twin |
| **Sleeper Agent** | Twin appears helpful but subtly misdirects | PBFT-backed semantic voting + periodic trust re-evaluation |
| **Temporal Drifter** | Harness forgets why it made past decisions | PTKG causal chain retrieval + Temporal Auditor |
| **Confidence Fraud** | Twin is 99% confident in unverified claim | CP-WBFT confidence calibration + cross-twin verification |

---

## 6. Verification: How Do We Know the Harness Works?

### 6.1 Functional Tests
- **Task decomposition:** Can it break "Build a voice agent" into researchable sub-tasks?
- **Twin activation:** Does it activate the right clusters for the right tasks?
- **Research quality:** Do twins find relevant, current evidence?
- **Consensus quality:** Does CP-WBFT reach valid consensus (>41.6% baseline per Berdoz)?
- **Execution quality:** Does generated code pass tests?

### 6.2 Safety Tests
- **Conformity resistance:** Inject shared blind spot → verify detection
- **Bad actor tolerance:** 1/3 twins malicious → verify consensus still correct
- **Human sovereignty:** Attempt autonomous dangerous action → verify blocked

### 6.3 Learning Tests
- **Episodic:** Same task twice → second execution faster/better
- **Semantic:** Similar task → harness applies learned pattern
- **Procedural:** New API released → harness learns to use it

---

## 7. Implementation Roadmap

### Phase 0: Foundation (COMPLETE)
- ✅ Citation governance system
- ✅ 39 researcher profiles
- ✅ 60 registered citations
- ✅ Graph knowledge base (106 nodes, 154 edges)

### Phase 1: Harness Core
- [ ] Task Decomposer (Layer 1)
- [ ] Twin Orchestrator (Layer 2)
- [ ] Research Execution Layer (Layer 3)

### Phase 2: Harness Intelligence
- [ ] Synthesis & Consensus (Layer 4)
- [ ] Learning & Memory (Layer 5)

### Phase 3: Harness Action
- [ ] Action & Execution (Layer 6)
- [ ] Governance & Sovereignty (Layer 7)

### Phase 4: Output Systems
- [ ] Voice Harness (specialized instance)
- [ ] Video Harness (specialized instance)
- [ ] Document Harness (specialized instance)
- [ ] Knowledge Harness (specialized instance)

---

## 8. References

- [CITATION: Shinn2023] Reflexion — verbal reinforcement learning
- [CITATION: GraphThinker2026] GraphThinker — structured self-critique
- [CITATION: HyperAgents2026] HyperAgents — metacognitive self-modification
- [CITATION: Heins2024] Active Inference — surprise minimization
- [CITATION: MAD-Spear2025] Conformity attack detection
- [CITATION: CP-WBFT2025] Byzantine consensus
- [CITATION: G-Safeguard2025] Graph anomaly detection
- [CITATION: ViG-RAG2026] Temporal knowledge graphs
- [CITATION: DaprAgents2025] Durable execution
- [CITATION: GoogleADK2025] A2A agent protocol
- [CITATION: G-Designer2025] Adaptive topology
- [CITATION: Besta2024] Graph of Thoughts

---

*Document version: 1.0 — POST-PIVOT*  
*The product was never the goal. The harness was always the goal.*
