#!/usr/bin/env python3
"""
Project State Awareness: The harness observing itself.

Uses the AwarenessSubsystem to track project progress, detect drift
from the original plan, and report health.

Principle: A conscious system must observe its own state.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from harness.awareness import (
    AwarenessSubsystem,
    AwarenessLevel,
    GoalState,
    CurrentState,
)
from tools.date_tool import DateTool


# ── Task Registry ──────────────────────────────────────────────────

TASK_REGISTRY = {
    "P0": {"total": 4, "file": "tasks/P0-IMMEDIATE.md"},
    "P1": {"total": 6, "file": "tasks/P1-FOUNDATION.md"},
    "P2": {"total": 3, "file": "tasks/P2-COGNITIVE-TWINS.md"},
    "P3": {"total": 7, "file": "tasks/P3-HARNESS-LAYERS.md"},
    "P4": {"total": 6, "file": "tasks/P4-ADRS.md"},
    "P5": {"total": 4, "file": "tasks/P5-OUTPUT-SYSTEMS.md"},
    "P6": {"total": 10, "file": "tasks/P6-RESEARCH-GAPS.md"},
}


def scan_task_file(filepath: Path) -> Dict[str, Any]:
    """Scan a task file for completed and pending items."""
    content = filepath.read_text()
    
    # Count checkboxes
    completed = len(re.findall(r'- \[x\]', content)) + len(re.findall(r'- \[X\]', content))
    pending = len(re.findall(r'- \[ \]', content))
    total = completed + pending
    
    # Check for section-level completion markers
    section_complete = len(re.findall(r'~~.*~~ ✅ COMPLETE', content))
    
    # Extract task names
    task_names = re.findall(r'## ([^\n]+)', content)
    
    return {
        "completed": completed,
        "pending": pending,
        "total": total,
        "sections_complete": section_complete,
        "task_names": task_names,
    }


def build_project_state(project_root: Path) -> Dict[str, Any]:
    """Build comprehensive project state from task files."""
    state = {
        "date": DateTool.get().date,
        "year": DateTool.get().year,
        "layers": {},
        "totals": {"completed": 0, "pending": 0, "total": 0},
        "tests": {},
        "code_metrics": {},
    }
    
    # Scan each task layer
    for layer, info in TASK_REGISTRY.items():
        filepath = project_root / info["file"]
        if filepath.exists():
            layer_state = scan_task_file(filepath)
            state["layers"][layer] = layer_state
            state["totals"]["completed"] += layer_state["completed"]
            state["totals"]["pending"] += layer_state["pending"]
            state["totals"]["total"] += layer_state["total"]
    
    # Count test files and tests
    test_dir = project_root / "tests"
    if test_dir.exists():
        test_files = list(test_dir.rglob("test_*.py"))
        state["tests"]["test_files"] = len(test_files)
        # Count test functions
        total_tests = 0
        for tf in test_files:
            content = tf.read_text()
            total_tests += len(re.findall(r'    def test_', content))
        state["tests"]["test_functions"] = total_tests
    
    # Count source files
    src_dir = project_root / "acn" / "src"
    if src_dir.exists():
        py_files = list(src_dir.rglob("*.py"))
        state["code_metrics"]["source_files"] = len(py_files)
        total_lines = sum(len(f.read_text().splitlines()) for f in py_files)
        state["code_metrics"]["total_lines"] = total_lines
    
    # Citation status
    citation_registry = project_root / "acn" / "docs" / "research" / "citation_registry.json"
    if citation_registry.exists():
        import json
        registry = json.loads(citation_registry.read_text())
        state["citations"] = len(registry.get("citations", {}))
    
    return state


def track_with_awareness(state: Dict[str, Any]) -> Dict[str, Any]:
    """Feed project state into AwarenessSubsystem for meta-cognitive tracking."""
    awareness = AwarenessSubsystem(level=AwarenessLevel.FULL)
    
    # Register project goal
    project_goal = GoalState(
        goal_id="acn-project",
        description="Build Autonomous Cognitive Network: meta-cognitive harness with conscious agent swarm",
        success_criteria=[
            "P0 complete (4/4)",
            "P1 complete (6/6)",
            "P2 complete (3/3)",
            "P3 complete (7/7)",
            "All ADRs approved",
            "Citation governance enforced",
            "Integration tests pass",
        ],
    )
    awareness.set_goal(project_goal)
    
    # Record current project state
    totals = state["totals"]
    progress = totals["completed"] / max(totals["total"], 1)
    
    current = CurrentState(
        task_id="acn-project",
        phase="P1-execution",
        active_twins=list(state["layers"].keys()),
        completed_subtasks=totals["completed"],
        total_subtasks=totals["total"],
        confidence=0.85 if state["tests"]["test_functions"] > 50 else 0.6,
        resource_usage={
            "test_files": state["tests"].get("test_files", 0),
            "source_files": state["code_metrics"].get("source_files", 0),
            "citations": state.get("citations", 0),
        },
    )
    awareness.record_state(current)
    
    # Compute direction
    direction = awareness.compute_direction("acn-project", current)
    
    # Get full report
    report = awareness.get_status_report()
    report["project_progress"] = progress
    report["direction"] = {
        "alignment_score": direction.alignment_score,
        "velocity": direction.velocity,
        "drift_detected": direction.drift_detected,
        "drift_magnitude": direction.drift_magnitude,
    }
    
    return report


def detect_drift(state: Dict[str, Any]) -> List[str]:
    """Detect if project has drifted from intended plan."""
    drift_signals = []
    
    # P0 should be 100% complete before P1 work
    p0 = state["layers"].get("P0", {})
    if p0.get("completed", 0) < p0.get("total", 4):
        drift_signals.append("P0 incomplete but work proceeding on later layers")
    
    # Tests should exist for every major subsystem
    if state["tests"].get("test_functions", 0) < 20:
        drift_signals.append("Insufficient test coverage (<20 tests)")
    
    # Citations should be maintained
    if state.get("citations", 0) < 50:
        drift_signals.append("Citation registry below threshold (<50)")
    
    # P1-1 and P1-2 should be done before P1-6
    p1 = state["layers"].get("P1", {})
    if p1.get("completed", 0) < 2 and "P1-6" in str(state):
        drift_signals.append("P1-6 started before P1-1/P1-2 complete")
    
    return drift_signals


def print_project_dashboard(state: Dict[str, Any], report: Dict[str, Any]) -> None:
    """Print formatted project state dashboard."""
    print("╔" + "═" * 68 + "╗")
    print("║" + " PROJECT STATE AWARENESS DASHBOARD ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print(f"📅 Date: {state['date']} | Year: {state['year']}")
    print()
    
    # Progress bar
    totals = state["totals"]
    pct = (totals["completed"] / max(totals["total"], 1)) * 100
    bar_width = 40
    filled = int(bar_width * pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"Progress: [{bar}] {pct:.1f}%")
    print(f"          {totals['completed']} done / {totals['pending']} pending / {totals['total']} total")
    print()
    
    # Layer breakdown
    print("Layer Breakdown:")
    for layer, info in state["layers"].items():
        pct_layer = (info["completed"] / max(info["total"], 1)) * 100
        status = "✅" if pct_layer >= 100 else "🔄" if pct_layer > 0 else "⏳"
        print(f"  {status} {layer}: {info['completed']}/{info['total']} ({pct_layer:.0f}%)")
    print()
    
    # Code metrics
    print(f"Codebase: {state['code_metrics'].get('source_files', 0)} files, {state['code_metrics'].get('total_lines', 0):,} lines")
    print(f"Tests:    {state['tests'].get('test_files', 0)} files, {state['tests'].get('test_functions', 0)} test functions")
    print(f"Citations: {state.get('citations', 0)} registered")
    print()
    
    # Health and direction
    print(f"Health Score: {report['health_score']:.2f}")
    print(f"Active Goals: {report['active_goals']}")
    print(f"States Recorded: {report['total_states_recorded']}")
    print(f"Total Alerts: {report['total_alerts']}")
    print()
    
    dir_info = report["direction"]
    print("Direction Vector:")
    print(f"  Alignment:    {dir_info['alignment_score']:+.3f}")
    print(f"  Velocity:     {dir_info['velocity']:.4f}")
    print(f"  Drift:        {'⚠️ YES' if dir_info['drift_detected'] else '✅ None'} (magnitude: {dir_info['drift_magnitude']:.3f})")
    print()
    
    # Drift detection
    drift_signals = detect_drift(state)
    if drift_signals:
        print("Drift Signals:")
        for signal in drift_signals:
            print(f"  ⚠️  {signal}")
    else:
        print("Drift Signals: ✅ None detected")
    print()
    
    print("═" * 70)


def main():
    project_root = Path(__file__).parent.parent.parent
    
    print("Building project state from task files...")
    state = build_project_state(project_root)
    
    print("Tracking with AwarenessSubsystem...")
    report = track_with_awareness(state)
    
    print_project_dashboard(state, report)
    
    return state, report


if __name__ == "__main__":
    main()
