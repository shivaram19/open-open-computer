# P3: Harness Layers (After Twins Validated)

**Prerequisite:** P2 complete (twins validated).

**Goal:** Build the 7-layer harness core. One layer at a time.

---

## Layer 1: Task Decomposer

- [ ] Intent parser (classify task type)
- [ ] Sub-task generator (3–7 researchable sub-tasks)
- [ ] Dependency graph (DAG of sub-tasks)
- [ ] Criteria definition (success metrics per sub-task)
- [ ] Integration test: complex task → correct decomposition

**Citations:** `Besta2024`

---

## Layer 2: Twin Orchestrator

- [ ] Task-to-twin matching (expertise routing algorithm)
- [ ] Parallel activation (async twin spawning)
- [ ] Resource allocation (compute budget per twin)
- [ ] Inter-twin messaging (A2A protocol implementation)
- [ ] Load balancing (don't overload single twin type)

**Citations:** `GoogleADK2025`, `G-Designer2025`

---

## Layer 3: Research Execution

- [ ] Web search integration (SearchWeb API wrapper)
- [ ] Paper fetch integration (FetchURL + PDF parsing)
- [ ] Scratch pad workspace (persistent reasoning log per twin)
- [ ] Citation verification loop (auto-check @cite() decorators)
- [ ] Benchmark execution (run tests, capture results)

**Citations:** `CITATIONS-GOVERNANCE`

---

## Layer 4: Synthesis & Consensus

- [ ] CP-WBFT voting across twin outputs
- [ ] G-Safeguard anomaly detection on proposals
- [ ] MAD-Spear conformity checking
- [ ] Temporal Auditor causal consistency check
- [ ] Conflict resolution (when twins disagree fundamentally)

**Citations:** `CP-WBFT2025`, `G-Safeguard2025`, `MAD-Spear2025`, `Lamport1978`

---

## Layer 5: Learning & Memory

- [ ] PTKG update on task completion
- [ ] StreamForest trace storage
- [ ] Skill registry (acquired capabilities)
- [ ] Surprise minimization (Active Inference updates)
- [ ] Forgetting policies (per memory type)

**Citations:** `ViG-RAG2026`, `Heins2024`, `Shinn2023`

---

## Layer 6: Action & Execution

- [ ] Code generation (structured file creation)
- [ ] Test execution (pytest integration)
- [ ] Deployment orchestration (Docker/K8s templates)
- [ ] Monitoring & feedback (health checks, alerts)

**Citations:** `DaprAgents2025`

---

## Layer 7: Governance & Sovereignty

- [ ] Human override mechanism (manual approval gates)
- [ ] Ethical constraint enforcement (hard rules)
- [ ] Kill switch (emergency halt)
- [ ] Council of Ten integration (deliberation trigger)
- [ ] Audit trail (every decision logged with reasoning)

**Citations:** `ADR-001`, `ADR-010`

---

*Next file to open: `P4-ADRS.md` — parallel with layer implementation.*
