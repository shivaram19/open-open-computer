# DIP Audit — Dependency Inversion Principle

> **"High-level modules should not depend on low-level modules. Both should depend on abstractions."**
> — Robert C. Martin, *The C++ Report*, June 1996
>
> **"Abstractions should not depend on details. Details should depend on abstractions."**
> — Robert C. Martin, *Agile Software Development*, 2002

**Scope:** ACN Repository (`acn/src/*`)
**Date:** 2026-05-07
**Test Baseline:** 883/883 passing

---

## Table of Contents

1. [Why DIP Exists](#1-why-dip-exists)
2. [The Software Rot Problem](#2-the-software-rot-problem)
3. [Detection Methodology](#3-detection-methodology)
4. [Critical Violations](#4-critical-violations)
5. [High Violations](#5-high-violations)
6. [Remediation Tasks](#6-remediation-tasks)
7. [Success Criteria](#7-success-criteria)

---

## 1. Why DIP Exists

### Historical Origin

Robert C. Martin introduced DIP in a **June 1996 column for *The C++ Report***. He had been observing that conventional layered architectures (UI → Business Logic → Database) caused "software rot" — high-level business logic was directly coupled to low-level implementation details like database schemas, UI frameworks, and network protocols.

Martin's insight was that the **direction of dependency** was wrong. In traditional layered architecture:

```
High-level Business Rules → Low-level Database
```

The most stable, valuable part of the system (business rules) was being destabilized by volatile implementation details (database). DIP inverts this:

```
High-level Business Rules → Abstract Interface ← Low-level Database
```

Both sides depend on the abstraction. The abstraction is owned by the high-level module and implemented by the low-level module.

### The Core Problem DIP Solves

**Directional coupling corrupting stable logic.** When high-level modules depend on low-level concretions:
1. Changes to low-level details (database, UI, network) force high-level recompilation/retesting
2. High-level logic cannot be reused in different contexts
3. Testing requires the full low-level infrastructure
4. Framework upgrades become high-risk operations

> *"The implication of this principle is quite simple. Every dependency in the design should target an interface, or an abstract class. No dependency should target a concrete class."*

### DIP in the ACN Context

`ConsciousAgent` (the highest-level module in the agent hierarchy) directly instantiates 10+ concrete classes. Replacing `MultiModalMemory` with a Redis-backed implementation would require editing `ConsciousAgent`. Testing `ConsciousAgent` in isolation requires mocking 10+ concrete classes. This is exactly the corruption DIP was designed to prevent.

---

## 2. The Software Rot Problem

### Traditional Layered Architecture (Violates DIP)

```
ConsciousAgent (high-level)
    ↓ directly imports
MultiModalMemory (low-level)
    ↓ directly imports
PTKG (lower-level)
    ↓ directly imports
HybridLogicalClock (lowest-level)
```

**Problem:** A change to `HybridLogicalClock` (e.g., adding a new constructor parameter) ripples up through `PTKG`, `MultiModalMemory`, and finally `ConsciousAgent`.

### Inverted Architecture (Follows DIP)

```
ConsciousAgent (high-level)
    ↓ depends on
MemoryStore (abstraction, owned by ConsciousAgent)
    ↑ implemented by
MultiModalMemory (low-level)

ConsciousAgent (high-level)
    ↓ depends on
Clock (abstraction, owned by ConsciousAgent)
    ↑ implemented by
HybridLogicalClock (low-level)
```

**Benefit:** A change to `HybridLogicalClock` affects only `HybridLogicalClock`. `ConsciousAgent` is protected.

---

## 3. Detection Methodology

| Heuristic | Threshold | Rationale |
|-----------|-----------|-----------|
| `from concrete_module import ConcreteClass` in high-level modules | Any | Direct concrete dependency |
| Direct instantiation (`self.x = ConcreteClass()`) in `__init__` | > 3 per class | Lack of injection |
| Internal field access (`obj._private_dict`) across module boundaries | Any | Breaks encapsulation |
| No ABC/protocol at module boundaries | Any | No abstraction to depend on |
| High-level class has > 5 concrete dependencies | Any | Architecture corruption |

---

## 4. Critical Violations

### 4.1 `ConsciousAgent` directly instantiates 10+ concrete classes (`agents/conscious_agent.py`, lines 125–198)

**Full dependency inventory:**

```python
from harness.awareness import AwarenessSubsystem          # concrete
from memory.architecture import MultiModalMemory          # concrete
from memory.ptkg import PTKG                              # concrete
from memory.graph_retrieval import GraphRetriever         # concrete
from consensus.hlc import HybridLogicalClock              # concrete
from harness.experience_buffer import ExperienceBuffer    # concrete
from harness.meta_cognitive_reflection import ReflectionEngine  # concrete
from harness.policy_optimizer import PolicyOptimizer      # concrete
from harness.skill_evolution import SkillEvolution        # concrete
from perception.cross_modal_fusion import CrossModalFusion  # concrete
from perception.video_scene_graph import TemporalSceneGraph  # concrete
from perception.action_tube import ActionTubeLibrary      # concrete
from perception.temporal_grounding import TemporalIndex   # concrete
from tools.date_tool import DateTool                      # concrete
from tools.web_search_tool import WebSearchTool           # concrete
```

**Instantiation in `__init__`:**
```python
self.awareness = AwarenessSubsystem()           # line 139
self.memory = MultiModalMemory()                # line 140
self.hlc_clock = HybridLogicalClock()           # line 147
self.experience_buffer = ExperienceBuffer()     # line 173
self.reflection_engine = ReflectionEngine()     # line 174
self.policy_optimizer = PolicyOptimizer()       # line 175
self.skill_evolution = SkillEvolution()         # line 176
self.cross_modal_fusion = CrossModalFusion()    # line 193
```

**Verdict:** The highest-level module depends on 10+ low-level concretions. There is no `AwarenessProvider`, `MemoryStore`, `Clock`, `ExperienceBuffer`, `ReflectionEngine`, `PolicyOptimizer`, `SkillEvolution`, or `CrossModalFusion` abstraction.

**Impact:**
- Replacing `MultiModalMemory` with Redis requires editing `ConsciousAgent`
- Testing `ConsciousAgent` requires mocking 10+ concrete classes
- Adding P7 requires editing `ConsciousAgent.__init__`

**Fix:** Define protocols and inject with defaults:

```python
# NEW: agents/protocols.py
from typing import Protocol, Dict, Any, List, Optional

class AwarenessProvider(Protocol):
    def set_goal(self, goal): ...
    def record_state(self, state): ...
    def compute_direction(self, goal_id, state): ...
    def register_alert_handler(self, handler): ...

class MemoryStore(Protocol):
    def store(self, trace): ...
    def retrieve(self, memory_type, strategy, query, limit): ...

class Clock(Protocol):
    def now(self): ...
    def send(self): ...
    def receive(self, timestamp): ...
    def reset(self): ...

class ExperienceBuffer(Protocol):
    def add(self, experience): ...
    def sample(self, batch_size): ...

class ReflectionEngine(Protocol):
    def reflect(self, experiences): ...

class PolicyOptimizer(Protocol):
    def register_policy(self, policy): ...
    def optimize(self, agent_id, experiences): ...

class SkillEvolution(Protocol):
    def evolve(self, agent_id, experiences): ...
```

```python
# REFACTORED: ConsciousAgent
class ConsciousAgent:
    def __init__(
        self,
        agent_id: str,
        name: str,
        cluster: str,
        awareness_level: AwarenessLevel = AwarenessLevel.FULL,
        context_scope: Optional[Dict[str, Any]] = None,
        # Injected dependencies with defaults
        awareness: Optional[AwarenessProvider] = None,
        memory: Optional[MemoryStore] = None,
        clock: Optional[Clock] = None,
        experience_buffer: Optional[ExperienceBuffer] = None,
        reflection_engine: Optional[ReflectionEngine] = None,
        policy_optimizer: Optional[PolicyOptimizer] = None,
        skill_evolution: Optional[SkillEvolution] = None,
    ):
        self.awareness = awareness or AwarenessSubsystem(level=awareness_level)
        self.memory = memory or MultiModalMemory()
        self.hlc_clock = clock or HybridLogicalClock(node_id=agent_id)
        self.experience_buffer = experience_buffer or ExperienceBuffer()
        self.reflection_engine = reflection_engine or ReflectionEngine()
        self.policy_optimizer = policy_optimizer or PolicyOptimizer()
        self.skill_evolution = skill_evolution or SkillEvolution()
```

This preserves backward compatibility (all existing code works) while enabling:
- `ConsciousAgent(agent_id="x", memory=RedisMemoryStore())`
- `ConsciousAgent(agent_id="x", clock=MockClock())`
- Testing with all dependencies mocked

---

### 4.2 `SwarmOrchestrator` directly instantiates 8+ concrete classes (`agents/swarm_orchestrator.py`, lines 80–112)

```python
self.deliberation_engine = DeliberationEngine()          # concrete
self.temporal_auditor = TemporalAuditor()                # concrete
self.consensus_engine = DistributedConsensusEngine()     # concrete
self.topology_optimizer = TopologyOptimizer()            # concrete
self.self_improvement_loop = SelfImprovementLoop()       # concrete
```

**Verdict:** Same pattern as `ConsciousAgent` — direct instantiation of all infrastructure.

**Fix:** Same injection pattern with defaults.

---

### 4.3 `TwinAgent` loads concrete twins without protocol (`agents/twin_agent.py`, lines 79–83)

```python
def _load_twin(self) -> Any:
    module = importlib.import_module(self.twin_module_path)
    twin_class = getattr(module, self.twin_class_name)
    return twin_class()
```

**Violation:** While dynamic loading is flexible, there is no `CognitiveTwin` abstraction to load against. The code loads a concrete class by string name and assumes it has `think()` and `get_cognitive_signature()` methods. This is "duck typing without a protocol" — brittle and untypeable.

**Fix:**
```python
from twins.base import CognitiveTwin  # ABC with think() and get_cognitive_signature()

def _load_twin(self) -> CognitiveTwin:
    module = importlib.import_module(self.twin_module_path)
    twin_class = getattr(module, self.twin_class_name)
    twin = twin_class()
    if not isinstance(twin, CognitiveTwin):
        raise TypeError(f"{self.twin_class_name} must implement CognitiveTwin")
    return twin
```

---

### 4.4 Memory classes directly depend on `PTKG` (`memory/graph_retrieval.py`, `memory/causal_chain.py`, `memory/reputation_graph.py`, `memory/persistence.py`)

**Four classes access `PTKG` internals directly:**

```python
# graph_retrieval.py, lines 135–136
for node_id, node in self.graph._nodes.items():
    ...

# causal_chain.py
self.graph.get_node(...)  # Depends on concrete PTKG

# reputation_graph.py, line 83
for node in self.graph._nodes.values():
    ...

# persistence.py, line 62, 78, 96
ptkg_data = self.graph.to_dict()
self.graph = PTKG.from_dict(data)
```

**Violation:** Four clients depend on the concrete `PTKG` class. Three access internal `_nodes` and `_edges` dicts, breaking encapsulation.

**Fix:** Define a `Graph` protocol (see ISP audit) and have all clients depend on it:
```python
class Graph(Protocol):
    def add_node(self, node_id, node_type, **kwargs): ...
    def get_node(self, node_id): ...
    def add_edge(self, source, target, edge_type, **kwargs): ...
    def get_edge(self, edge_id): ...
    def get_nodes(self): ...
    def get_edges(self): ...
```

---

### 4.5 Consensus classes directly depend on `HybridLogicalClock` (`consensus/distributed_consensus.py`, `consensus/temporal_auditor.py`, `consensus/cross_block_messenger.py`)

```python
# temporal_auditor.py, line 113
self._hlc = HybridLogicalClock(node_id=auditor_id, max_skew_ms=max_skew_ms)

# cross_block_messenger.py, lines 90, 97–98
self._hlc_clocks[agent_id] = HybridLogicalClock(node_id=agent_id)

# distributed_consensus.py (AgentVote dataclass)
@dataclass
class AgentVote:
    timestamp: Optional[HLCTimestamp] = None  # Direct dependency on HLC type
```

**Violation:** Three classes instantiate or manage `HybridLogicalClock` directly with no `Clock` or `TimestampGenerator` abstraction.

**Fix:**
```python
class Clock(Protocol):
    def now(self) -> Timestamp: ...
    def send(self) -> Timestamp: ...
    def receive(self, timestamp: Timestamp) -> Timestamp: ...
    def reset(self) -> None: ...

class Timestamp(Protocol):
    def compare(self, other: Timestamp) -> int: ...
    def to_dict(self) -> Dict: ...

# HybridLogicalClock implements Clock
# HLCTimestamp implements Timestamp
```

---

## 5. High Violations

### 5.1 `GraphRetriever` accesses `PTKG._nodes` and `_edges` directly (`memory/graph_retrieval.py`)

```python
for node_id, node in self.graph._nodes.items():
    ...
```

**Violation:** Direct field access across module boundaries breaks encapsulation and creates hidden dependencies.

**Fix:** Use `GraphStorage.get_nodes()` protocol method.

---

## 6. Remediation Tasks

### Immediate (Week 1)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| DIP-1 | Create `Clock` protocol; `HybridLogicalClock` implements it | `consensus/clock.py` (new) | OCP, SRP |
| DIP-2 | Create `Graph` protocol (node/edge CRUD) | `memory/graph_protocols.py` (new) | ISP, SRP |
| DIP-3 | Create `MemoryStore` protocol | `memory/stores.py` (new) | OCP, SRP |
| DIP-4 | Update 4 memory clients to depend on `Graph` protocol, not `PTKG` | `memory/*.py` | ISP |
| DIP-5 | Update 3 consensus classes to depend on `Clock` protocol, not `HybridLogicalClock` | `consensus/*.py` | OCP, SRP |

### Short-term (Week 2)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| DIP-6 | Add dependency injection to `ConsciousAgent.__init__` with default fallbacks | `agents/conscious_agent.py` | SRP |
| DIP-7 | Add dependency injection to `SwarmOrchestrator.__init__` with default fallbacks | `agents/swarm_orchestrator.py` | SRP |
| DIP-8 | Enforce `CognitiveTwin` protocol at `TwinAgent._load_twin()` | `agents/twin_agent.py` | LSP |
| DIP-9 | Remove all `._nodes` / `._edges` direct access | `memory/*.py` | ISP |

### Medium-term (Week 3)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| DIP-10 | Create full protocol suite: `AwarenessProvider`, `ExperienceBuffer`, `ReflectionEngine`, `PolicyOptimizer`, `SkillEvolution` | `agents/protocols.py` | SRP |
| DIP-11 | Refactor tests to use injected mocks instead of monkey-patching | `tests/` | — |
| DIP-12 | Document dependency injection conventions in `AGENTS.md` | `AGENTS.md` | — |

---

## 7. Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| `ConsciousAgent` concrete dependencies | 10+ direct instantiations | 0 (all injected with defaults) |
| `SwarmOrchestrator` concrete dependencies | 8+ direct instantiations | 0 (all injected with defaults) |
| Memory clients depending on `PTKG` directly | 4 | 0 (use `Graph` protocol) |
| Consensus classes depending on `HybridLogicalClock` directly | 3 | 0 (use `Clock` protocol) |
| Internal field access (`._nodes`, `._edges`) | 4 locations | 0 |
| `TwinAgent` loads twin without type check | Yes | No (enforces `CognitiveTwin`) |
| Test files with `sys.path.insert` | 14 | 0 (via `conftest.py`) |

---

*Generated from SOLID_COMPLIANCE_AUDIT.md — DIP Section*
