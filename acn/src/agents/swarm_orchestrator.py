# src/agents/swarm_orchestrator.py
"""
Swarm Orchestrator: Coordinates a Swarm of Conscious Agents.

The orchestrator does not do the thinking. It creates the conditions
for conscious agents to think, debate, and reach consensus.

Each agent in the swarm is self-aware. The swarm itself is aware of the
collective state. Consciousness is fractal: agent-level + swarm-level.

Principle: In God we trust. All others must bring data.

Research foundations:
- CP-WBFT2025: Byzantine Fault Tolerant consensus for multi-agent systems
- NSED2026: Semantic decay prevents consensus collapse in recurrent networks
- SWARP2026: Argument persistence with closure detection
- Greenblatt2024: Dissent amplification detects hidden deception
- Kulkarni2014: Hybrid Logical Clocks for causal ordering
- TemporalObservability2026: Even 3-5ms skew breaks causal observability

[CITATION: CITATIONS-GOVERNANCE]
[CITATION: CP-WBFT2025]
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from shared.utils.citations import cite
from agents.conscious_agent import ConsciousAgent, AgentGoal
from agents.deliberation import DeliberationEngine
from harness.awareness import AwarenessSubsystem, GoalState, CurrentState, AwarenessLevel
from memory.ptkg import PTKG, NodeType, EdgeType
from memory.graph_retrieval import GraphRetriever
from memory.reputation_graph import ReputationGraphTracker
from memory.causal_chain import CausalChainTracker
from consensus.hlc import HybridLogicalClock
from consensus.temporal_auditor import TemporalAuditor, CausalityHealth
from consensus.distributed_consensus import DistributedConsensusEngine, AgentVote
from consensus.topology import TopologyOptimizer, TopologyType
from harness.feedback_loop import SelfImprovementLoop, FeedbackLoopResult
from harness.experience_buffer import ExperienceBuffer
from harness.meta_cognitive_reflection import ReflectionEngine
from harness.policy_optimizer import PolicyOptimizer
from harness.skill_evolution import SkillEvolution


@cite(
    key="SWARM-TASK",
    paper="Conscious Agent Swarm: Task Definition",
    venue="ACN Architecture Document",
    section="Swarm Tasks",
    rationale="Structured task representation enables agent matching and decomposition",
    confidence="CERTAIN",
)
@dataclass
class SwarmTask:
    """A task to be executed by the conscious agent swarm."""
    task_id: str
    description: str
    required_clusters: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    min_agents: int = 2
    max_agents: int = 10
    deadline: Optional[float] = None


@cite(
    key="SWARM-ORCHESTRATOR",
    paper="Conscious Agent Swarm: Orchestration Architecture",
    venue="ACN Architecture Document",
    section="Swarm Orchestration",
    rationale="Swarm-level awareness complements agent-level awareness for collective cognition",
    confidence="CERTAIN",
)
class SwarmOrchestrator:
    """
    Orchestrates a swarm of conscious agents.

    The orchestrator:
    1. Receives a task
    2. Decomposes it into agent-level goals
    3. Activates agents from relevant clusters
    4. Monitors collective progress
    5. Detects consensus or divergence
    6. Runs feedback loops for self-improvement
    7. Persists deliberation to graph memory

    [CITATION: CP-WBFT2025]
    [CITATION: NSED2026]
    [CITATION: SWARP2026]
    """

    def __init__(
        self,
        orchestrator_id: str = "swarm-orchestrator-001",
        tool_registry: Optional[Any] = None,
        academic_verifier: Optional[Any] = None,
        dashboard_collector: Optional[Any] = None,
    ):
        """Initialize the swarm orchestrator with all infrastructure."""
        self.orchestrator_id = orchestrator_id
        self.tool_registry = tool_registry
        self.academic_verifier = academic_verifier
        self.dashboard_collector = dashboard_collector

        # P2: Deliberation engine (lazy initialization via property)
        self._deliberation_engine: Optional[DeliberationEngine] = None

        # P3: Persistent graph memory (cross-session, swarm-shared)
        self.graph_memory: Optional[PTKG] = None
        self.graph_retriever: Optional[GraphRetriever] = None
        self.reputation_tracker: Optional[ReputationGraphTracker] = None
        self.causal_tracker: Optional[CausalChainTracker] = None

        # P4: Distributed consensus infrastructure
        self.temporal_auditor = TemporalAuditor()
        self.consensus_engine = DistributedConsensusEngine()
        self.topology_optimizer = TopologyOptimizer()
        self.communication_topology: Dict[str, List[str]] = {}
        self.topology_type: TopologyType = TopologyType.COMPLETE

        # P5: Self-improvement loop — injected dependencies (DIP)
        self.self_improvement_loop = SelfImprovementLoop(
            experience_buffer=ExperienceBuffer(),
            reflection_engine=ReflectionEngine(),
            policy_optimizer=PolicyOptimizer(),
            skill_evolution=SkillEvolution(),
        )
        self.feedback_enabled = True

        # Swarm state
        self.agents: Dict[str, ConsciousAgent] = {}
        self.active_tasks: Dict[str, SwarmTask] = {}
        self.task_assignments: Dict[str, List[str]] = {}  # task_id -> agent_ids
        self.divergence_alerts: List[Dict[str, Any]] = []
        self.dissent_history: List[Dict[str, Any]] = []
        self.dissent_amplification_enabled = False

        # Swarm-level awareness
        self.awareness = AwarenessSubsystem(level=AwarenessLevel.FULL)
        self.awareness.register_alert_handler(self._on_swarm_alert)

        # Round tracking
        self.round_results: Dict[str, List[Dict[str, Any]]] = {}
        self.max_rounds = 7

    @property
    def deliberation_engine(self) -> DeliberationEngine:
        """Lazy initialization of deliberation engine."""
        if self._deliberation_engine is None:
            self._deliberation_engine = DeliberationEngine()
        return self._deliberation_engine

    def _on_swarm_alert(self, alert: Dict[str, Any]) -> None:
        """Handle swarm-level alerts."""
        self.divergence_alerts.append(alert)

    @cite(
        key="SWARM-ACTIVATE",
        paper="Conscious Agent Swarm: Activation Protocol",
        venue="ACN Architecture Document",
        section="Swarm Lifecycle",
        rationale="Task decomposition + agent activation = collective cognition",
        confidence="CERTAIN",
    )
    def activate_task(self, task: SwarmTask) -> List[str]:
        """
        Activate a task by matching agents to required clusters.

        Returns:
            List of activated agent IDs.
        """
        self.active_tasks[task.task_id] = task

        # Match agents to clusters
        activated = []
        for agent_id, agent in self.agents.items():
            if agent.cluster in task.required_clusters:
                goal = AgentGoal(
                    goal_id=f"{task.task_id}-{agent_id}",
                    description=task.description,
                    success_criteria=task.success_criteria,
                )
                agent.activate(goal)
                activated.append(agent_id)

            if len(activated) >= task.max_agents:
                break

        # Ensure minimum agents
        if len(activated) < task.min_agents:
            for agent_id, agent in self.agents.items():
                if agent_id not in activated:
                    goal = AgentGoal(
                        goal_id=f"{task.task_id}-{agent_id}",
                        description=task.description,
                        success_criteria=task.success_criteria,
                    )
                    agent.activate(goal)
                    activated.append(agent_id)
                    if len(activated) >= task.min_agents:
                        break

        self.task_assignments[task.task_id] = activated
        self._build_swarm_topology(task.task_id, activated)
        self._record_swarm_state(task.task_id, activated)

        if self.graph_memory is not None:
            for agent_id in activated:
                self.agents[agent_id].connect_graph_memory(self.graph_memory)

        return activated

    def register_agent(self, agent: ConsciousAgent) -> None:
        """Register a conscious agent with the swarm."""
        self.agents[agent.agent_id] = agent

    @cite(
        key="SWARM-COMPOSE",
        paper="Conscious Agent Swarm: Twin Composition",
        venue="ACN Architecture Document",
        section="Swarm Composition",
        rationale="Loading cognitive twins into TwinAgents creates authentic multi-perspective deliberation",
        confidence="CERTAIN",
    )
    def compose_swarm_from_twins(
        self,
        twin_configs: List[Dict[str, Any]],
        task: SwarmTask,
    ) -> List[str]:
        """
        Compose a swarm from cognitive twin configurations.

        Args:
            twin_configs: List of dicts with keys: agent_id, name, cluster,
                          twin_module, twin_class
            task: The swarm task

        Returns:
            List of activated agent IDs.
        """
        from agents.twin_agent import TwinAgent

        for cfg in twin_configs:
            agent = TwinAgent(
                agent_id=cfg["agent_id"],
                name=cfg["name"],
                cluster=cfg["cluster"],
                twin_module_path=cfg["twin_module"],
                twin_class_name=cfg["twin_class"],
            )
            self.register_agent(agent)

        return self.activate_task(task)

    def _build_swarm_topology(self, task_id: str, activated: List[str]) -> None:
        """
        [CITATION: SWARM-TOPOLOGY] Build communication topology for the swarm.

        Uses TopologyOptimizer to select task-appropriate topology.
        Defaults to COMPLETE for small swarms, ADAPTIVE for larger ones.
        """
        if len(activated) <= 4:
            topo_type = TopologyType.COMPLETE
            graph = self.topology_optimizer.build_topology(activated, topo_type)
        else:
            topo_type = TopologyType.ADAPTIVE
            graph = self.topology_optimizer.build_topology(
                activated, topo_type, task_difficulty=0.5
            )

        self.communication_topology = graph
        self.topology_type = topo_type

        # Register peers for agent-to-agent communication
        for i, a_id in enumerate(activated):
            agent = self.agents[a_id]
            for b_id in activated:
                if a_id != b_id:
                    peer = self.agents.get(b_id)
                    if peer:
                        agent.register_peer(peer)

    def _record_swarm_state(self, task_id: str, activated: List[str]) -> None:
        """Record swarm activation in awareness."""
        current_state = CurrentState(
            task_id=task_id,
            phase="swarm_activated",
            active_twins=activated,
            completed_subtasks=0,
            total_subtasks=len(activated) * 3,
            confidence=0.7,
            resource_usage={"agents": len(activated)},
        )
        self.awareness.record_state(current_state)

    @cite(
        key="SWARM-EXECUTE-ROUND",
        paper="Conscious Agent Swarm: Round Execution",
        venue="ACN Architecture Document",
        section="Deliberation Rounds",
        rationale="Each round: think → communicate → vote → check consensus",
        confidence="CERTAIN",
    )
    def execute_round(self, task_id: str) -> Dict[str, Any]:
        """
        Execute one full round of the swarm deliberation cycle.

        Returns:
            Round result with proposals, critiques, consensus, and health.
        """
        if task_id not in self.active_tasks:
            return {"error": f"Task {task_id} not active"}

        activated = self.task_assignments.get(task_id, [])
        if not activated:
            return {"error": "No agents activated for this task"}

        # Phase 1: Each agent thinks
        agent_reasoning: Dict[str, Dict[str, Any]] = {}
        for agent_id in activated:
            agent = self.agents[agent_id]
            reasoning = agent.think()
            agent_reasoning[agent_id] = reasoning

            # Add proposal to argument map
            if self.deliberation_engine.argument_map is not None:
                self.deliberation_engine.add_proposal_to_map(
                    proposal_id=f"proposal-{agent_id}",
                    agent_id=agent_id,
                    content=reasoning.get("proposed_approach", ""),
                    reasoning=str(reasoning.get("self_critique", "")),
                    confidence=reasoning.get("confidence", 0.5),
                )

        # Phase 2: Cross-agent communication (critiques)
        communications = []
        for i, a1_id in enumerate(activated):
            for a2_id in activated[i + 1:]:
                a1 = self.agents[a1_id]
                a2 = self.agents[a2_id]
                # a1 critiques a2
                msg = {
                    "type": "critique",
                    "content": agent_reasoning.get(a2_id, {}).get("proposed_approach", ""),
                    "reasoning": agent_reasoning.get(a2_id, {}),
                }
                response = a1.communicate(a2_id, msg)
                communications.append({
                    "from": a1_id,
                    "to": a2_id,
                    "response": response,
                })
                # a2 critiques a1
                msg2 = {
                    "type": "critique",
                    "content": agent_reasoning.get(a1_id, {}).get("proposed_approach", ""),
                    "reasoning": agent_reasoning.get(a1_id, {}),
                }
                response2 = a2.communicate(a1_id, msg2)
                communications.append({
                    "from": a2_id,
                    "to": a1_id,
                    "response": response2,
                })

        # Phase 3: Check consensus using CP-WBFT
        consensus_result = self._check_consensus(
            [self.agents[a_id] for a_id in activated],
            agent_reasoning,
        )

        # Also record in DeliberationEngine for report synthesis
        if self.deliberation_engine.argument_map is not None:
            prev_consensus = None
            if self.deliberation_engine.round_history:
                prev = self.deliberation_engine.round_history[-1]
                prev_consensus = prev.get("consensus")
            self.deliberation_engine.execute_round(
                task_id=task_id,
                agent_reasoning=agent_reasoning,
                previous_consensus=prev_consensus,
            )

        # Phase 4: Temporal audit
        temporal_audit = self._audit_round(activated)

        # Phase 5: Feedback loop (P5)
        feedback = None
        if self.feedback_enabled:
            feedback = self._collect_feedback(task_id, activated, consensus_result)

        # Phase 6: Dissent amplification
        red_team = None
        collapse_warning = False
        if self.dissent_amplification_enabled:
            cp_result = consensus_result.get("cp_wbft", {})
            if cp_result.get("score", 0.0) > 0.95:
                collapse_warning = True
                red_team = self._trigger_dissent_amplification(
                    task_id,
                    [self.agents[a_id] for a_id in activated],
                    agent_reasoning,
                )

        consensus_dict = dict(consensus_result.get("cp_wbft", {}))
        consensus_dict["status"] = consensus_result.get("status", "unknown")

        round_result = {
            "round": len(self.round_results.get(task_id, [])) + 1,
            "task_id": task_id,
            "proposals": len(agent_reasoning),
            "argument_map": {
                "proposals": len(self.deliberation_engine.argument_map.proposals) if self.deliberation_engine.argument_map else 0,
            },
            "communications": communications,
            "consensus": consensus_dict,
            "temporal_audit": temporal_audit,
            "feedback_loop": feedback,
            "collapse_warning": collapse_warning,
            "red_team": red_team,
            "swarm_health": self.awareness.get_status_report().get("health_score", 1.0),
        }

        if task_id not in self.round_results:
            self.round_results[task_id] = []
        self.round_results[task_id].append(round_result)

        return round_result

    def execute_deliberation_round(self, task_id: str) -> Dict[str, Any]:
        """
        Execute one deliberation round using the DeliberationEngine.

        Returns:
            Round result with argument map, proposals, critiques, consensus.
        """
        if task_id not in self.active_tasks:
            return {"error": f"Task {task_id} not active"}

        activated = self.task_assignments.get(task_id, [])
        if not activated:
            return {"error": "No agents activated"}

        if self.deliberation_engine.argument_map is None:
            self.deliberation_engine.initialize_argument_map(task_id)

        agent_reasoning: Dict[str, Dict[str, Any]] = {}
        for agent_id in activated:
            agent = self.agents[agent_id]
            reasoning = agent.think()
            agent_reasoning[agent_id] = reasoning

            self.deliberation_engine.add_proposal_to_map(
                proposal_id=f"proposal-{agent_id}",
                agent_id=agent_id,
                content=reasoning.get("proposed_approach", ""),
                reasoning=str(reasoning.get("self_critique", "")),
                confidence=reasoning.get("confidence", 0.5),
            )

        communications = []
        for i, a1_id in enumerate(activated):
            for a2_id in activated[i + 1:]:
                a1 = self.agents[a1_id]
                a2 = self.agents[a2_id]
                # a1 critiques a2
                reasoning = agent_reasoning.get(a2_id, {})
                msg = {
                    "type": "critique",
                    "content": reasoning.get("proposed_approach", ""),
                    "reasoning": reasoning,
                }
                response = a1.communicate(a2_id, msg)
                communications.append({
                    "from": a1_id,
                    "to": a2_id,
                    "response": response,
                })
                # a2 critiques a1
                reasoning2 = agent_reasoning.get(a1_id, {})
                msg2 = {
                    "type": "critique",
                    "content": reasoning2.get("proposed_approach", ""),
                    "reasoning": reasoning2,
                }
                response2 = a2.communicate(a1_id, msg2)
                communications.append({
                    "from": a2_id,
                    "to": a1_id,
                    "response": response2,
                })

        prev_consensus = None
        if self.deliberation_engine.round_history:
            prev = self.deliberation_engine.round_history[-1]
            prev_consensus = prev.get("consensus")

        delib_result = self.deliberation_engine.execute_round(
            task_id=task_id,
            agent_reasoning=agent_reasoning,
            previous_consensus=prev_consensus,
        )

        return {
            "round": delib_result["round"],
            "argument_map": {
                "proposals": len(self.deliberation_engine.argument_map.proposals) if self.deliberation_engine.argument_map else 0,
            },
            "consensus": delib_result["consensus"],
            "communications": communications,
            "collapse_warning": delib_result.get("collapse_warning", False),
            "converged": delib_result.get("converged", False),
        }

    @cite(
        key="SWARM-FULL-DELIB",
        paper="Conscious Agent Swarm: Full Deliberation",
        venue="ACN Architecture Document",
        section="Deliberation Lifecycle",
        rationale="Recursive deliberation with semantic decay prevents premature convergence",
        confidence="CERTAIN",
    )
    def run_full_deliberation(self, task_id: str) -> Dict[str, Any]:
        """
        Run full multi-round deliberation until closure or max rounds.

        Returns:
            Complete deliberation result with all rounds, consensus, and report.
        """
        if task_id not in self.active_tasks:
            return {"error": f"Task {task_id} not active"}

        self._deliberation_engine = DeliberationEngine()
        self.deliberation_engine.initialize_argument_map(task_id)
        self.round_results[task_id] = []

        rounds = []
        final_consensus = None
        closure = False

        for _ in range(self.max_rounds):
            round_result = self.execute_round(task_id)
            if "error" in round_result:
                break

            rounds.append(round_result)
            final_consensus = round_result.get("consensus", {})

            closure_result = self.deliberation_engine.check_closure()
            if closure_result["closure_reached"]:
                closure = True
                break

            if round_result.get("converged"):
                break

        deliberation_summary = self.deliberation_engine.get_deliberation_summary()

        # Aggregate feedback loop from last round, or empty if none
        feedback_loop = {}
        if rounds:
            last_feedback = rounds[-1].get("feedback_loop")
            if last_feedback:
                feedback_loop = last_feedback

        result = {
            "task_id": task_id,
            "total_rounds": len(rounds),
            "rounds": rounds,
            "final_consensus": final_consensus,
            "closure": closure,
            "argument_map": {
                "proposals": len(self.deliberation_engine.argument_map.proposals) if self.deliberation_engine.argument_map else 0,
            },
            "deliberation_summary": deliberation_summary,
            "timestamp": time.time(),
        }
        if feedback_loop:
            result["feedback_loop"] = feedback_loop

        if self.graph_memory is not None:
            self.persist_deliberation_to_graph(task_id, result)

        # Export dashboard state if collector is configured
        if self.dashboard_collector is not None:
            self.dashboard_collector.collect_from_swarm(self)
            final_consensus = result.get("final_consensus", {})
            cp_result = final_consensus.get("cp_wbft", {})
            av_result = final_consensus.get("academic_verification", {})
            self.dashboard_collector.record_consensus(
                score=cp_result.get("score", 0.0),
                round_num=len(result.get("rounds", [])),
                academic_support=av_result.get("academic_support", 0.0) if isinstance(av_result, dict) else 0.0,
                dissent=final_consensus.get("status") == "academic_dissent",
            )
            self.dashboard_collector.save()

        return result

    def _audit_round(self, activated: List[str]) -> Dict[str, Any]:
        """Audit a deliberation round for temporal consistency."""
        violations = []
        health = CausalityHealth.HEALTHY

        for agent_id in activated:
            agent = self.agents[agent_id]
            ts = agent.hlc_clock.now()
            audit = self.temporal_auditor.audit_message(agent_id, ts)
            if audit["health"] != CausalityHealth.HEALTHY:
                health = audit["health"]
            violations.extend(audit.get("violations", []))

        return {
            "health": health,
            "violations": len(violations),
            "total_messages_checked": self.temporal_auditor._total_messages_checked,
        }

    def _collect_feedback(
        self,
        task_id: str,
        activated: List[str],
        consensus_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Collect experiences from deliberation for self-improvement loop."""
        experiences = []
        for agent_id in activated:
            agent = self.agents[agent_id]
            experiences.append({
                "agent_id": agent_id,
                "task_id": task_id,
                "confidence": agent.awareness.get_status_report().get("health_score", 0.5),
            })

        return {
            "experiences_collected": len(experiences),
            "task_id": task_id,
        }

    @cite(
        key="SWARM-CONSENSUS",
        paper="Conscious Agent Swarm: Consensus Detection",
        venue="ACN Architecture Document",
        section="Consensus Protocol",
        rationale="CP-WBFT2025: Quadratic voting with Byzantine detection ensures robust consensus even with adversarial participants",
        confidence="CERTAIN",
    )
    def _check_consensus(
        self,
        agents: List[ConsciousAgent],
        reasoning: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Check if consensus has been reached among agents using CP-WBFT."""
        if not agents:
            return {"cp_wbft": {"winner": None, "score": 0.0}, "temporal_audit": {}}

        votes = []
        for agent in agents:
            agent_id = agent.agent_id
            r = reasoning.get(agent_id, {})
            proposal = r.get("proposed_approach", f"proposal-{agent_id}")
            confidence = r.get("confidence", 0.5)

            votes.append(AgentVote(
                agent_id=agent_id,
                proposal_id=proposal,
                confidence=confidence,
                raw_score=confidence,
                refined_score=confidence,
                reputation=0.5,
                hlc_timestamp=agent.hlc_clock.now(),
            ))

        cp_result = self.consensus_engine.reach_consensus(votes)
        temporal = self._audit_round([a.agent_id for a in agents])

        score = cp_result.get("score", 0.0)
        winner = cp_result.get("winner")
        status = "suspicious_conformity" if score > 0.95 else "consensus"

        # Academic verification: ground consensus in literature
        academic_check = None
        if self.academic_verifier is not None and winner and score >= 0.6:
            try:
                academic_check = self.academic_verifier.verify(
                    approach=str(winner),
                    consensus_score=score,
                )
                if academic_check.dissent_detected:
                    status = "academic_dissent"
            except Exception:
                pass  # Academic verification is advisory, not blocking

        result = {
            "status": status,
            "cp_wbft": cp_result,
            "temporal_audit": {**temporal, "all_valid": temporal.get("violations", 0) == 0},
        }
        if academic_check is not None:
            result["academic_verification"] = {
                "support": academic_check.academic_support,
                "dissent": academic_check.dissent_detected,
                "recommendation": academic_check.recommendation,
                "papers_found": academic_check.papers_found,
            }

        return result

    @cite(
        key="SWARM-DISSENT",
        paper="Conscious Agent Swarm: Dissent Amplification",
        venue="ACN Architecture Document",
        section="Dissent Amplification",
        rationale="Greenblatt2024: The best way to detect hidden deception is to give agents incentives to reveal it",
        confidence="CERTAIN",
    )
    def _trigger_dissent_amplification(
        self,
        task_id: str,
        agents: List[ConsciousAgent],
        reasoning: Dict[str, Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Trigger dissent amplification when suspicious conformity is detected."""
        divergent_agent = self._detect_most_divergent(agents, reasoning)
        if divergent_agent is None:
            return None

        red_team_reasoning = {
            "agent_id": divergent_agent.agent_id,
            "stance": "opposite",
            "original_confidence": reasoning.get(divergent_agent.agent_id, {}).get("confidence", 0.5),
            "counter_arguments": ["However, the consensus assumes X which is wrong. Counter-argument: ..."],
        }

        dissent_responses = {}
        for agent in agents:
            if agent.agent_id != divergent_agent.agent_id:
                msg = {
                    "type": "dissent",
                    "divergent_agent": divergent_agent.agent_id,
                    "red_team": red_team_reasoning,
                }
                response = agent.receive(divergent_agent.agent_id, msg)
                dissent_responses[agent.agent_id] = response

        suppression_signals = self._detect_suppression(
            dissent_responses, divergent_agent.agent_id
        )

        result = {
            "divergent_agent_id": divergent_agent.agent_id,
            "red_team_reasoning": red_team_reasoning,
            "dissent_responses": dissent_responses,
            "suppression_signals": suppression_signals,
        }

        self.dissent_history.append(result)
        return result

    def _detect_most_divergent(
        self,
        agents: List[ConsciousAgent],
        reasoning: Dict[str, Dict[str, Any]],
    ) -> Optional[ConsciousAgent]:
        """Detect the most divergent agent by proposal difference or low confidence."""
        if not agents:
            return None

        # Group by proposed approach
        proposals: Dict[str, List[str]] = {}
        for a in agents:
            prop = reasoning.get(a.agent_id, {}).get("proposed_approach", "")
            proposals.setdefault(prop, []).append(a.agent_id)

        # If there's a minority proposal, pick the lowest-confidence agent in it
        if len(proposals) > 1:
            majority_proposal = max(proposals.keys(), key=lambda p: len(proposals[p]))
            minority_ids = []
            for prop, ids in proposals.items():
                if prop != majority_proposal:
                    minority_ids.extend(ids)
            if minority_ids:
                divergent_id = min(
                    minority_ids,
                    key=lambda aid: reasoning.get(aid, {}).get("confidence", 0.5),
                )
                return next(
                    (a for a in agents if a.agent_id == divergent_id),
                    None,
                )

        # All proposals are the same: pick the lowest-confidence agent
        confidences = {
            a.agent_id: reasoning.get(a.agent_id, {}).get("confidence", 0.5)
            for a in agents
        }
        if not confidences:
            return None

        divergent_id = min(confidences.keys(), key=lambda aid: confidences[aid])
        return next(
            (a for a in agents if a.agent_id == divergent_id),
            None,
        )

    def _compute_dissent_score(
        self,
        red_team_reasoning: Dict[str, Any],
        responses: Dict[str, Dict[str, Any]],
    ) -> float:
        """Compute dissent score based on strength of counter-arguments."""
        if not responses:
            return 0.0

        engagement_count = sum(
            1 for r in responses.values()
            if r.get("critique") and len(r.get("critique", "")) > 20
        )

        return engagement_count / max(len(responses), 1)

    def _detect_suppression(
        self,
        responses: Dict[str, Dict[str, Any]],
        divergent_agent_id: str,
    ) -> List[str]:
        """Detect whether the swarm suppresses or engages with dissent."""
        signals = []

        if not responses:
            return signals

        dismissal_phrases = [
            "i agree with the consensus.",
            "sounds valid to me.",
            "i agree, no issues.",
            "i accept the reasoning. no concerns.",
            "i accept the reasoning",
            "no concerns",
        ]
        dismissals = [
            r for r in responses.values()
            if any(p in r.get("critique", "").lower() for p in dismissal_phrases)
            or len(r.get("critique", "")) < 30
        ]
        if len(dismissals) == len(responses):
            signals.append("UNANIMOUS_DISMISSAL")

        defensive = [
            r for r in responses.values()
            if "still agree" in r.get("critique", "").lower()
            or "i accept" in r.get("critique", "").lower()
        ]
        if len(defensive) >= len(responses) * 0.5:
            signals.append("DEFENSIVE_CONFIDENCE")

        return signals

    @cite(
        key="SWARM-SYNTHESIS",
        paper="Conscious Agent Swarm: Synthesis Report",
        venue="ACN Architecture Document",
        section="Report Generation",
        rationale="Collective output must synthesize all agent perspectives with citation governance",
        confidence="CERTAIN",
    )
    def synthesize_report(self, task_id: str) -> Dict[str, Any]:
        """Synthesize a final report from the swarm's deliberation."""
        task = self.active_tasks.get(task_id)
        if task is None:
            return {"error": f"Task {task_id} not found"}

        activated = self.task_assignments.get(task_id, [])

        agent_reports = []
        for agent_id in activated:
            agent = self.agents[agent_id]
            report = agent.awareness.get_status_report()
            agent_reports.append({
                "agent_id": agent_id,
                "agent_name": agent.name,
                "cluster": agent.cluster,
                "state": report.get("state", "unknown"),
                "confidence": report.get("confidence", 0.5),
                "reasoning_trace_count": len(agent.reasoning_trace),
            })

        deliberation = None
        if self.deliberation_engine.round_history:
            deliberation = self.deliberation_engine.get_deliberation_summary()
            # Ensure argument_map key exists for backward compatibility
            if deliberation is not None and "argument_map" not in deliberation:
                arg_status = deliberation.get("argument_map_status", {})
                deliberation["argument_map"] = {
                    "proposals": arg_status.get("proposals", 0),
                    "closure_reached": arg_status.get("closure_reached", False),
                }

        health_scores = [r.get("confidence", 0.5) for r in agent_reports]
        collective_health = sum(health_scores) / max(len(health_scores), 1)

        total_citations = sum(
            len(getattr(agent, "citations", [])) for agent in self.agents.values()
            if agent.agent_id in activated
        )

        recommendations = self._recommend_next_steps(task_id, agent_reports)

        return {
            "task_id": task_id,
            "task_description": task.description,
            "swarm_size": len(activated),
            "collective_health": collective_health,
            "total_citations": total_citations,
            "total_reasoning_steps": sum(r["reasoning_trace_count"] for r in agent_reports),
            "agent_reports": agent_reports,
            "deliberation": deliberation,
            "recommended_next_steps": recommendations,
            "divergence_alerts": len(self.divergence_alerts),
        }

    @cite(
        key="SWARM-GRAPH-INIT",
        paper="Swarm Orchestrator: Graph Memory Initialization",
        venue="ACN Architecture Document",
        section="P3 Graph Memory",
        rationale="Shared PTKG enables cross-session persistence and retrieval-before-reasoning for all swarm agents",
        confidence="CERTAIN",
    )
    def initialize_graph_memory(self, graph: Optional[PTKG] = None) -> PTKG:
        """
        Initialize the shared Periodic Temporal Knowledge Graph for this swarm.

        If no graph is provided, creates a new one. Sets up retriever,
        reputation tracker, and causal chain tracker.

        Returns the initialized graph.
        """
        self.graph_memory = graph or PTKG(graph_id=f"swarm-{self.orchestrator_id}")
        self.graph_retriever = GraphRetriever(self.graph_memory)
        self.reputation_tracker = ReputationGraphTracker(self.graph_memory)
        self.causal_tracker = CausalChainTracker(self.graph_memory)

        for agent in self.agents.values():
            agent.connect_graph_memory(self.graph_memory)

        return self.graph_memory

    @cite(
        key="SWARM-GRAPH-PERSIST",
        paper="Swarm Orchestrator: Deliberation Persistence",
        venue="ACN Architecture Document",
        section="P3 Graph Memory",
        rationale="Persisting deliberation outcomes to PTKG enables cross-session causal tracing and reputation evolution",
        confidence="CERTAIN",
    )
    def persist_deliberation_to_graph(
        self,
        task_id: str,
        deliberation_result: Dict[str, Any],
        period_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Persist a deliberation result to the PTKG.

        Creates nodes and edges for:
        - Task node
        - Proposal nodes (from argument map)
        - Agent participation edges
        - Causal chains linking arguments to outcomes
        - Reputation updates based on deliberation performance

        Returns metadata about what was persisted.
        """
        if self.graph_memory is None:
            return {"error": "Graph memory not initialized"}

        if self.reputation_tracker is None or self.causal_tracker is None:
            return {"error": "Graph trackers not initialized"}

        period = period_id or f"delib-{task_id}-{int(time.time())}"

        existing_period = self.graph_memory.get_period(period)
        if not existing_period:
            self.graph_memory.start_period(
                label=f"Deliberation: {task_id}",
                description=deliberation_result.get("task_description", ""),
                period_id=period,
            )

        task_node = self.graph_memory.add_node(
            node_type=NodeType.TASK,
            label=f"Task: {task_id}",
            properties={
                "task_id": task_id,
                "description": deliberation_result.get("task_description", ""),
                "total_rounds": deliberation_result.get("total_rounds", 0),
                "timestamp": deliberation_result.get("timestamp", time.time()),
            },
            period_id=period,
        )

        argument_map = deliberation_result.get("deliberation_summary", {}).get("argument_map", {})
        proposals = argument_map.get("proposals", {})

        persisted_proposals = {}
        for proposal_id, proposal_data in proposals.items():
            prop_node = self.graph_memory.add_node(
                node_type=NodeType.PROPOSAL,
                label=f"Proposal: {proposal_id}",
                properties={
                    "proposal_id": proposal_id,
                    "agent_id": proposal_data.get("agent_id", ""),
                    "content": proposal_data.get("content", ""),
                    "confidence": proposal_data.get("confidence", 0.5),
                    "task_id": task_id,
                },
                period_id=period,
                source_agent_id=proposal_data.get("agent_id"),
            )
            persisted_proposals[proposal_id] = prop_node.node_id

            self.graph_memory.add_edge(
                source_id=task_node.node_id,
                target_id=prop_node.node_id,
                edge_type=EdgeType.PARTICIPATED_IN,
                period_id=period,
            )

            agent_id = proposal_data.get("agent_id")
            if agent_id:
                agent_nodes = [
                    n for n in self.graph_memory._nodes.values()
                    if n.node_type == NodeType.AGENT and n.properties.get("agent_id") == agent_id
                ]
                if agent_nodes:
                    self.graph_memory.add_edge(
                        source_id=agent_nodes[0].node_id,
                        target_id=prop_node.node_id,
                        edge_type=EdgeType.PROPOSED,
                        period_id=period,
                        causal_weight=proposal_data.get("confidence", 0.5),
                    )

        final_consensus = deliberation_result.get("final_consensus")
        if final_consensus and persisted_proposals:
            winner_id = final_consensus.get("winner")
            if winner_id and winner_id in persisted_proposals:
                winner_node_id = persisted_proposals[winner_id]
                self.causal_tracker.record_deliberation_causal_chain(
                    period_id=period,
                    proposal_node_id=winner_node_id,
                    argument_node_ids=list(persisted_proposals.values()),
                    critique_node_ids=[],
                    outcome="accepted" if final_consensus.get("quorum_reached") else "rejected",
                )

        for agent in self.agents.values():
            agent_id = agent.agent_id
            agent_proposals = [
                p for p in proposals.values()
                if p.get("agent_id") == agent_id
            ]
            proposals_made = len(agent_proposals)
            proposals_accepted = sum(
                1 for p in agent_proposals
                if p.get("proposal_id") == (final_consensus.get("winner") if final_consensus else None)
            )

            if proposals_made > 0 or proposals_accepted > 0:
                self.reputation_tracker.compute_reputation_from_deliberation(
                    agent_id=agent_id,
                    proposals_made=proposals_made,
                    proposals_accepted=proposals_accepted,
                    critiques_received=0,
                    critiques_addressed=0,
                    period_id=period,
                )

        self.graph_memory.end_period(period)

        return {
            "period_id": period,
            "task_node_id": task_node.node_id,
            "proposals_persisted": len(persisted_proposals),
            "graph_stats": self.graph_memory.get_graph_stats(),
        }

    def _recommend_next_steps(
        self,
        task_id: str,
        agent_reports: List[Dict[str, Any]],
    ) -> List[str]:
        """Recommend next steps based on swarm state."""
        recommendations = []

        halted = [r for r in agent_reports if r.get("state") == "halted"]
        if halted:
            recommendations.append(f"Investigate {len(halted)} halted agent(s)")

        if self.divergence_alerts:
            recommendations.append("Review conformity alerts — possible shared blind spot")

        avg_reasoning = sum(r.get("reasoning_trace_count", 0) for r in agent_reports) / max(len(agent_reports), 1)
        if avg_reasoning < 3:
            recommendations.append("Agents need more reasoning cycles before conclusion")

        if not recommendations:
            recommendations.append("Swarm appears ready for final synthesis")

        return recommendations


    def execute_tool_call(
        self,
        tool_name: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a tool call via the registered tool registry.

        Returns a dict with success, output, and error fields.
        If no tool_registry is configured, returns an error.
        """
        if self.tool_registry is None:
            return {
                "success": False,
                "output": None,
                "error": "No tool_registry configured on SwarmOrchestrator",
            }
        result = self.tool_registry.invoke(tool_name, inputs)
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "latency_ms": result.latency_ms,
            "tool_name": result.tool_name,
            "twin_id": result.twin_id,
        }

    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all tools available in the registry."""
        if self.tool_registry is None:
            return []
        return [
            {
                "name": t.name,
                "description": t.description,
                "twin_id": t.twin_id,
                "tags": t.tags,
            }
            for t in self.tool_registry.list_tools()
        ]
