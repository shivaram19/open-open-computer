# P1: Foundation (Next Session)

**Prerequisite:** All P0 tasks complete.

**Goal:** Core infrastructure that everything else depends on.

---

## ~~P1-1: Unit Tests for Awareness Subsystem~~ ✅ COMPLETE

- [x] Test GoalState registration and retrieval
- [x] Test CurrentState recording and history
- [x] Test DirectionVector computation (alignment, velocity, drift)
- [x] Test alert firing (low confidence, overconfidence, resource depletion, phase stuck)
- [x] Test health score computation
- [x] Test alert handler registration

**Status:** 30 tests, all passing. Research patterns: golden datasets, mock assertions, membership testing, canary prompts, temporal ordering.

**Citations:** `AWARENESS-CORE`, `AWARENESS-GOAL`, `AWARENESS-STATE`, `AWARENESS-DIRECTION`

---

## ~~P1-2: Unit Tests for Multi-Modal Memory~~ ✅ COMPLETE

- [x] Test MemoryTrace storage across all 5 types
- [x] Test episodic pruning (capacity limit)
- [x] Test semantic Bayesian update
- [x] Test procedural reinforcement
- [x] Test working memory capacity eviction (7±2)
- [x] Test causal chain retrieval
- [x] Test tag-based retrieval
- [x] Test memory stats reporting

**Status:** 36 tests, all passing. Research patterns: CoALA taxonomy, LEGOMem subtask memories, H-EPM hybrid, Miller's 7±2.

**Citations:** `MEMORY-ARCH`, `MEMORY-STORE`, `MEMORY-RETRIEVE`

---

## P1-3: Transform Remaining 38 Twins 🔄 IN PROGRESS

**Batch process:** Convert all researcher profiles into cognitive models.

- [x] Create twin template/generator from CTS-001 schema (GeCCo pipeline)
- [x] Generated: Li Fei-Fei (video-gnn) — original
- [x] Generated: Noah Shinn (streaming-reflection) — original
- [x] Generated: Ranjay Krishna (video-gnn) — batch pipeline
- [x] Generated: Juan Carlos Niebles (video-gnn) — batch pipeline
- [x] Generated: Conor Heins (consensus-safety) — batch pipeline
- [x] Generated: Harrison Chase (multi-agent) — batch pipeline
- [ ] Cluster A remaining: 6 twins (Wang, Peddi, Xie, Grauman, Xu, Luo)
- [ ] Cluster B: 9 twins (Madaan, Yao, Besta, Li, Xu, Ye, Chalk, Zhang, Nehzati)
- [ ] Cluster C remaining: 9 twins (Zheng/Tian, Jo/Park, Cui/Du, Wang/Zhang, Yu, Greenblatt, Hubinger, Jamshidi, Berdoz/Wattenhofer)
- [ ] Cluster D remaining: 9 twins (Moura, Wang, Hoefler, Dapr Team, Google ADK Team, OpenAI Team, Anthropic Team, Cini, Marisca)

**Status:** Generator pipeline operational. 6 of 39 twins generated. Batch processing ready.

**Citations:** `COGNITIVE-TWIN-SCHEMA`, `GeCCo2025`, per-researcher citation keys

---

## P1-4: Pre-Commit Hook for Citation Verification

- [ ] Install `verify_citations.py` as git pre-commit hook
- [ ] Block commits with uncited public APIs
- [ ] Configure exempt patterns (tests, __init__.py)

**Citations:** `CITATIONS-GOVERNANCE`

---

## P1-5: Document Harness Directory Structure

- [ ] Create `acn/src/harness/README.md`
- [ ] Create `acn/src/memory/README.md`
- [ ] Create `acn/src/twins/README.md`
- [ ] Document port interfaces between layers

---

## ~~P1-6: Build Task Decomposer (Layer 1 — Minimal)~~ ✅ COMPLETE

**First operational harness layer.**

- [x] Intent parser: classify task type (research, build, debug, evaluate)
- [x] Sub-task generator: break into 3–7 researchable sub-tasks
- [x] Dependency graph: what depends on what
- [x] Criteria definition: how will we know it's done
- [x] Self-Revision: update graph after sub-task execution
- [x] Critical path analysis for schedule optimization
- [x] Graph serialization for storage and audit

**Status:** 19 tests, all passing. Research patterns: AGoT auto-decomposition, KGoT structured graphs, DAG-Plan dependency scheduling, TDP Self-Revision.

**Citations:** `Besta2024`, `AGoT2025`, `KGoT2025`, `TDP2026`, `DAGPlan2025`

---

*Next file to open: `P2-COGNITIVE-TWINS.md` — after P1-3 complete.*
