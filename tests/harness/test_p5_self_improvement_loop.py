"""
Tests for P5: Self-Improvement Loop (Svādhyāya + Abhyāsa).

Covers:
- ExperienceBuffer: add, sample, per-agent isolation, reward statistics
- ReflectionEngine: overconfidence, underconfidence, blind spots, repeated failures, consensus divergence
- PolicyOptimizer: gradient computation, policy updates, reflection adjustments, momentum
- SkillEvolution: create, mutate, crossover, select, prune, evolve generation
- SelfImprovementLoop: collect experience, run feedback cycle, improvement trend
- Integration: ConsciousAgent P5 substrates, SwarmOrchestrator feedback loop wiring

Citations:
- SuttonBarto2018: Reinforcement Learning fundamentals
- Lin1992: Experience replay
- Schaul2015: Prioritized experience replay
- Shinn2023: Reflexion — verbal reinforcement learning
- Yao2023: ReAct — reasoning and acting
- Schmidhuber1991: Meta-learning
- Ziegler2019: RLHF
- Ouyang2022: InstructGPT
- Mikkulainen2019: Evolving deep neural networks
- Real2017: Large-scale evolution
"""



import pytest

from harness.experience_buffer import ExperienceBuffer, Experience
from harness.meta_cognitive_reflection import ReflectionEngine, Reflection
from harness.policy_optimizer import PolicyOptimizer, Policy
from harness.skill_evolution import SkillEvolution, Skill
from harness.feedback_loop import SelfImprovementLoop, FeedbackLoopResult
from agents.conscious_agent import ConsciousAgent, AgentGoal
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from conftest import default_agent_kwargs


# ── Experience Buffer Tests ────────────────────────────────────────

class TestExperienceBuffer:
    """Tests for ExperienceBuffer implementation."""

    def test_add_experience(self):
        buf = ExperienceBuffer()
        exp = Experience(
            agent_id="a1", task_id="t1", state={}, action="propose",
            reward=0.5, next_state={}, confidence_before=0.7, confidence_after=0.8,
        )
        buf.add(exp)
        assert len(buf) == 1

    def test_sample_returns_correct_size(self):
        buf = ExperienceBuffer()
        for i in range(10):
            buf.add(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=0.1 * i, next_state={}, confidence_before=0.5, confidence_after=0.6,
            ))
        sampled = buf.sample(batch_size=5)
        assert len(sampled) == 5

    def test_sample_from_empty_buffer(self):
        buf = ExperienceBuffer()
        assert buf.sample(batch_size=5) == []

    def test_per_agent_sampling(self):
        buf = ExperienceBuffer()
        for i in range(5):
            buf.add(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=0.1, next_state={}, confidence_before=0.5, confidence_after=0.6,
            ))
        for i in range(3):
            buf.add(Experience(
                agent_id="a2", task_id="t1", state={}, action="critique",
                reward=0.2, next_state={}, confidence_before=0.6, confidence_after=0.7,
            ))
        a1_samples = buf.sample(batch_size=10, agent_id="a1")
        assert all(s.agent_id == "a1" for s in a1_samples)
        assert len(a1_samples) == 5

    def test_get_agent_experiences(self):
        buf = ExperienceBuffer()
        buf.add(Experience(
            agent_id="a1", task_id="t1", state={}, action="propose",
            reward=0.5, next_state={}, confidence_before=0.7, confidence_after=0.8,
        ))
        buf.add(Experience(
            agent_id="a2", task_id="t1", state={}, action="critique",
            reward=0.3, next_state={}, confidence_before=0.6, confidence_after=0.7,
        ))
        a1_exps = buf.get_agent_experiences("a1")
        assert len(a1_exps) == 1
        assert a1_exps[0].agent_id == "a1"

    def test_reward_statistics(self):
        buf = ExperienceBuffer()
        for r in [-0.5, 0.0, 0.5, 1.0]:
            buf.add(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=r, next_state={}, confidence_before=0.5, confidence_after=0.6,
            ))
        stats = buf.get_reward_statistics()
        assert stats["count"] == 4
        assert stats["mean"] == 0.25
        assert stats["min"] == -0.5
        assert stats["max"] == 1.0

    def test_buffer_capacity(self):
        buf = ExperienceBuffer(capacity=5)
        for i in range(10):
            buf.add(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=0.1 * i, next_state={}, confidence_before=0.5, confidence_after=0.6,
            ))
        assert len(buf) == 5

    def test_clear_buffer(self):
        buf = ExperienceBuffer()
        buf.add(Experience(
            agent_id="a1", task_id="t1", state={}, action="propose",
            reward=0.5, next_state={}, confidence_before=0.7, confidence_after=0.8,
        ))
        buf.clear()
        assert len(buf) == 0
        assert buf.get_reward_statistics()["count"] == 0

    def test_priority_sampling_biased_toward_high_reward(self):
        buf = ExperienceBuffer(alpha=1.0)
        buf.add(Experience(
            agent_id="a1", task_id="t1", state={}, action="propose",
            reward=0.9, next_state={}, confidence_before=0.5, confidence_after=0.6,
        ))
        for _ in range(10):
            buf.add(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=0.1, next_state={}, confidence_before=0.5, confidence_after=0.6,
            ))
        # High reward experience should be sampled more frequently
        samples = buf.sample(batch_size=5)  # Sample less than buffer size
        high_reward_count = sum(1 for s in samples if s.reward > 0.5)
        # With alpha=1.0, priority is proportional to reward
        # High reward priority = 0.9, each low = 0.1, total = 1.9
        # Expected high proportion = 0.9 / 1.9 ≈ 47%
        # Run many times to get statistical confidence
        total_high = 0
        total_samples = 0
        for _ in range(200):
            s = buf.sample(batch_size=5)
            total_high += sum(1 for x in s if x.reward > 0.5)
            total_samples += len(s)
        proportion = total_high / total_samples
        assert proportion > 0.30  # Significantly above uniform 1/11 ≈ 9%


# ── Reflection Engine Tests ───────────────────────────────────────

class TestReflectionEngine:
    """Tests for ReflectionEngine (Svādhyāya)."""

    def test_detect_overconfidence(self):
        engine = ReflectionEngine()
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.4, next_state={}, confidence_before=0.95, confidence_after=0.9),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.3, next_state={}, confidence_before=0.92, confidence_after=0.88),
        ]
        reflections = engine.reflect_on_experiences("a1", experiences, [])
        assert any(r.insight_type == "overconfidence" for r in reflections)

    def test_detect_underconfidence(self):
        engine = ReflectionEngine()
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.6, next_state={}, confidence_before=0.2, confidence_after=0.3),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.5, next_state={}, confidence_before=0.25, confidence_after=0.35),
        ]
        reflections = engine.reflect_on_experiences("a1", experiences, [])
        assert any(r.insight_type == "underconfidence" for r in reflections)

    def test_detect_blind_spots_no_memories(self):
        engine = ReflectionEngine()
        reasoning_traces = [{"relevant_memories": [], "risks": []}]
        reflections = engine.reflect_on_experiences("a1", [], reasoning_traces)
        assert any(r.insight_type == "blind_spot" for r in reflections)

    def test_detect_blind_spots_high_risk_no_peer(self):
        engine = ReflectionEngine()
        reasoning_traces = [
            {"relevant_memories": ["m1"], "risks": ["r1", "r2", "r3"], "confidence": 0.8}
        ]
        reflections = engine.reflect_on_experiences("a1", [], reasoning_traces)
        assert any(r.insight_type == "blind_spot" for r in reflections)

    def test_detect_repeated_failures(self):
        engine = ReflectionEngine()
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="agree",
                      reward=-0.4, next_state={}, confidence_before=0.5, confidence_after=0.4),
            Experience(agent_id="a1", task_id="t1", state={}, action="agree",
                      reward=-0.3, next_state={}, confidence_before=0.5, confidence_after=0.4),
            Experience(agent_id="a1", task_id="t1", state={}, action="agree",
                      reward=-0.5, next_state={}, confidence_before=0.5, confidence_after=0.3),
        ]
        reflections = engine.reflect_on_experiences("a1", experiences, [])
        assert any(r.insight_type == "repeated_failure" for r in reflections)

    def test_analyze_consensus_divergence_negative(self):
        engine = ReflectionEngine()
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.3, next_state={}, confidence_before=0.5, confidence_after=0.4,
                      metadata={"swarm_consensus_reached": True, "agent_aligned_with_consensus": False}),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.2, next_state={}, confidence_before=0.5, confidence_after=0.4,
                      metadata={"swarm_consensus_reached": True, "agent_aligned_with_consensus": False}),
        ]
        reflections = engine.reflect_on_experiences("a1", experiences, [])
        assert any(r.insight_type == "consensus_divergence" for r in reflections)

    def test_analyze_constructive_dissent(self):
        engine = ReflectionEngine()
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.5, next_state={}, confidence_before=0.5, confidence_after=0.6,
                      metadata={"swarm_consensus_reached": True, "agent_aligned_with_consensus": False}),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.4, next_state={}, confidence_before=0.5, confidence_after=0.6,
                      metadata={"swarm_consensus_reached": True, "agent_aligned_with_consensus": False}),
        ]
        reflections = engine.reflect_on_experiences("a1", experiences, [])
        assert any(r.insight_type == "constructive_dissent" for r in reflections)

    def test_get_agent_reflections_filtered(self):
        engine = ReflectionEngine()
        engine.reflections = [
            Reflection(agent_id="a1", insight_type="overconfidence", severity="high",
                      description="test", recommended_action="fix", confidence_delta=-0.1),
            Reflection(agent_id="a1", insight_type="blind_spot", severity="low",
                      description="test", recommended_action="fix", confidence_delta=-0.05),
            Reflection(agent_id="a2", insight_type="overconfidence", severity="critical",
                      description="test", recommended_action="fix", confidence_delta=-0.2),
        ]
        a1_high = engine.get_agent_reflections("a1", min_severity="high")
        assert len(a1_high) == 1
        assert a1_high[0].severity == "high"

    def test_pattern_summary(self):
        engine = ReflectionEngine()
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.4, next_state={}, confidence_before=0.95, confidence_after=0.9),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.3, next_state={}, confidence_before=0.92, confidence_after=0.88),
        ]
        engine.reflect_on_experiences("a1", experiences, [])
        summary = engine.get_pattern_summary("a1")
        assert summary["total_reflections"] == 1
        assert summary["top_pattern"] == "overconfidence"

    def test_clear_reflections(self):
        engine = ReflectionEngine()
        engine.reflections.append(Reflection(agent_id="a1", insight_type="test", severity="low",
                                            description="test", recommended_action="fix", confidence_delta=0.0))
        engine.clear()
        assert len(engine.reflections) == 0


# ── Policy Optimizer Tests ─────────────────────────────────────────

class TestPolicyOptimizer:
    """Tests for PolicyOptimizer (Abhyāsa)."""

    def test_register_and_get_policy(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.7)
        opt.register_policy(policy)
        assert opt.get_policy("a1") is not None
        assert opt.get_policy("a1").base_confidence == 0.7

    def test_compute_gradient_positive_reward(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.5, confidence_learning_rate=0.1)
        opt.register_policy(policy)
        # Use multiple experiences so baseline doesn't zero out the gradient
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.8, next_state={}, confidence_before=0.5, confidence_after=0.7),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.2, next_state={}, confidence_before=0.5, confidence_after=0.6),
        ]
        grad = opt.compute_gradient("a1", experiences)
        assert "base_confidence" in grad
        # Positive reward with confidence increase → positive gradient
        assert grad["base_confidence"] > 0

    def test_compute_gradient_negative_reward(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.5, confidence_learning_rate=0.1)
        opt.register_policy(policy)
        # Negative reward with confidence INCREASE (overconfidence punished)
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=-0.6, next_state={}, confidence_before=0.5, confidence_after=0.8),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.2, next_state={}, confidence_before=0.5, confidence_after=0.6),
        ]
        grad = opt.compute_gradient("a1", experiences)
        # Negative reward with confidence increase → negative gradient
        assert grad["base_confidence"] < 0

    def test_gradient_clipping(self):
        opt = PolicyOptimizer(max_gradient_norm=0.1)
        policy = Policy(agent_id="a1", base_confidence=0.5, confidence_learning_rate=1.0)
        opt.register_policy(policy)
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=10.0, next_state={}, confidence_before=0.1, confidence_after=0.9),
        ]
        grad = opt.compute_gradient("a1", experiences)
        assert abs(grad["base_confidence"]) <= 0.1

    def test_update_policy_changes_values(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.5)
        opt.register_policy(policy)
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.8, next_state={}, confidence_before=0.5, confidence_after=0.7),
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.2, next_state={}, confidence_before=0.5, confidence_after=0.6),
        ]
        old_conf = policy.base_confidence
        result = opt.update_policy("a1", experiences)
        assert result["status"] == "updated"
        assert policy.base_confidence != old_conf

    def test_update_policy_with_reflection_adjustments(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.7)
        opt.register_policy(policy)
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.5, next_state={}, confidence_before=0.7, confidence_after=0.7),
        ]
        result = opt.update_policy("a1", experiences, reflection_adjustments={"confidence_delta": -0.1})
        assert result["status"] == "updated"
        assert policy.base_confidence < 0.7

    def test_policy_bounds(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.95)
        opt.register_policy(policy)
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=1.0, next_state={}, confidence_before=0.9, confidence_after=1.0),
        ]
        opt.update_policy("a1", experiences)
        assert policy.base_confidence <= 1.0
        assert policy.base_confidence >= 0.1

    def test_exploration_decay(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", exploration_rate=0.3, exploration_decay=0.9)
        opt.register_policy(policy)
        experiences = [
            Experience(agent_id="a1", task_id="t1", state={}, action="propose",
                      reward=0.5, next_state={}, confidence_before=0.5, confidence_after=0.6),
        ]
        opt.update_policy("a1", experiences)
        assert policy.exploration_rate < 0.3
        assert policy.exploration_rate >= 0.05

    def test_policy_summary(self):
        opt = PolicyOptimizer()
        policy = Policy(agent_id="a1", base_confidence=0.7)
        opt.register_policy(policy)
        summary = opt.get_policy_summary("a1")
        assert summary["agent_id"] == "a1"
        assert summary["base_confidence"] == 0.7


# ── Skill Evolution Tests ──────────────────────────────────────────

class TestSkillEvolution:
    """Tests for SkillEvolution (Abhyāsa structural)."""

    def test_create_skill(self):
        evo = SkillEvolution()
        skill = evo.create_skill("a1", "spatial_reasoning", "reasoning", {"attention": 0.7})
        assert skill.name == "spatial_reasoning"
        assert skill.parameters["attention"] == 0.7
        assert len(evo.get_agent_skills("a1")) == 1

    def test_mutate_skill(self):
        evo = SkillEvolution(mutation_rate=1.0, mutation_strength=0.1)
        skill = evo.create_skill("a1", "spatial_reasoning", "reasoning", {"attention": 0.7})
        mutated = evo.mutate_skill("a1", skill.skill_id)
        assert mutated is not None
        assert mutated.parent_id == skill.skill_id
        assert mutated.generation == 1
        assert len(evo.get_agent_skills("a1")) == 2

    def test_crossover_skills(self):
        evo = SkillEvolution()
        skill_a = evo.create_skill("a1", "skill_a", "reasoning", {"param1": 0.8, "param2": 0.2})
        skill_b = evo.create_skill("a1", "skill_b", "reasoning", {"param1": 0.2, "param2": 0.8})
        child = evo.crossover_skills("a1", skill_a.skill_id, skill_b.skill_id)
        assert child is not None
        assert child.generation == 1
        # Child param should be roughly average (allowing for Gaussian noise)
        assert 0.2 < child.parameters["param1"] < 0.8

    def test_select_skills_by_fitness(self):
        evo = SkillEvolution()
        s1 = evo.create_skill("a1", "good", "reasoning", {})
        s1.success_count = 10
        s1.failure_count = 1
        s1.usage_count = 11
        
        s2 = evo.create_skill("a1", "bad", "reasoning", {})
        s2.success_count = 1
        s2.failure_count = 10
        s2.usage_count = 11
        
        selected = evo.select_skills("a1")
        assert selected[0].name == "good"

    def test_prune_skills(self):
        evo = SkillEvolution(max_skills_per_agent=3)
        for i in range(5):
            evo.create_skill("a1", f"skill_{i}", "reasoning", {})
        removed = evo.prune_skills("a1")
        assert removed == 2
        assert len(evo.get_agent_skills("a1")) == 3

    def test_evolve_generation(self):
        evo = SkillEvolution()
        evo.create_skill("a1", "parent1", "reasoning", {"p": 0.5})
        evo.create_skill("a1", "parent2", "reasoning", {"p": 0.6})
        # Force mutation by running multiple times
        total_offspring = 0
        for _ in range(10):
            result = evo.evolve_generation("a1")
            total_offspring += result["offspring_created"]
        assert total_offspring > 0

    def test_fitness_computation(self):
        skill = Skill(skill_id="s1", name="test", skill_type="reasoning", parameters={})
        skill.success_count = 8
        skill.failure_count = 2
        skill.total_reward = 1.5
        skill.usage_count = 10
        # fitness = 0.8 * 0.6 + (1.5 + 1)/2 * 0.3 + min(10/10, 0.1) = 0.48 + 0.375 + 0.1 = 0.955
        assert skill.fitness > 0.8

    def test_get_best_skill(self):
        evo = SkillEvolution()
        s1 = evo.create_skill("a1", "good", "reasoning", {})
        s1.success_count = 10
        s1.failure_count = 0
        s1.usage_count = 10
        
        s2 = evo.create_skill("a1", "bad", "reasoning", {})
        s2.success_count = 1
        s2.failure_count = 9
        s2.usage_count = 10
        
        best = evo.get_best_skill("a1")
        assert best.name == "good"

    def test_skill_record_usage(self):
        skill = Skill(skill_id="s1", name="test", skill_type="reasoning", parameters={})
        skill.record_usage(reward=0.5, success=True)
        assert skill.usage_count == 1
        assert skill.success_count == 1
        assert skill.total_reward == 0.5

    def test_evolution_summary(self):
        evo = SkillEvolution()
        s1 = evo.create_skill("a1", "reasoning_skill", "reasoning", {})
        s1.success_count = 5
        s1.failure_count = 1
        s1.usage_count = 6
        
        summary = evo.get_evolution_summary("a1")
        assert summary["total_skills"] == 1
        assert "reasoning" in summary["type_summaries"]


# ── Self-Improvement Loop Tests ────────────────────────────────────

class TestSelfImprovementLoop:
    """Tests for SelfImprovementLoop orchestrator."""

    def test_collect_experience_consensus_reached(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        deliberation = {
            "consensus": {"status": "consensus", "score": 0.8},
            "closure": {"closure_reached": True},
        }
        exp = loop.collect_experience_from_deliberation(
            task_id="t1", agent_id="a1", deliberation_result=deliberation,
            agent_reasoning={"confidence": 0.8}, confidence_before=0.7, confidence_after=0.8,
        )
        assert exp.reward > 0.0
        assert exp.metadata["swarm_consensus_reached"] is True

    def test_collect_experience_byzantine_detected(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        deliberation = {
            "consensus": {
                "status": "divergent",
                "score": 0.3,
                "cp_wbft": {"byzantine_detected": ["a1"]},
            },
        }
        exp = loop.collect_experience_from_deliberation(
            task_id="t1", agent_id="a1", deliberation_result=deliberation,
            agent_reasoning={"confidence": 0.3}, confidence_before=0.7, confidence_after=0.3,
        )
        assert exp.reward < 0.0
        assert exp.metadata.get("byzantine_detected") is True

    def test_run_feedback_cycle_no_experiences(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        result = loop.run_feedback_cycle("t1", ["a1"])
        assert result.experiences_collected == 0
        assert result.reflections_generated == 0

    def test_run_feedback_cycle_with_experiences(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        # Register policy
        policy = Policy(agent_id="a1", base_confidence=0.7)
        loop.policy_optimizer.register_policy(policy)
        # Add experiences
        for _ in range(5):
            loop.experience_buffer.add(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=0.5, next_state={}, confidence_before=0.6, confidence_after=0.7,
            ))
        result = loop.run_feedback_cycle("t1", ["a1"])
        assert result.experiences_collected == 5
        assert result.reflections_generated >= 0

    def test_improvement_trend_improving(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        # Simulate improving trend
        for i in range(4):
            result = FeedbackLoopResult(
                task_id=f"t{i}", experiences_collected=1, reflections_generated=1,
                policies_updated=1, skills_evolved=1, avg_reward=-0.2 + i * 0.15,
            )
            loop._loop_history.append(result)
        trend = loop.get_improvement_trend()
        assert trend["trend"] == "improving"

    def test_improvement_trend_stable(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        for i in range(4):
            result = FeedbackLoopResult(
                task_id=f"t{i}", experiences_collected=1, reflections_generated=1,
                policies_updated=1, skills_evolved=1, avg_reward=0.5,
            )
            loop._loop_history.append(result)
        trend = loop.get_improvement_trend()
        assert trend["trend"] == "stable"

    def test_enable_disable(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        loop.disable()
        result = loop.run_feedback_cycle("t1", ["a1"])
        assert result.experiences_collected == 0
        loop.enable()
        result = loop.run_feedback_cycle("t1", ["a1"])
        assert result.experiences_collected == 0  # Still no experiences

    def test_loop_history(self):
        loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        loop._loop_history.append(FeedbackLoopResult(
            task_id="t1", experiences_collected=1, reflections_generated=1,
            policies_updated=1, skills_evolved=1, avg_reward=0.5,
        ))
        assert len(loop.get_loop_history()) == 1


# ── ConsciousAgent P5 Integration Tests ────────────────────────────

class TestConsciousAgentP5Integration:
    """Tests for ConsciousAgent P5 integration."""

    def test_agent_has_experience_buffer(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        assert agent.experience_buffer is not None
        assert len(agent.experience_buffer) == 0

    def test_agent_has_reflection_engine(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        assert agent.reflection_engine is not None

    def test_agent_has_policy_optimizer(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        assert agent.policy_optimizer is not None
        assert agent.policy_optimizer.get_policy("a1") is not None

    def test_agent_has_skill_evolution(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        assert agent.skill_evolution is not None
        skills = agent.skill_evolution.get_agent_skills("a1")
        assert len(skills) > 0  # Default skills initialized

    def test_agent_default_skills_by_cluster(self):
        agent = ConsciousAgent("a1", "Video Agent", "video-gnn", **default_agent_kwargs("a1"))
        skills = agent.skill_evolution.get_agent_skills("a1")
        skill_names = [s.name for s in skills]
        assert "spatial_reasoning" in skill_names or "feature_extraction" in skill_names

    def test_agent_record_experience(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        exp = Experience(
            agent_id="a1", task_id="t1", state={}, action="propose",
            reward=0.5, next_state={}, confidence_before=0.7, confidence_after=0.8,
        )
        agent.record_experience(exp)
        assert len(agent.experience_buffer) == 1

    def test_agent_reflect(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        for _ in range(3):
            agent.record_experience(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=-0.4, next_state={}, confidence_before=0.95, confidence_after=0.9,
            ))
        reflections = agent.reflect()
        assert len(reflections) > 0

    def test_agent_update_policy(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        for _ in range(3):
            agent.record_experience(Experience(
                agent_id="a1", task_id="t1", state={}, action="propose",
                reward=0.8, next_state={}, confidence_before=0.5, confidence_after=0.7,
            ))
        result = agent.update_policy()
        assert result["status"] == "updated"

    def test_agent_evolve_skills(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        result = agent.evolve_skills()
        assert result["status"] == "evolved"

    def test_agent_get_policy_parameters(self):
        agent = ConsciousAgent("a1", "Test Agent", "multi-agent", **default_agent_kwargs("a1"))
        params = agent.get_policy_parameters()
        assert "base_confidence" in params
        assert "peer_trust_weight" in params


# ── SwarmOrchestrator P5 Integration Tests ─────────────────────────

class TestSwarmOrchestratorP5Integration:
    """Tests for SwarmOrchestrator P5 integration."""

    def test_orchestrator_has_feedback_loop(self):
        orch = SwarmOrchestrator()
        assert orch.self_improvement_loop is not None
        assert orch.feedback_enabled is True

    def test_full_deliberation_runs_feedback_loop(self):
        orch = SwarmOrchestrator()
        
        # Register agents
        agent1 = ConsciousAgent("a1", "Agent 1", "multi-agent", **default_agent_kwargs("a1"))
        agent2 = ConsciousAgent("a2", "Agent 2", "multi-agent", **default_agent_kwargs("a2"))
        agent3 = ConsciousAgent("a3", "Agent 3", "multi-agent", **default_agent_kwargs("a3"))
        orch.register_agent(agent1)
        orch.register_agent(agent2)
        orch.register_agent(agent3)
        
        task = SwarmTask(
            task_id="test-task",
            description="Test deliberation",
            required_clusters=["multi-agent"],
            success_criteria=["reach consensus"],
        )
        orch.activate_task(task)
        result = orch.run_full_deliberation("test-task")
        
        assert "feedback_loop" in result
        assert result["feedback_loop"]["experiences_collected"] >= 0

    def test_feedback_loop_disabled(self):
        orch = SwarmOrchestrator()
        orch.feedback_enabled = False
        
        agent1 = ConsciousAgent("a1", "Agent 1", "multi-agent", **default_agent_kwargs("a1"))
        agent2 = ConsciousAgent("a2", "Agent 2", "multi-agent", **default_agent_kwargs("a2"))
        orch.register_agent(agent1)
        orch.register_agent(agent2)
        
        task = SwarmTask(
            task_id="test-task",
            description="Test deliberation",
            required_clusters=["multi-agent"],
            success_criteria=["reach consensus"],
        )
        orch.activate_task(task)
        result = orch.run_full_deliberation("test-task")
        
        # When disabled, feedback_loop may still be in result but with 0s
        # or may not be present depending on implementation
        if "feedback_loop" in result:
            assert result["feedback_loop"]["experiences_collected"] == 0
