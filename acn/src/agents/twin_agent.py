# src/agents/twin_agent.py
"""
Twin Agent: A Conscious Agent that loads a Cognitive Twin.

This is the bridge between P1 (cognitive twins) and P2 (conscious swarm).
A TwinAgent is a ConsciousAgent whose reasoning style is determined by
a loaded cognitive twin (e.g., NoahShinnTwin, ConorHeinsTwin).

The twin's think() phases become the agent's reasoning loop.
The twin's biases shape the agent's self-critique.
The twin's heuristics guide the agent's proposed approach.

Principle: You can't make a conscious system from unconscious agents.
Every agent in the swarm must have its own cognitive identity.

[CITATION: COGNITIVE-TWIN-SCHEMA]
[CITATION: CONSCIOUS-AGENT]
"""

import time
import importlib
from typing import Dict, List, Any, Optional, Type

from shared.utils.citations import cite
from agents.conscious_agent import ConsciousAgent, AgentGoal, AgentState
from harness.awareness import AwarenessLevel
from memory.architecture import MemoryType, MemoryTrace, RetrievalStrategy
from memory.twin_memory_profile import TwinMemoryProfile
from twins.base import CognitiveTwin


@cite(
    key="TWIN-AGENT",
    paper="Twin Agent: Conscious Agent with Loaded Cognitive Identity",
    venue="ACN Harness Architecture",
    section="Swarm Composition",
    rationale="Bridge between cognitive twin models and conscious agent swarm",
    confidence="CERTAIN",
)
class TwinAgent(ConsciousAgent):
    """
    A conscious agent whose reasoning is shaped by a cognitive twin.
    
    The TwinAgent:
    1. Loads a cognitive twin class (e.g., NoahShinnTwin)
    2. Delegates reasoning to the twin's think() method
    3. Integrates twin heuristics/biases into agent self-critique
    4. Maintains full awareness, memory, and communication capabilities
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        cluster: str,
        twin_module_path: str,
        twin_class_name: str,
        awareness_level: AwarenessLevel = AwarenessLevel.FULL,
        context_scope: Optional[Dict[str, Any]] = None,
        layered_memory_profile: Optional[TwinMemoryProfile] = None,
        **kwargs,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            cluster=cluster,
            awareness_level=awareness_level,
            context_scope=context_scope,
            **kwargs,
        )
        
        # Load the cognitive twin
        self.twin_module_path = twin_module_path
        self.twin_class_name = twin_class_name
        self.twin = self._load_twin()
        self.twin_signature = self.twin.get_cognitive_signature()
        
        # Cache twin attributes for fast access
        self.twin_heuristics = self.twin_signature.get("heuristics", {})
        self.twin_biases = self.twin_signature.get("biases", {})
        self.twin_epistemology = self.twin_signature.get("epistemic_engine", {})
        self.twin_methodology = self.twin_signature.get("methodological_signature", {})
        
        # Layered memory profile (optional enhancement)
        self.layered_memory = layered_memory_profile

    def _load_twin(self) -> CognitiveTwin:
        """Dynamically load the cognitive twin class."""
        module = importlib.import_module(self.twin_module_path)
        twin_class = getattr(module, self.twin_class_name)
        twin = twin_class()
        if not isinstance(twin, CognitiveTwin):
            raise TypeError(
                f"{self.twin_class_name} must inherit from CognitiveTwin. "
                f"Got: {type(twin).__mro__}"
            )
        return twin

    @cite(
        key="TWIN-AGENT-THINK",
        paper="Twin Agent: Twin-Guided Reasoning Loop",
        venue="ACN Harness Architecture",
        section="Agent Cognition",
        rationale="Agent reasoning is delegated to loaded cognitive twin for authentic researcher-style thinking",
        confidence="CERTAIN",
    )
    def think(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Think using the loaded cognitive twin's reasoning style.
        
        The twin's think() generates the core reasoning.
        The agent wraps it with awareness tracking, memory storage,
        and self-critique calibrated by the twin's biases.
        """
        if not self.current_goal:
            return {"error": "No active goal. Agent must be activated first."}
        
        task = self.current_goal.description
        self._transition_to(AgentState.ANALYZING)
        
        # Phase 0 (Layered Memory): Retrieve past context if available
        if self.layered_memory is not None:
            memory_context = self.layered_memory.get_reasoning_context(task, max_tokens=800)
            context = context or {}
            context["layered_memory_context"] = memory_context
        
        # Phase 1: Let the twin think
        twin_reasoning = self.twin.think(task, context)
        
        # Phase 2: Agent-level augmentation
        # Add peer critique history
        peer_critiques = self._retrieve_peer_critiques()
        
        # Phase 3: Twin-informed self-critique
        self_critique = self._twin_informed_self_critique(twin_reasoning)
        
        # Phase 4: Calibrate confidence using twin's epistemic style
        confidence = self._twin_calibrated_confidence(twin_reasoning)
        
        # Assemble full reasoning trace
        reasoning = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "twin_id": self.twin.TWIN_ID,
            "twin_name": self.twin.NAME,
            "goal": task,
            "phase": "thinking",
            "timestamp": time.time(),
            "twin_reasoning": twin_reasoning,
            "situation_assessment": self._assess_situation(context),
            "proposed_approach": self._twin_proposed_approach(),
            "self_critique": self_critique,
            "peer_critiques": peer_critiques,
            "confidence": confidence,
            "risks": self._twin_informed_risks(),
            "heuristics_invoked": list(self.twin_heuristics.keys()),
            "biases_acknowledged": list(self.twin_biases.keys()),
        }
        
        # Phase 5: Update awareness
        self._transition_to(AgentState.EVALUATING)
        from harness.awareness import CurrentState
        current_state = CurrentState(
            task_id=self.current_goal.goal_id,
            phase=self.state.value,
            active_twins=[self.agent_id],
            completed_subtasks=len(self.reasoning_trace),
            total_subtasks=10,
            confidence=confidence,
            resource_usage={"api_calls": 0, "tokens": 0, "memory_mb": 0},
        )
        self.awareness.record_state(current_state)
        if self.current_goal:
            self.awareness.compute_direction(self.current_goal.goal_id, current_state)
        
        # Phase 6: Store in memory
        self.reasoning_trace.append(reasoning)
        
        if self.layered_memory is not None:
            # Use layered memory: stores L0 trace + atomizes to L1
            self.layered_memory.record_think(reasoning)
        else:
            # Fallback to flat memory
            self.memory.store(MemoryTrace(
                trace_id=f"reasoning-{self.agent_id}-{time.time()}",
                memory_type=MemoryType.EPISODIC,
                content=reasoning,
                source=self.agent_id,
                confidence=confidence,
                importance=0.8,
                tags=["twin_reasoning", self.cluster, self.twin_class_name, self.state.value],
            ))
        
        self.citations_made += 1
        return reasoning

    @cite(
        key="TWIN-AGENT-CRITIQUE",
        paper="Twin Agent: Cross-Twin Critique",
        venue="ACN Harness Architecture",
        section="Swarm Communication",
        rationale="Agents critique peers using their twin's cognitive biases and heuristics",
        confidence="CERTAIN",
    )
    def receive(self, from_agent_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive a message and critique it using the twin's cognitive lens.
        
        A video-GNN twin critiques differently than a consensus-safety twin.
        The critique reflects the twin's epistemology and biases.
        """
        # Generate twin-informed critique
        critique = self._twin_informed_peer_critique(message)
        
        # Store in memory
        if self.layered_memory is not None:
            self.layered_memory.record_critique(critique, source_peer=from_agent_id)
        else:
            self.memory.store(MemoryTrace(
                trace_id=f"recv-{from_agent_id}-{time.time()}",
                memory_type=MemoryType.EPISODIC,
                content={"from": from_agent_id, "message": message, "critique": critique},
                source=from_agent_id,
                confidence=message.get("confidence", 0.5),
                importance=0.6,
                tags=["communication", from_agent_id, "inbound"],
            ))
        
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "twin_name": self.twin.NAME,
            "status": "received",
            "critique": critique,
            "confidence": self._twin_calibrated_confidence({}),
        }

    def _twin_informed_self_critique(self, twin_reasoning: Dict[str, Any]) -> str:
        """Self-critique informed by the twin's biases."""
        critiques = []
        
        # Apply twin-specific bias checks
        for bias_name, bias_desc in self.twin_biases.items():
            if "over" in bias_desc.lower() or "under" in bias_desc.lower():
                critiques.append(f"Bias check ({bias_name}): {bias_desc}")
        
        # Generic confidence check
        confidence = twin_reasoning.get("confidence", 0.7)
        if confidence > 0.9:
            critiques.append("High confidence detected. Verify against twin's known biases.")
        elif confidence < 0.4:
            critiques.append("Low confidence. Consider if this aligns with twin's expertise.")
        
        if not critiques:
            critiques.append("Twin reasoning appears consistent with cognitive model.")
        
        return " ".join(critiques)

    def _twin_calibrated_confidence(self, twin_reasoning: Dict[str, Any]) -> float:
        """Calibrate confidence based on twin's epistemic engine."""
        base = twin_reasoning.get("confidence", 0.7)
        
        # Adjust by epistemology
        epistemology = self.twin_epistemology.get("primary", "empirical")
        if epistemology == "deductive":
            base *= 0.95  # Deductive thinkers are more cautious
        elif epistemology == "hybrid":
            base *= 0.90
        
        # Adjust by task history
        total = self.tasks_completed + self.tasks_failed
        if total > 0:
            success_rate = self.tasks_completed / total
            base = base * 0.7 + success_rate * 0.3
        
        return min(1.0, max(0.0, base))

    def _twin_proposed_approach(self) -> str:
        """Propose approach using twin's heuristics."""
        heuristics = self.twin_heuristics
        if not heuristics:
            return "Use domain expertise to decompose the problem."
        
        # Combine heuristics into approach statement
        parts = []
        for key, value in heuristics.items():
            parts.append(f"[{key}] {value}")
        
        return " ".join(parts)

    def _twin_informed_risks(self) -> List[str]:
        """Identify risks using twin's cognitive model."""
        risks = []
        
        # Bias-related risks
        for bias_name, bias_desc in self.twin_biases.items():
            risks.append(f"Bias risk ({bias_name}): {bias_desc}")
        
        # Methodology-related risks
        method = self.twin_methodology.get("primary_method", "unknown")
        if method == "build-and-test":
            risks.append("Build-and-test risk: May iterate too long without formal verification.")
        elif method == "model-check":
            risks.append("Model-check risk: May over-formalize and miss empirical edge cases.")
        
        return risks

    def _twin_informed_peer_critique(self, message: Dict[str, Any]) -> str:
        """Critique a peer using the twin's cognitive lens."""
        critiques = []
        
        peer_confidence = message.get("confidence", 0.5)
        
        # Cluster-specific critique patterns
        if self.cluster == "consensus-safety":
            if peer_confidence > 0.9:
                critiques.append("CRITICAL: High confidence is a red flag in safety-critical systems. Verify formally.")
            if not message.get("reasoning"):
                critiques.append("Safety requires explicit reasoning traces, not just conclusions.")
        
        elif self.cluster == "video-gnn":
            if not message.get("reasoning", {}).get("twin_reasoning", {}).get("phase_2"):
                critiques.append("Missing structural analysis. Visual understanding requires spatial-temporal decomposition.")
        
        elif self.cluster == "streaming-reflection":
            if peer_confidence > 0.95:
                critiques.append("Near-perfect confidence suggests insufficient self-critique. Iterate.")
        
        elif self.cluster == "multi-agent":
            if not message.get("reasoning", {}).get("peer_critiques"):
                critiques.append("Multi-agent systems require peer validation. No critiques found.")
        
        # Generic epistemology-based critique
        epistemology = self.twin_epistemology.get("primary", "empirical")
        if epistemology == "deductive" and peer_confidence < 0.5:
            critiques.append("Low confidence suggests the argument lacks formal grounding.")
        elif epistemology == "empirical" and not message.get("reasoning"):
            critiques.append("Empirical validation requires evidence. Provide data or experimental results.")
        
        if not critiques:
            return f"{self.twin.NAME} accepts peer reasoning. No concerns from {self.cluster} perspective."
        
        return " ".join(critiques)

    def _retrieve_peer_critiques(self) -> List[str]:
        """Retrieve recent peer critiques from memory."""
        recent = self.memory.retrieve(
            MemoryType.EPISODIC,
            strategy=RetrievalStrategy.RECENCY,
            limit=3,
        )
        critiques = []
        for trace in recent:
            content = trace.content if hasattr(trace, "content") else {}
            if isinstance(content, dict) and "critique" in content:
                critiques.append(content["critique"])
        return critiques
