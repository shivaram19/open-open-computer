# ACN Agent Operating Principles

> **"Any measurement you make without the knowledge of uncertainty is meaningless."**
> — Walter Lewin

This principle governs all refactoring, testing, and architectural work in this codebase.

## Application

- **Before removing code:** Measure who calls it. Know the blast radius.
- **After every change:** Run the full test suite. Count pass/fail. Compare to baseline.
- **Before claiming safety:** State the uncertainty explicitly — flaky tests, untested paths, race conditions.
- **TDD discipline:** Write failing test → minimal green → refactor. No implementation without a failing test first.
- **No blind demolition:** Legacy code paths are removed only after verifying the replacement path is exercised by tests.

## Process Discipline

1. **At the start of every task block:** Query the todo list (`SetTodoList` with no args).
2. **Before declaring completion:** Update the todo list with accurate statuses.
3. **When context is compacted:** Re-query the todo list immediately after compaction to restore bearings.
4. **Never work without knowing the current item.**

## Current Phase Tracker

- Phase 4 COMPLETE: removed legacy backward-compatibility code. Reconstructed swarm_orchestrator.py after corruption. 917→927 tests passing.
- Phase 5 IN PROGRESS: P5-5 Autonomous Executor built — TaskDecomposer → SwarmOrchestrator → SandboxAgent pipeline operational.
- Baseline: 927 tests passing (established 2026-05-07).
