# P0: Do Right Now (This Session)

**Rule:** Only 3–5 tasks. Nothing more. Finish these before opening any other file.

---

## ~~P0-1: Fix Citation Violations on New Harness Code~~ ✅ COMPLETE

**What:** `verify_citations.py --strict` found 9 uncited elements in awareness.py, memory/architecture.py, and li_fei_fei.py + 1 unregistered key.

**Why:** Citation governance is non-negotiable. Every class and function must cite its source.

**Done when:** `python acn/scripts/verify_citations.py --strict --registry-check` exits 0.

**Completed:** 2026-05-07. Also fixed `cite()` decorator class inheritance bug. All 60+ citations verified.

---

## ~~P0-2: Create 1 More Cognitive Twin Example~~ ✅ COMPLETE

**What:** Build a second cognitive twin (e.g., Noah Shinn for reflection, or Roger Wattenhofer for consensus) to prove the schema works across different cognitive styles.

**Why:** One twin could be a fluke. Two different styles prove the schema is general.

**Done when:** Twin has full cognitive model + generates distinct reasoning trace + passes style consistency test.

**Completed:** 2026-05-07. Li Fei-Fei (empirical, scale-first) + Noah Shinn (verbal RL, reflection) both operational.

---

## ~~P0-3: Write One Integration Test~~ ✅ COMPLETE

**What:** A single test that demonstrates: task → twin thinks → awareness tracks → memory stores → status report.

**Why:** Proves the subsystems actually connect. Not just isolated components.

**Done when:** `pytest tests/harness/test_integration.py` passes.

**Completed:** 2026-05-07. `test_integration.py` passes + `test_deerflow_enhanced_swarm.py` passes.

---

## ~~P0-4: Update Session Log~~ ✅ COMPLETE

**What:** Record what was done in this session in `tasks/SESSION-LOG.md`.

**Why:** Prevents re-reading everything next session. One-line summary per task.

**Done when:** SESSION-LOG.md has an entry for today.

**Completed:** 2026-05-07. SESSION-LOG.md updated with session entries.

---

✅ **ALL P0 TASKS COMPLETE** — Next: `P1-FOUNDATION.md`
