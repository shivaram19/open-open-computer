# Clean Code Audit

> **"Clean code is simple and direct. Clean code reads like well-written prose."**
> — Robert C. Martin, *Clean Code*, 2008
>
> **"The only valid measurement of code quality: WTFs/minute."**
> — Attributed to Robert C. Martin

**Scope:** ACN Repository (`acn/src/*`, `tests/`)
**Date:** 2026-05-07
**Test Baseline:** 883/883 passing
**Files Audited:** ~72 Python files, ~19,500 lines

---

## Table of Contents

1. [Clean Code Principles](#1-clean-code-principles)
2. [Naming Violations](#2-naming-violations)
3. [Function/Method Violations](#3-functionmethod-violations)
4. [Comment Violations](#4-comment-violations)
5. [Formatting & Style Violations](#5-formatting--style-violations)
6. [Error Handling Violations](#6-error-handling-violations)
7. [Magic Numbers & Constants](#7-magic-numbers--constants)
8. [Test Code Violations](#8-test-code-violations)
9. [Remediation Tasks](#9-remediation-tasks)
10. [Success Criteria](#10-success-criteria)

---

## 1. Clean Code Principles

Clean Code (Robert C. Martin, 2008) complements SOLID by addressing readability at the function and line level. The core principles:

| Principle | Rule | ACN Relevance |
|-----------|------|---------------|
| **Meaningful Names** | Names reveal intent | Mixed — some excellent, some generic |
| **Small Functions** | < 20 lines, does one thing | Violated — many 50+ line methods |
| **Single Level of Abstraction** | One concept per function | Violated — mixing high/low level |
| **DRY** | Don't repeat yourself | 80+ violations catalogued |
| **Comments** | Explain WHY, not WHAT | Over-commented in places |
| **Error Handling** | Use exceptions, not return codes | Generally OK |

---

## 2. Naming Violations

### 2.1 Generic Variable Names

| Location | Name | Problem | Better |
|----------|------|---------|--------|
| `swarm_orchestrator.py` | `a` (line 142) | Loop variable for agents | `agent` |
| `distributed_consensus.py` | `v` (line 155) | Vote variable | `vote` |
| `causal_chain.py` | `n` | Node in BFS | `current_node` |
| `graph_retrieval.py` | `r` | Reasoning result | `reasoning_trace` |

### 2.2 Inconsistent Naming Conventions

| Pattern | Example | Consistency |
|---------|---------|-------------|
| Private methods | `_store_episodic` vs `_calibrate_confidence` | Mix of verb-noun and verb-only |
| Boolean flags | `dissent_amplification_enabled` vs `feedback_enabled` | OK — consistent `-enabled` suffix |
| Counters | `tasks_completed` vs `citations_made` | OK — past participle pattern |

### 2.3 Abbreviations Without Context

| Abbreviation | Full Meaning | File |
|-------------|-------------|------|
| `PTKG` | Persistent Temporal Knowledge Graph | `memory/ptkg.py` |
| `HLC` | Hybrid Logical Clock | `consensus/hlc.py` |
| `CP-WBFT` | Credible Path Weighted Byzantine Fault Tolerance | `consensus/distributed_consensus.py` |
| `BFS` | Breadth-First Search | `memory/causal_chain.py` |

**Verdict:** Abbreviations are documented and consistent. Acceptable given domain complexity.

---

## 3. Function/Method Violations

### 3.1 Methods Exceeding 20 Lines

| Method | File | Lines | Concern |
|--------|------|-------|---------|
| `think()` | `conscious_agent.py` | ~90 | SRP + Clean Code violation |
| `think()` | `twin_agent.py` | ~80 | SRP + Clean Code violation |
| `activate_task()` | `swarm_orchestrator.py` | ~55 | Multiple responsibilities |
| `execute_round()` | `swarm_orchestrator.py` | ~70 | Multiple responsibilities |
| `execute_deliberation_round()` | `swarm_orchestrator.py` | ~120 | Severe violation |
| `audit_message()` | `temporal_auditor.py` | ~140 | Sequential rule checks |
| `stage1_probe_and_refine()` | `distributed_consensus.py` | ~70 | Complex algorithm |
| `stage2_weighted_aggregation()` | `distributed_consensus.py` | ~90 | Complex algorithm |
| `build_reasoning_context()` | `graph_retrieval.py` | ~65 | Multiple strategies |
| `find_causes()` | `causal_chain.py` | ~65 | Duplicated with `find_effects` |
| `find_effects()` | `causal_chain.py` | ~60 | Duplicated with `find_causes` |

### 3.2 Functions Doing More Than One Thing

**Evidence — `ConsciousAgent.think()`:**
```python
def think(self, context=None):
    # Thing 1: State transition
    self._transition_to(AgentState.ANALYZING)
    
    # Thing 2: Memory retrieval
    relevant_memories = self.memory.retrieve(...)
    recent_episodes = self.memory.retrieve(...)
    
    # Thing 3: Graph context building
    if self.graph_retriever is not None:
        graph_context = self.graph_retriever.build_reasoning_context(...)
    
    # Thing 4: Reasoning dict assembly
    reasoning = {...}
    
    # Thing 5: Self-evaluation
    reasoning["self_critique"] = self._self_critique(reasoning)
    
    # Thing 6: Awareness update
    current_state = CurrentState(...)
    self.awareness.record_state(current_state)
    
    # Thing 7: Memory storage
    self.reasoning_trace.append(reasoning)
    self.memory.store(MemoryTrace(...))
```

**Fix:** Extract helper methods:
```python
def think(self, context=None):
    self._transition_to(AgentState.ANALYZING)
    memories = self._gather_relevant_memories()
    reasoning = self._assemble_reasoning(memories, context)
    reasoning = self._evaluate_reasoning(reasoning)
    self._update_awareness(reasoning)
    self._store_reasoning(reasoning)
    return reasoning
```

### 3.3 Mixed Levels of Abstraction

**Evidence — `SwarmOrchestrator.execute_deliberation_round()`:**
```python
def execute_deliberation_round(self, task_id):
    # HIGH LEVEL: Task validation
    task = self.active_tasks.get(task_id)
    if not task:
        return {"error": f"Task {task_id} not found"}
    
    # HIGH LEVEL: Initialize argument map
    if self.deliberation_engine.argument_map is None:
        self.deliberation_engine.initialize_argument_map(task_id)
    
    # LOW LEVEL: Find active agents (filter implementation detail)
    active_agents = [a for a in self.agents.values() if a.current_goal and a.current_goal.parent_goal_id == task_id]
    
    # LOW LEVEL: Build proposal ID string
    proposal_id = f"proposal-{agent.agent_id}-r{len(self.deliberation_engine.round_history) + 1}"
```

**Fix:** Extract high-level orchestration and low-level details into separate methods.

---

## 4. Comment Violations

### 4.1 Redundant Comments

```python
# Line 227: "Record in memory"
self.memory.store(MemoryTrace(...))

# Line 148: "Initialize to current physical time"
self.hlc_clock.reset()
```

These comments state the obvious. The code already says what it does.

### 4.2 Commented-Out Code

**No instances found.** Good practice maintained.

### 4.3 Excessive Docstring Boilerplate

Every method has a `@cite` decorator with 6+ fields. While citation governance is important, the repetition creates noise:

```python
@cite(
    key="AGENT-THINK",
    paper="Conscious Agent: Reasoning Loop",
    venue="ACN Architecture Document",
    section="Agent Cognition",
    rationale="Explicit reasoning phases enable introspection and validation",
    confidence="CERTAIN",
)
def think(self, context=None):
    ...
```

**Recommendation:** Consider a class-level `@cite` that applies to all methods, with method-level overrides only when different.

### 4.4 Inline Comments for Workarounds

**Good examples found:**
```python
# estimated — should be dynamic
total_subtasks=10,

# up to 3 per cluster
for agent in cluster_agents[:3]:
```

These explain *why* a magic number exists. Positive pattern.

---

## 5. Formatting & Style Violations

### 5.1 Line Length

| File | Lines > 100 chars | Example |
|------|-------------------|---------|
| `swarm_orchestrator.py` | 12 | Long dict constructions |
| `distributed_consensus.py` | 8 | Long f-strings |
| `twin_agent.py` | 5 | Long import lines |

**Recommendation:** Enforce 100-character line limit via `flake8` or `ruff`.

### 5.2 Import Organization

**Good:** Imports are grouped (stdlib, third-party, local).
**Issue:** `from harness.awareness import CurrentState` appears inside `TwinAgent.think()` (line 142) rather than at module top. This is a local import anti-pattern that hides dependencies.

### 5.3 Blank Lines

**Good:** Consistent 2 blank lines between class definitions, 1 between methods.

---

## 6. Error Handling Violations

### 6.1 Silent Failures

```python
# graph_retrieval.py
if self.graph_retriever is not None:
    graph_context = self.graph_retriever.build_reasoning_context(...)
```

If `graph_retriever` is None, graph context is silently empty. Should this be an error for agents configured to use graph memory?

### 6.2 Generic Error Returns

```python
# conscious_agent.py
if not self.current_goal:
    return {"error": "No active goal. Agent must be activated first."}
```

Returning dicts with `"error"` keys is a C-style pattern. Better:
```python
if not self.current_goal:
    raise AgentNotActivatedError("Agent must be activated before thinking")
```

### 6.3 Missing Input Validation

```python
# distributed_consensus.py
all_ids = [v.agent_id for v in agent_votes]
neighbor_graph = {aid: [x for x in all_ids if x != aid] for aid in all_ids}
```

No validation that `agent_votes` is non-empty. Empty list would produce empty graph without error.

---

## 7. Magic Numbers & Constants

### 7.1 Uncatalogued Magic Numbers

| Value | Location | Meaning | Risk |
|-------|----------|---------|------|
| `0.5` | 15+ files | Default confidence / neutral reputation | Inconsistent — some use 0.5, some 0.7 |
| `0.67` | `swarm_orchestrator.py` | 2/3 consensus threshold | Should be configurable |
| `7` | `swarm_orchestrator.py` | Max deliberation rounds | Should be configurable |
| `0.85` | `swarm_orchestrator.py` | Semantic decay rate | Should be configurable |
| `3` | `conscious_agent.py` | Memory retrieve limit | Should be configurable |
| `10` | `conscious_agent.py`, `twin_agent.py` | Estimated total subtasks | Hardcoded "estimate" comment admits it's wrong |
| `0.7` | `conscious_agent.py` | Default base confidence | Duplicated in `Policy` dataclass |
| `1000` | `experience_buffer.py` | Buffer capacity | Should be configurable |
| `0.6` | `experience_buffer.py` | Priority alpha | Should be configurable |
| `0.2` | `policy_optimizer.py` | Max gradient norm | Should be configurable |

### 7.2 Duplicated Configuration

```python
# conscious_agent.py, line 181
base_confidence=0.7,

# policy_optimizer.py, line 42
base_confidence: float = 0.7
```

Same default in two places. Change one, forget the other.

**Fix:** Centralize in `acn/config.py`:
```python
class Config:
    DEFAULT_CONFIDENCE = 0.7
    CONSENSUS_THRESHOLD = 0.67
    MAX_DELIBERATION_ROUNDS = 7
    SEMANTIC_DECAY_RATE = 0.85
    DEFAULT_MEMORY_LIMIT = 3
    EXPERIENCE_BUFFER_CAPACITY = 1000
    PRIORITY_ALPHA = 0.6
    MAX_GRADIENT_NORM = 0.2
```

---

## 8. Test Code Violations

### 8.1 `sys.path.insert` Duplication

All 14 test files contain:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'acn', 'src'))
```

**Fix:** Create `tests/conftest.py` or `pytest.ini` with proper `pythonpath`.

### 8.2 Test File Naming Inconsistency

| Pattern | Count | Example |
|---------|-------|---------|
| `test_pN_*.py` | 6 | `test_p2_full_deliberation.py` |
| `test_*.py` | 8 | `test_twins.py` |

**Recommendation:** Standardize on `test_<module>_<feature>.py`.

### 8.3 Magic Numbers in Tests

```python
# test_conscious_agent.py (hypothetical)
assert agent.confidence == 0.7
```

Tests should reference `Config.DEFAULT_CONFIDENCE` rather than hardcoding.

---

## 9. Remediation Tasks

### Immediate (Week 1)

| # | Task | Files | Impact |
|---|------|-------|--------|
| CC-1 | Create `acn/config.py` with all magic numbers | New file | Eliminates 30+ magic numbers |
| CC-2 | Replace all `sys.path.insert` with `pytest.ini` / `conftest.py` | `tests/` | Eliminates 14× duplication |
| CC-3 | Extract `think()` into 5–7 focused helper methods | `agents/conscious_agent.py` | Improves readability |
| CC-4 | Extract `execute_deliberation_round()` into phases | `agents/swarm_orchestrator.py` | Improves readability |
| CC-5 | Remove obvious redundant comments | All files | Reduces noise |

### Short-term (Week 2)

| # | Task | Files | Impact |
|---|------|-------|--------|
| CC-6 | Enforce 100-character line limit via `ruff` | `pyproject.toml` | Consistency |
| CC-7 | Move inline imports to module top | `agents/twin_agent.py` | Clarity |
| CC-8 | Replace `"error"` dict returns with proper exceptions | `agents/*.py` | Better error handling |
| CC-9 | Add input validation for empty collections | `consensus/*.py` | Robustness |
| CC-10 | Standardize test file naming | `tests/` | Consistency |

### Medium-term (Week 3)

| # | Task | Files | Impact |
|---|------|-------|--------|
| CC-11 | Add `flake8` / `ruff` to CI pipeline | `.github/workflows/` | Automated enforcement |
| CC-12 | Add pre-commit hook for formatting | `.pre-commit-config.yaml` | Automated enforcement |
| CC-13 | Document Clean Code conventions in `AGENTS.md` | `AGENTS.md` | Team alignment |

---

## 10. Success Criteria

| Metric | Before | Target |
|--------|--------|--------|
| Methods > 50 lines | 11 | ≤ 3 |
| Magic numbers hardcoded | 30+ | 0 (all in `config.py`) |
| `sys.path.insert` in test files | 14 | 0 |
| Lines > 100 characters | ~25 | 0 |
| Inline imports | 1 | 0 |
| `"error"` dict returns | 3+ | 0 (use exceptions) |
| Missing input validations | 5+ | 0 |

---

*Generated from SOLID_COMPLIANCE_AUDIT.md — Clean Code Section*
