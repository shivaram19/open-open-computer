# LSP Audit — Liskov Substitution Principle

> **"If for each object o1 of type S there is an object o2 of type T such that for all programs P defined in terms of T, the behavior of P is unchanged when o1 is substituted for o2, then S is a subtype of T."**
> — Barbara Liskov, *Data Abstraction and Hierarchy*, 1987
>
> **"Functions that use pointers or references to base classes must be able to use objects of derived classes without knowing it."**
> — Robert C. Martin, *Design Principles and Design Patterns*, 2000

**Scope:** ACN Repository (`acn/src/*`)
**Date:** 2026-05-07
**Test Baseline:** 883/883 passing

---

## Table of Contents

1. [Why LSP Exists](#1-why-lsp-exists)
2. [Design by Contract](#2-design-by-contract)
3. [Detection Methodology](#3-detection-methodology)
4. [Critical Violations](#4-critical-violations)
5. [High Violations](#5-high-violations)
6. [Remediation Tasks](#6-remediation-tasks)
7. [Success Criteria](#7-success-criteria)

---

## 1. Why LSP Exists

### Historical Origin

Barbara Liskov introduced the substitution principle in her 1987 conference keynote *"Data Abstraction and Hierarchy"* at the Conference on Object-Oriented Programming. She was designing **CLU**, the first programming language built on structured modules rather than GOTO statements. CLU introduced **data abstraction** — the idea that a type should hide its internal representation and expose only operations.

Liskov realized that naive inheritance breaks the mathematical contracts that type systems rely on. The famous **Square-Rectangle problem** illustrates this:

```python
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # Breaks Rectangle contract!
```

A client expecting `Rectangle` behavior (independent width/height) gets broken behavior when passed a `Square`. LSP prevents this by requiring subtypes to honor the **contract** of their supertypes.

### The Core Problem LSP Solves

**Broken polymorphism.** Inheritance is not just code reuse — it is a **semantic contract**. When a subtype violates that contract, code that works with the base type fails silently or catastrophically when the subtype is substituted.

> *"The Liskov substitution principle is the most technical principle of all. However, it is the one that most helps to develop decoupled applications, which is the foundation of designing reusable components."*

### LSP in the ACN Context

`TwinAgent` inherits from `ConsciousAgent` but overrides `think()` with completely different behavior. A swarm orchestrator that passes `TwinAgent` objects to methods expecting `ConsciousAgent` behavior may get surprising results. More critically, the 39 cognitive twins have no common base class at all — polymorphism is impossible.

---

## 2. Design by Contract

Bertrand Meyer's **Design by Contract (DbC)** provides the formal framework for LSP. Every method has:

| Contract Element | Definition | Subtype Rule |
|-----------------|-----------|------------|
| **Preconditions** | What the method requires to be true on entry | Cannot be **strengthened** (subtype must accept same or weaker input) |
| **Postconditions** | What the method guarantees on exit | Cannot be **weakened** (subtype must provide same or stronger output) |
| **Invariants** | Properties that remain true throughout object's lifetime | Must be **preserved** |

### ACN Contract Analysis

#### `ConsciousAgent.think()` Contract

| Element | Base Class Guarantee |
|---------|---------------------|
| Precondition | `self.current_goal is not None` |
| Postcondition | Returns `Dict[str, Any]` with keys: `agent_id`, `agent_name`, `goal`, `phase`, `timestamp`, `situation_assessment`, `proposed_approach`, `confidence`, `risks`, `self_critique` |
| Side effects | Transitions state to `EVALUATING`, stores reasoning in memory, updates awareness |

#### `TwinAgent.think()` Violations

| Contract Element | Violation |
|-----------------|-----------|
| Precondition | Same (`current_goal` check) — OK |
| Postcondition | Returns additional keys (`twin_reasoning`, `twin_id`, `twin_name`, `peer_critiques`, `heuristics_invoked`, `biases_acknowledged`) — **strengthened** (OK per LSP) |
| Side effects | Does NOT call parent's memory-storage logic. Re-implements `CurrentState` construction. — **behavioral inconsistency** |

The postcondition strengthening is acceptable (LSP allows subtypes to return *more*). But the behavioral inconsistency is not: `TwinAgent.think()` does not perform the same side effects as `ConsciousAgent.think()` (memory trace storage pattern differs).

---

## 3. Detection Methodology

| Heuristic | Threshold | Rationale |
|-----------|-----------|-----------|
| Subclass overrides parent method without calling `super()` | Any | Risk of contract violation |
| Subclass changes return type shape significantly | Any | Postcondition weakening |
| Subclass throws exceptions parent does not throw | Any | Contract violation |
| Subclass strengthens preconditions | Any | Client code breaks |
| No common base class where polymorphism is needed | Any | LSP cannot be satisfied |
| `isinstance()` checks defeating polymorphism | Any | Signals broken hierarchy |

---

## 4. Critical Violations

### 4.1 `TwinAgent.think()` breaks `ConsciousAgent` contract (`agents/twin_agent.py`, lines 93–170)

**The inheritance relationship:**
```python
class TwinAgent(ConsciousAgent):
    def think(self, context=None) -> Dict[str, Any]:
        # Does NOT call super().think()
        # Re-implements memory storage
        # Re-implements CurrentState construction
        # Returns different dict shape
```

**Specific violations:**

1. **No `super()` call:** `TwinAgent.think()` completely replaces the parent's cognitive loop instead of augmenting it. This means any bug fix or enhancement to `ConsciousAgent.think()` must be manually mirrored in `TwinAgent.think()`.

2. **Re-implemented memory storage (lines ~155–170):**
```python
# TwinAgent manually stores reasoning:
self.reasoning_trace.append(reasoning)
self.memory.store(MemoryTrace(
    trace_id=f"twin-reasoning-{self.agent_id}-{time.time()}",
    memory_type=MemoryType.EPISODIC,
    content=reasoning,
    # ... slightly different from ConsciousAgent's storage
))
```

3. **Re-implemented `CurrentState` construction (lines ~142–150):**
```python
from harness.awareness import CurrentState
current_state = CurrentState(
    task_id=self.current_goal.goal_id,
    phase=self.state.value,
    active_twins=[self.agent_id],
    completed_subtasks=len(self.reasoning_trace),
    total_subtasks=10,
    confidence=confidence,
    resource_usage={"api_calls": 0, "tokens": 0, "memory_mb": 0},
)
```
This is identical to `ConsciousAgent.think()` lines 313–321 — duplicated because `TwinAgent` doesn't call `super()`.

**Root cause:** `TwinAgent` uses **inheritance for code reuse** rather than **composition for behavior variation**. The twin should be a strategy plugged into the agent, not a different kind of agent.

**Fix — Composition over Inheritance:**
```python
# NEW: agents/reasoning_strategy.py
from typing import Protocol, Dict, Any

class ReasoningStrategy(Protocol):
    def think(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]: ...
    def get_signature(self) -> Dict[str, Any]: ...

# ConsciousAgent delegates to strategy:
class ConsciousAgent:
    def __init__(self, ..., reasoning_strategy: Optional[ReasoningStrategy] = None):
        self._reasoning_strategy = reasoning_strategy
    
    def think(self, context=None):
        # Core loop ALWAYS runs
        reasoning = self._execute_think_loop(context)
        
        # If strategy present, augment reasoning
        if self._reasoning_strategy:
            twin_reasoning = self._reasoning_strategy.think(
                self.current_goal.description, context
            )
            reasoning["twin_reasoning"] = twin_reasoning
            reasoning["twin_signature"] = self._reasoning_strategy.get_signature()
        
        return reasoning

# TwinAgent becomes a thin wrapper:
class TwinAgent(ConsciousAgent):
    def __init__(self, ..., twin_module_path: str, twin_class_name: str):
        twin = self._load_twin(twin_module_path, twin_class_name)
        super().__init__(..., reasoning_strategy=twin)
```

This way:
- `TwinAgent` IS-A `ConsciousAgent` (inheritance preserved)
- `TwinAgent.think()` does not override `think()` at all
- The parent's full cognitive loop runs unchanged
- Twin reasoning is injected as augmentation

---

### 4.2 39 cognitive twins have NO common base class (`twins/cognitive_models/*.py`)

**The problem:**
```python
# li_fei_fei.py
class LiFeiFeiTwin:
    def think(self, task, context): ...
    def get_cognitive_signature(self): ...

# noah_shinn.py
class NoahShinnTwin:
    def think(self, task, context): ...
    def get_cognitive_signature(self): ...

# No shared base. No protocol. No ABC.
```

**Impact:**
1. **No polymorphism:** A harness cannot write `for twin in twins: twin.think()` without importing 39 concrete classes.
2. **No contract enforcement:** A twin developer might forget `get_cognitive_signature()`, breaking consumers at runtime.
3. **No default behavior:** Every twin re-implements generic phase methods (`_express_skepticism`, `_recommend`) that are identical across files.

**Fix:**
```python
# NEW: twins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class CognitiveTwin(ABC):
    """Abstract base class for all cognitive twins."""
    
    TWIN_ID: str = ""
    NAME: str = ""
    CLUSTER: str = ""
    EPISTEMOLOGY: str = ""
    REASONING_DIRECTION: str = ""
    PRIMARY_METHOD: str = ""
    
    HEURISTICS: Dict[str, str] = {}
    BIASES: Dict[str, str] = {}
    
    @abstractmethod
    def think(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate reasoning for the given task."""
        ...
    
    def get_cognitive_signature(self) -> Dict[str, Any]:
        """Default implementation — subclasses override only if needed."""
        return {
            "twin_id": self.TWIN_ID,
            "name": self.NAME,
            "cluster": self.CLUSTER,
            "epistemic_engine": self.EPISTEMOLOGY,
            "methodological_signature": self.PRIMARY_METHOD,
            "heuristics": self.HEURISTICS,
            "biases": self.BIASES,
        }
    
    # Default phase fallbacks — subclasses override only researcher-specific phases
    def _express_skepticism(self, task: str) -> str:
        return f"Skeptical evaluation of {task}: verify assumptions."
    
    def _recommend(self, task: str) -> str:
        return f"Recommend systematic approach for {task}."
```

**Migration:**
```python
# Before: li_fei_fei.py (180 lines)
class LiFeiFeiTwin:
    # 180 lines of boilerplate + 2 unique methods

# After: li_fei_fei.py (25 lines)
from twins.base import CognitiveTwin

class LiFeiFeiTwin(CognitiveTwin):
    TWIN_ID = "li-fei-fei"
    NAME = "Li Fei-Fei"
    CLUSTER = "video-understanding"
    EPISTEMOLOGY = "Empirical"
    REASONING_DIRECTION = "Bottom-up"
    PRIMARY_METHOD = "Large-scale visual recognition"
    
    HEURISTICS = {
        "dataset_bias_mitigation": "Actively seek diverse data",
        "visual_semantic_alignment": "Map pixels to meaning",
    }
    
    BIASES = {
        "scale_preference": "Favor large-scale solutions",
        "visual_dominance": "Prioritize visual over textual cues",
    }
    
    def think(self, task, context=None):
        return {
            "phase_1": self._identify_problem(task),
            "phase_2": self._assess_data_needs(task, context),
            # ... etc
            "phase_6": self._recommend(task),
        }
    
    def _identify_problem(self, task):
        return f"Li Fei-Fei identifies visual recognition challenge in: {task}"
    
    # Only researcher-specific phases are overridden
    # Generic fallbacks inherited from CognitiveTwin
```

---

## 5. High Violations

### 5.1 `TwinAgent._transition_to()` may not handle all `AgentState` values

`ConsciousAgent` defines 8 states. `TwinAgent` does not override `_transition_to()`, so it inherits the parent's implementation. This is actually correct per LSP. However, `TwinAgent` introduces twin-specific behavior (loading twin heuristics) that is not triggered on certain state transitions.

**Minor concern:** Not a strict LSP violation, but a behavioral gap.

---

## 6. Remediation Tasks

### Immediate (Week 1)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| LSP-1 | Create `CognitiveTwin` ABC with `think()`, `get_cognitive_signature()`, default phase fallbacks | `twins/base.py` (new) | DIP, OCP, ISP, SRP |
| LSP-2 | Create `ReasoningStrategy` protocol | `agents/reasoning_strategy.py` (new) | DIP, SRP |
| LSP-3 | Refactor `TwinAgent` to use composition: inject twin as `ReasoningStrategy`, remove `think()` override | `agents/twin_agent.py` | SRP, DIP |

### Short-term (Week 2)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| LSP-4 | Migrate 39 twin files to inherit from `CognitiveTwin` | `twins/cognitive_models/*.py` | OCP, ISP, SRP |
| LSP-5 | Add type hints enforcing `CognitiveTwin` protocol at all call sites | `agents/twin_agent.py`, harness files | DIP |
| LSP-6 | Add LSP contract tests: verify `TwinAgent` can substitute for `ConsciousAgent` | `tests/` | — |

### Medium-term (Week 3)

| # | Task | Files | SOLID Partners |
|---|------|-------|---------------|
| LSP-7 | Delete committed generated twin code OR generate at build time | `twins/` | DRY |
| LSP-8 | Add `@abstractmethod` enforcement for twin phases that must be implemented | `twins/base.py` | ISP |
| LSP-9 | Document LSP compliance requirements in `AGENTS.md` | `AGENTS.md` | — |

---

## 7. Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| `TwinAgent.think()` overrides parent | Yes | No (delegates to `super()`) |
| Cognitive twins with common base class | 0 / 39 | 39 / 39 |
| Twins that can be used polymorphically | 0 | 39 |
| `isinstance` checks for twin types | Scattered | 0 (use protocol) |
| LSP contract tests | 0 | ≥ 3 |
| Lines per twin file (average) | ~180 | ~25 |

---

*Generated from SOLID_COMPLIANCE_AUDIT.md — LSP Section*
