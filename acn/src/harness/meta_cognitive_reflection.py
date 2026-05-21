# src/harness/meta_cognitive_reflection.py
"""
Meta-Cognitive Reflection Engine: Svādhyāya (Self-Study).

Analyzes reasoning traces and experiences to extract actionable insights.
Inspired by:
- Shinn2023: Reflexion — verbal reinforcement learning through self-reflection
- Yao2023: ReAct — reasoning and acting with language models
- Schmidhuber1991: Meta-learning — learning to learn

Principle: Svādhyāya is not mere introspection but disciplined self-study
that produces concrete behavioral adjustments. Reflection without action
is philosophy; reflection with action is growth.

[CITATION: Shinn2023]
[CITATION: Yao2023]
[CITATION: Schmidhuber1991]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite


@cite(
    key="META-REFLECTION",
    paper="Meta-Cognitive Reflection Engine",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Structured reflection extracts lessons from experiences with severity classification",
    confidence="CERTAIN",
)
@dataclass
class Reflection:
    """A single reflection insight extracted from agent behavior."""
    agent_id: str
    insight_type: str              # e.g., "overconfidence", "missed_opportunity", "blind_spot"
    severity: str                  # "low", "medium", "high", "critical"
    description: str
    recommended_action: str
    confidence_delta: float        # How much confidence should shift
    timestamp: float = field(default_factory=time.time)
    evidence: List[str] = field(default_factory=list)


@cite(
    key="META-REFLECTION",
    paper="Meta-Cognitive Reflection Engine",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Pattern detection across reasoning traces enables systematic self-improvement",
    confidence="CERTAIN",
)
class ReflectionEngine:
    """
    Svādhyāya — analyzes agent experiences and reasoning traces to produce
    structured reflections with actionable recommendations.
    
    Detects patterns:
    1. Overconfidence: high confidence + low reward
    2. Underconfidence: low confidence + high reward
    3. Blind spots: missing relevant memories in reasoning
    4. Repeated failures: same action leading to negative rewards
    5. Missed consensus: agent diverged from successful swarm consensus
    """

    def __init__(self):
        self.reflections: List[Reflection] = []
        self._pattern_history: Dict[str, List[Dict[str, Any]]] = {}

    def reflect_on_experiences(
        self,
        agent_id: str,
        experiences: List[Any],  # Experience objects
        reasoning_traces: List[Dict[str, Any]],
    ) -> List[Reflection]:
        """
        Generate reflections from an agent's experiences and reasoning traces.
        
        Returns a list of Reflection objects with severity-graded insights.
        """
        reflections = []
        
        # Pattern 1: Overconfidence detection
        overconfidence = self._detect_overconfidence(agent_id, experiences)
        if overconfidence:
            reflections.append(overconfidence)
        
        # Pattern 2: Underconfidence detection
        underconfidence = self._detect_underconfidence(agent_id, experiences)
        if underconfidence:
            reflections.append(underconfidence)
        
        # Pattern 3: Blind spots in reasoning
        blind_spots = self._detect_blind_spots(agent_id, reasoning_traces)
        reflections.extend(blind_spots)
        
        # Pattern 4: Repeated failure patterns
        repeated_failures = self._detect_repeated_failures(agent_id, experiences)
        reflections.extend(repeated_failures)
        
        # Pattern 5: Consensus divergence analysis
        consensus_divergence = self._analyze_consensus_divergence(agent_id, experiences)
        if consensus_divergence:
            reflections.append(consensus_divergence)
        
        # Store reflections
        self.reflections.extend(reflections)
        
        # Update pattern history
        if agent_id not in self._pattern_history:
            self._pattern_history[agent_id] = []
        for r in reflections:
            self._pattern_history[agent_id].append({
                "type": r.insight_type,
                "severity": r.severity,
                "timestamp": r.timestamp,
            })
        
        return reflections

    def _detect_overconfidence(self, agent_id: str, experiences: List[Any]) -> Optional[Reflection]:
        """Detect when high confidence precedes negative reward."""
        high_conf_low_reward = [
            e for e in experiences
            if e.confidence_before > 0.8 and e.reward < 0.0
        ]
        
        if len(high_conf_low_reward) >= 2:
            avg_conf = sum(e.confidence_before for e in high_conf_low_reward) / len(high_conf_low_reward)
            avg_reward = sum(e.reward for e in high_conf_low_reward) / len(high_conf_low_reward)
            
            return Reflection(
                agent_id=agent_id,
                insight_type="overconfidence",
                severity="high" if len(high_conf_low_reward) >= 3 else "medium",
                description=(
                    f"Agent showed high confidence (avg {avg_conf:.2f}) but received "
                    f"negative rewards (avg {avg_reward:.2f}) in {len(high_conf_low_reward)} cases."
                ),
                recommended_action="Reduce confidence calibration by 0.1 when no peer validation exists.",
                confidence_delta=-0.1,
                evidence=[f"exp_{i}: conf={e.confidence_before:.2f}, reward={e.reward:.2f}" 
                         for i, e in enumerate(high_conf_low_reward)],
            )
        return None

    def _detect_underconfidence(self, agent_id: str, experiences: List[Any]) -> Optional[Reflection]:
        """Detect when low confidence precedes positive reward."""
        low_conf_high_reward = [
            e for e in experiences
            if e.confidence_before < 0.4 and e.reward > 0.3
        ]
        
        if len(low_conf_high_reward) >= 2:
            avg_conf = sum(e.confidence_before for e in low_conf_high_reward) / len(low_conf_high_reward)
            avg_reward = sum(e.reward for e in low_conf_high_reward) / len(low_conf_high_reward)
            
            return Reflection(
                agent_id=agent_id,
                insight_type="underconfidence",
                severity="medium",
                description=(
                    f"Agent showed low confidence (avg {avg_conf:.2f}) but received "
                    f"positive rewards (avg {avg_reward:.2f}) in {len(low_conf_high_reward)} cases."
                ),
                recommended_action="Increase base confidence by 0.05 when historical success rate > 0.6.",
                confidence_delta=+0.05,
                evidence=[f"exp_{i}: conf={e.confidence_before:.2f}, reward={e.reward:.2f}" 
                         for i, e in enumerate(low_conf_high_reward)],
            )
        return None

    def _detect_blind_spots(
        self,
        agent_id: str,
        reasoning_traces: List[Dict[str, Any]],
    ) -> List[Reflection]:
        """Detect missing relevant memories in reasoning traces."""
        reflections = []
        
        for i, trace in enumerate(reasoning_traces):
            relevant = trace.get("relevant_memories", [])
            risks = trace.get("risks", [])
            
            # No memories retrieved
            if not relevant:
                reflections.append(Reflection(
                    agent_id=agent_id,
                    insight_type="blind_spot",
                    severity="high",
                    description=f"Reasoning trace {i} retrieved zero relevant memories.",
                    recommended_action="Expand memory retrieval query or increase retrieval limit.",
                    confidence_delta=-0.05,
                    evidence=[f"trace_{i}: zero memories"],
                ))
            
            # High risk but no peer consultation
            if len(risks) > 2 and trace.get("confidence", 0.5) > 0.7:
                reflections.append(Reflection(
                    agent_id=agent_id,
                    insight_type="blind_spot",
                    severity="medium",
                    description=f"High-risk reasoning ({len(risks)} risks) with no peer consultation.",
                    recommended_action="Consult peers when risks exceed 2 and confidence > 0.7.",
                    confidence_delta=-0.05,
                    evidence=[f"trace_{i}: {len(risks)} risks, no peer_communication"],
                ))
        
        return reflections

    def _detect_repeated_failures(self, agent_id: str, experiences: List[Any]) -> List[Reflection]:
        """Detect when the same action repeatedly leads to negative rewards."""
        action_rewards: Dict[str, List[float]] = {}
        for e in experiences:
            action = e.action
            if action not in action_rewards:
                action_rewards[action] = []
            action_rewards[action].append(e.reward)
        
        reflections = []
        for action, rewards in action_rewards.items():
            if len(rewards) >= 3:
                avg_reward = sum(rewards) / len(rewards)
                if avg_reward < -0.1:
                    reflections.append(Reflection(
                        agent_id=agent_id,
                        insight_type="repeated_failure",
                        severity="critical" if avg_reward < -0.3 else "high",
                        description=(
                            f"Action '{action}' consistently yields negative reward "
                            f"(avg {avg_reward:.2f} over {len(rewards)} attempts)."
                        ),
                        recommended_action=f"Deprioritize '{action}' or seek mentor agent guidance.",
                        confidence_delta=-0.1,
                        evidence=[f"{action}_attempt_{i}: reward={r:.2f}" for i, r in enumerate(rewards)],
                    ))
        
        return reflections

    def _analyze_consensus_divergence(self, agent_id: str, experiences: List[Any]) -> Optional[Reflection]:
        """Analyze whether agent diverged from successful swarm consensus."""
        diverged_positive = [
            e for e in experiences
            if e.metadata.get("swarm_consensus_reached") and 
               e.metadata.get("agent_aligned_with_consensus") is False and
               e.reward > 0.0
        ]
        
        diverged_negative = [
            e for e in experiences
            if e.metadata.get("swarm_consensus_reached") and 
               e.metadata.get("agent_aligned_with_consensus") is False and
               e.reward < 0.0
        ]
        
        if len(diverged_negative) >= 2:
            return Reflection(
                agent_id=agent_id,
                insight_type="consensus_divergence",
                severity="high",
                description=(
                    f"Agent diverged from swarm consensus {len(diverged_negative)} times "
                    f"and received negative rewards."
                ),
                recommended_action="Increase weight of peer signals in confidence calibration.",
                confidence_delta=-0.08,
                evidence=[f"divergence_{i}: reward={e.reward:.2f}" for i, e in enumerate(diverged_negative)],
            )
        
        if len(diverged_positive) >= 2:
            return Reflection(
                agent_id=agent_id,
                insight_type="constructive_dissent",
                severity="low",
                description=(
                    f"Agent constructively diverged from consensus {len(diverged_positive)} times "
                    f"with positive rewards."
                ),
                recommended_action="Maintain independent thinking but document divergence rationale.",
                confidence_delta=+0.03,
                evidence=[f"dissent_{i}: reward={e.reward:.2f}" for i, e in enumerate(diverged_positive)],
            )
        
        return None

    def get_agent_reflections(self, agent_id: str, min_severity: str = "low") -> List[Reflection]:
        """Get reflections for a specific agent, filtered by severity."""
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        min_level = severity_order.get(min_severity, 0)
        
        return [
            r for r in self.reflections
            if r.agent_id == agent_id and severity_order.get(r.severity, 0) >= min_level
        ]

    def get_pattern_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get a summary of detected patterns for an agent."""
        history = self._pattern_history.get(agent_id, [])
        if not history:
            return {"total_reflections": 0, "severity_counts": {}, "top_pattern": None}
        
        severity_counts = {}
        type_counts = {}
        for h in history:
            severity_counts[h["severity"]] = severity_counts.get(h["severity"], 0) + 1
            type_counts[h["type"]] = type_counts.get(h["type"], 0) + 1
        
        top_pattern = max(type_counts, key=type_counts.get) if type_counts else None
        
        return {
            "total_reflections": len(history),
            "severity_counts": severity_counts,
            "type_counts": type_counts,
            "top_pattern": top_pattern,
        }

    def clear(self) -> None:
        """Clear all reflections."""
        self.reflections.clear()
        self._pattern_history.clear()
