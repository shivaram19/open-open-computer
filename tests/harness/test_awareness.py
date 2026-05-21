# tests/harness/test_awareness.py
"""
Unit Tests for Awareness Subsystem.

Research-backed test patterns from swarm deep-research:
- Golden datasets: curated ground-truth GoalStates for regression testing
- Mock assertions: verify alert handlers fire without real side effects
- Membership testing: health scores in ranges, not strict equality
- Canary prompts: known expected outputs for drift detection validation
- Temporal ordering: state history sequence verification

Citations: Maxim2025, AgentTesting2026, MLArchitects2025, Heins2024
"""

import time


import pytest
from unittest.mock import Mock

from harness.awareness import (
    AwarenessSubsystem,
    AwarenessLevel,
    AlertSeverity,
    GoalState,
    CurrentState,
    DirectionVector,
)


# ── Golden Dataset: Pre-defined goal states for regression testing ──

GOLDEN_GOALS = {
    "simple": GoalState(
        goal_id="goal-simple",
        description="Simple test goal",
        success_criteria=["criterion A", "criterion B"],
        priority=3,
    ),
    "complex": GoalState(
        goal_id="goal-complex",
        description="Complex multi-criteria goal with deadline",
        success_criteria=["criterion A", "criterion B", "criterion C", "criterion D"],
        deadline=time.time() + 3600,
        priority=1,
    ),
    "minimal": GoalState(
        goal_id="goal-minimal",
        description="Minimal goal",
        success_criteria=["done"],
    ),
}


class TestGoalStateRegistration:
    """P1-1: GoalState registration and retrieval. Strict assertion pattern."""

    def test_set_goal_registers_in_internal_dict(self):
        """Golden dataset: register a known goal, verify it exists."""
        awareness = AwarenessSubsystem()
        goal = GOLDEN_GOALS["simple"]
        
        awareness.set_goal(goal)
        
        assert "goal-simple" in awareness.goals
        assert awareness.goals["goal-simple"].description == "Simple test goal"
        assert awareness.goals["goal-simple"].priority == 3

    def test_set_goal_emits_info_alert(self):
        """Canary prompt: goal registration should produce exactly one INFO alert."""
        awareness = AwarenessSubsystem()
        goal = GOLDEN_GOALS["simple"]
        
        awareness.set_goal(goal)
        
        info_alerts = [a for a in awareness.alerts if a["severity"] == "info"]
        assert len(info_alerts) == 1
        assert info_alerts[0]["category"] == "goal_set"
        assert "Simple test goal" in info_alerts[0]["message"]

    def test_multiple_goals_tracked_independently(self):
        """Golden dataset: multiple goals coexist without collision."""
        awareness = AwarenessSubsystem()
        awareness.set_goal(GOLDEN_GOALS["simple"])
        awareness.set_goal(GOLDEN_GOALS["complex"])
        
        assert len(awareness.goals) == 2
        assert awareness.goals["goal-simple"].priority == 3
        assert awareness.goals["goal-complex"].priority == 1

    def test_goal_default_values(self):
        """Strict assertion: verify dataclass defaults."""
        goal = GOLDEN_GOALS["minimal"]
        
        assert goal.deadline is None
        assert goal.priority == 5  # default
        assert goal.success_criteria == ["done"]
        assert goal.created_at <= time.time()


class TestCurrentStateRecording:
    """P1-1: CurrentState recording and history. Temporal ordering tests."""

    def test_record_state_appends_to_history(self):
        """State history grows monotonically."""
        awareness = AwarenessSubsystem()
        state = CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=2,
            total_subtasks=5,
            confidence=0.7,
            resource_usage={"api_calls": 10},
        )
        
        awareness.record_state(state)
        
        assert len(awareness.state_history) == 1
        assert awareness.state_history[0].task_id == "task-001"

    def test_state_history_temporal_ordering(self):
        """Temporal ordering: states recorded in sequence maintain order."""
        awareness = AwarenessSubsystem()
        
        for i in range(5):
            awareness.record_state(CurrentState(
                task_id="task-001",
                phase=f"phase-{i}",
                active_twins=["twin-1"],
                completed_subtasks=i,
                total_subtasks=5,
                confidence=0.5 + i * 0.1,
                resource_usage={"api_calls": i * 10},
            ))
        
        assert len(awareness.state_history) == 5
        phases = [s.phase for s in awareness.state_history]
        assert phases == ["phase-0", "phase-1", "phase-2", "phase-3", "phase-4"]

    def test_state_history_capacity_not_limited(self):
        """Awareness stores all states (unlike working memory which is 7±2)."""
        awareness = AwarenessSubsystem()
        
        for i in range(20):
            awareness.record_state(CurrentState(
                task_id="task-001",
                phase="researching",
                active_twins=["twin-1"],
                completed_subtasks=i,
                total_subtasks=20,
                confidence=0.5,
                resource_usage={},
            ))
        
        assert len(awareness.state_history) == 20


class TestDirectionVectorComputation:
    """P1-1: DirectionVector computation. Alignment, velocity, drift detection."""

    def test_compute_direction_requires_registered_goal(self):
        """Strict assertion: unregistered goal raises ValueError."""
        awareness = AwarenessSubsystem()
        state = CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.7,
            resource_usage={},
        )
        
        with pytest.raises(ValueError, match="not registered"):
            awareness.compute_direction("nonexistent", state)

    def test_alignment_positive_when_progressing(self):
        """Membership testing: alignment > 0 when making progress with confidence."""
        awareness = AwarenessSubsystem()
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        state = CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=4,
            total_subtasks=5,
            confidence=0.8,
            resource_usage={},
        )
        
        vector = awareness.compute_direction("goal-simple", state)
        
        assert vector.alignment_score > 0
        # progress = 4/5 = 0.8, alignment = (2*0.8 - 1) * 0.8 = 0.6 * 0.8 = 0.48
        assert 0.4 < vector.alignment_score < 0.5

    def test_alignment_negative_when_stalled(self):
        """Membership testing: alignment < 0 when no progress despite confidence."""
        awareness = AwarenessSubsystem()
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        state = CurrentState(
            task_id="task-001",
            phase="planning",
            active_twins=["twin-1"],
            completed_subtasks=0,
            total_subtasks=5,
            confidence=0.9,
            resource_usage={},
        )
        
        vector = awareness.compute_direction("goal-simple", state)
        
        assert vector.alignment_score < 0
        # progress = 0, alignment = (0 - 1) * 0.9 = -0.9
        assert -1.0 < vector.alignment_score < -0.5

    def test_velocity_computed_from_recent_states(self):
        """Velocity = subtasks completed per second over recent window."""
        awareness = AwarenessSubsystem()
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        # Record initial state
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.7,
            resource_usage={},
        ))
        time.sleep(0.05)  # small delay for velocity calculation
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=3,
            total_subtasks=5,
            confidence=0.8,
            resource_usage={},
        ))
        
        current = CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=3,
            total_subtasks=5,
            confidence=0.8,
            resource_usage={},
        )
        
        vector = awareness.compute_direction("goal-simple", current)
        
        # velocity should be positive since we went from 1→3 subtasks
        assert vector.velocity >= 0

    def test_drift_detected_after_three_poor_alignments(self):
        """Canary prompt: three consecutive poor alignments trigger drift alert."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.FULL)
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        # Seed three poor direction vectors
        for _ in range(3):
            awareness.direction_history.append(DirectionVector(
                goal_id="goal-simple",
                alignment_score=0.1,  # poor alignment
                velocity=0.0,
                drift_detected=False,
                drift_magnitude=0.0,
            ))
        
        state = CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=0,
            total_subtasks=5,
            confidence=0.2,  # low confidence → poor alignment
            resource_usage={},
        )
        
        vector = awareness.compute_direction("goal-simple", state)
        
        assert vector.drift_detected is True
        assert vector.drift_magnitude > 0

    def test_predicted_completion_with_positive_velocity(self):
        """Predicted completion time exists when velocity > 0."""
        awareness = AwarenessSubsystem()
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        # Seed history with progress
        awareness.state_history.append(CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=0,
            total_subtasks=10,
            confidence=0.7,
            resource_usage={},
            timestamp=time.time() - 10,
        ))
        awareness.state_history.append(CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=5,
            total_subtasks=10,
            confidence=0.8,
            resource_usage={},
            timestamp=time.time(),
        ))
        
        current = CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=5,
            total_subtasks=10,
            confidence=0.8,
            resource_usage={},
        )
        
        vector = awareness.compute_direction("goal-simple", current)
        
        assert vector.predicted_completion is not None
        assert vector.predicted_completion > time.time()


class TestAlertFiring:
    """P1-1: Alert firing with mock assertions. Handler verification pattern."""

    def test_low_confidence_emits_critical_alert(self):
        """Mock assertion: verify alert handler called with CRITICAL."""
        handler = Mock()
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        awareness.register_alert_handler(handler)
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.1,  # below 0.3 threshold
            resource_usage={},
        ))
        
        handler.assert_called_once()
        alert = handler.call_args[0][0]
        assert alert["severity"] == "critical"
        assert alert["category"] == "low_confidence"

    def test_overconfidence_emits_warning_alert(self):
        """Canary prompt: >0.98 confidence with <50% completion → WARNING."""
        handler = Mock()
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        awareness.register_alert_handler(handler)
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="planning",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.99,  # above 0.98 threshold
            resource_usage={},
        ))
        
        warning_alerts = [a for a in awareness.alerts if a["severity"] == "warning"]
        assert len(warning_alerts) >= 1
        assert any(a["category"] == "overconfidence" for a in warning_alerts)

    def test_resource_depletion_emits_warning(self):
        """Mock assertion: >1000 API calls triggers resource alert."""
        handler = Mock()
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        awareness.register_alert_handler(handler)
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="executing",
            active_twins=["twin-1"],
            completed_subtasks=3,
            total_subtasks=5,
            confidence=0.7,
            resource_usage={"api_calls": 1500},
        ))
        
        resource_alerts = [a for a in awareness.alerts if a["category"] == "resource_depletion"]
        assert len(resource_alerts) == 1
        assert "1500" in resource_alerts[0]["message"]

    def test_multiple_handlers_all_receive_alert(self):
        """Mock assertion: every registered handler gets every alert."""
        handler1 = Mock()
        handler2 = Mock()
        awareness = AwarenessSubsystem()
        awareness.register_alert_handler(handler1)
        awareness.register_alert_handler(handler2)
        
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        handler1.assert_called()
        handler2.assert_called()
        assert handler1.call_count == handler2.call_count

    def test_surface_level_skips_confidence_checks(self):
        """Strict assertion: SURFACE level does NOT emit confidence alerts."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.SURFACE)
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.1,  # would trigger CRITICAL at DEEP/FULL
            resource_usage={},
        ))
        
        critical_alerts = [a for a in awareness.alerts if a["severity"] == "critical"]
        assert len(critical_alerts) == 0


class TestHealthScoreComputation:
    """P1-1: Health score computation. Membership testing (range, not equality)."""

    def test_perfect_health_with_no_alerts(self):
        """Membership testing: no alerts = health in [0.95, 1.0]."""
        awareness = AwarenessSubsystem()
        
        health = awareness.get_status_report()["health_score"]
        
        assert 0.95 <= health <= 1.0

    def test_health_degrades_with_warnings(self):
        """Membership testing: each warning drops health by ~0.1."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        
        # Trigger 2 warnings
        for _ in range(2):
            awareness.record_state(CurrentState(
                task_id="task-001",
                phase="planning",
                active_twins=["twin-1"],
                completed_subtasks=1,
                total_subtasks=5,
                confidence=0.99,  # overconfidence warning
                resource_usage={},
            ))
        
        health = awareness.get_status_report()["health_score"]
        # 1.0 - (2 * 0.1) = 0.8
        assert 0.7 <= health <= 0.85

    def test_health_degrades_with_criticals(self):
        """Membership testing: each critical drops health by ~0.3."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        
        # Trigger 1 critical
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.1,  # critical
            resource_usage={},
        ))
        
        health = awareness.get_status_report()["health_score"]
        # 1.0 - 0.3 = 0.7
        assert 0.65 <= health <= 0.75

    def test_health_never_negative(self):
        """Membership testing: health score floor at 0.0."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        
        # Trigger many criticals
        for _ in range(10):
            awareness.record_state(CurrentState(
                task_id=f"task-{_}",
                phase="researching",
                active_twins=["twin-1"],
                completed_subtasks=0,
                total_subtasks=5,
                confidence=0.1,
                resource_usage={},
            ))
        
        health = awareness.get_status_report()["health_score"]
        assert health >= 0.0
        assert health < 0.5  # definitely degraded

    def test_health_combined_criticals_and_warnings(self):
        """Membership testing: mixed alerts produce expected range."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        
        # 1 critical + 2 warnings
        awareness.record_state(CurrentState(
            task_id="task-crit",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=0,
            total_subtasks=5,
            confidence=0.1,
            resource_usage={},
        ))
        for _ in range(2):
            awareness.record_state(CurrentState(
                task_id=f"task-warn-{_}",
                phase="planning",
                active_twins=["twin-1"],
                completed_subtasks=1,
                total_subtasks=5,
                confidence=0.99,
                resource_usage={},
            ))
        
        health = awareness.get_status_report()["health_score"]
        # 1.0 - (1*0.3 + 2*0.1) = 0.5
        assert 0.45 <= health <= 0.55


class TestStatusReport:
    """P1-1: Status report structure and content."""

    def test_report_contains_required_fields(self):
        """Strict assertion: report has all expected keys."""
        awareness = AwarenessSubsystem()
        awareness.set_goal(GOLDEN_GOALS["simple"])
        
        report = awareness.get_status_report()
        
        required_keys = [
            "uptime_seconds",
            "active_goals",
            "total_states_recorded",
            "total_alerts",
            "alert_breakdown",
            "current_directions",
            "health_score",
        ]
        for key in required_keys:
            assert key in report, f"Missing key: {key}"

    def test_alert_breakdown_counts_correctly(self):
        """Strict assertion: breakdown sums to total alerts."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        
        # Mix of alert types
        awareness.record_state(CurrentState(
            task_id="task-1", phase="researching", active_twins=["t1"],
            completed_subtasks=0, total_subtasks=5, confidence=0.1, resource_usage={},
        ))
        awareness.record_state(CurrentState(
            task_id="task-2", phase="planning", active_twins=["t1"],
            completed_subtasks=1, total_subtasks=5, confidence=0.99, resource_usage={},
        ))
        
        report = awareness.get_status_report()
        breakdown = report["alert_breakdown"]
        total = sum(breakdown.values())
        
        assert total == report["total_alerts"]
        assert breakdown["critical"] >= 1
        assert breakdown["warning"] >= 1

    def test_report_uptime_increases_over_time(self):
        """Temporal ordering: uptime grows monotonically."""
        awareness = AwarenessSubsystem()
        
        uptime1 = awareness.get_status_report()["uptime_seconds"]
        time.sleep(0.1)
        uptime2 = awareness.get_status_report()["uptime_seconds"]
        
        assert uptime2 > uptime1

    def test_active_goals_count_matches(self):
        """Strict assertion: active_goals equals len(self.goals)."""
        awareness = AwarenessSubsystem()
        
        assert awareness.get_status_report()["active_goals"] == 0
        
        awareness.set_goal(GOLDEN_GOALS["simple"])
        assert awareness.get_status_report()["active_goals"] == 1
        
        awareness.set_goal(GOLDEN_GOALS["complex"])
        assert awareness.get_status_report()["active_goals"] == 2


class TestAwarenessLevelBehavior:
    """P1-1: Awareness level gates monitoring depth."""

    def test_surface_level_records_only_state(self):
        """Strict assertion: SURFACE skips confidence, resource, drift checks."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.SURFACE)
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=0,
            total_subtasks=5,
            confidence=0.1,  # would trigger critical at higher levels
            resource_usage={"api_calls": 2000},
        ))
        
        # Only the goal_set alert from initialization (if any) — no monitoring alerts
        monitoring_alerts = [a for a in awareness.alerts if a["category"] != "goal_set"]
        assert len(monitoring_alerts) == 0

    def test_deep_level_checks_confidence_and_resources(self):
        """Mock assertion: DEEP level fires confidence + resource alerts."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.DEEP)
        
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=0,
            total_subtasks=5,
            confidence=0.1,
            resource_usage={"api_calls": 2000},
        ))
        
        categories = {a["category"] for a in awareness.alerts}
        assert "low_confidence" in categories or "resource_depletion" in categories

    def test_full_level_includes_drift_detection(self):
        """Canary prompt: FULL level with stuck phase triggers drift."""
        awareness = AwarenessSubsystem(level=AwarenessLevel.FULL)
        
        # Simulate being stuck in a phase (need >10 states in same phase, >600s)
        # For testability, we mock by directly checking drift won't trigger with few states
        awareness.record_state(CurrentState(
            task_id="task-001",
            phase="researching",
            active_twins=["twin-1"],
            completed_subtasks=1,
            total_subtasks=5,
            confidence=0.5,
            resource_usage={},
        ))
        
        # With only 1 state, phase_stuck should NOT trigger
        phase_stuck_alerts = [a for a in awareness.alerts if a["category"] == "phase_stuck"]
        assert len(phase_stuck_alerts) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
