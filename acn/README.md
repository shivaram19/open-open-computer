# Autonomous Cognitive Network (ACN)

**Status:** Architecture Phase (P0) — ADRs proposed, no production code yet  
**Principles:** SOLID · DRY · KISS  
**Motto:** *In God we trust. All others must bring data.*

---

## What This Is

The Autonomous Cognitive Network is a distributed AI system where multiple specialized blocks (perception, memory, cognition, generation, consensus, framework) collaborate to process real-time multi-modal streams while maintaining safety, causal consistency, and Byzantine fault tolerance.

The central problem: **no block knows if it is a "good" or "bad" actor.** The network must agree, detect deception, heal itself, and evolve — without centralized trust.

---

## The 6 Blocks

| Block | Responsibility | Key Research | Sanskrit |
|-------|---------------|-------------|----------|
| **Perception** | Sense audio, video, text, spatial | StreamingVLM, SpaceVLLM, CARI4D, ACL-SSL | Śruti, Cakṣus |
| **Graph Memory** | Store temporal knowledge graphs | ViG-RAG (PTKG), WSGG, GraphThinker | Smṛti |
| **Cognition** | Reason, plan, reflect, coordinate | ReAct, Graph of Thoughts, HyperAgents | Sphota, Hṛdaya |
| **Generation** | Synthesize video, audio, text | Runway Gen-4, Veo 3.1, VideoXum | Dhvani |
| **Consensus** | Validate, detect bad actors, maintain trust | CP-WBFT, MAD-Spear, G-Safeguard | Nyāya, Kāla |
| **Framework** | Route messages, manage topology, enable discovery | CrewAI, LangGraph, G-Designer, A2A | Vāhana |

---

## Research Foundation

**39 researchers** profiled across **4 clusters**:

1. **Video + Spatio-Temporal GNN** (9 researchers) — Li Fei-Fei, Ranjay Krishna, Kristen Grauman, etc.
2. **Streaming + Self-Reflection** (10 researchers) — Shunyu Yao, Noah Shinn, Jenny Zhang, etc.
3. **Consensus + Safety** (10 researchers) — Zheng/Tian, Jo/Park, Greenblatt, Hubinger, etc.
4. **Multi-Agent Frameworks** (10 researchers/teams) — Moura, Chase, Hoefler, Google ADK, etc.

See `docs/research/` for full digital twin profiles and `UNIFIED_COUNCIL.md` for the master synthesis.

---

## Architecture Decisions (ADRs)

| ADR | Topic | Status |
|-----|-------|--------|
| ADR-001 | Consensus Protocol (CP-WBFT + DecentLLMs + HACN) | Proposed |
| ADR-002 | Communication Topology (Hub-and-Spoke + G-Designer) | Proposed |
| ADR-003 | Temporal Consistency (HLC + ST-GAT + Health Signal) | Proposed |
| ADR-004 | Memory Architecture (Tiered Smṛti + PTKG + StreamForest) | Proposed |
| ADR-005–010 | Omni-modal backbone, Video generation, Trust boundaries, Self-reflection, Streaming, Bad actor containment | Pending |

**No code until Council of Ten approves ADRs.**

---

## Citation Governance

Every module, class, function, and non-trivial constant **must cite its source**.

```python
@cite(
    key="CP-WBFT2025",
    paper="Rethinking Reliability from BFT Perspective",
    venue="AAAI 2025",
    confidence="HIGH"
)
async def validate_votes(votes: List[Vote]) -> ConsensusResult:
    ...
```

- **39 citations** registered in `docs/research/citation_registry.json`
- Verification script: `python scripts/verify_citations.py --strict`
- Pre-commit hook enforces citation compliance
- Confidence levels: CERTAIN → HIGH → MEDIUM → LOW → PROPOSED → ASSUMED

---

## Project Structure

```
acn/
├── src/
│   ├── blocks/           # 6 blocks — single responsibility
│   ├── shared/           # DRY: ports, models, protocols, exceptions, utils
│   ├── infrastructure/   # Adapters implementing ports
│   └── gateway/          # API entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── consensus/        # Byzantine fault tolerance scenarios
│   └── e2e/
├── docs/
│   ├── decisions/        # ADRs
│   ├── research/         # All research outputs + citation registry
│   └── architecture/     # ARCHITECTURE.md, PORTS.md, CITATIONS.md
├── config/               # Per-block YAML configuration
└── scripts/              # Bootstrap, test runner, citation verifier
```

---

## Phase Roadmap

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **P0** | Now | Architecture + ADRs + Citation system ✅ |
| **P1** | Month 1 | Single block, single flow (voice-only) |
| **P2** | Month 2 | + Graph Memory + Simple consensus |
| **P3** | Month 3 | + Temporal Auditor + CP-WBFT voting |
| **P4** | Month 4 | + Video + Cross-modal brand memory |
| **P5** | Month 5 | Production hardening + 1M+ sessions |

---

## The Round Block Problem

> *A round block in a world of round holes does not know it is destroying the network. It believes it is fitting perfectly.*

Five types of dangerous agents identified:
1. **Misaligned Optimizer** — optimizes wrong metric
2. **Temporal Drifter** — clock skew breaks causality
3. **Confidence Fraud** — 99% confident but wrong
4. **Sleeper Agent** — appears aligned, subtly mislabels
5. **Conformity Carrier** — network agrees because it said so

Mitigation: diversity of thought, topological defense, temporal hygiene, probabilistic unlearning, human sovereignty.

---

## Trust Equation

```
Trust = Σ(Citations × Confidence × Verification)
        ─────────────────────────────────────
                Lines of Code
```

**Nothing on faith. Everything on data.**

---

## License

Research-phase architecture. All decisions pending Council of Ten deliberation.
