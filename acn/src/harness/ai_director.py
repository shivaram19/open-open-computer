# src/harness/ai_director.py
"""
AI Director: Meta-cognitive orchestration layer for autonomous execution.

Inspired by WeirdDream's AI Director (Count Bayesie, 2026):
- Observes the last frame (execution result, consensus, artifacts)
- Generates the next prompt (revised task description, approach, critique)
- Meta-prompt driven: system + user prompts define directorial vision
- Memory-aware: maintains narrative continuity across sub-tasks

The Director does not execute — it directs. It sits between execution
steps and decides what the swarm should attempt next.

Principle: The director's job is coherence. The swarm's job is execution.

[CITATION: WeirdDream2026]
"""

import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path

_DEFAULT = object()  # sentinel for "argument not provided"

from shared.utils.citations import cite


@dataclass
class DirectorObservation:
    """What the AI Director observes about the current swarm state."""
    task_id: str
    subtask_id: str
    consensus_approach: Optional[str]
    consensus_score: float
    execution_status: str  # "completed", "failed", "partial"
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    previous_directions: List[str] = field(default_factory=list)
    swarm_health: float = 1.0
    memory_context: str = ""  # Retrieved narrative context from past steps


@dataclass
class Direction:
    """A directorial decision: what the swarm should do next."""
    action: str  # "continue", "retry", "redirect", "critique", "complete"
    revised_task_description: str
    reasoning: str
    confidence: float
    meta_prompt_used: str = ""
    latency_ms: float = 0.0


@cite(
    key="AI-DIRECTOR",
    paper="AI Director for Autonomous Cognitive Networks",
    venue="ACN Harness Architecture",
    section="P5-5 AI Director",
    rationale="Meta-cognitive layer that maintains coherence across swarm executions",
    confidence="HIGH",
)
class AIDirector:
    """
    Directs the swarm by observing outputs and generating next-step prompts.

    Usage:
        director = AIDirector()
        direction = director.direct(observation)
        # direction.revised_task_description → passed to next sub-task
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        user_prompt_template: Optional[str] = None,
        model: str = "gpt-4o-mini",
        api_key: Union[str, None, object] = _DEFAULT,
        custom_director: Optional[Callable[[DirectorObservation], Direction]] = None,
    ):
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.user_prompt_template = user_prompt_template or self._default_user_prompt()
        self.model = model
        if api_key is _DEFAULT:
            self.api_key = os.environ.get("OPENAI_API_KEY")
        else:
            self.api_key = api_key  # can be None (force fallback) or a string
        self._client: Optional[Any] = None
        self._direction_history: List[Direction] = []
        self.custom_director = custom_director

    def _default_system_prompt(self) -> str:
        return (
            "You are an AI Director overseeing a multi-agent cognitive swarm. "
            "Your job is to maintain coherence, quality, and narrative continuity "
            "across autonomous task execution steps. "
            "You observe the swarm's output and decide what they should do next. "
            "Be concise. Respond ONLY with a JSON object containing: "
            "action (continue|retry|redirect|critique|complete), "
            "revised_task_description (string), reasoning (string), confidence (0.0-1.0)."
        )

    def _default_user_prompt(self) -> str:
        return (
            "Observe the current swarm state and decide the next step.\n\n"
            "Task: {task_id}\n"
            "Sub-task: {subtask_id}\n"
            "Consensus approach: {consensus_approach}\n"
            "Consensus score: {consensus_score}\n"
            "Execution status: {execution_status}\n"
            "Artifacts: {artifacts}\n"
            "Swarm health: {swarm_health}\n"
            "Memory context: {memory_context}\n"
            "Previous directions: {previous_directions}\n\n"
            "What should the swarm do next?"
        )

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError as exc:
                raise RuntimeError("openai package not installed") from exc
        return self._client

    @cite(
        key="AI-DIRECT-DIRECT",
        paper="AI Director: Direction Generation",
        venue="ACN Harness Architecture",
        section="P5-5",
        rationale="LLM-based direction generation with structured output",
        confidence="HIGH",
    )
    def direct(self, observation: DirectorObservation) -> Direction:
        """
        Generate a directorial decision based on swarm observation.

        If a custom_director callable was provided, it takes precedence.
        Otherwise uses the LLM with meta-prompts.
        """
        start = time.time()

        if self.custom_director is not None:
            direction = self.custom_director(observation)
            direction.latency_ms = (time.time() - start) * 1000
            self._direction_history.append(direction)
            return direction

        if not self.api_key:
            direction = self._fallback_direction(observation, start)
        else:
            user_prompt = self.user_prompt_template.format(
                task_id=observation.task_id,
                subtask_id=observation.subtask_id,
                consensus_approach=observation.consensus_approach or "none",
                consensus_score=observation.consensus_score,
                execution_status=observation.execution_status,
                artifacts=str(observation.artifacts),
                swarm_health=observation.swarm_health,
                memory_context=observation.memory_context or "none",
                previous_directions=str(observation.previous_directions),
            )

            try:
                client = self._get_client()
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=1024,
                    temperature=0.3,
                )

                content = response.choices[0].message.content or "{}"
                import json
                parsed = json.loads(content)

                direction = Direction(
                    action=parsed.get("action", "continue"),
                    revised_task_description=parsed.get("revised_task_description", observation.subtask_id),
                    reasoning=parsed.get("reasoning", "No reasoning provided"),
                    confidence=parsed.get("confidence", 0.5),
                    meta_prompt_used=self.system_prompt[:100],
                    latency_ms=(time.time() - start) * 1000,
                )

            except Exception as exc:
                direction = Direction(
                    action="continue",
                    revised_task_description=f"Continue with caution: {exc}",
                    reasoning=f"LLM director failed: {exc}. Falling back to continue.",
                    confidence=0.3,
                    latency_ms=(time.time() - start) * 1000,
                )

        self._direction_history.append(direction)
        return direction

    def _fallback_direction(
        self,
        observation: DirectorObservation,
        start_time: float,
    ) -> Direction:
        """Rule-based fallback when no LLM is available."""
        if observation.execution_status == "failed":
            action = "retry"
            desc = f"Retry: {observation.subtask_id}"
            conf = 0.5
        elif observation.consensus_score < 0.5:
            action = "critique"
            desc = f"Critique and revise: {observation.subtask_id}"
            conf = 0.6
        elif observation.consensus_score > 0.9 and observation.execution_status == "completed":
            action = "continue"
            desc = f"Proceed to next: {observation.subtask_id}"
            conf = 0.95
        else:
            action = "continue"
            desc = f"Continue: {observation.subtask_id}"
            conf = observation.consensus_score

        return Direction(
            action=action,
            revised_task_description=desc,
            reasoning="Rule-based fallback (no LLM available)",
            confidence=conf,
            latency_ms=(time.time() - start_time) * 1000,
        )

    def load_meta_prompts_from_files(
        self,
        system_path: Path,
        user_path: Path,
    ) -> None:
        """Load system and user prompts from text files (WeirdDream-style)."""
        if system_path.exists():
            self.system_prompt = system_path.read_text()
        if user_path.exists():
            self.user_prompt_template = user_path.read_text()

    def get_direction_history(self) -> List[Direction]:
        """Get all directions issued by this director."""
        return self._direction_history

    def get_narcissistic_report(self) -> Dict[str, Any]:
        """
        Self-evaluation: how often did the director intervene?
        """
        total = len(self._direction_history)
        if total == 0:
            return {"interventions": 0, "avg_confidence": 0.0}

        actions = [d.action for d in self._direction_history]
        interventions = sum(1 for a in actions if a != "continue")

        return {
            "total_directions": total,
            "interventions": interventions,
            "intervention_rate": interventions / total,
            "avg_confidence": sum(d.confidence for d in self._direction_history) / total,
            "action_distribution": {
                a: actions.count(a) for a in set(actions)
            },
        }
