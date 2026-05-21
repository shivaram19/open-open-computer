# Clean Architecture Audit

> **"The goal of software architecture is to minimize the human resources required to build and maintain the required system."**
> — Robert C. Martin, *Clean Architecture*, 2017
>
> **"Architecture is about the important stuff. Whatever that is."**
> — Ralph Johnson

**Scope:** ACN Repository (`acn/src/*`)
**Date:** 2026-05-07
**Test Baseline:** 883/883 passing
**Files Audited:** ~72 Python files, ~19,500 lines

---

## Table of Contents

1. [Why Clean Architecture Exists](#1-why-clean-architecture-exists)
2. [The Dependency Rule](#2-the-dependency-rule)
3. [Current ACN Layer Analysis](#3-current-acn-layer-analysis)
4. [Dependency Rule Violations](#4-dependency-rule-violations)
5. [Boundary Crossings](#5-boundary-crossings)
6. [Framework & Driver Coupling](#6-framework--driver-coupling)
7. [Remediation Tasks](#7-remediation-tasks)
8. [Success Criteria](#8-success-criteria)

---

## 1. Why Clean Architecture Exists

### Historical Origin

Robert C. Martin's *Clean Architecture* (2017) is the culmination of decades of work on software design. It builds on:
- **Alister Cockburn's Hexagonal Architecture** (2005) — ports and adapters
- **Jeffrey Palermo's Onion Architecture** (2008) — domain at the center
- **Domain-Driven Design** (Eric Evans, 2003) — bounded contexts

The core insight: **dependencies should point inward**. The most stable, high-level policies (business rules) should not depend on volatile, low-level details (frameworks, databases, UI, external services).

### The Four Concentric Layers

```
┌─────────────────────────────────────┐
│  Frameworks & Drivers (outer)       │  UI, Web, DB, External APIs
│  ─────────────────────────────────  │
│  Interface Adapters                 │  Controllers, Presenters, Gateways
│  ─────────────────────────────────  │
│  Use Cases / Application Business   │  Orchestration, workflows
│  ─────────────────────────────────  │
│  Entities / Enterprise Business     │  Core business rules, domain models
│  (inner)                            │
└─────────────────────────────────────┘
```

**The Dependency Rule:** Source code dependencies must point only inward, toward higher-level policies.

### Clean Architecture in the ACN Context

ACN's natural layers would be:

```
┌─────────────────────────────────────┐
│  Tools & External APIs              │  WebSearchTool, DateTool
│  ─────────────────────────────────  │
│  Perception Subsystems              │  SceneGraph, ActionTube, Fusion
│  ─────────────────────────────────  │
│  Consensus & Communication          │  HLC, DistributedConsensus, Topology
│  ─────────────────────────────────  │
│  Memory & Persistence               │  PTKG, MultiModalMemory, Retrieval
│  ─────────────────────────────────  │
│  Harness & Self-Improvement         │  ExperienceBuffer, PolicyOptimizer
│  ─────────────────────────────────  │
│  Agents & Swarm (inner)             │  ConsciousAgent, SwarmOrchestrator
└─────────────────────────────────────┘
```

**Current reality:** Dependencies point in all directions. `ConsciousAgent` (inner) directly imports `WebSearchTool` (outer). This violates the Dependency Rule.

---

## 2. The Dependency Rule

> **"Nothing in an inner circle can know anything at all about something in an outer circle."**

### What the Dependency Rule Means

| Allowed | Forbidden |
|---------|-----------|
| `agents/` imports from `harness/` | `harness/` imports from `agents/` |
| `harness/` imports from `memory/` | `memory/` imports from `harness/` |
| `memory/` imports from `consensus/` | `consensus/` imports from `memory/` |
| Use cases depend on entities | Entities depend on use cases |
| Interface adapters depend on use cases | Use cases depend on interface adapters |

### The Exception: Dependency Inversion

The inner circle can declare an **interface/protocol** that the outer circle implements:

```python
# Inner circle (agents/) declares what it needs:
class ResearchTool(Protocol):
    def search(self, query: str) -> List[SearchResult]: ...

# Outer circle (tools/) implements it:
class WebSearchTool:
    def search(self, query: str) -> List[SearchResult]: ...
```

This satisfies the Dependency Rule because `agents/` depends on an abstraction, not on `tools/`.

---

## 3. Current ACN Layer Analysis

### 3.1 Package Dependency Graph

```
agents/
├── imports from: harness, memory, consensus, perception, tools, shared
├── imported by: tests

harness/
├── imports from: shared
├── imported by: agents, tests

memory/
├── imports from: consensus, shared
├── imported by: agents, harness, tests

consensus/
├── imports from: shared
├── imported by: agents, memory, tests

perception/
├── imports from: shared
├── imported by: agents, tests

tools/
├── imports from: shared
├── imported by: agents, scripts, tests

shared/
├── imports from: (none — should be innermost)
├── imported by: ALL packages

twins/
├── imports from: shared
├── imported by: agents, tests
```

### 3.2 Layer Assignment

| Layer | Packages | Stability |
|-------|----------|-----------|
| **Inner (Entities)** | `shared/` | Highest — utility functions, citations |
| **Inner-Mid (Use Cases)** | `harness/`, `memory/`, `consensus/` | High — core algorithms |
| **Outer-Mid (Adapters)** | `perception/`, `tools/`, `twins/` | Medium — external interfaces |
| **Outer (Frameworks)** | `scripts/`, `tests/` | Low — automation, validation |

**Problem:** `agents/` sits conceptually at the center (orchestrating all others) but imports from every other package. In Clean Architecture, the center should be the **most abstract** layer, not the **most coupled**.

---

## 4. Dependency Rule Violations

### 4.1 `ConsciousAgent` Imports from Outer Layers

`agents/conscious_agent.py` imports from 6 packages, including outer layers:

```python
from perception.video_scene_graph import TemporalSceneGraph      # Outer layer
from perception.action_tube import ActionTubeLibrary             # Outer layer
from perception.cross_modal_fusion import CrossModalFusion       # Outer layer
from perception.temporal_grounding import TemporalIndex          # Outer layer
from tools.date_tool import DateTool, get_current_date           # Outer layer
from tools.web_search_tool import WebSearchTool                  # Outer layer
```

**Violation:** Inner-layer `ConsciousAgent` depends on outer-layer perception and tools.

**Fix:** Define protocols in `agents/` and have outer layers implement them:
```python
# NEW: agents/protocols.py (inner layer)
class ResearchTool(Protocol):
    def search(self, query: str) -> List[SearchResult]: ...

class PerceptionSubsystem(Protocol):
    def process_frame(self, frame) -> PerceptionResult: ...

# REFACTORED: ConsciousAgent (inner layer)
class ConsciousAgent:
    def __init__(self, ..., research_tool: Optional[ResearchTool] = None):
        self.research_tool = research_tool

# tools/web_search_tool.py (outer layer)
class WebSearchTool:
    def search(self, query: str) -> List[SearchResult]: ...
    # Implements ResearchTool without knowing about agents/
```

### 4.2 `SwarmOrchestrator` Imports from All Layers

`agents/swarm_orchestrator.py` imports from 9 packages:

```python
from agents.conscious_agent import ConsciousAgent, AgentGoal           # Same layer (OK)
from agents.deliberation import DeliberationEngine                     # Same layer (OK)
from harness.awareness import AwarenessSubsystem, GoalState, CurrentState  # Inner-mid (OK)
from memory.ptkg import PTKG, NodeType, EdgeType                       # Inner-mid (OK)
from memory.graph_retrieval import GraphRetriever                      # Inner-mid (OK)
from memory.reputation_graph import ReputationGraphTracker             # Inner-mid (OK)
from memory.causal_chain import CausalChainTracker                     # Inner-mid (OK)
from consensus.hlc import HybridLogicalClock                           # Inner-mid (OK)
from consensus.temporal_auditor import TemporalAuditor, CausalityHealth  # Inner-mid (OK)
from consensus.distributed_consensus import DistributedConsensusEngine, AgentVote  # Inner-mid (OK)
from consensus.topology import TopologyOptimizer, TopologyType         # Inner-mid (OK)
from harness.feedback_loop import SelfImprovementLoop, FeedbackLoopResult  # Inner-mid (OK)
```

**Assessment:** `SwarmOrchestrator` imports only from `agents/` and inner-mid layers. This is **architecturally correct** per the Dependency Rule. However, it directly instantiates 8+ concrete classes (DIP violation, separate audit).

### 4.3 `memory/` Imports from `consensus/`

```python
# memory/ptkg.py — NO imports from consensus (GOOD)
# memory/architecture.py — NO imports from consensus (GOOD)
# memory/graph_retrieval.py — NO imports from consensus (GOOD)
# memory/causal_chain.py — NO imports from consensus (GOOD)
```

**Assessment:** Memory does not import from consensus. Correct.

However, `consensus/` does not import from `memory/` either. This suggests the layers are properly separated.

### 4.4 `harness/` Imports from `memory/`

```python
# harness/feedback_loop.py
# harness/skill_evolution.py
# harness/policy_optimizer.py
# harness/experience_buffer.py
```

**Assessment:** Harness files do NOT import from memory. This is correct — harness (self-improvement) is a separate concern from memory.

### 4.5 `tests/` Import Chaos

Test files import from all layers directly:
```python
# tests/harness/test_p2_full_deliberation.py
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'acn', 'src'))
from agents.swarm_orchestrator import SwarmOrchestrator
from agents.conscious_agent import ConsciousAgent
from consensus.distributed_consensus import DistributedConsensusEngine
```

**Violation:** Tests reach across all layers without clear structure. This is common but can be improved with test layer alignment.

**Fix:** Organize tests by layer:
```
tests/
├── unit/              # Single class/function tests
│   ├── agents/
│   ├── harness/
│   ├── memory/
│   ├── consensus/
│   └── perception/
├── integration/       # Cross-package tests
│   ├── agent_harness/
│   ├── memory_consensus/
│   └── swarm_full/
└── e2e/               # End-to-end scenarios
```

### 4.6 `scripts/` Imports from All Layers

```python
# scripts/research_swarm.py
from agents.conscious_agent import ConsciousAgent
from agents.swarm_orchestrator import SwarmOrchestrator
from tools.web_search_tool import WebSearchTool
```

**Assessment:** Scripts are outer-layer drivers. It's acceptable for them to import from inner layers. However, scripts should not contain business logic — they should delegate to use cases.

**Current issue:** `scripts/mvp_web_search_demo.py` may contain demo logic that should be in a use case class.

---

## 5. Boundary Crossings

### 5.1 Data Crossing Boundaries

In Clean Architecture, data that crosses boundaries should be in the **simplest possible form** — primitive types, dicts, or simple DTOs.

**ACN Assessment:**

| Boundary | Data Format | Assessment |
|----------|-------------|------------|
| `agents` → `harness` | `CurrentState`, `GoalState` dataclasses | Good — simple DTOs |
| `agents` → `memory` | `MemoryTrace` dataclass | Good — simple DTO |
| `agents` → `consensus` | `AgentVote` dataclass | Good — simple DTO |
| `agents` → `perception` | `ModalityFeature`, `FusionContext` | Acceptable — domain objects |
| `agents` → `tools` | Raw strings, dicts | Good — primitives |
| `memory` → `consensus` | `HLCTimestamp` | Concerning — consensus type leaking into memory |

**Issue:** `memory/` should not know about `consensus.HLCTimestamp`. If memory traces need timestamps, they should use a generic `Timestamp` type from `shared/`.

### 5.2 Use Case Boundaries

**Missing in ACN:** There is no explicit "use case" layer. Orchestration logic is embedded in `ConsciousAgent.think()` and `SwarmOrchestrator.execute_round()`.

**Recommendation:** Extract use cases:
```python
# NEW: agents/use_cases.py
class ConductResearch:
    """Use case: Agent conducts research on a topic."""
    def __init__(self, research_tool: ResearchTool, memory: MemoryStore):
        self.research_tool = research_tool
        self.memory = memory
    
    def execute(self, agent: ConsciousAgent, topic: str) -> ResearchResult:
        findings = self.research_tool.search(topic)
        self.memory.store(MemoryTrace(...))
        return ResearchResult(findings=findings)

class ReachConsensus:
    """Use case: Swarm reaches consensus on a decision."""
    def __init__(self, consensus_engine: ConsensusEngine, topology: TopologyBuilder):
        self.consensus_engine = consensus_engine
        self.topology = topology
    
    def execute(self, swarm: SwarmOrchestrator, votes: List[AgentVote]) -> ConsensusResult:
        topology = self.topology.build(swarm.agents)
        return self.consensus_engine.reach_consensus(votes, topology)
```

This makes the use cases testable in isolation and makes the architecture explicit.

---

## 6. Framework & Driver Coupling

### 6.1 External Service Coupling

| Service | Location | Coupling Level |
|---------|----------|---------------|
| Web search | `tools/web_search_tool.py` | Loose — wrapped in class |
| Date/time | `tools/date_tool.py` | Loose — wrapped in class |
| File system | `memory/persistence.py` | Tight — direct `json.dump` |

**Assessment:** External services are reasonably well-isolated. The `WebSearchTool` and `DateTool` act as adapters.

### 6.2 Python Standard Library Coupling

| Dependency | Location | Risk |
|------------|----------|------|
| `json` | `memory/persistence.py` | Low — standard, stable |
| `uuid` | `conscious_agent.py` | Low — standard, stable |
| `time` | All files | Low — standard, stable |
| `importlib` | `twin_agent.py` | Medium — dynamic loading without protocol |

**Assessment:** No problematic framework coupling detected.

### 6.3 Missing Abstractions for Future Drivers

The P5-OUTPUT-SYSTEMS.md spec mentions future output harnesses:
- Voice harness
- Video harness
- Document harness
- Knowledge harness

**Current risk:** Adding these would require editing `ConsciousAgent` (inner layer) to import new outer-layer packages. This violates the Dependency Rule.

**Fix:** Define `OutputHarness` protocol in `agents/protocols.py` now:
```python
class OutputHarness(Protocol):
    def emit(self, content: Dict[str, Any], format: str) -> None: ...
    def supports(self, format: str) -> bool: ...
```

---

## 7. Remediation Tasks

### Immediate (Week 1)

| # | Task | Files | Impact |
|---|------|-------|--------|
| CA-1 | Create `agents/protocols.py` with `ResearchTool`, `PerceptionSubsystem`, `OutputHarness` | New file | Establishes inner-layer abstractions |
| CA-2 | Move `DateTool` / `WebSearchTool` interfaces to protocols | `agents/protocols.py`, `tools/*.py` | Inverts dependency direction |
| CA-3 | Create `shared/timestamp.py` generic timestamp type | New file | Eliminates `memory` → `consensus` leakage |
| CA-4 | Document layer boundaries in `AGENTS.md` | `AGENTS.md` | Team alignment |

### Short-term (Week 2)

| # | Task | Files | Impact |
|---|------|-------|--------|
| CA-5 | Extract use cases from `ConsciousAgent` and `SwarmOrchestrator` | `agents/use_cases.py` (new) | Makes architecture explicit |
| CA-6 | Refactor `scripts/` to delegate to use cases | `scripts/*.py` | Removes business logic from drivers |
| CA-7 | Reorganize `tests/` by layer (unit/integration/e2e) | `tests/` | Aligns tests with architecture |
| CA-8 | Add import linting to enforce layer boundaries | `pyproject.toml` | Automated enforcement |

### Medium-term (Week 3)

| # | Task | Files | Impact |
|---|------|-------|--------|
| CA-9 | Extract `PerceptionSubsystem` as injectable dependency | `agents/conscious_agent.py`, `perception/` | Separates concerns |
| CA-10 | Create `OutputHarness` registry for P5+ output systems | `agents/output_registry.py` | Enables future extensions |
| CA-11 | Add architectural fitness tests | `tests/architecture/` | Verify dependency rule |
| CA-12 | Draw and publish dependency graph | `docs/architecture/` | Documentation |

---

## 8. Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| `agents/` imports from `tools/` | Direct imports | Protocol-only imports |
| `agents/` imports from `perception/` | Direct imports | Protocol-only imports |
| `memory/` imports from `consensus/` | `HLCTimestamp` | Generic `Timestamp` from `shared/` |
| Use case classes | 0 | ≥ 3 |
| Protocol definitions in `agents/` | 0 | ≥ 5 |
| Test organization by layer | Flat | `unit/`, `integration/`, `e2e/` |
| Import linting | None | `ruff` or `import-linter` |
| Architectural fitness tests | 0 | ≥ 2 |

---

*Generated from SOLID_COMPLIANCE_AUDIT.md — Clean Architecture Section*
