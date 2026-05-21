# src/harness/feedback_loop.py
"""
Self-Improvement Loop: Svādhyāya + Abhyāsa + Reward Propagation.

Orchestrates the full meta-cognitive feedback cycle:
1. Collect experiences from deliberation outcomes
2. Run Svādhyāya (reflection) on experiences
3. Optimize policies using reward-weighted gradients
4. Evolve skills through mutation and selection
5. Propagate improvements back to agents

Inspired by:
- SuttonBarto2018: RL agent-environment loop
- Shinn2023: Reflexion — self-reflection for improvement
- Schmidhuber1991: Meta-learning at the system level

Principle: The harness learns from its own deliberations. Each swarm
execution is not just a task completion but a training episode for
the collective intelligence.

[CITATION: SuttonBarto2018]
[CITATION: Shinn2023]
[CITATION: Schmidhuber1991]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from harness.experience_buffer import ExperienceBuffer, Experience
from harness.meta_cognitive_reflection import ReflectionEngine, Reflection
from harness.policy_optimizer import PolicyOptimizer, Policy
from harness.skill_evolution import SkillEvolution, Skill


@cite(
    key="FEEDBACK-LOOP",
    paper="Self-Improvement Loop for ACN Harness",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Orchestrates the full meta-cognitive cycle from experience to behavioral change",
    confidence="CERTAIN",
)
@dataclass
class FeedbackLoopResult:
    """Result of running one feedback loop iteration."""
    task_id: str
    experiences_collected: int
    reflections_generated: int
    policies_updated: int
    skills_evolved: int
    avg_reward: float
    timestamp: float = field(default_factory=time.time)
    agent_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    reflection_details: List[Reflection] = field(default_factory=list)


@cite(
    key="FEEDBACK-LOOP",
    paper="Self-Improvement Loop for ACN Harness",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Unified orchestrator connecting experience, reflection, policy, and skill layers",
    confidence="CERTAIN",
)
class SelfImprovementLoop:
    """
    The master orchestrator for agent self-improvement.
    
    Connects:
    - ExperienceBuffer: stores episodes
    - ReflectionEngine: Svādhyāya — extracts insights
    - PolicyOptimizer: reward-weighted parameter updates
    - SkillEvolution: Abhyāsa — structural skill evolution
    """

    def __init__(
        self,
        experience_buffer: ExperienceBuffer,
        reflection_engine: ReflectionEngine,
        policy_optimizer: PolicyOptimizer,
        skill_evolution: SkillEvolution,
    ):
        self.experience_buffer = experience_buffer
        self.reflection_engine = reflection_engine
        self.policy_optimizer = policy_optimizer
        self.skill_evolution = skill_evolution
        
        self._loop_history: List[FeedbackLoopResult] = []
        self._enabled = True

    def collect_experience_from_deliberation(
        self,
        task_id: str,
        agent_id: str,
        deliberation_result: Dict[str, Any],
        agent_reasoning: Dict[str, Any],
        confidence_before: float,
        confidence_after: float,
        action: str = "propose",
    ) -> Experience:
        """
        Shape a reward from deliberation outcome and store as experience.
        
        Reward shaping:
        - Consensus reached: +0.5
        - Agent aligned with consensus: +0.3
        - Closure reached: +0.2
        - Dissent suppression detected: -0.4
        - Byzantine detected: -0.5
        """
        reward = 0.0
        metadata = {}
        
        # Consensus reward
        consensus = deliberation_result.get("consensus", {})
        consensus_status = consensus.get("status", "")
        consensus_score = consensus.get("score", 0.0)
        
        if consensus_status == "consensus":
            reward += 0.5
            metadata["swarm_consensus_reached"] = True
        elif consensus_status == "partial":
            reward += 0.2
            metadata["swarm_consensus_reached"] = False
        else:
            reward -= 0.1
            metadata["swarm_consensus_reached"] = False
        
        # Score quality
        reward += (consensus_score - 0.5) * 0.4
        
        # Closure reward
        closure = deliberation_result.get("closure", {})
        if closure.get("closure_reached"):
            reward += 0.2
        
        # Dissent suppression penalty
        if deliberation_result.get("dissent_triggered"):
            suppression = deliberation_result.get("red_team", {}).get("suppression_signals", [])
            if suppression:
                reward -= 0.4
                metadata["suppression_detected"] = True
        
        # Byzantine penalty
        byzantine = consensus.get("cp_wbft", {}).get("byzantine_detected", [])
        if agent_id in byzantine:
            reward -= 0.5
            metadata["byzantine_detected"] = True
        
        # Alignment with consensus
        agent_score = agent_reasoning.get("confidence", 0.5)
        aligned = abs(agent_score - consensus_score) < 0.2
        metadata["agent_aligned_with_consensus"] = aligned
        if aligned and consensus_status == "consensus":
            reward += 0.3
        
        experience = Experience(
            agent_id=agent_id,
            task_id=task_id,
            state={
                "confidence": confidence_before,
                "reasoning_depth": len(agent_reasoning.get("reasoning_trace", [])),
            },
            action=action,
            reward=max(-1.0, min(1.0, reward)),
            next_state={
                "confidence": confidence_after,
                "consensus_score": consensus_score,
            },
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            metadata=metadata,
        )
        
        self.experience_buffer.add(experience)
        return experience

    def run_feedback_cycle(
        self,
        task_id: str,
        agent_ids: List[str],
        deliberation_result: Optional[Dict[str, Any]] = None,
    ) -> FeedbackLoopResult:
        """
        Run one complete feedback cycle for a set of agents.
        
        Steps:
        1. Collect experiences (if deliberation result provided)
        2. Run reflection on each agent's experiences
        3. Update policies with reflection adjustments
        4. Evolve skills
        5. Return summary
        """
        if not self._enabled:
            return FeedbackLoopResult(task_id=task_id, experiences_collected=0,
                                      reflections_generated=0, policies_updated=0,
                                      skills_evolved=0, avg_reward=0.0)
        
        total_experiences = 0
        total_reflections = 0
        policies_updated = 0
        skills_evolved = 0
        agent_summaries = {}
        all_reflections = []
        all_rewards = []
        
        for agent_id in agent_ids:
            # Get agent's experiences
            experiences = self.experience_buffer.get_agent_experiences(agent_id)
            total_experiences += len(experiences)
            
            if not experiences:
                continue
            
            all_rewards.extend([e.reward for e in experiences])
            
            # Step 2: Reflection (Svādhyāya)
            # Extract reasoning traces from experiences
            reasoning_traces = [e.state for e in experiences]
            reflections = self.reflection_engine.reflect_on_experiences(
                agent_id=agent_id,
                experiences=experiences,
                reasoning_traces=reasoning_traces,
            )
            total_reflections += len(reflections)
            all_reflections.extend(reflections)
            
            # Step 3: Policy update
            # Aggregate reflection adjustments
            reflection_adjustments = {}
            if reflections:
                avg_conf_delta = sum(r.confidence_delta for r in reflections) / len(reflections)
                reflection_adjustments["confidence_delta"] = avg_conf_delta
            
            if agent_id in [p.agent_id for p in self.policy_optimizer._policies.values()]:
                update_result = self.policy_optimizer.update_policy(
                    agent_id=agent_id,
                    experiences=experiences,
                    reflection_adjustments=reflection_adjustments if reflection_adjustments else None,
                )
                if update_result.get("status") == "updated":
                    policies_updated += 1
            
            # Step 4: Skill evolution
            skill_result = self.skill_evolution.evolve_generation(agent_id)
            if skill_result.get("status") == "evolved":
                skills_evolved += 1
            
            # Agent summary
            agent_summaries[agent_id] = {
                "experience_count": len(experiences),
                "reflection_count": len(reflections),
                "policy_updated": policies_updated > 0,
                "skills_evolved": skill_result.get("offspring_created", 0),
                "top_reflection": reflections[0].insight_type if reflections else None,
            }
        
        avg_reward = sum(all_rewards) / len(all_rewards) if all_rewards else 0.0
        
        result = FeedbackLoopResult(
            task_id=task_id,
            experiences_collected=total_experiences,
            reflections_generated=total_reflections,
            policies_updated=policies_updated,
            skills_evolved=skills_evolved,
            avg_reward=avg_reward,
            agent_summaries=agent_summaries,
            reflection_details=all_reflections,
        )
        
        self._loop_history.append(result)
        return result

    def get_loop_history(self) -> List[FeedbackLoopResult]:
        """Get history of all feedback loop runs."""
        return self._loop_history

    def get_improvement_trend(self) -> Dict[str, Any]:
        """Analyze improvement trend across feedback loop iterations."""
        if not self._loop_history:
            return {"trend": "none", "avg_reward_delta": 0.0}
        
        rewards = [r.avg_reward for r in self._loop_history]
        if len(rewards) < 2:
            return {"trend": "insufficient_data", "avg_reward": rewards[0] if rewards else 0.0}
        
        # Simple trend: compare first half to second half
        mid = len(rewards) // 2
        first_half = sum(rewards[:mid]) / max(mid, 1)
        second_half = sum(rewards[mid:]) / max(len(rewards) - mid, 1)
        
        trend = "improving" if second_half > first_half + 0.05 else \
                "declining" if second_half < first_half - 0.05 else "stable"
        
        return {
            "trend": trend,
            "avg_reward_first_half": first_half,
            "avg_reward_second_half": second_half,
            "reward_delta": second_half - first_half,
            "total_iterations": len(self._loop_history),
        }

    def enable(self) -> None:
        """Enable the feedback loop."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the feedback loop."""
        self._enabled = False
