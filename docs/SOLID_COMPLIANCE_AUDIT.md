# ACN Repository — SOLID & DRY Compliance Audit

**Date:** 2026-05-07  
**Auditor:** Kimi Code CLI (Subagent-assisted)  
**Scope:** Full repository (`acn/src/*`, `tests/`)  
**Test Baseline:** 883/883 passing  
**Files Audited:** ~72 Python files, ~19,500 lines  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Historical Origins: Why SOLID Was Created](#2-historical-origins-why-solid-was-created)
3. [The Four Symptoms of Rotting Design](#3-the-four-symptoms-of-rotting-design)
4. [Principle-by-Principle Audit](#4-principle-by-principle-audit)
   - 4.1 SRP — Single Responsibility Principle
   - 4.2 OCP — Open/Closed Principle
   - 4.3 LSP — Liskov Substitution Principle
   - 4.4 ISP — Interface Segregation Principle
   - 4.5 DIP — Dependency Inversion Principle
5. [DRY ↔ SOLID Cross-Reference Matrix](#5-dry--solid-cross-reference-matrix)
6. [Severity Summary](#6-severity-summary)
7. [Unified Remediation Roadmap](#7-unified-remediation-roadmap)
8. [Appendix: Detection Methodology](#8-appendix-detection-methodology)

---

## 1. Executive Summary

This audit assesses the ACN (Autonomous Cognitive Network) codebase against the **SOLID** principles of object-oriented design and the **DRY** (Don't Repeat Yourself) principle. While the codebase is functionally correct (all 883 tests pass), architectural debt has accumulated across all six implementation phases (P1–P6). The codebase exhibits clear symptoms of **software rot** as defined by Robert C. Martin: **rigidity**, **fragility**, **immobility**, and **viscosity**.

### Key Findings at a Glance

| Principle | Violations Found | Severity |
|-----------|-----------------|----------|
| **SRP** | 14 god classes, 8 mixed-concern modules | 🔴 CRITICAL |
| **OCP** | 6 enum-dispatch chains, 0 strategy patterns | 🔴 CRITICAL |
| **LSP** | 1 broken inheritance (TwinAgent), no base class for 39 twins | 🔴 CRITICAL |
| **ISP** | 5 fat classes forcing unused dependencies | 🟡 HIGH |
| **DIP** | 40+ direct concrete dependencies, 0 injected abstractions | 🔴 CRITICAL |
| **DRY** | 80+ violations (11 critical, 30+ high) | 🔴 CRITICAL |

### Architectural Debt by Package

| Package | Primary SOLID Failures | Lines |
|---------|----------------------|-------|
| `agents/` | SRP, DIP, OCP | ~2,600 |
| `consensus/` | SRP, OCP, DIP | ~1,800 |
| `memory/` | SRP, ISP, OCP, DIP | ~2,400 |
| `twins/` | **ALL FIVE** + DRY | ~6,900 |
| `harness/` | SRP, DIP | ~1,400 |
| `perception/` | SRP, DIP | ~800 |
| `tests/` | DRY only | ~3,600 |

---

## 2. Historical Origins: Why SOLID Was Created

Understanding *why* the SOLID principles were created is essential for judging their relevance to the ACN codebase. These were not abstract aesthetic preferences — they were survival tactics developed by practitioners fighting against **software rot**.

### 2.1 The Crisis: Software Rot (1990s)

In the late 1990s, Robert C. Martin ("Uncle Bob") observed a recurring pattern in enterprise software projects: codebases that started clean would progressively degrade until they became unmaintainable. In his seminal 2000 paper *"Design Principles and Design Patterns"*, he identified **four symptoms of rotting design** that plagued object-oriented systems:

| Symptom | Definition | ACN Manifestation |
|---------|-----------|-------------------|
| **Rigidity** | Software is difficult to change; every change causes a cascade of dependent modifications. | Adding a new memory type requires edits to `MultiModalMemory.store()`, `.retrieve()`, and all helper methods. |
| **Fragility** | Changes break the software in unrelated places. | Modifying `ConsciousAgent.think()` formatting risks breaking `TwinAgent.think()` which re-implements the loop. |
| **Immobility** | It's easier to rewrite than reuse modules because of excessive dependencies. | The 39 twin files cannot be reused polymorphically — each is an isolated concrete class. |
| **Viscosity** | Doing things the "right way" is harder than hacking. | Adding a new twin means copy-pasting 180 lines rather than subclassing. |

> *"The design of many software applications begins as a vital image in the minds of its designers. At this stage it is clean and elegant. However, as time passes, new requirements emerge, and bugs appear as the design is bent and pulled in different directions..."* — Robert C. Martin, 2000

### 2.2 The Five Principles: Origins and Motivations

#### **S — Single Responsibility Principle (SRP)**
- **Formulated by:** Robert C. Martin, inspired by **Tom DeMarco's cohesion** and **Edsger Dijkstra's separation of concerns**.
- **Original definition (2000):** *"A class should have one, and only one, reason to change."*
- **Later refinement (Clean Architecture):** *"Gather together the things that change for the same reasons. Separate those things that change for different reasons."*
- **Why it was created:** Martin observed that when a class mixed responsibilities owned by different organizational roles (e.g., CFO's pay calculation, COO's hours reporting, CTO's database persistence), a change requested by one role would break functionality owned by another. The "reason to change" is ultimately a **person** — a stakeholder who requests the modification.
- **Root cause it solves:** Tight coupling of unrelated concerns within a single module, leading to cascade changes and unexpected breakage.

#### **O — Open/Closed Principle (OCP)**
- **Formulated by:** **Bertrand Meyer** in 1988, in his book *Object-Oriented Software Construction* (Eiffel language).
- **Original definition:** *"Software entities should be open for extension, but closed for modification."*
- **Martin's reinterpretation (1990s):** Extended Meyer's inheritance-based approach to emphasize **polymorphism through abstractions** (interfaces/abstract classes) rather than just inheritance.
- **Why it was created:** Meyer observed that modifying working code to add features was the primary source of bugs. His paradoxical insight: you should be able to change what a module *does* without changing its *source code*. This is achieved by defining stable contracts (abstractions) and varying behavior through new implementations.
- **Root cause it solves:** The "if-else epidemic" — adding new types requires editing existing stable code, which introduces regression risk.

#### **L — Liskov Substitution Principle (LSP)**
- **Formulated by:** **Barbara Liskov** (MIT, Turing Award winner) in her 1987 keynote *"Data Abstraction and Hierarchy"*; formalized with Jeannette Wing in 1994.
- **Original definition:** *"If for each object o1 of type S there is an object o2 of type T such that for all programs P defined in terms of T, the behavior of P is unchanged when o1 is substituted for o2, then S is a subtype of T."*
- **Martin's rephrasing:** *"Functions that use pointers or references to base classes must be able to use objects of derived classes without knowing it."*
- **Why it was created:** Liskov was designing **CLU**, the first non-goto structured programming language. She realized that naive inheritance (e.g., Square inheriting from Rectangle) breaks the mathematical contracts that type systems rely on. Subtypes must honor the **Design by Contract** preconditions, postconditions, and invariants of their supertypes.
- **Root cause it solves:** Broken polymorphism — a "subtype" that cannot truly substitute for its parent, causing runtime failures when the substitution is attempted.

#### **I — Interface Segregation Principle (ISP)**
- **Formulated by:** Robert C. Martin while consulting for **Xerox** in the 1990s.
- **Original context:** Xerox had built a multifunction printer system (print, staple, fax). A single `Job` class was used by all tasks. Even a simple stapling job depended on the entire print-job interface. A one-hour redeployment cycle meant every tiny change was excruciating.
- **Definition:** *"Clients should not be forced to depend on interfaces they do not use."*
- **Why it was created:** Fat interfaces create unnecessary coupling. When a client depends on a method it doesn't use, changes to that method's signature or behavior force the client to rebuild/redeploy even though the change is irrelevant to it.
- **Root cause it solves:** Accidental coupling through bloated contracts — modules know about (and are affected by) functionality they never invoke.

#### **D — Dependency Inversion Principle (DIP)**
- **Formulated by:** Robert C. Martin in a **June 1996 column for The C++ Report**.
- **Original insight:** Conventional layered architectures (UI → Business Logic → Database) caused "software rot" because high-level business logic was directly coupled to low-level implementation details.
- **Definition:** 
  1. *"High-level modules should not depend on low-level modules. Both should depend on abstractions."*
  2. *"Abstractions should not depend on details. Details should depend on abstractions."*
- **Why it was created:** Martin observed that the most stable parts of a system (business rules) were being destabilized by volatile implementation details (database schemas, UI frameworks, network protocols). Inverting dependencies so that both sides depend on stable abstractions protects the core from external volatility.
- **Root cause it solves:** Directional coupling — high-value, stable logic is corrupted by direct dependencies on low-value, volatile implementations.

### 2.3 The SOLID Acronym

The acronym **SOLID** was coined around **2004 by Michael Feathers** (author of *Working Effectively with Legacy Code*), who noticed that the first letters of Martin's five principles spelled a memorable word. Feathers suggested the reordering to Martin, who adopted it in *Clean Architecture* (2017).

### 2.4 Why This Matters for ACN

The ACN codebase exhibits **all four symptoms of rotting design** that SOLID was created to prevent:

1. **Rigidity:** Adding P7 (future phase) would require modifying `ConsciousAgent.__init__`, `SwarmOrchestrator.__init__`, `MultiModalMemory.store()`/`retrieve()`, and `TopologyOptimizer.build_topology()` — a cascade across 4+ packages.
2. **Fragility:** The 11× repeated memory-storage block in `ConsciousAgent` means a bug fix in one location (e.g., missing `importance` field) may be forgotten in others.
3. **Immobility:** `PTKG` is 420+ lines of graph-database functionality, yet it cannot be reused without dragging in `HybridLogicalClock`, `CausalChainTracker`, and `ReputationGraphTracker` dependencies.
4. **Viscosity:** The easiest way to add a new twin is to copy-paste an existing file. The "right way" (defining a base class, refactoring the generator, regenerating all files, updating imports) is so hard that it never happens.

---

## 3. The Four Symptoms of Rotting Design in ACN

### 3.1 Rigidity — The Cascade Problem

**Definition:** Every change causes a cascade of dependent modifications.

**Evidence in ACN:**
- Adding a new `MemoryType` requires edits to `MultiModalMemory.__init__` (new storage container), `.store()` (new elif branch), `.retrieve()` (new elif branch), plus a new private helper method trio (`_store_*`, `_retrieve_*`, `_prune_*`).
- Adding a new `TopologyType` requires editing `TopologyOptimizer.build_topology()` (new elif branch) and adding a new private `_build_*` method.
- Adding a new consensus fallback strategy requires editing `DistributedConsensusEngine.stage2_weighted_aggregation()` inline logic.
- Adding a new audit rule requires editing `TemporalAuditor.audit_message()` sequential checks.

**Root SOLID violation:** OCP (not closed for modification) + SRP (multiple concerns per class).

### 3.2 Fragility — The Whack-a-Mole Problem

**Definition:** Changes break software in conceptually unrelated places.

**Evidence in ACN:**
- `TwinAgent.think()` re-implements the core reasoning loop from `ConsciousAgent.think()` but with twin-specific wrapping. A formatting change to the reasoning dict in the base class (e.g., renaming `"confidence"` to `"calibrated_confidence"`) would not automatically propagate.
- `find_causes()` and `find_effects()` in `CausalChainTracker` are near-identical BFS traversals. A bug fix for cycle detection in one might be missed in the other.
- The `CausalityViolation` instantiation block is repeated 4× in `temporal_auditor.py`. Adding a new field (e.g., `remediation_hint`) requires editing all four locations.

**Root SOLID violation:** DRY → SRP (duplicated logic scattered across methods that should be unified).

### 3.3 Immobility — The Rewrite Problem

**Definition:** It's easier to rewrite modules than reuse them because of excessive dependencies.

**Evidence in ACN:**
- `PTKG` (420+ lines) encapsulates node storage, edge storage, period management, indexing, temporal queries, graph traversal, causal-path finding, period consolidation, serialization, and statistics. No client uses all of these, yet all clients must depend on the full class.
- The 39 cognitive twin files are standalone concrete classes with no shared base. A harness that wants to use twins polymorphically would need to import all 39 modules individually.
- `ConsciousAgent` directly instantiates 10+ concrete dependencies in `__init__`: `AwarenessSubsystem`, `MultiModalMemory`, `HybridLogicalClock`, `ExperienceBuffer`, `ReflectionEngine`, `PolicyOptimizer`, `SkillEvolution`, `CrossModalFusion`, and potentially `TemporalSceneGraph`, `ActionTubeLibrary`, `TemporalIndex`.

**Root SOLID violation:** DIP (high-level modules depend on low-level concretions) + ISP (fat classes force unused dependencies).

### 3.4 Viscosity — The Hacking Problem

**Definition:** Doing things the right way is harder than doing them the wrong way.

**Evidence in ACN:**
- Adding a new cognitive twin: the "wrong way" is `cp li_fei_fei.py new_twin.py` + find-replace names (2 minutes). The "right way" would require refactoring `generator.py`, adding cluster data, running generation, and updating imports (30+ minutes).
- Adding a new memory type: the "wrong way" is copy-pasting an existing `_store_*` / `_retrieve_*` pair and editing the `if-elif` chains (5 minutes). The "right way" would require extracting a `MemoryStore` interface, creating a new implementation, and registering it (1+ hour).
- Adding test coverage: all 14 test files contain identical `sys.path.insert(0, ...)` boilerplate. The "wrong way" is copy-pasting it again. The "right way" would require setting up a proper `conftest.py` or `pytest.ini` (15 minutes, but nobody does it).

**Root SOLID violation:** OCP (lack of extension points encourages hacking) + DIP (lack of abstractions encourages direct coupling).

---

## 4. Principle-by-Principle Audit

### 4.1 SRP — Single Responsibility Principle

> *"A class should have one, and only one, reason to change."* — Robert C. Martin

#### 4.1.1 Detection Methodology

SRP violations were identified using these heuristics:
1. **Method count > 15** per class (indicates multiple concerns)
2. **Import count > 10** from distinct packages (indicates cross-cutting coupling)
3. **Docstring claims multiple distinct roles** (e.g., "stores, retrieves, prunes, indexes")
4. **DRY duplication of structurally similar blocks** (suggests missing extracted responsibility)
5. **Changes to one feature conceptually risk another** (subjective but informed by codebase knowledge)

#### 4.1.2 Violations Catalog

##### 🔴 CRITICAL — `ConsciousAgent` (`agents/conscious_agent.py`, 1039 lines)

**Reasons to change (stakeholders who might request modifications):**

| Stakeholder | Concern | Lines |
|-------------|---------|-------|
| Cognition Team | `think()` reasoning loop | 250–341 |
| Perception Team | P6 video/cross-modal perception | 190–195, ~400–600 |
| Memory Team | Memory storage/retrieval patterns | 227–240, 328–337 |
| Consensus Team | HLC timestamping, clock management | 147–148 |
| Self-Improvement Team | P5 experience buffer, policy optimizer, reflection, skill evolution | 172–188 |
| Communication Team | `communicate()`, `receive()`, `report()` | ~700–900 |
| Research Team | `research()`, web search, date grounding | ~400–500 |

**Verdict:** `ConsciousAgent` has **at least 7 distinct reasons to change**, each corresponding to a different stakeholder/team. This is a classic "God Class" — the exact antipattern SRP was created to prevent.

**Evidence of mixed concerns in `__init__`:**
```python
# Lines 125–198: 12 distinct subsystem initializations
self.awareness = AwarenessSubsystem()      # Awareness
self.memory = MultiModalMemory()           # Memory
self.graph_memory = None                   # Graph memory
self.hlc_clock = HybridLogicalClock()      # Consensus
self.experience_buffer = ExperienceBuffer() # Self-improvement
self.reflection_engine = ReflectionEngine() # Self-improvement
self.policy_optimizer = PolicyOptimizer()   # Self-improvement
self.skill_evolution = SkillEvolution()     # Self-improvement
self.scene_graph = None                     # Perception
self.action_tube_library = None             # Perception
self.cross_modal_fusion = CrossModalFusion() # Perception
self.temporal_index = None                  # Perception
```

##### 🔴 CRITICAL — `SwarmOrchestrator` (`agents/swarm_orchestrator.py`, 1222 lines)

**Reasons to change:**

| Stakeholder | Concern | Lines |
|-------------|---------|-------|
| Task Management | Task activation, agent matching | 123–177 |
| Execution | Round execution, agent communication | 187–254 |
| Deliberation | Structured debate, argument maps | 264–~400 |
| Consensus | CP-WBFT voting, topology | ~400–600 |
| Self-Improvement | P5 feedback loops | ~600–800 |
| Health Monitoring | Divergence detection, dissent | ~800–1000 |
| Graph Memory | P3 persistent memory integration | Scattered |

**Verdict:** 7+ reasons to change. The orchestrator is simultaneously a task manager, execution engine, deliberation facilitator, consensus coordinator, and health monitor.

**Evidence of SRP violation — active-agent filter repeated 4×:**
```python
# Lines 198–201
active_agents = [a for a in self.agents.values() if a.current_goal and a.current_goal.parent_goal_id == task_id]
# Lines 285–288
active_agents = [a for a in self.agents.values() if a.current_goal and a.current_goal.parent_goal_id == task_id]
# Same pattern in execute_deliberation_round, run_full_deliberation, _check_consensus
```
This filter is repeated because there is no `SwarmTaskContext` or `AgentSelector` abstraction. The orchestrator is forced to know *how* to find active agents instead of delegating that responsibility.

##### 🔴 CRITICAL — `MultiModalMemory` (`memory/architecture.py`, 361 lines)

**Reasons to change:**
1. Episodic memory storage policy changes
2. Semantic memory merge strategy changes
3. Procedural memory retrieval logic changes
4. Prospective memory deadline handling changes
5. Working memory capacity limits change

**Verdict:** 5 distinct memory subsystems in one class. Each has different storage containers (list vs dict), retention rules, and pruning strategies. This should be 5 `MemoryStore` implementations.

**Evidence:**
```python
# Lines 99–125: 5 storage containers
self._episodic: List[MemoryTrace] = []
self._semantic: Dict[str, MemoryTrace] = {}
self._procedural: Dict[str, MemoryTrace] = {}
self._prospective: Dict[str, MemoryTrace] = {}
self._working: List[MemoryTrace] = []
```

##### 🔴 CRITICAL — `DistributedConsensusEngine` (`consensus/distributed_consensus.py`, 439 lines)

**Reasons to change:**
1. Confidence-probe refinement algorithm
2. Weighted aggregation & quorum logic
3. Statistical fallback (geometric median)
4. Byzantine-fault detection heuristics
5. Information-theory utilities (entropy)

**Verdict:** 5 distinct algorithmic concerns. A change to Byzantine detection should not require editing the same class as aggregation weight tuning.

##### 🔴 CRITICAL — `TemporalAuditor` (`consensus/temporal_auditor.py`, 354 lines)

**Reasons to change:**
1. Single-message auditing rules
2. Deliberation-round auditing
3. Health signal computation
4. Health report formatting
5. Violation window management

**Verdict:** 5 concerns. The `audit_message()` method alone hardcodes 6 sequential checks (lines 120–260), each a distinct rule that could evolve independently.

##### 🔴 CRITICAL — `PTKG` (`memory/ptkg.py`, 698 lines)

**Reasons to change:**
1. Node/edge storage schema
2. Period management
3. Indexing strategy (adjacency, reverse, type, period)
4. Temporal query logic
5. Graph traversal (BFS)
6. Causal-path finding
7. Period consolidation
8. Serialization format
9. Statistics computation

**Verdict:** This is the most severe SRP violation in the codebase. `PTKG` effectively *is* the graph database. It should be decomposed into `NodeStore`, `EdgeStore`, `PeriodManager`, `GraphIndex`, `GraphTraversal`, `CausalPathFinder`, `GraphSerializer`, and `GraphStatistics`.

##### 🔴 CRITICAL — `TwinAgent` (`agents/twin_agent.py`, 328 lines)

**Reasons to change:**
1. Twin loading mechanism (`_load_twin`)
2. Twin reasoning delegation (`think()`)
3. Twin-informed self-critique (`_twin_informed_self_critique`)
4. Twin-calibrated confidence (`_twin_calibrated_confidence`)
5. Situation assessment (`_assess_situation`)
6. Memory storage pattern (duplicated from `ConsciousAgent`)

**Verdict:** `TwinAgent` is both a twin loader *and* an agent cognition orchestrator *and* a memory manager. More critically, it re-implements `ConsciousAgent.think()`'s memory-storage and awareness-update blocks rather than delegating to the parent class.

##### 🟡 HIGH — `TopologyOptimizer` (`consensus/topology.py`, 374 lines)

**Reasons to change:**
1. Graph construction algorithms (complete, star, chain, tree, random, layered, adaptive)
2. Graph analytics (BFS diameter, fault-tolerance metrics)
3. Constraint-based optimization

**Verdict:** 3 concerns. Construction and analytics should be separated.

##### 🟡 HIGH — `GraphRetriever` (`memory/graph_retrieval.py`, 413 lines)

**Reasons to change:**
1. Retrieval strategy implementations (6 strategies)
2. Reputation registry management
3. Reasoning context assembly

**Verdict:** 3 concerns. Reputation management should be in a separate `ReputationProvider`.

##### 🟡 HIGH — `CausalChainTracker` (`memory/causal_chain.py`, 383 lines)

**Reasons to change:**
1. Chain recording (`record_event`, `record_cause`)
2. Traversal (`find_causes`, `find_effects`)
3. Analytics (`get_causal_strength`, `get_cross_session_impact`)

**Verdict:** 3 concerns. The traversal logic should be extracted to a `GraphTraversal` strategy.

##### 🟡 HIGH — `CrossBlockMessenger` (`consensus/cross_block_messenger.py`, 220 lines)

**Reasons to change:**
1. Message transport (`send`, `broadcast`, `poll`, `deliver_all`)
2. HLC clock lifecycle management
3. Queue management (max-size eviction)
4. Causal-dependency tracking

**Verdict:** 4 concerns. Transport logic is inseparable from clock synchronization.

##### 🟡 HIGH — `HybridLogicalClock` (`consensus/hlc.py`, ~200 lines)

**Reasons to change:**
1. Core timestamp generation (`now`, `send`, `receive`)
2. Skew detection (`detect_skew`)

**Verdict:** 2 concerns. Skew detection is an orthogonal audit concern that couples the clock to physical-time logic.

#### 4.1.3 SRP Summary

| Severity | Count | Examples |
|----------|-------|----------|
| 🔴 CRITICAL | 7 | `ConsciousAgent`, `SwarmOrchestrator`, `MultiModalMemory`, `DistributedConsensusEngine`, `TemporalAuditor`, `PTKG`, `TwinAgent` |
| 🟡 HIGH | 5 | `TopologyOptimizer`, `GraphRetriever`, `CausalChainTracker`, `CrossBlockMessenger`, `HybridLogicalClock` |
| 🟢 LOW | 2 | `ReflectionEngine`, `PolicyOptimizer` (minor) |

---

### 4.2 OCP — Open/Closed Principle

> *"Software entities should be open for extension, but closed for modification."* — Bertrand Meyer, 1988

#### 4.2.1 Detection Methodology

OCP violations were identified using these heuristics:
1. **Enum-dispatched `if-elif` chains** checking types to select behavior
2. **No strategy/registry pattern** for variation points
3. **Adding a feature requires editing existing stable code**
4. **No abstract base class or interface** at natural extension points

#### 4.2.2 Violations Catalog

##### 🔴 CRITICAL — `TopologyOptimizer.build_topology()` (`consensus/topology.py`, lines 117–132)

```python
if topology_type == TopologyType.COMPLETE:
    return self._build_complete(agent_ids)
elif topology_type == TopologyType.STAR:
    return self._build_star(agent_ids, hub_agent)
elif topology_type == TopologyType.CHAIN:
    return self._build_chain(agent_ids)
# ... etc
```

**Violation:** Adding a new topology type requires editing `build_topology()`. There is no `TopologyBuilder` interface or registry.

**Fix:** Define `TopologyBuilder` protocol with `build(agent_ids) -> Dict` method. Register builders in a dict. New topologies = new class.

##### 🔴 CRITICAL — `MultiModalMemory.store()` / `.retrieve()` (`memory/architecture.py`, lines 170–192, 237–255)

```python
if trace.memory_type == MemoryType.EPISODIC:
    self._store_episodic(trace)
elif trace.memory_type == MemoryType.SEMANTIC:
    self._store_semantic(trace)
# ... etc
```

**Violation:** Adding a 6th memory type requires editing both `store` and `retrieve`, plus adding new fields, storage containers, and helper methods.

**Fix:** Define `MemoryStore` protocol with `store(trace)`, `retrieve(query)`, `prune()`. Register stores in a dict keyed by `MemoryType`.

##### 🔴 CRITICAL — `GraphRetriever.retrieve()` (`memory/graph_retrieval.py`, lines 97–129)

```python
if strategy == GraphRetrievalStrategy.NEIGHBOR:
    return self._retrieve_neighbor(...)
elif strategy == GraphRetrievalStrategy.MULTI_HOP_BFS:
    return self._retrieve_multi_hop_bfs(...)
# ... etc
```

**Violation:** Adding a new retrieval strategy requires editing `retrieve()`.

**Fix:** Define `RetrievalStrategy` protocol with `retrieve(graph, query, params)` method. Register strategies in a dict.

##### 🔴 CRITICAL — `DistributedConsensusEngine.stage2_weighted_aggregation()` (`consensus/distributed_consensus.py`, line 241)

```python
if len(trusted_votes) < quorum:
    return self._geometric_median_consensus(refined_votes)
```

**Violation:** The fallback path is baked into the method. Adding quadratic voting or another fallback requires editing the class.

**Fix:** Define `AggregationStrategy` protocol. Inject fallback strategy.

##### 🔴 CRITICAL — `TemporalAuditor.audit_message()` (`consensus/temporal_auditor.py`, lines 120–260)

**Violation:** 6 sequential hardcoded checks inside a single method. Adding a new audit rule (e.g., signature verification) requires editing `audit_message()`.

**Fix:** Define `AuditRule` protocol with `check(message, hlc) -> Optional[CausalityViolation]`. Register rules in a list and iterate.

##### 🔴 CRITICAL — `TwinGenerator` (`twins/generator.py`, 741 lines)

**Violation:** The generator encodes all cluster definitions in nested dicts (`COGNITIVE_CLUSTERS`, `cluster_heuristics`, `cluster_biases`, `cluster_phases`, `bodies`). Adding a new cluster requires editing `generator.py`.

**Fix:** Move cluster definitions to declarative data files (YAML/JSON). The generator should read data and apply templates, not encode data.

##### 🟡 HIGH — `ConsciousAgent.__init__()` (`agents/conscious_agent.py`, lines 125–198)

**Violation:** P4–P6 substrates are directly instantiated. Adding P7 would require editing `__init__`.

**Fix:** Use a substrate registry or factory pattern. Each phase registers its own substrates.

#### 4.2.3 OCP Summary

| Severity | Count | Examples |
|----------|-------|----------|
| 🔴 CRITICAL | 6 | `build_topology`, `store/retrieve`, `GraphRetriever.retrieve`, `consensus fallback`, `audit_message`, `TwinGenerator` |
| 🟡 HIGH | 1 | `ConsciousAgent.__init__` substrate coupling |

---

### 4.3 LSP — Liskov Substitution Principle

> *"If S is a subtype of T, then objects of type T may be replaced with objects of type S without altering any of the desirable properties of the program."* — Barbara Liskov, 1987

#### 4.3.1 Detection Methodology

LSP violations were identified using these heuristics:
1. **Subclass overrides parent method but changes its contract** (different return shape, different side effects)
2. **Subclass re-implements parent logic instead of calling `super()`**
3. **No common base class** where polymorphism is obviously needed
4. **`isinstance()` checks** that defeat polymorphism

#### 4.3.2 Violations Catalog

##### 🔴 CRITICAL — `TwinAgent` breaks `ConsciousAgent.think()` contract (`agents/twin_agent.py`, lines 93–170)

`TwinAgent` inherits from `ConsciousAgent` but overrides `think()` with a completely different implementation that:
1. Does NOT call `super().think()`
2. Re-implements the memory-storage block (lines ~155–170) instead of reusing the parent's logic
3. Re-implements the `CurrentState` construction (lines ~142–150) instead of reusing the parent's logic
4. Returns a different dict shape (includes `"twin_reasoning"`, `"twin_id"`, `"twin_name"`)

**Violation:** A client expecting `ConsciousAgent.think()` behavior would be surprised by `TwinAgent.think()`. The subclass does not preserve the parent's contract — it replaces it entirely.

**The deeper problem:** `TwinAgent` should not be overriding `think()` at all. It should be using **composition** (the twin is a strategy plugged into the agent) rather than **inheritance** (the twin IS an agent with a different think method).

**Fix:** Make `think()` call `super().think()` and inject twin reasoning as an augmentation, OR extract a `ReasoningStrategy` protocol that both `ConsciousAgent` and `TwinAgent` delegate to.

##### 🔴 CRITICAL — 39 cognitive twins have NO common base class (`twins/cognitive_models/*.py`)

**Violation:** There is no `CognitiveTwin` base class or protocol. Every twin is a standalone concrete class:

```python
# li_fei_fei.py
class LiFeiFeiTwin:
    ...

# noah_shinn.py  
class NoahShinnTwin:
    ...
```

**Impact:** LSP cannot even be evaluated because the prerequisite abstraction is missing. Clients cannot treat twins polymorphically. A harness that wants to invoke `twin.think()` must import 39 specific concrete classes.

**Fix:** Introduce `CognitiveTwin` ABC or Protocol with `think()`, `get_cognitive_signature()`, and default implementations for generic phase methods.

##### 🟡 HIGH — `AgentState` enum values may not be handled uniformly

**Minor concern:** `TwinAgent._transition_to()` may not handle all `AgentState` values that `ConsciousAgent` handles. This is a weak LSP concern but worth noting.

#### 4.3.3 LSP Summary

| Severity | Count | Examples |
|----------|-------|----------|
| 🔴 CRITICAL | 2 | `TwinAgent.think()` breaks parent contract; 39 twins lack common base |
| 🟡 HIGH | 1 | Minor state transition inconsistency |

---

### 4.4 ISP — Interface Segregation Principle

> *"Clients should not be forced to depend on interfaces they do not use."* — Robert C. Martin, 1996

#### 4.4.1 Detection Methodology

ISP violations were identified using these heuristics:
1. **Classes with 20+ public methods** that different clients use disjoint subsets of
2. **Client code accessing internal fields** (e.g., `graph._nodes`) rather than using public API
3. **Classes mixing orthogonal concerns** that force clients to depend on unrelated functionality

#### 4.4.2 Violations Catalog

##### 🔴 CRITICAL — `PTKG` (`memory/ptkg.py`, 20+ public methods)

**Clients and their actual needs:**

| Client | Needs | Does NOT Need |
|--------|-------|---------------|
| `CausalChainTracker` | `add_node`, `add_edge`, `get_node`, traversal | period management, serialization, statistics |
| `GraphRetriever` | `get_node`, `get_edge`, traversal | period consolidation, causal paths |
| `PTKGPersistence` | `to_dict`, `from_dict` | traversal, analytics |
| `ReputationGraphTracker` | `add_node`, `add_edge` | temporal queries, BFS |

**Violation:** All four clients are forced to depend on the full surface area of `PTKG` (20+ public methods) even though each uses only 3–5 methods. This is the exact "fat class" problem that ISP was created to solve.

**Fix:** Split `PTKG` into `GraphStorage` (node/edge CRUD), `TemporalGraph` (period queries), `GraphTraversal` (BFS/DFS), `CausalGraph` (path finding), `GraphSerializer` (dict conversion), `GraphStatistics` (metrics).

##### 🟡 HIGH — `ConsciousAgent` forces perception substrates on all clients (`agents/conscious_agent.py`)

**Violation:** Even agents that never process video (e.g., text-only research agents) carry `TemporalSceneGraph`, `ActionTubeLibrary`, and `CrossModalFusion` as instance variables. There is no `PerceptionEnabledAgent` subtype.

**Fix:** Extract perception into a `PerceptionSubsystem` that is optionally injected, or create a `PerceivingAgent` subclass.

##### 🟡 HIGH — `GraphRetriever` forces reputation methods on retrieval-only clients (`memory/graph_retrieval.py`)

**Violation:** Any client that calls `retrieve()` must depend on a class that also carries `set_agent_reputation` and `get_agent_reputation`.

**Fix:** Move reputation methods to a separate `ReputationProvider` interface/class.

##### 🟡 HIGH — `SwarmOrchestrator` forces P3–P5 infrastructure on all tasks (`agents/swarm_orchestrator.py`)

**Violation:** A simple 3-agent task with no deliberation still carries `TemporalAuditor`, `DistributedConsensusEngine`, `TopologyOptimizer`, `SelfImprovementLoop`, `ReputationGraphTracker`, and `CausalChainTracker` as instance variables.

**Fix:** Use lazy initialization or dependency injection. Only instantiate infrastructure when a task requires it.

#### 4.4.3 ISP Summary

| Severity | Count | Examples |
|----------|-------|----------|
| 🔴 CRITICAL | 1 | `PTKG` fat class |
| 🟡 HIGH | 3 | `ConsciousAgent` perception bloat, `GraphRetriever` reputation bloat, `SwarmOrchestrator` infrastructure bloat |

---

### 4.5 DIP — Dependency Inversion Principle

> *"High-level modules should not depend on low-level modules. Both should depend on abstractions."* — Robert C. Martin, 1996

#### 4.5.1 Detection Methodology

DIP violations were identified using these heuristics:
1. **`from concrete_module import ConcreteClass`** in high-level modules
2. **Direct instantiation** (`self.x = ConcreteClass()`) rather than injection
3. **Internal field access** (`obj._private_dict`) across module boundaries
4. **No abstract base class or protocol** at module boundaries

#### 4.5.2 Violations Catalog

##### 🔴 CRITICAL — `ConsciousAgent` directly instantiates 10+ concrete classes (`agents/conscious_agent.py`, lines 125–198)

```python
self.awareness = AwarenessSubsystem()           # concrete
self.memory = MultiModalMemory()                # concrete
self.hlc_clock = HybridLogicalClock()           # concrete
self.experience_buffer = ExperienceBuffer()     # concrete
self.reflection_engine = ReflectionEngine()     # concrete
self.policy_optimizer = PolicyOptimizer()       # concrete
self.skill_evolution = SkillEvolution()         # concrete
self.cross_modal_fusion = CrossModalFusion()    # concrete
# ... and optional perception concretions
```

**Violation:** The highest-level module in the agent hierarchy (`ConsciousAgent`) depends directly on 10+ low-level concrete implementations. There is no `AwarenessProvider`, `MemoryStore`, `Clock`, `ExperienceBuffer`, `ReflectionEngine`, `PolicyOptimizer`, `SkillEvolution`, or `CrossModalFusion` abstraction.

**Impact:** Replacing `MultiModalMemory` with a Redis-backed implementation would require editing `ConsciousAgent`. Testing `ConsciousAgent` in isolation requires mocking 10+ concrete classes.

**Fix:** Define protocols/ABCs for each subsystem and inject them via `__init__` with defaults.

##### 🔴 CRITICAL — `SwarmOrchestrator` directly instantiates 8+ concrete classes (`agents/swarm_orchestrator.py`, lines 80–112)

```python
self.deliberation_engine = DeliberationEngine()          # concrete
self.temporal_auditor = TemporalAuditor()                # concrete
self.consensus_engine = DistributedConsensusEngine()     # concrete
self.topology_optimizer = TopologyOptimizer()            # concrete
self.self_improvement_loop = SelfImprovementLoop()       # concrete
```

**Violation:** Same pattern as `ConsciousAgent` — direct instantiation of all infrastructure.

##### 🔴 CRITICAL — `TwinAgent` uses `importlib` to load concrete twins dynamically (`agents/twin_agent.py`, lines 79–83)

```python
module = importlib.import_module(self.twin_module_path)
twin_class = getattr(module, self.twin_class_name)
return twin_class()
```

**Violation:** While dynamic loading is flexible, there is no `CognitiveTwin` abstraction to load against. The code loads a concrete class by string name and assumes it has `think()` and `get_cognitive_signature()` methods. This is "duck typing without a protocol" — brittle and untypeable.

##### 🔴 CRITICAL — Memory package classes directly depend on `PTKG` (`memory/graph_retrieval.py`, `memory/causal_chain.py`, `memory/reputation_graph.py`, `memory/persistence.py`)

**Violation:** Four classes depend on the concrete `PTKG` class and access its internal `_nodes` and `_edges` dicts:

```python
# graph_retrieval.py, lines 135–136
for node_id, node in self.graph._nodes.items():
    ...

# causal_chain.py
self.graph.get_node(...)  # Depends on concrete PTKG

# reputation_graph.py, line 83
for node in self.graph._nodes.values():
    ...
```

**Fix:** Define a `Graph` protocol with `add_node`, `get_node`, `add_edge`, `get_edge`, `get_nodes`, `get_edges`. Make `PTKG` implement it. Have all clients depend on `Graph`.

##### 🔴 CRITICAL — Consensus classes directly depend on `HybridLogicalClock` (`consensus/distributed_consensus.py`, `consensus/temporal_auditor.py`, `consensus/cross_block_messenger.py`)

**Violation:** Three classes instantiate or manage `HybridLogicalClock` directly with no `Clock` or `TimestampGenerator` abstraction.

```python
# temporal_auditor.py, line 113
self._hlc = HybridLogicalClock(node_id=auditor_id, max_skew_ms=max_skew_ms)

# cross_block_messenger.py, lines 90, 97–98
self._hlc_clocks[agent_id] = HybridLogicalClock(node_id=agent_id)
```

**Fix:** Define a `Clock` protocol with `now()`, `send()`, `receive()`. Inject it.

##### 🟡 HIGH — `GraphRetriever` accesses `PTKG._nodes` and `_edges` directly (`memory/graph_retrieval.py`)

**Violation:** Direct field access across module boundaries breaks encapsulation and creates hidden dependencies.

#### 4.5.3 DIP Summary

| Severity | Count | Examples |
|----------|-------|----------|
| 🔴 CRITICAL | 5 | `ConsciousAgent` (10+ concretions), `SwarmOrchestrator` (8+ concretions), `TwinAgent` dynamic load without protocol, Memory→PTKG coupling (4 classes), Consensus→HLC coupling (3 classes) |
| 🟡 HIGH | 1 | `GraphRetriever` internal field access |

---

## 5. DRY ↔ SOLID Cross-Reference Matrix

Every DRY violation is a symptom of an underlying SOLID violation. This matrix maps the 80+ DRY findings from the prior audit to their root SOLID causes.

| DRY Violation | Location | Count | Root SOLID Cause |
|---------------|----------|-------|-----------------|
| `TwinAgent.think()` re-implements `ConsciousAgent.think()` | `agents/twin_agent.py` | 1 | **LSP** (broken inheritance) + **SRP** (TwinAgent does too much) |
| Memory-storage pattern repeated 11× | `agents/` | 11 | **SRP** (agent manages its own memory storage) + **DIP** (no `MemoryManager` abstraction) |
| Confidence calibration duplicated | `ConsciousAgent`, `TwinAgent` | 2 | **SRP** (calibration logic in agent instead of policy) |
| Active-agent filter duplicated 4× | `SwarmOrchestrator` | 4 | **SRP** (orchestrator does its own agent selection) |
| Task validation duplicated 4× | `SwarmOrchestrator` | 4 | **SRP** (no `TaskValidator` abstraction) |
| Complete-graph construction duplicated | `topology.py`, `distributed_consensus.py` | 2 | **DIP** (no `GraphBuilder` abstraction) |
| `CausalityViolation` block repeated 4× | `temporal_auditor.py` | 4 | **SRP** (no `ViolationFactory`) + **OCP** (new violation types require editing) |
| `CrossBlockMessenger.send()` re-implements HLC init | `cross_block_messenger.py` | 1 | **DIP** (direct HLC coupling) + **SRP** (messenger manages clocks) |
| `find_causes()` / `find_effects()` identical BFS | `causal_chain.py` | 2 | **SRP** (traversal mixed with tracking) + **OCP** (no generic traversal strategy) |
| `_retrieve_semantic()` / `_retrieve_procedural()` identical | `architecture.py` | 2 | **SRP** (no reusable retrieval strategy) |
| 39 twin files are structural clones | `twins/cognitive_models/` | 39 | **ALL FIVE** (no base class, no polymorphism, fat interface, concrete dependencies, no SRP) |
| Magic numbers (`0.5`, `0.67`, `7`, `0.85`) | Scattered | 30+ | **OCP** (values hardcoded instead of configured) |
| Empty-safe index append pattern | Scattered | 10× | **SRP** (no utility extracted) |
| `CurrentState` construction repeated 7× | Scattered | 7 | **SRP** (no `StateBuilder` / `StateFactory`) |
| Empty consensus result dicts share 6/7 keys | `distributed_consensus.py` | 3+ | **SRP** (no result builder/factory) |
| `@cite` boilerplate repeated 50+ | All modules | 50+ | **SRP** (citation metadata could be declarative) |
| `sys.path.insert` in all 14 test files | `tests/` | 14 | **DIP** (test infrastructure should be abstracted) |

### Insight: DRY and SOLID Are Complementary

- **DRY tells you WHAT is wrong:** "This code is duplicated."
- **SOLID tells you WHY it's wrong:** "There is no abstraction to unify these concerns, so duplication was the only option."
- **Fixing SOLID fixes DRY permanently:** Extracting a `GraphTraversal` strategy (OCP + SRP) eliminates the `find_causes`/`find_effects` duplication. Extracting a `MemoryStore` interface (DIP + OCP) eliminates the 11× memory-storage duplication.

---

## 6. Severity Summary

### By Principle

| Principle | 🔴 Critical | 🟡 High | 🟢 Low | Total |
|-----------|------------|---------|--------|-------|
| SRP | 7 | 5 | 2 | 14 |
| OCP | 6 | 1 | 0 | 7 |
| LSP | 2 | 1 | 0 | 3 |
| ISP | 1 | 3 | 0 | 4 |
| DIP | 5 | 1 | 0 | 6 |
| DRY | 11 | 30+ | 40+ | 80+ |

### By Package

| Package | Critical | High | Total Impact Score |
|---------|----------|------|-------------------|
| `twins/` | 5 | 3 | **Highest** |
| `agents/` | 4 | 4 | High |
| `memory/` | 4 | 3 | High |
| `consensus/` | 4 | 2 | High |
| `harness/` | 1 | 2 | Medium |
| `perception/` | 1 | 1 | Medium |
| `tests/` | 0 | 1 | Low |

### Risk Assessment

| Risk | Likelihood | Impact | Score |
|------|-----------|--------|-------|
| P7 implementation blocked by cascade changes | High | High | 🔴 |
| Bug fix in memory storage missed in one of 11 locations | Medium | High | 🔴 |
| New twin added by copy-paste, diverging from template | High | Medium | 🟡 |
| Test breakages from `sys.path` inconsistencies | Low | Low | 🟢 |
| Performance regression from O(N) graph scans in reputation | Medium | Medium | 🟡 |

---

## 7. Unified Remediation Roadmap

The following tasks are prioritized by **architectural leverage** (how many downstream problems they solve) and **regression risk** (how likely they are to break existing tests).

### Phase A: Foundation (Week 1–2) — Extract Abstractions

These tasks create the stable interfaces that all other refactoring depends on. They are low-risk because they add new code without changing existing behavior.

| # | Task | Files | SOLID Target | DRY Impact | Risk |
|---|------|-------|-------------|------------|------|
| A1 | Create `CognitiveTwin` ABC with `think()`, `get_cognitive_signature()`, default phase fallbacks | `twins/base.py` (new) | LSP, DIP, OCP, ISP | Eliminates 39 clones | Low |
| A2 | Create `MemoryStore` protocol + 5 implementations (`EpisodicStore`, `SemanticStore`, etc.) | `memory/stores.py` (new) | SRP, OCP, DIP | Eliminates 11× storage pattern | Low |
| A3 | Create `Graph` protocol + `GraphTraversal` strategy | `memory/graph_protocol.py` (new) | DIP, ISP, OCP | Eliminates `find_causes`/`find_effects` dup | Low |
| A4 | Create `Clock` protocol; `HybridLogicalClock` implements it | `consensus/clock.py` (new) | DIP | Decouples 3 consensus classes from HLC | Low |
| A5 | Create `TopologyBuilder` protocol + registry | `consensus/topology_builders.py` (new) | OCP, SRP | Enables new topologies without edits | Low |
| A6 | Create `AuditRule` protocol + list-based execution | `consensus/audit_rules.py` (new) | OCP, SRP | Eliminates 4× `CausalityViolation` blocks | Low |
| A7 | Create `GraphBuilder` utility for complete-graph construction | `shared/graph_utils.py` (new) | DIP | Eliminates topology/consensus dup | Low |
| A8 | Setup `pytest.ini` / `conftest.py` to eliminate `sys.path.insert` | `tests/conftest.py` (new) | DIP | Eliminates 14× test boilerplate | Low |

### Phase B: Structural Refactoring (Week 3–4) — Decompose God Classes

These tasks restructure the largest classes. Medium risk because they move code between files.

| # | Task | Files | SOLID Target | Risk |
|---|------|-------|-------------|------|
| B1 | Refactor `TwinAgent` to delegate to `super().think()` + inject twin via `ReasoningStrategy` | `agents/twin_agent.py` | LSP, SRP | Medium |
| B2 | Refactor `MultiModalMemory` to delegate to injected `MemoryStore` registry | `memory/architecture.py` | SRP, OCP | Medium |
| B3 | Decompose `PTKG` into `NodeStore`, `EdgeStore`, `PeriodManager`, `GraphTraversal`, `GraphSerializer` | `memory/ptkg.py` | SRP, ISP | Medium-High |
| B4 | Extract `SwarmTaskContext` / `AgentSelector` from `SwarmOrchestrator` | `agents/swarm_orchestrator.py` | SRP | Medium |
| B5 | Extract `ViolationFactory` from `TemporalAuditor` | `consensus/temporal_auditor.py` | SRP, OCP | Low |
| B6 | Extract `RetrievalStrategy` registry from `GraphRetriever` | `memory/graph_retrieval.py` | OCP, SRP | Medium |
| B7 | Extract `AggregationStrategy` from `DistributedConsensusEngine` | `consensus/distributed_consensus.py` | OCP, SRP | Medium |
| B8 | Add dependency injection to `ConsciousAgent.__init__` with default fallbacks | `agents/conscious_agent.py` | DIP | Medium |
| B9 | Add dependency injection to `SwarmOrchestrator.__init__` with default fallbacks | `agents/swarm_orchestrator.py` | DIP | Medium |

### Phase C: Cleanup (Week 5) — Eliminate Clones and Duplication

These tasks are low-risk mechanical cleanups that depend on Phases A and B.

| # | Task | Files | DRY Impact | Risk |
|---|------|-------|-----------|------|
| C1 | Refactor 39 twins to inherit from `CognitiveTwin` ABC; each file < 30 lines | `twins/cognitive_models/*.py` | Eliminates ~6,500 clone lines | Low |
| C2 | Delete committed generated twin code OR generate at build time | `twins/` | Eliminates generator drift | Low |
| C3 | Replace `CurrentState` inline construction with `StateBuilder` factory | `agents/conscious_agent.py`, `agents/twin_agent.py`, `agents/swarm_orchestrator.py` | Eliminates 7× dup | Low |
| C4 | Extract `TagBasedRetrieval` strategy for semantic/procedural stores | `memory/architecture.py` | Eliminates 2× dup | Low |
| C5 | Unify `find_causes`/`find_effects` via `_traverse(direction)` | `memory/causal_chain.py` | Eliminates 2× dup | Low |
| C6 | Extract shared `ConsensusResult` builder/factory | `consensus/distributed_consensus.py` | Eliminates 3× dup | Low |
| C7 | Extract `ConfidenceCalibrator` utility | `agents/conscious_agent.py`, `agents/twin_agent.py` | Eliminates 2× dup | Low |
| C8 | Centralize magic numbers in config/constants module | All modules | Eliminates 30+ magic numbers | Low |

### Phase D: Hardening (Week 6) — Tests and Documentation

| # | Task | Purpose |
|----|------|---------|
| D1 | Add tests for all new protocols/ABCs | Ensure abstractions have contracts |
| D2 | Add integration tests verifying no regressions | Maintain 883/883 passing |
| D3 | Update `AGENTS.md` with architecture conventions | Prevent future violations |
| D4 | Add pre-commit hook for DRY/SOLID smell detection | Automated prevention |
| D5 | Update citation registry for new files | Maintain governance |

### Recommended Execution Order

```
Week 1: A1–A4 (protocols for twins, memory, graph, clock)
Week 2: A5–A8 + B5 (topology, audit rules, graph builder, test infra, violation factory)
Week 3: B1–B4 (twin agent, multimodal memory, PTKG decomposition, orchestrator)
Week 4: B6–B9 + C1 (retrieval strategy, aggregation strategy, DI for agents, twin cleanup)
Week 5: C2–C8 (all remaining duplication cleanup)
Week 6: D1–D5 (tests, docs, hooks, citations)
```

---

## 8. Appendix: Detection Methodology

### 8.1 Tools Used

1. **Manual code review** of all 72 Python files
2. **Subagent-assisted exploration** using `explore` subagents for parallel package auditing
3. **Pattern matching** for `if-elif` chains, `isinstance` checks, direct instantiation
4. **Structural comparison** of twin files using line counts and diff analysis
5. **Import graph analysis** to detect cross-package coupling

### 8.2 Research Sources

This audit draws on the following authoritative sources for SOLID principle definitions and historical context:

| Source | Author | Year | Contribution |
|--------|--------|------|-------------|
| *Design Principles and Design Patterns* | Robert C. Martin | 2000 | Original formulation of SRP, OCP, DIP; definition of software rot symptoms |
| *Object-Oriented Software Construction* | Bertrand Meyer | 1988 | Original OCP formulation |
| *Data Abstraction and Hierarchy* (keynote) | Barbara Liskov | 1987 | Original LSP formulation |
| *Agile Software Development: Principles, Patterns, and Practices* | Robert C. Martin | 2002 | Full SOLID treatment |
| *Clean Architecture* | Robert C. Martin | 2017 | SRP refinement; "reasons to change = people" |
| Xerox printer consulting case | Robert C. Martin | 1990s | ISP origin story |
| *Working Effectively with Legacy Code* | Michael Feathers | 2004 | SOLID acronym coinage |
| *Are We SOLID Yet?* (arXiv 2509.03093) | Multiple authors | 2025 | LLM-based SOLID detection methodology |

### 8.3 Limitations

1. This audit is **static analysis only** — runtime behavior was inferred from code structure and test coverage.
2. Some SRP judgments are **subjective** — "one reason to change" depends on organizational structure (which stakeholders might request changes).
3. The audit does **not** assess whether the *current* design is "good enough" for present needs — it assesses architectural resilience to *future* change.
4. **False positives possible** — some violations may be intentionally pragmatic trade-offs.

---

*End of Audit*
