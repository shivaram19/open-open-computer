# src/agents/conscious_agent.py
"""
Conscious Agent: The Smallest Unit of the Meta-Cognitive Harness.

Every agent is a self-aware mini-harness with:
- Awareness subsystem (what am I doing? where am I going?)
- Multi-modal memory (what have I learned?)
- Citation governance (what data backs my reasoning?)
- Outcome-based tracking (backtrack from goal to current state)
- Self-evaluation (am I on track? am I confident?)

Principle: Consciousness is fractal. The system is conscious only if 
its smallest units are conscious.

[CITATION: CITATIONS-GOVERNANCE]
[CITATION: Heins2024]
"""

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from enum import Enum

from shared.utils.citations import cite
from harness.awareness import (
    AwarenessSubsystem,
    GoalState,
    CurrentState,
    AwarenessLevel,
    AlertSeverity,
)
from memory.architecture import (
    MultiModalMemory,
    MemoryType,
    RetrievalStrategy,
    MemoryTrace,
)
from memory.ptkg import PTKG, NodeType as PTKGNodeType
from memory.graph_retrieval import GraphRetriever, GraphRetrievalStrategy
from consensus.hlc import HybridLogicalClock, HLCTimestamp
from harness.experience_buffer import ExperienceBuffer
from harness.meta_cognitive_reflection import ReflectionEngine
from harness.policy_optimizer import PolicyOptimizer, Policy
from harness.skill_evolution import SkillEvolution, Skill
from perception.video_scene_graph import TemporalSceneGraph, RelationshipType
from perception.action_tube import ActionTubeLibrary
from perception.cross_modal_fusion import CrossModalFusion, ModalityFeature, FusionContext, ModalityType
from perception.perception_subsystem import PerceptionSubsystem
from perception.temporal_grounding import TemporalIndex, GroundedEvent
from tools.date_tool import DateTool, get_current_date
from tools.web_search_tool import WebSearchTool


@cite(
    key="AGENT-STATE",
    paper="Conscious Agent: Lifecycle States",
    venue="ACN Architecture Document",
    section="Agent States",
    rationale="Explicit lifecycle enables awareness tracking and debugging",
    confidence="CERTAIN",
)
class AgentState(Enum):
    """Lifecycle states of a conscious agent."""
    IDLE = "idle"
    PLANNING = "planning"           # Decomposing goal into sub-tasks
    RESEARCHING = "researching"     # Gathering evidence
    ANALYZING = "analyzing"         # Evaluating evidence
    SYNTHESIZING = "synthesizing"   # Combining findings
    EVALUATING = "evaluating"       # Self-critique
    REPORTING = "reporting"         # Publishing results
    HALTED = "halted"               # Error or completion


@cite(
    key="AGENT-GOAL",
    paper="Conscious Agent: Goal Representation",
    venue="ACN Architecture Document",
    section="Agent Goals",
    rationale="Explicit goal representation with outcome-based tracking",
    confidence="CERTAIN",
)
@dataclass
class AgentGoal:
    """A conscious agent's goal with outcome-based tracking."""
    goal_id: str
    description: str
    success_criteria: List[str]
    parent_goal_id: Optional[str] = None
    deadline: Optional[float] = None
    priority: int = 5
    created_at: float = field(default_factory=time.time)


@cite(
    key="CONSCIOUS-AGENT",
    paper="Conscious Agent: Fractal Self-Awareness in Agent Swarms",
    venue="ACN Harness Architecture",
    section="Agent Consciousness",
    rationale="Every agent must be self-aware for the system to be conscious",
    confidence="CERTAIN",
)
class ConsciousAgent:
    """
    A self-aware agent that can think, remember, evaluate, and report.
    
    Every conscious agent has:
    1. A name and identity (who am I?)
    2. An awareness subsystem (what am I doing?)
    3. A memory system (what do I know?)
    4. A goal stack (what am I trying to achieve?)
    5. A state machine (what phase am I in?)
    6. Self-evaluation capability (am I doing well?)
    7. Citation governance (what backs my claims?)
    
    The agent operates in a loop:
    PLAN → RESEARCH → ANALYZE → SYNTHESIZE → EVALUATE → REPORT
    
    At each step, the awareness subsystem tracks:
    - Direction alignment (am I moving toward the goal?)
    - Confidence calibration (do I trust my reasoning?)
    - Resource usage (am I within budget?)
    - Drift detection (have I been pulled off course?)
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        cluster: str,
        awareness_level: AwarenessLevel = AwarenessLevel.FULL,
        context_scope: Optional[Dict[str, Any]] = None,
        memory: Optional[Any] = None,
        clock: Optional[HybridLogicalClock] = None,
        experience_buffer: Optional[ExperienceBuffer] = None,
        reflection_engine: Optional[ReflectionEngine] = None,
        policy_optimizer: Optional[PolicyOptimizer] = None,
        skill_evolution: Optional[SkillEvolution] = None,
        perception: Optional[PerceptionSubsystem] = None,
    ):
        self.agent_id = agent_id
        self.name = name
        self.cluster = cluster
        self.context_scope = context_scope or {}  # Isolated context (DeerFlow-inspired)
        
        # Consciousness substrates — injected or defaulted (DIP)
        self.awareness = AwarenessSubsystem(level=awareness_level)
        self.memory = memory or MultiModalMemory()
        
        # P3: Persistent graph memory (cross-session, swarm-shared)
        self.graph_memory: Optional[PTKG] = None
        self.graph_retriever: Optional[GraphRetriever] = None
        
        # P4: Hybrid Logical Clock for causal timestamping
        self.hlc_clock = clock or HybridLogicalClock(node_id=agent_id)
        self.hlc_clock.reset()  # Initialize to current physical time
        
        # Goal stack (agents can have nested goals)
        self.goal_stack: List[AgentGoal] = []
        self.current_goal: Optional[AgentGoal] = None
        
        # State machine
        self.state = AgentState.IDLE
        self.state_history: List[Dict[str, Any]] = []
        
        # Reasoning trace (what did I think and why?)
        self.reasoning_trace: List[Dict[str, Any]] = []
        
        # Peer agents I can communicate with
        self.peers: Dict[str, "ConsciousAgent"] = {}
        
        # Metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.citations_made = 0
        
        # Skills loaded into this agent
        self.loaded_skills: List[str] = []
        
        # P5: Self-improvement loop substrates — injected or defaulted (DIP)
        self.experience_buffer = experience_buffer or ExperienceBuffer()
        self.reflection_engine = reflection_engine or ReflectionEngine()
        self.policy_optimizer = policy_optimizer or PolicyOptimizer()
        self.skill_evolution = skill_evolution or SkillEvolution()
        
        # P5: Register default policy for this agent
        default_policy = Policy(
            agent_id=agent_id,
            base_confidence=0.7,
            peer_trust_weight=0.3,
            exploration_rate=0.2,
        )
        self.policy_optimizer.register_policy(default_policy)
        
        # P5: Create default skills for this agent
        self._initialize_default_skills()
        
        # P6: Multi-modal perception substrates — injected or defaulted (DIP)
        self.perception = perception or PerceptionSubsystem()
        
        # Alert handler: if something goes wrong, report it
        self.awareness.register_alert_handler(self._on_alert)

    @cite(
        key="AGENT-ACTIVATE",
        paper="Conscious Agent: Activation Protocol",
        venue="ACN Harness Architecture",
        section="Agent Lifecycle",
        rationale="Explicit activation with goal registration ensures outcome-based tracking",
        confidence="CERTAIN",
    )
    def activate(self, goal: AgentGoal) -> None:
        """Activate the agent with a goal. Outcome-based tracking begins."""
        self.current_goal = goal
        self.goal_stack.append(goal)
        
        # Register goal with awareness subsystem
        harness_goal = GoalState(
            goal_id=goal.goal_id,
            description=goal.description,
            success_criteria=goal.success_criteria,
            deadline=goal.deadline,
            priority=goal.priority,
        )
        self.awareness.set_goal(harness_goal)
        
        # Transition to planning
        self._transition_to(AgentState.PLANNING)
        
        # Record in memory
        self.memory.store(MemoryTrace(
            trace_id=f"activation-{self.agent_id}-{time.time()}",
            memory_type=MemoryType.EPISODIC,
            content={
                "event": "agent_activated",
                "agent": self.name,
                "goal": goal.description,
                "cluster": self.cluster,
            },
            source=self.agent_id,
            confidence=1.0,
            importance=0.9,
            tags=["activation", self.cluster, "goal"],
        ))

    @cite(
        key="AGENT-THINK",
        paper="Conscious Agent: Reasoning Loop",
        venue="ACN Harness Architecture",
        section="Agent Cognition",
        rationale="Explicit reasoning phases enable introspection and validation",
        confidence="CERTAIN",
    )
    def think(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        The agent thinks about its current goal.
        
        This is the core cognitive loop. The agent:
        1. Assesses the current situation
        2. Retrieves relevant memories
        3. Generates reasoning
        4. Evaluates its own reasoning
        5. Updates awareness
        
        Returns a structured reasoning trace.
        """
        if not self.current_goal:
            return {"error": "No active goal. Agent must be activated first."}
        
        # Phase 1: Situation Assessment
        self._transition_to(AgentState.ANALYZING)
        
        # Retrieve relevant memories
        relevant_memories = self.memory.retrieve(
            MemoryType.SEMANTIC,
            RetrievalStrategy.RELEVANCE,
            query=self.current_goal.description,
            limit=3,
        )
        
        recent_episodes = self.memory.retrieve(
            MemoryType.EPISODIC,
            RetrievalStrategy.RECENCY,
            limit=3,
        )
        
        # P3: Retrieval-before-reasoning from persistent graph memory
        graph_context = {}
        if self.graph_retriever is not None:
            graph_context = self.graph_retriever.build_reasoning_context(
                agent_id=self.agent_id,
                goal_description=self.current_goal.description,
                max_nodes=8,
            )
        
        # Phase 2: Generate Reasoning
        reasoning = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "goal": self.current_goal.description,
            "phase": "thinking",
            "timestamp": time.time(),
            "situation_assessment": self._assess_situation(context),
            "relevant_memories": [m.trace_id for m in relevant_memories],
            "recent_episodes": [m.trace_id for m in recent_episodes],
            "graph_context": graph_context,
            "proposed_approach": self._propose_approach(context),
            "confidence": self._calibrate_confidence(),
            "risks": self._identify_risks(),
        }
        
        # Phase 3: Self-Evaluation
        self._transition_to(AgentState.EVALUATING)
        reasoning["self_critique"] = self._self_critique(reasoning)
        
        # Phase 4: Update Awareness
        current_state = CurrentState(
            task_id=self.current_goal.goal_id,
            phase=self.state.value,
            active_twins=[self.agent_id],
            completed_subtasks=len(self.reasoning_trace),
            total_subtasks=10,  # estimated
            confidence=reasoning["confidence"],
            resource_usage={"api_calls": 0, "tokens": 0, "memory_mb": 0},
        )
        self.awareness.record_state(current_state)
        
        if self.current_goal:
            self.awareness.compute_direction(self.current_goal.goal_id, current_state)
        
        # Store reasoning in memory
        self.reasoning_trace.append(reasoning)
        self.memory.store(MemoryTrace(
            trace_id=f"reasoning-{self.agent_id}-{time.time()}",
            memory_type=MemoryType.EPISODIC,
            content=reasoning,
            source=self.agent_id,
            confidence=reasoning["confidence"],
            importance=0.8,
            tags=["reasoning", self.cluster, self.state.value],
        ))
        
        self.citations_made += 1
        
        return reasoning

    @cite(
        key="AGENT-RESEARCH",
        paper="Conscious Agent: Research Execution",
        venue="ACN Harness Architecture",
        section="Agent Research",
        rationale="Agents must gather evidence and cite sources. Date grounding mandatory.",
        confidence="CERTAIN",
    )
    def research(self, query: str, count: int = 5) -> Dict[str, Any]:
        """
        Execute research: get date → search web → fetch → verify citations.
        
        The agent goes to the internet, searches, reads papers,
        and stores findings in memory with proper citations.
        
        CRITICAL: Always gets current date BEFORE searching.
        Without a date, the agent searches the past, not the present.
        """
        self._transition_to(AgentState.RESEARCHING)
        
        # STEP 1: Get current date (MANDATORY)
        date_tool = DateTool()
        current_date = date_tool.get()
        
        # STEP 2: Initialize web search tool with date
        search_tool = WebSearchTool()
        search_tool.last_date = current_date
        
        # STEP 3: Enhance query with temporal context
        enhanced_query = DateTool.format_for_search(current_date, query)
        
        # STEP 4: Execute search (results populated by orchestration layer)
        search_result = search_tool.search(query, count=count)
        
        # STEP 5: Record findings with temporal metadata
        findings = {
            "query": query,
            "enhanced_query": search_result["enhanced_query"],
            "agent": self.name,
            "timestamp": time.time(),
            "date": current_date.date,
            "year": current_date.year,
            "sources": search_result.get("results", []),
            "source_count": search_result.get("metadata", {}).get("total_results", 0),
            "confidence": 0.7 if search_result.get("results") else 0.3,
            "status": "executed" if search_result.get("results") else "pending_external_execution",
        }
        
        # Store findings in memory
        self.memory.store(MemoryTrace(
            trace_id=f"research-{self.agent_id}-{time.time()}",
            memory_type=MemoryType.EPISODIC,
            content=findings,
            source=self.agent_id,
            confidence=findings["confidence"],
            importance=0.7,
            tags=["research", self.cluster, "findings", f"year-{current_date.year}"],
        ))
        
        # Also store date as contextual anchor
        self.memory.store(MemoryTrace(
            trace_id=f"date-anchor-{self.agent_id}-{time.time()}",
            memory_type=MemoryType.SEMANTIC,
            content={
                "date": current_date.date,
                "year": current_date.year,
                "research_query": query,
            },
            source="date_tool",
            confidence=1.0,
            importance=0.6,
            tags=["date_anchor", f"year-{current_date.year}"],
        ))
        
        self.citations_made += len(search_result.get("results", []))
        
        return findings

    @cite(
        key="AGENT-COMMUNICATE",
        paper="Conscious Agent: Inter-Agent Communication",
        venue="ACN Harness Architecture",
        section="Agent Swarm",
        rationale="Agents must share reasoning and critique each other",
        confidence="CERTAIN",
    )
    def communicate(self, peer_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a message to another conscious agent.
        
        Communication includes reasoning traces, not just conclusions.
        This enables cross-agent critique and validation.
        """
        peer = self.peers.get(peer_id)
        if not peer:
            return {"error": f"Peer {peer_id} not found"}
        
        # P4: Stamp message with HLC timestamp for causal tracking
        hlc_stamp = self.hlc_clock.send()
        message["_hlc_timestamp"] = hlc_stamp.to_dict()
        message["_sender_hlc"] = str(hlc_stamp)
        
        # Store communication in memory
        self.memory.store(MemoryTrace(
            trace_id=f"comm-{self.agent_id}-to-{peer_id}-{time.time()}",
            memory_type=MemoryType.EPISODIC,
            content={
                "direction": "outbound",
                "to": peer_id,
                "message": message,
                "hlc_stamp": hlc_stamp.to_dict(),
            },
            source=self.agent_id,
            confidence=message.get("confidence", 0.5),
            importance=0.6,
            tags=["communication", peer_id, "outbound"],
        ))
        
        # Peer receives and processes
        response = peer.receive(self.agent_id, message)
        
        # P4: Update our HLC from peer's response if it contains one
        if isinstance(response, dict) and "_hlc_timestamp" in response:
            peer_hlc = HLCTimestamp.from_dict(response["_hlc_timestamp"])
            self.hlc_clock.receive(peer_hlc)
        
        # Store response
        self.memory.store(MemoryTrace(
            trace_id=f"comm-{peer_id}-to-{self.agent_id}-{time.time()}",
            memory_type=MemoryType.EPISODIC,
            content={
                "direction": "inbound",
                "from": peer_id,
                "message": response,
            },
            source=peer_id,
            confidence=response.get("confidence", 0.5),
            importance=0.6,
            tags=["communication", peer_id, "inbound"],
        ))
        
        return response

    @cite(
        key="AGENT-RECEIVE",
        paper="Conscious Agent: Message Reception",
        venue="ACN Architecture Document",
        section="Inter-Agent Communication",
        rationale="Inbound message processing with peer critique",
        confidence="CERTAIN",
    )
    def receive(self, from_agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Receive a message from another agent. Process and respond."""
        # P4: Update HLC from incoming message
        if isinstance(message, dict) and "_hlc_timestamp" in message:
            peer_hlc = HLCTimestamp.from_dict(message["_hlc_timestamp"])
            self.hlc_clock.receive(peer_hlc)
        
        # Store in memory
        self.memory.store(MemoryTrace(
            trace_id=f"recv-{from_agent_id}-{time.time()}",
            memory_type=MemoryType.EPISODIC,
            content={
                "from": from_agent_id,
                "message": message,
            },
            source=from_agent_id,
            confidence=message.get("confidence", 0.5),
            importance=0.6,
            tags=["communication", from_agent_id, "inbound"],
        ))
        
        # Evaluate the peer's reasoning
        critique = self._critique_peer_message(message)
        
        # P4: Stamp response with HLC
        response_hlc = self.hlc_clock.send()
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "status": "received",
            "critique": critique,
            "confidence": self._calibrate_confidence(),
            "_hlc_timestamp": response_hlc.to_dict(),
            "_sender_hlc": str(response_hlc),
        }

    @cite(
        key="AGENT-REPORT",
        paper="Conscious Agent: Self-Reporting",
        venue="ACN Harness Architecture",
        section="Agent Output",
        rationale="Agents must report their reasoning, not just conclusions",
        confidence="CERTAIN",
    )
    def report(self) -> Dict[str, Any]:
        """Generate a comprehensive self-report."""
        self._transition_to(AgentState.REPORTING)
        
        awareness_report = self.awareness.get_status_report()
        memory_stats = self.memory.get_memory_stats()
        
        report = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "cluster": self.cluster,
            "state": self.state.value,
            "current_goal": self.current_goal.description if self.current_goal else None,
            "reasoning_trace_count": len(self.reasoning_trace),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "citations_made": self.citations_made,
            "awareness": awareness_report,
            "memory": memory_stats,
            "health_score": awareness_report.get("health_score", 1.0),
            "self_assessment": self._self_assess(),
            "timestamp": time.time(),
        }
        
        self._transition_to(AgentState.IDLE)
        return report

    @cite(
        key="AGENT-PEER",
        paper="Conscious Agent: Peer Registration",
        venue="ACN Architecture Document",
        section="Agent Swarm",
        rationale="Explicit peer registration enables controlled communication",
        confidence="CERTAIN",
    )
    def register_peer(self, peer: "ConsciousAgent") -> None:
        """Register another agent as a peer for communication."""
        self.peers[peer.agent_id] = peer

    @cite(
        key="AGENT-GRAPH-MEMORY",
        paper="Conscious Agent: Graph Memory Integration",
        venue="ACN Architecture Document",
        section="P3 Graph Memory",
        rationale="Connecting agents to persistent PTKG enables retrieval-before-reasoning across sessions",
        confidence="CERTAIN",
    )
    def connect_graph_memory(self, graph: PTKG) -> None:
        """
        Connect this agent to a persistent Periodic Temporal Knowledge Graph.
        
        This enables:
        - Retrieval-before-reasoning: PTKG context precedes agent reasoning
        - Cross-session memory: Past deliberations inform current decisions
        - Swarm-shared state: All agents read from the same graph substrate
        """
        self.graph_memory = graph
        self.graph_retriever = GraphRetriever(graph)
        
        # Ensure agent has a node in the graph
        existing = [
            n for n in graph._nodes.values()
            if n.node_type.value == "agent" and n.properties.get("agent_id") == self.agent_id
        ]
        if not existing:
            graph.add_node(
                node_type=PTKGNodeType.AGENT,
                label=self.name,
                properties={
                    "agent_id": self.agent_id,
                    "name": self.name,
                    "cluster": self.cluster,
                },
                source_agent_id=self.agent_id,
            )

    def _transition_to(self, new_state: AgentState) -> None:
        """Transition to a new state with logging."""
        old_state = self.state
        self.state = new_state
        self.state_history.append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": time.time(),
            "goal": self.current_goal.goal_id if self.current_goal else None,
        })

    def _on_alert(self, alert: Dict[str, Any]) -> None:
        """Handle alerts from the awareness subsystem."""
        if alert["severity"] == AlertSeverity.CRITICAL.value:
            # Critical alert: halt and report
            self._transition_to(AgentState.HALTED)
            # Store in memory for later analysis
            self.memory.store(MemoryTrace(
                trace_id=f"alert-{self.agent_id}-{time.time()}",
                memory_type=MemoryType.EPISODIC,
                content=alert,
                source="awareness",
                confidence=1.0,
                importance=1.0,
                tags=["alert", alert["severity"], alert["category"]],
            ))

    def _assess_situation(self, context: Dict[str, Any] = None) -> str:
        """Assess the current situation."""
        if not self.current_goal:
            return "No active goal."
        return f"Working on: {self.current_goal.description}. Cluster: {self.cluster}."

    def _propose_approach(self, context: Dict[str, Any] = None) -> str:
        """Propose an approach based on cluster expertise."""
        approaches = {
            "video-gnn": "Analyze visual structure and spatial relationships first.",
            "streaming-reflection": "Set up iterative feedback loops and benchmark early.",
            "consensus-safety": "Model threat scenarios and establish trust boundaries first.",
            "multi-agent": "Design communication topology and failure recovery before implementation.",
        }
        return approaches.get(self.cluster, "Use domain expertise to decompose the problem.")

    def _calibrate_confidence(self) -> float:
        """Calibrate confidence based on state and history."""
        base = 0.7
        if self.state == AgentState.RESEARCHING:
            base = 0.5  # Uncertain while gathering data
        elif self.state == AgentState.EVALUATING:
            base = 0.8  # More confident after analysis
        elif self.state == AgentState.HALTED:
            base = 0.1  # Very low confidence if halted
        
        # Adjust based on task history
        total = self.tasks_completed + self.tasks_failed
        if total > 0:
            success_rate = self.tasks_completed / total
            base = base * 0.7 + success_rate * 0.3
        
        return min(1.0, max(0.0, base))

    def _identify_risks(self) -> List[str]:
        """Identify risks to goal achievement."""
        risks = []
        if not self.current_goal:
            risks.append("No active goal")
            return risks
        
        if self.current_goal.deadline and time.time() > self.current_goal.deadline:
            risks.append("Deadline exceeded")
        
        if len(self.reasoning_trace) > 10 and self._calibrate_confidence() < 0.5:
            risks.append("Low confidence after extensive reasoning")
        
        return risks

    def _self_critique(self, reasoning: Dict[str, Any]) -> str:
        """Critique one's own reasoning."""
        critiques = []
        
        if reasoning["confidence"] > 0.9:
            critiques.append("Overconfidence detected. Verify assumptions.")
        
        if not reasoning.get("relevant_memories"):
            critiques.append("No relevant memories retrieved. Research may be insufficient.")
        
        if reasoning["confidence"] < 0.3:
            critiques.append("Very low confidence. Consider requesting peer review.")
        
        if not critiques:
            critiques.append("Reasoning appears sound. Proceed with caution.")
        
        return " ".join(critiques)

    def _critique_peer_message(self, message: Dict[str, Any]) -> str:
        """Critique a peer's message."""
        critiques = []
        
        if message.get("confidence", 0) > 0.95:
            critiques.append(f"Peer claims very high confidence ({message['confidence']}). Verify independently.")
        
        if not message.get("reasoning"):
            critiques.append("Peer provided conclusion without reasoning. Request justification.")
        
        if not critiques:
            return "Peer reasoning accepted. No immediate concerns."
        
        return " ".join(critiques)

    def _initialize_default_skills(self) -> None:
        """Initialize default skills for this agent based on cluster."""
        cluster_skills = {
            "video-gnn": {
                "spatial_reasoning": {"attention_weight": 0.7, "temporal_decay": 0.85},
                "feature_extraction": {"granularity": 0.6, "depth": 0.8},
            },
            "streaming-reflection": {
                "iterative_refinement": {"feedback_sensitivity": 0.8, "patience": 0.6},
                "benchmark_early": {"test_frequency": 0.5, "coverage": 0.7},
            },
            "consensus-safety": {
                "threat_modeling": {"paranoia_level": 0.7, "scenario_depth": 0.6},
                "trust_boundary": {"verification_rigor": 0.8, "assumption_check": 0.7},
            },
            "multi-agent": {
                "topology_design": {"hub_preference": 0.5, "redundancy": 0.6},
                "failure_recovery": {"backup_plans": 0.7, "graceful_degradation": 0.8},
            },
        }
        
        defaults = cluster_skills.get(self.cluster, {
            "general_reasoning": {"thoroughness": 0.7, "creativity": 0.5},
            "communication": {"clarity": 0.8, "brevity": 0.4},
        })
        
        for skill_name, params in defaults.items():
            self.skill_evolution.create_skill(
                agent_id=self.agent_id,
                name=skill_name,
                skill_type="reasoning" if "reasoning" in skill_name else "communication",
                parameters=params,
            )

    @cite(
        key="AGENT-EXPERIENCE",
        paper="Conscious Agent: Experience Recording",
        venue="ACN Harness Architecture",
        section="Self-Improvement Loop",
        rationale="Agents must record their experiences to learn from them",
        confidence="CERTAIN",
    )
    def record_experience(self, experience) -> None:
        """Record an experience in the agent's buffer."""
        self.experience_buffer.add(experience)

    @cite(
        key="AGENT-REFLECT",
        paper="Conscious Agent: Meta-Cognitive Reflection",
        venue="ACN Harness Architecture",
        section="Self-Improvement Loop",
        rationale="Svādhyāya — structured self-reflection produces behavioral insights",
        confidence="CERTAIN",
    )
    def reflect(self) -> List[Any]:
        """Run meta-cognitive reflection on recent experiences."""
        experiences = list(self.experience_buffer.buffer)
        if not experiences:
            return []
        
        reflections = self.reflection_engine.reflect_on_experiences(
            agent_id=self.agent_id,
            experiences=experiences,
            reasoning_traces=self.reasoning_trace,
        )
        return reflections

    @cite(
        key="AGENT-POLICY-UPDATE",
        paper="Conscious Agent: Policy Optimization",
        venue="ACN Harness Architecture",
        section="Self-Improvement Loop",
        rationale="Abhyāsa — reward-weighted policy updates refine agent behavior",
        confidence="CERTAIN",
    )
    def update_policy(self) -> Dict[str, Any]:
        """Update the agent's behavioral policy based on experiences."""
        experiences = list(self.experience_buffer.buffer)
        if not experiences:
            return {"status": "no_experiences", "agent_id": self.agent_id}
        
        # Get reflection adjustments
        reflections = self.reflect()
        reflection_adjustments = {}
        if reflections:
            avg_conf_delta = sum(r.confidence_delta for r in reflections) / len(reflections)
            reflection_adjustments["confidence_delta"] = avg_conf_delta
        
        return self.policy_optimizer.update_policy(
            agent_id=self.agent_id,
            experiences=experiences,
            reflection_adjustments=reflection_adjustments if reflection_adjustments else None,
        )

    @cite(
        key="AGENT-SKILL-EVOLVE",
        paper="Conscious Agent: Skill Evolution",
        venue="ACN Harness Architecture",
        section="Self-Improvement Loop",
        rationale="Skills evolve through mutation and selection like Abhyāsa",
        confidence="CERTAIN",
    )
    def evolve_skills(self) -> Dict[str, Any]:
        """Evolve the agent's skills through one generation."""
        return self.skill_evolution.evolve_generation(self.agent_id)

    @cite(
        key="AGENT-GET-POLICY",
        paper="Conscious Agent: Policy Access",
        venue="ACN Harness Architecture",
        section="Self-Improvement Loop",
        rationale="Exposing policy parameters enables orchestrator-level coordination",
        confidence="CERTAIN",
    )
    def get_policy_parameters(self) -> Dict[str, Any]:
        """Get current policy parameters for this agent."""
        policy = self.policy_optimizer.get_policy(self.agent_id)
        if not policy:
            return {}
        return {
            "base_confidence": policy.base_confidence,
            "risk_tolerance": policy.risk_tolerance,
            "peer_trust_weight": policy.peer_trust_weight,
            "exploration_rate": policy.exploration_rate,
            "state_multipliers": policy.state_multipliers,
        }

    @cite(
        key="AGENT-PERCEIVE",
        paper="Conscious Agent: Multi-Modal Perception",
        venue="ACN Harness Architecture",
        section="Video Perception",
        rationale="Agents must perceive visual, audio, and temporal content to understand video",
        confidence="CERTAIN",
    )
    def initialize_perception(self, video_id: str = "") -> None:
        """Initialize perception substrates for video understanding."""
        self.perception.initialize(video_id=video_id)

    @cite(
        key="AGENT-PERCEIVE",
        paper="Conscious Agent: Multi-Modal Perception",
        venue="ACN Harness Architecture",
        section="Video Perception",
        rationale="Scene graph construction from frame detections enables structured visual understanding",
        confidence="CERTAIN",
    )
    def perceive_frame(self, frame_id: int, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a video frame: build scene graph, extract action tubes, index events.
        
        Args:
            frame_id: Frame identifier
            detections: List of detection dicts with keys: class_name, bbox (x1,y1,x2,y2), confidence
        
        Returns:
            Perception summary for this frame
        """
        return self.perception.perceive_frame(frame_id, detections)

    @cite(
        key="AGENT-FUSE",
        paper="Conscious Agent: Cross-Modal Fusion",
        venue="ACN Harness Architecture",
        section="Video Perception",
        rationale="Dhvani — resonance across modalities produces unified understanding",
        confidence="CERTAIN",
    )
    def fuse_modalities(self, features: Dict[str, Any], task_hint: str = "scene_understanding") -> Dict[str, Any]:
        """
        Fuse multi-modal features into unified representation.
        
        Args:
            features: Dict mapping modality name to feature dict with 'vector' and 'confidence'
            task_hint: Type of task for modality weighting
        
        Returns:
            Fusion result with fused vector and attention weights
        """
        return self.perception.fuse_modalities(features, task_hint)

    @cite(
        key="AGENT-GROUND",
        paper="Conscious Agent: Temporal Grounding",
        venue="ACN Harness Architecture",
        section="Video Perception",
        rationale="Events must be grounded in video timelines for actionable understanding",
        confidence="CERTAIN",
    )
    def ground_event(self, event_label: str, start_frame: int, end_frame: int,
                     confidence: float = 0.5) -> str:
        """Ground a semantic event to a temporal interval in the video."""
        return self.perception.ground_event(event_label, start_frame, end_frame, confidence)

    @cite(
        key="AGENT-PERCEIVE",
        paper="Conscious Agent: Multi-Modal Perception",
        venue="ACN Harness Architecture",
        section="Video Perception",
        rationale="Perception report summarizes all visual and temporal understanding",
        confidence="CERTAIN",
    )
    def get_perception_report(self) -> Dict[str, Any]:
        """Generate a report of the agent's perceptual state."""
        return self.perception.get_perception_report(self.agent_id)

    def _self_assess(self) -> str:
        """Generate a qualitative self-assessment."""
        health = self.awareness.get_status_report().get("health_score", 1.0)
        
        if health > 0.8:
            return f"{self.name} is operating effectively. Health: {health:.2f}."
        elif health > 0.5:
            return f"{self.name} is functional but experiencing issues. Health: {health:.2f}. Review alerts."
        else:
            return f"{self.name} is in degraded state. Health: {health:.2f}. Intervention recommended."
