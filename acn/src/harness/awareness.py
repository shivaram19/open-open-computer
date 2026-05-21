# src/harness/awareness.py
"""
Awareness Subsystem for the Meta-Cognitive Harness.

This module provides continuous self-monitoring, direction tracking,
and metacognitive oversight. It is the "consciousness" of the harness —
not sentience, but operational self-awareness.

Principle: In God we trust. All others must bring data.

[CITATION: CITATIONS-GOVERNANCE]
Source: ACN Architecture Document, Awareness Subsystem
Rationale: A harness that cannot observe itself cannot correct itself.
"""

import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="AWARENESS-LEVEL",
    paper="Meta-Cognitive Harness: Awareness Subsystem",
    venue="ACN Architecture Document",
    section="Awareness Levels",
    rationale="Granularity levels for self-monitoring",
    confidence="CERTAIN",
)
class AwarenessLevel(Enum):
    """Granularity of self-monitoring."""
    SURFACE = "surface"
    DEEP = "deep"
    FULL = "full"


@cite(
    key="AWARENESS-ALERT",
    paper="Meta-Cognitive Harness: Awareness Subsystem",
    venue="ACN Architecture Document",
    section="Alert Severity",
    rationale="Standardized alert severity levels for harness health monitoring",
    confidence="CERTAIN",
)
class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class GoalState:
    """
    The desired outcome that the harness is working toward.
    
    [CITATION: CITATIONS-GOVERNANCE]
    Outcome-based thinking requires explicit goal representation.
    """
    goal_id: str
    description: str
    success_criteria: List[str]
    deadline: Optional[float] = None
    priority: int = 5
    created_at: float = field(default_factory=time.time)


@dataclass
class CurrentState:
    """
    The actual state of the harness at a point in time.
    
    [CITATION: CITATIONS-GOVERNANCE]
    Operational awareness requires continuous state capture.
    """
    task_id: str
    phase: str
    active_twins: List[str]
    completed_subtasks: int
    total_subtasks: int
    confidence: float
    resource_usage: Dict[str, float]
    timestamp: float = field(default_factory=time.time)


@dataclass
class DirectionVector:
    """
    Measures whether current actions lead toward or away from the goal.
    
    [CITATION: Heins2024]
    Active Inference: agents minimize expected free energy by aligning
    actions with preferred outcomes. DirectionVector quantifies this alignment.
    """
    goal_id: str
    alignment_score: float
    velocity: float
    drift_detected: bool
    drift_magnitude: float
    predicted_completion: Optional[float] = None
    timestamp: float = field(default_factory=time.time)


@cite(
    key="AWARENESS-CORE",
    paper="Meta-Cognitive Harness: Awareness Subsystem",
    venue="ACN Architecture Document",
    section="Awareness Subsystem",
    rationale="Continuous self-monitoring enables autonomous error detection and correction",
    confidence="CERTAIN",
)
class AwarenessSubsystem:
    """
    The consciousness of the harness.
    
    Continuously monitors:
    1. Goal state vs current state (the gap)
    2. Direction alignment (are we moving toward the goal?)
    3. Confidence calibration (do we trust our own reasoning?)
    4. Resource constraints (are we running out of compute/time/budget?)
    5. Risk assessment (what could go wrong?)
    6. Direction drift (have we been pulled off course?)
    
    Emits alerts when thresholds are breached.
    """

    def __init__(self, level: AwarenessLevel = AwarenessLevel.FULL):
        self.level = level
        self.goals: Dict[str, GoalState] = {}
        self.state_history: List[CurrentState] = []
        self.direction_history: List[DirectionVector] = []
        self.alerts: List[Dict[str, Any]] = []
        self.alert_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self._start_time = time.time()

    @cite(
        key="AWARENESS-GOAL",
        paper="Meta-Cognitive Harness: Awareness Subsystem",
        venue="ACN Architecture Document",
        section="Goal Tracking",
        rationale="Explicit goal representation prevents implicit drift",
        confidence="CERTAIN",
    )
    def set_goal(self, goal: GoalState) -> None:
        """Register a new goal for tracking."""
        self.goals[goal.goal_id] = goal
        self._emit_alert(
            severity=AlertSeverity.INFO,
            category="goal_set",
            message=f"Goal registered: {goal.description}",
            goal_id=goal.goal_id,
        )

    @cite(
        key="AWARENESS-STATE",
        paper="Meta-Cognitive Harness: Awareness Subsystem",
        venue="ACN Architecture Document",
        section="State Capture",
        rationale="Historical state enables drift detection and causal analysis",
        confidence="CERTAIN",
    )
    def record_state(self, state: CurrentState) -> None:
        """Record current harness state."""
        self.state_history.append(state)
        
        if self.level in (AwarenessLevel.DEEP, AwarenessLevel.FULL):
            self._check_confidence(state)
            self._check_resources(state)
        
        if self.level == AwarenessLevel.FULL:
            self._detect_drift(state)

    @cite(
        key="AWARENESS-DIRECTION",
        paper="Meta-Cognitive Harness: Awareness Subsystem",
        venue="ACN Architecture Document",
        section="Direction Tracking",
        rationale="Outcome-based thinking requires continuous alignment verification",
        confidence="CERTAIN",
    )
    def compute_direction(
        self,
        goal_id: str,
        current_state: CurrentState,
    ) -> DirectionVector:
        """
        Compute whether current actions align with goal.
        
        Uses progress velocity + confidence trend + subtask completion rate
        to estimate alignment. Negative alignment = moving away from goal.
        """
        goal = self.goals.get(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not registered")

        # Compute velocity: subtasks completed per unit time
        recent_states = [
            s for s in self.state_history
            if s.task_id == current_state.task_id
            and time.time() - s.timestamp < 300
        ]
        
        if len(recent_states) >= 2:
            dt = recent_states[-1].timestamp - recent_states[0].timestamp
            d_completed = (
                recent_states[-1].completed_subtasks
                - recent_states[0].completed_subtasks
            )
            velocity = d_completed / dt if dt > 0 else 0.0
        else:
            velocity = 0.0

        # Alignment: correlation between confidence and progress
        if current_state.total_subtasks > 0:
            progress = current_state.completed_subtasks / current_state.total_subtasks
        else:
            progress = 0.0
        
        alignment = (2 * progress - 1) * current_state.confidence

        # Drift detection: compare current trajectory to initial trajectory
        drift_detected = False
        drift_magnitude = 0.0
        
        if len(self.direction_history) >= 3:
            recent = self.direction_history[-3:]
            avg_alignment = sum(d.alignment_score for d in recent) / 3
            if avg_alignment < 0.3 and alignment < 0.3:
                drift_detected = True
                drift_magnitude = abs(avg_alignment - alignment)
                self._emit_alert(
                    severity=AlertSeverity.WARNING,
                    category="direction_drift",
                    message=f"Direction drift detected for goal {goal_id}",
                    goal_id=goal_id,
                )

        # Predict completion
        predicted = None
        if velocity > 0 and current_state.total_subtasks > current_state.completed_subtasks:
            remaining = current_state.total_subtasks - current_state.completed_subtasks
            seconds_remaining = remaining / velocity
            predicted = time.time() + seconds_remaining

        vector = DirectionVector(
            goal_id=goal_id,
            alignment_score=alignment,
            velocity=velocity,
            drift_detected=drift_detected,
            drift_magnitude=drift_magnitude,
            predicted_completion=predicted,
        )
        self.direction_history.append(vector)
        return vector

    def _check_confidence(self, state: CurrentState) -> None:
        """Alert if confidence is critically low or suspiciously high."""
        if state.confidence < 0.3:
            self._emit_alert(
                severity=AlertSeverity.CRITICAL,
                category="low_confidence",
                message=f"Critical confidence drop: {state.confidence:.2f} in phase {state.phase}",
                task_id=state.task_id,
            )
        elif state.confidence > 0.98 and state.completed_subtasks < state.total_subtasks * 0.5:
            self._emit_alert(
                severity=AlertSeverity.WARNING,
                category="overconfidence",
                message=f"Suspicious overconfidence: {state.confidence:.2f} with low completion",
                task_id=state.task_id,
            )

    def _check_resources(self, state: CurrentState) -> None:
        """Alert if resources are depleted."""
        usage = state.resource_usage
        if usage.get("api_calls", 0) > 1000:
            self._emit_alert(
                severity=AlertSeverity.WARNING,
                category="resource_depletion",
                message=f"High API usage: {usage['api_calls']} calls",
                task_id=state.task_id,
            )

    def _detect_drift(self, state: CurrentState) -> None:
        """Detect if harness has been pulled off course by sub-tasks."""
        phase_states = [s for s in self.state_history if s.phase == state.phase]
        if len(phase_states) > 10:
            time_in_phase = time.time() - phase_states[0].timestamp
            if time_in_phase > 600:
                self._emit_alert(
                    severity=AlertSeverity.WARNING,
                    category="phase_stuck",
                    message=f"Stuck in phase '{state.phase}' for {time_in_phase:.0f}s",
                    task_id=state.task_id,
                )

    def _emit_alert(self, severity: AlertSeverity, category: str, message: str, **kwargs) -> None:
        alert = {
            "severity": severity.value,
            "category": category,
            "message": message,
            "timestamp": time.time(),
            **kwargs,
        }
        self.alerts.append(alert)
        for handler in self.alert_handlers:
            handler(alert)

    @cite(
        key="AWARENESS-HANDLER",
        paper="Meta-Cognitive Harness: Awareness Subsystem",
        venue="ACN Architecture Document",
        section="Alert Handling",
        rationale="External handlers enable integration with monitoring systems",
        confidence="CERTAIN",
    )
    def register_alert_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback for alerts."""
        self.alert_handlers.append(handler)

    @cite(
        key="AWARENESS-REPORT",
        paper="Meta-Cognitive Harness: Awareness Subsystem",
        venue="ACN Architecture Document",
        section="Status Reporting",
        rationale="Self-awareness reports enable external monitoring and debugging",
        confidence="CERTAIN",
    )
    def get_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive self-awareness report."""
        return {
            "uptime_seconds": time.time() - self._start_time,
            "active_goals": len(self.goals),
            "total_states_recorded": len(self.state_history),
            "total_alerts": len(self.alerts),
            "alert_breakdown": self._alert_breakdown(),
            "current_directions": [
                asdict(d) for d in (self.direction_history[-5:] if self.direction_history else [])
            ],
            "health_score": self._compute_health_score(),
        }

    def _alert_breakdown(self) -> Dict[str, int]:
        breakdown = {"info": 0, "warning": 0, "critical": 0}
        for alert in self.alerts:
            breakdown[alert["severity"]] = breakdown.get(alert["severity"], 0) + 1
        return breakdown

    def _compute_health_score(self) -> float:
        """Overall harness health: 0.0 (dead) to 1.0 (perfect)."""
        if not self.alerts:
            return 1.0
        criticals = sum(1 for a in self.alerts if a["severity"] == "critical")
        warnings = sum(1 for a in self.alerts if a["severity"] == "warning")
        score = 1.0 - (criticals * 0.3 + warnings * 0.1)
        return max(0.0, score)
