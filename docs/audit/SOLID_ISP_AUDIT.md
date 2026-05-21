# ISP Audit — Interface Segregation Principle

> **"Clients should not be forced to depend on interfaces they do not use."**
> — Robert C. Martin, 1996
>
> **"Many client-specific interfaces are better than one general-purpose interface."**
> — Robert C. Martin, *Agile Software Development*, 2002

**Scope:** ACN Repository (`acn/src/*`)
**Date:** 2026-05-07
**Test Baseline:** 883/883 passing

---

## Table of Contents

1. [Why ISP Exists](#1-why-isp-exists)
2. [The Xerox Story](#2-the-xerox-story)
3. [Detection Methodology](#3-detection-methodology)
4. [Critical Violations](#4-critical-violations)
5. [High Violations](#5-high-violations)
6. [Remediation Tasks](#6-remediation-tasks)
7. [Success Criteria](#7-success-criteria)

---

## 1. Why ISP Exists

### Historical Origin

Robert C. Martin formulated ISP while consulting for **Xerox** in the 1990s. Xerox had built a multifunction printer system that could print, staple, fax, and scan. The software was created from the ground up. As it grew, making modifications became excruciating — even the smallest change required a **one-hour redeployment cycle**.

The root cause: a single `Job` class was used by almost all tasks. Whenever a print job or stapling job needed to be performed, a call was made to the `Job` class. This created a "fat" class with multitudes of methods specific to different clients. A stapling job knew about all the methods of the print job, even though it had no use for them.

Martin's solution: instead of one large `Job` interface, create `StapleJob`, `PrintJob`, and `FaxJob` interfaces — each client depends only on the methods it uses.

### The Core Problem ISP Solves

**Accidental coupling through bloated contracts.** When a client depends on a method it doesn't use:
1. Changes to that method force the client to rebuild/redeploy
2. The client is exposed to bugs in unrelated functionality
3. The interface becomes a change magnet — every modification affects all clients
4. Testing requires mocking unused methods

### ISP in the ACN Context

`PTKG` has 20+ public methods. Four different clients use it, but each only needs 3–5 methods. Yet all four are forced to depend on the full surface area. A change to `consolidate_period()` (used only by `PTKGPersistence`) forces `CausalChainTracker` to rebuild.

---

## 2. The Xerox Story

| Element | Xerox Problem | ACN Equivalent |
|---------|--------------|----------------|
| Fat class | `Job` (print + staple + fax methods) | `PTKG` (storage + traversal + serialization + statistics) |
| Client 1 uses | Print methods | `CausalChainTracker` uses node/edge access + traversal |
| Client 2 uses | Staple methods | `GraphRetriever` uses node/edge access + traversal |
| Client 3 uses | Fax methods | `PTKGPersistence` uses `to_dict`/`from_dict` |
| Client 4 uses | All methods | None — no client uses all PTKG methods |
| Solution | `PrintJob`, `StapleJob`, `FaxJob` interfaces | `GraphStorage`, `GraphTraversal`, `GraphSerializer` interfaces |

---

## 3. Detection Methodology

| Heuristic | Threshold | Rationale |
|-----------|-----------|-----------|
| Classes with >20 public methods | Any | Likely serving multiple clients |
| Clients accessing disjoint subsets of a class | Any | Classic ISP symptom |
| Client accessing internal fields (`_private`) | Any | Exposed to implementation details it doesn't need |
| Classes mixing orthogonal concerns | Any | Different clients need different concerns |
| "God class" pattern | Any | One class doing everything for everyone |

---

## 4. Critical Violations

### 4.1 `PTKG` — The Fat Class (`memory/ptkg.py`, 20+ public methods, 698 lines)

**Public method inventory:**

| Method | Used By |
|--------|---------|
| `add_node`, `get_node`, `add_edge`, `get_edge` | All clients |
| `start_period`, `end_period`, `get_period` | `TemporalAuditor`, `GraphRetriever` |
| `get_nodes_valid_at`, `get_edges_in_period` | `GraphRetriever` |
| `bfs_traversal` | `CausalChainTracker`, `GraphRetriever` |
| `find_causal_paths` | `CausalChainTracker` |
| `consolidate_period` | `PTKGPersistence` |
| `to_dict`, `from_dict` | `PTKGPersistence` |
| `get_graph_stats` | Tests, diagnostics |

**Client dependency matrix:**

| Client | Methods Used | Methods Forced To Depend On |
|--------|-------------|----------------------------|
| `CausalChainTracker` | 5 | 15+ (period mgmt, serialization, stats) |
| `GraphRetriever` | 6 | 14+ (causal paths, consolidation, stats) |
| `PTKGPersistence` | 2 | 18+ (traversal, causal paths, period mgmt) |
| `ReputationGraphTracker` | 4 | 16+ (traversal, serialization, stats) |

**Verdict:** This is the exact "fat class" problem that ISP was created to solve. Every client is forced to depend on methods it never calls.

**Fix:** Split `PTKG` into role-specific interfaces:

```python
# NEW: memory/graph_protocols.py
from typing import Protocol, Dict, List, Optional, Any

class GraphStorage(Protocol):
    """Core node/edge CRUD — needed by all clients."""
    def add_node(self, node_id: str, node_type: str, **kwargs) -> None: ...
    def get_node(self, node_id: str) -> Optional[Dict]: ...
    def add_edge(self, source: str, target: str, edge_type: str, **kwargs) -> None: ...
    def get_edge(self, edge_id: str) -> Optional[Dict]: ...
    def has_node(self, node_id: str) -> bool: ...
    def has_edge(self, edge_id: str) -> bool: ...

class GraphTraversal(Protocol):
    """Graph traversal — needed by reasoning clients."""
    def bfs_traversal(self, start: str, max_depth: int = 3) -> List[str]: ...
    def get_neighbors(self, node_id: str) -> List[str]: ...
    def get_incoming_edges(self, node_id: str) -> List[Dict]: ...
    def get_outgoing_edges(self, node_id: str) -> List[Dict]: ...

class TemporalGraph(Protocol):
    """Time-aware queries — needed by temporal clients."""
    def start_period(self, period_id: str, timestamp: float) -> None: ...
    def end_period(self, period_id: str, timestamp: float) -> None: ...
    def get_nodes_valid_at(self, timestamp: float) -> List[Dict]: ...
    def get_edges_in_period(self, period_id: str) -> List[Dict]: ...

class CausalGraph(Protocol):
    """Causal path finding — needed by causal chain tracker."""
    def find_causal_paths(self, source: str, target: str, max_depth: int = 3) -> List[List[str]]: ...

class GraphSerializer(Protocol):
    """Serialization — needed by persistence clients."""
    def to_dict(self) -> Dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphSerializer": ...

class GraphStatistics(Protocol):
    """Metrics — needed by diagnostics."""
    def get_graph_stats(self) -> Dict[str, Any]: ...
```

`PTKG` implements all interfaces. Clients depend only on the interfaces they need:

```python
# Before:
class CausalChainTracker:
    def __init__(self, graph: PTKG):  # Forced to depend on 20+ methods
        self.graph = graph

# After:
class CausalChainTracker:
    def __init__(self, graph: GraphStorage & GraphTraversal & CausalGraph):
        self.graph = graph  # Depends on 9 methods only
```

---

## 5. High Violations

### 5.1 `ConsciousAgent` forces perception substrates on all agents (`agents/conscious_agent.py`, lines 190–195)

```python
# P6: Multi-modal perception substrates
self.scene_graph: Optional[TemporalSceneGraph] = None
self.action_tube_library: Optional[ActionTubeLibrary] = None
self.cross_modal_fusion = CrossModalFusion()
self.temporal_index: Optional[TemporalIndex] = None
self.perception_memory: List[Dict[str, Any]] = []
```

**Violation:** Even agents that never process video (e.g., text-only research agents) carry perception infrastructure. There is no `PerceptionEnabledAgent` subtype.

**Fix:** Extract perception into an optional subsystem:
```python
class PerceptionSubsystem:
    def __init__(self):
        self.scene_graph: Optional[TemporalSceneGraph] = None
        self.action_tube_library: Optional[ActionTubeLibrary] = None
        self.cross_modal_fusion = CrossModalFusion()
        self.temporal_index: Optional[TemporalIndex] = None

class ConsciousAgent:
    def __init__(self, ..., perception: Optional[PerceptionSubsystem] = None):
        self.perception = perception
```

Or create a subclass:
```python
class PerceivingAgent(ConsciousAgent):
    def __init__(self, ...):
        super().__init__(...)
        self.scene_graph = TemporalSceneGraph()
        # ... etc
```

---

### 5.2 `GraphRetriever` forces reputation methods on retrieval-only clients (`memory/graph_retrieval.py`)

```python
class GraphRetriever:
    def retrieve(self, strategy, query, ...): ...       # Used by all clients
    def set_agent_reputation(self, agent_id, score): ... # Used by consensus clients
    def get_agent_reputation(self, agent_id): ...        # Used by consensus clients
    def build_reasoning_context(self, ...): ...          # Used by reasoning clients
```

**Violation:** A client that only wants `retrieve()` must depend on a class that also carries reputation management.

**Fix:**
```python
class ReputationProvider(Protocol):
    def set_agent_reputation(self, agent_id: str, score: float) -> None: ...
    def get_agent_reputation(self, agent_id: str) -> float: ...

class GraphRetriever:
    def __init__(self, graph: GraphStorage, reputation: Optional[ReputationProvider] = None):
        self.graph = graph
        self.reputation = reputation
```

---

### 5.3 `SwarmOrchestrator` forces P3–P5 infrastructure on all tasks (`agents/swarm_orchestrator.py`, lines 80–112)

```python
self.deliberation_engine = DeliberationEngine()          # Deliberation tasks only
self.temporal_auditor = TemporalAuditor()                # P4 tasks only
self.consensus_engine = DistributedConsensusEngine()     # Consensus tasks only
self.topology_optimizer = TopologyOptimizer()            # Distributed tasks only
self.self_improvement_loop = SelfImprovementLoop()       # P5 tasks only
self.reputation_tracker = None                           # P3 tasks only
self.causal_tracker = None                               # P3 tasks only
```

**Violation:** A simple 3-agent task with no deliberation still carries all infrastructure. The orchestrator is forced to instantiate everything upfront.

**Fix:** Use lazy initialization or dependency injection:
```python
class SwarmOrchestrator:
    def __init__(self, ...):
        self._deliberation_engine: Optional[DeliberationEngine] = None
        self._temporal_auditor: Optional[TemporalAuditor] = None
        # ... etc
    
    @property
    def deliberation_engine(self) -> DeliberationEngine:
        if self._deliberation_engine is None:
            self._deliberation_engine = DeliberationEngine()
        return self._deliberation_engine
```

Or inject only what the task needs:
```python
class SwarmOrchestrator:
    def __init__(self, ..., infrastructure: Optional[SwarmInfrastructure] = None):
        self.infrastructure = infrastructure or SwarmInfrastructure()

@dataclass
class SwarmInfrastructure:
    deliberation: Optional[DeliberationEngine] = None
    consensus: Optional[DistributedConsensusEngine] = None
    topology: Optional[TopologyOptimizer] = None
    self_improvement: Optional[SelfImprovementLoop] = None
```

---

## 6. Remediation Tasks

### Immediate (Week 1)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| ISP-1 | Create `GraphStorage`, `GraphTraversal`, `TemporalGraph`, `CausalGraph`, `GraphSerializer`, `GraphStatistics` protocols | `memory/graph_protocols.py` (new) | DIP, SRP |
| ISP-2 | Make `PTKG` implement all graph protocols | `memory/ptkg.py` | SRP |
| ISP-3 | Update `CausalChainTracker` to depend on `GraphStorage & GraphTraversal & CausalGraph` only | `memory/causal_chain.py` | DIP |
| ISP-4 | Update `GraphRetriever` to depend on `GraphStorage & GraphTraversal` only | `memory/graph_retrieval.py` | DIP |

### Short-term (Week 2)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| ISP-5 | Create `ReputationProvider` protocol; extract from `GraphRetriever` | `memory/reputation_graph.py` | SRP, DIP |
| ISP-6 | Extract `PerceptionSubsystem` from `ConsciousAgent` | `agents/conscious_agent.py`, `perception/` | SRP, DIP |
| ISP-7 | Add lazy initialization or injection to `SwarmOrchestrator` | `agents/swarm_orchestrator.py` | DIP, SRP |
| ISP-8 | Update `PTKGPersistence` to depend on `GraphSerializer` only | `memory/persistence.py` | DIP |

### Medium-term (Week 3)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| ISP-9 | Add type hints enforcing minimal interface at all call sites | All memory/ clients | DIP |
| ISP-10 | Document interface contracts in `AGENTS.md` | `AGENTS.md` | — |
| ISP-11 | Add ISP compliance tests: verify clients only depend on needed methods | `tests/` | — |

---

## 7. Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| `PTKG` public methods per client dependency | 20+ | ≤ 9 (via protocols) |
| Clients depending on full `PTKG` | 4 | 0 |
| `ConsciousAgent` always carries perception | Yes | No (optional) |
| `GraphRetriever` carries reputation methods | Yes | No (separated) |
| `SwarmOrchestrator` instantiates all infra upfront | Yes | No (lazy or injected) |
| Protocol definitions | 0 | 6+ |

---

*Generated from SOLID_COMPLIANCE_AUDIT.md — ISP Section*
