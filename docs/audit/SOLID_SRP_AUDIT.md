# SRP Audit — Single Responsibility Principle

> **"A class should have one, and only one, reason to change."**
> — Robert C. Martin, *Agile Software Development*, 2002
>
> **"Gather together the things that change for the same reasons. Separate those things that change for different reasons."**
> — Robert C. Martin, *Clean Architecture*, 2017

**Scope:** ACN Repository (`acn/src/*`, `tests/`)
**Date:** 2026-05-07
**Test Baseline:** 883/883 passing

---

## Table of Contents

1. [Why SRP Exists](#1-why-srp-exists)
2. [Detection Methodology](#2-detection-methodology)
3. [Critical Violations](#3-critical-violations)
4. [High Violations](#4-high-violations)
5. [Low Violations](#5-low-violations)
6. [DRY-to-SRP Mapping](#6-dry-to-srp-mapping)
7. [Remediation Tasks](#7-remediation-tasks)
8. [Success Criteria](#8-success-criteria)

---

## 1. Why SRP Exists

### Historical Origin

Robert C. Martin formulated SRP in the late 1990s, drawing on two earlier principles:
- **Tom DeMarco's cohesion** (*Structured Analysis and Systems Specification*, 1978)
- **Edsger Dijkstra's separation of concerns** (*On the Criteria To Be Used in Decomposing Systems into Modules*, 1972)

Martin's breakthrough insight was that a "reason to change" is not a technical concern — it is a **person**. When a CFO requests a change to pay calculation, a COO requests a change to hours reporting, and a CTO requests a change to database persistence, and all three are implemented in the same `Employee` class, the class has three reasons to change. A change by one stakeholder breaks functionality owned by another.

### The Core Problem SRP Solves

**Cascade changes.** When unrelated responsibilities are mixed in one module, a modification to one responsibility risks breaking another. This creates:
- **Rigidity:** Every change requires modifying multiple unrelated parts of the same class
- **Fragility:** Changes in one area break conceptually unrelated functionality
- **Opacity:** Developers cannot predict the side effects of their changes

### SRP in the ACN Context

The ACN codebase has 7+ distinct stakeholder groups (cognition, perception, memory, consensus, self-improvement, communication, research). When all their concerns are packed into `ConsciousAgent`, a memory-team bug fix risks breaking consensus-team functionality.

---

## 2. Detection Methodology

| Heuristic | Threshold | Rationale |
|-----------|-----------|-----------|
| Method count per class | > 15 | Indicates multiple operational concerns |
| Import count from distinct packages | > 10 | Cross-cutting coupling signal |
| Docstring claims multiple roles | Any | Explicit admission of mixed concerns |
| DRY duplication of structurally similar blocks | > 2× | Missing extracted responsibility |
| Independent stakeholder could request change | Subjective | Core SRP definition |

---

## 3. Critical Violations

### 3.1 `ConsciousAgent` (`agents/conscious_agent.py`, 1039 lines)

**Stakeholders who might request changes:**

| Stakeholder | Concern | Lines | Change Example |
|-------------|---------|-------|---------------|
| Cognition Team | `think()` reasoning loop | 250–341 | Add reasoning phase |
| Perception Team | P6 video/cross-modal perception | 190–195, ~400–600 | Add new modality |
| Memory Team | Memory storage/retrieval patterns | 227–240, 328–337 | Change trace format |
| Consensus Team | HLC timestamping, clock management | 147–148 | Swap clock impl |
| Self-Improvement Team | P5 experience buffer, policy optimizer, reflection, skill evolution | 172–188 | Add new substrate |
| Communication Team | `communicate()`, `receive()`, `report()` | ~700–900 | New message format |
| Research Team | `research()`, web search, date grounding | ~400–500 | New search provider |

**`__init__` evidence (lines 125–198):**
```python
self.awareness = AwarenessSubsystem()       # Awareness concern
self.memory = MultiModalMemory()            # Memory concern
self.graph_memory = None                    # Graph memory concern
self.hlc_clock = HybridLogicalClock()       # Consensus concern
self.experience_buffer = ExperienceBuffer() # Self-improvement concern
self.reflection_engine = ReflectionEngine() # Self-improvement concern
self.policy_optimizer = PolicyOptimizer()   # Self-improvement concern
self.skill_evolution = SkillEvolution()     # Self-improvement concern
self.scene_graph = None                     # Perception concern
self.action_tube_library = None             # Perception concern
self.cross_modal_fusion = CrossModalFusion() # Perception concern
self.temporal_index = None                  # Perception concern
```

**Verdict:** 7+ reasons to change. Classic God Class.

**Refactoring target:** Extract `PerceptionSubsystem`, `SelfImprovementSubsystem`, `ConsensusSubsystem` as composable units. `ConsciousAgent` becomes an orchestrator that delegates.

---

### 3.2 `SwarmOrchestrator` (`agents/swarm_orchestrator.py`, 1222 lines)

**Stakeholders who might request changes:**

| Stakeholder | Concern | Lines |
|-------------|---------|-------|
| Task Management | Task activation, agent matching | 123–177 |
| Execution | Round execution, agent communication | 187–254 |
| Deliberation | Structured debate, argument maps | 264–~400 |
| Consensus | CP-WBFT voting, topology | ~400–600 |
| Self-Improvement | P5 feedback loops | ~600–800 |
| Health Monitoring | Divergence detection, dissent | ~800–1000 |
| Graph Memory | P3 persistent memory integration | Scattered |

**Active-agent filter duplication (lines 198–201, 285–288, and 2 more):**
```python
active_agents = [
    a for a in self.agents.values()
    if a.current_goal and a.current_goal.parent_goal_id == task_id
]
```
This filter is repeated 4× because there is no `SwarmTaskContext` or `AgentSelector` abstraction. The orchestrator is forced to know *how* to find active agents instead of delegating that responsibility.

**Refactoring target:** Extract `TaskActivator`, `RoundExecutor`, `DeliberationCoordinator`, `ConsensusCoordinator`, `HealthMonitor`.

---

### 3.3 `MultiModalMemory` (`memory/architecture.py`, 361 lines)

**Reasons to change:**
1. Episodic memory storage policy changes
2. Semantic memory merge strategy changes
3. Procedural memory retrieval logic changes
4. Prospective memory deadline handling changes
5. Working memory capacity limits change

**Evidence (lines 99–125):**
```python
self._episodic: List[MemoryTrace] = []
self._semantic: Dict[str, MemoryTrace] = {}
self._procedural: Dict[str, MemoryTrace] = {}
self._prospective: Dict[str, MemoryTrace] = {}
self._working: List[MemoryTrace] = []
```

**Verdict:** 5 distinct memory subsystems in one class. Each has different storage containers, retention rules, and pruning strategies.

**Refactoring target:** Decompose into 5 `MemoryStore` implementations behind a common protocol.

---

### 3.4 `DistributedConsensusEngine` (`consensus/distributed_consensus.py`, 439 lines)

**Reasons to change:**
1. Confidence-probe refinement algorithm
2. Weighted aggregation & quorum logic
3. Statistical fallback (geometric median)
4. Byzantine-fault detection heuristics
5. Information-theory utilities (entropy)

**Verdict:** 5 distinct algorithmic concerns in one engine.

**Refactoring target:** Extract `ProbeRefiner`, `AggregationStrategy`, `ByzantineDetector`, `EntropyCalculator`.

---

### 3.5 `TemporalAuditor` (`consensus/temporal_auditor.py`, 354 lines)

**Reasons to change:**
1. Single-message auditing rules
2. Deliberation-round auditing
3. Health signal computation
4. Health report formatting
5. Violation window management

**Evidence:** `audit_message()` (lines 120–260) hardcodes 6 sequential checks:
1. Missing timestamp
2. Skew exceeded (critical)
3. Skew exceeded (warning)
4. Message from future
5. Causal violation
6. (etc.)

Each check is a distinct rule that could evolve independently.

**Refactoring target:** Extract `AuditRule` protocol with `check(message, hlc) -> Optional[CausalityViolation]`. Register rules in a list.

---

### 3.6 `PTKG` (`memory/ptkg.py`, 698 lines)

**Reasons to change:**
1. Node/edge storage schema
2. Period management
3. Indexing strategy
4. Temporal query logic
5. Graph traversal (BFS)
6. Causal-path finding
7. Period consolidation
8. Serialization format
9. Statistics computation

**Verdict:** Most severe SRP violation in the codebase. `PTKG` effectively *is* the graph database.

**Refactoring target:** Decompose into `NodeStore`, `EdgeStore`, `PeriodManager`, `GraphIndex`, `GraphTraversal`, `CausalPathFinder`, `GraphSerializer`, `GraphStatistics`.

---

### 3.7 `TwinAgent` (`agents/twin_agent.py`, 328 lines)

**Reasons to change:**
1. Twin loading mechanism (`_load_twin`)
2. Twin reasoning delegation (`think()`)
3. Twin-informed self-critique
4. Twin-calibrated confidence
5. Situation assessment
6. Memory storage pattern (duplicated from `ConsciousAgent`)

**Verdict:** `TwinAgent` is a twin loader, cognition orchestrator, and memory manager. It re-implements `ConsciousAgent.think()` blocks rather than delegating to the parent class.

**Refactoring target:** Make `TwinAgent.think()` call `super().think()` and inject twin reasoning as an augmentation. Extract `ReasoningStrategy` protocol.

---

## 4. High Violations

### 4.1 `TopologyOptimizer` (`consensus/topology.py`, 374 lines)

**Concerns:** Graph construction (7 algorithms), graph analytics, constraint-based optimization.
**Fix:** Separate `TopologyBuilder` registry from `TopologyMetrics` analyzer.

### 4.2 `GraphRetriever` (`memory/graph_retrieval.py`, 413 lines)

**Concerns:** 6 retrieval strategies, reputation registry, reasoning context assembly.
**Fix:** Move reputation to `ReputationProvider`. Extract `RetrievalStrategy` registry.

### 4.3 `CausalChainTracker` (`memory/causal_chain.py`, 383 lines)

**Concerns:** Chain recording, traversal (`find_causes`/`find_effects`), analytics.
**Fix:** Extract `GraphTraversal` strategy. Separate `CausalAnalytics`.

### 4.4 `CrossBlockMessenger` (`consensus/cross_block_messenger.py`, 220 lines)

**Concerns:** Message transport, HLC clock lifecycle, queue management, causal-dependency tracking.
**Fix:** Extract `ClockProvider` and `MessageTransport` abstractions.

### 4.5 `HybridLogicalClock` (`consensus/hlc.py`, ~200 lines)

**Concerns:** Core timestamp generation, skew detection.
**Fix:** Extract `SkewDetector` as separate component.

---

## 5. Low Violations

### 5.1 `ReflectionEngine` (`harness/meta_cognitive_reflection.py`)

Minor: mixes reflection logic with formatting. Low impact due to small size.

### 5.2 `PolicyOptimizer` (`harness/policy_optimizer.py`)

Minor: mixes gradient computation with policy storage. Acceptable given scope.

---

## 6. DRY-to-SRP Mapping

| DRY Violation | Count | Root SRP Cause |
|---------------|-------|---------------|
| Memory-storage pattern repeated 11× | 11 | Agent manages its own memory storage (no `MemoryManager`) |
| Active-agent filter duplicated 4× | 4 | Orchestrator does its own agent selection (no `AgentSelector`) |
| Task validation duplicated 4× | 4 | No `TaskValidator` abstraction |
| `CausalityViolation` block repeated 4× | 4 | No `ViolationFactory` abstraction |
| `CurrentState` construction repeated 7× | 7 | No `StateBuilder` / `StateFactory` |
| Empty consensus result dicts share 6/7 keys | 3+ | No result builder/factory |
| `find_causes`/`find_effects` identical BFS | 2 | Traversal mixed with tracking (no `GraphTraversal`) |
| `_retrieve_semantic`/`_retrieve_procedural` identical | 2 | No reusable retrieval strategy |
| Confidence calibration duplicated | 2 | Calibration logic in agent instead of policy layer |
| `sys.path.insert` in all 14 test files | 14 | No test infrastructure abstraction |

---

## 7. Remediation Tasks

### Immediate (Week 1)

| # | Task | Files | Impact |
|---|------|-------|--------|
| SRP-1 | Extract `MemoryStore` protocol + 5 implementations | `memory/stores.py` (new), `memory/architecture.py` | Eliminates 11× storage pattern; fixes OCP too |
| SRP-2 | Extract `ViolationFactory` from `TemporalAuditor` | `consensus/temporal_auditor.py` | Eliminates 4× CausalityViolation blocks |
| SRP-3 | Extract `AgentSelector` / `SwarmTaskContext` from `SwarmOrchestrator` | `agents/swarm_orchestrator.py` | Eliminates 4× active-agent filter |
| SRP-4 | Extract `StateBuilder` factory for `CurrentState` | `agents/` | Eliminates 7× CurrentState construction |

### Short-term (Week 2–3)

| # | Task | Files | Impact |
|---|------|-------|--------|
| SRP-5 | Decompose `PTKG` into focused collaborators | `memory/ptkg.py`, `memory/stores.py` | Fixes ISP too |
| SRP-6 | Extract `GraphTraversal` strategy from `CausalChainTracker` | `memory/causal_chain.py` | Eliminates find_causes/find_effects dup |
| SRP-7 | Refactor `TwinAgent` to delegate to `super().think()` | `agents/twin_agent.py` | Fixes LSP too |
| SRP-8 | Extract `TagBasedRetrieval` for semantic/procedural stores | `memory/architecture.py` | Eliminates 2× retrieval dup |

### Medium-term (Week 4)

| # | Task | Files | Impact |
|---|------|-------|--------|
| SRP-9 | Decompose `ConsciousAgent` into composable subsystems | `agents/conscious_agent.py` | Largest refactoring; extracts PerceptionSubsystem, SelfImprovementSubsystem |
| SRP-10 | Decompose `SwarmOrchestrator` into coordinators | `agents/swarm_orchestrator.py` | Extract TaskActivator, RoundExecutor, DeliberationCoordinator |
| SRP-11 | Extract `ConsensusResult` builder/factory | `consensus/distributed_consensus.py` | Eliminates 3× dup |
| SRP-12 | Extract `ConfidenceCalibrator` utility | `agents/` | Eliminates 2× dup |

---

## 8. Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| God classes (>15 methods) | 7 | ≤ 2 |
| Classes with >10 distinct imports | 6 | ≤ 2 |
| Active-agent filter duplication | 4 locations | 1 (in `AgentSelector`) |
| Memory storage pattern duplication | 11 locations | 1 (in `MemoryStore` protocol) |
| `CurrentState` construction duplication | 7 locations | 1 (in `StateBuilder`) |
| Test `sys.path.insert` duplication | 14 files | 0 (via `conftest.py`) |

---

*Generated from SOLID_COMPLIANCE_AUDIT.md — SRP Section*
