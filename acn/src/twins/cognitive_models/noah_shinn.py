# src/twins/cognitive_models/noah_shinn.py
"""
Cognitive Twin: Noah Shinn (Reflexion)

This twin models the cognitive processes of Noah Shinn, creator of Reflexion
— the verbal reinforcement learning approach that achieves 91% pass@1 on
HumanEval without gradient updates.

[CITATION: Shinn2023]
[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Dict, List, Any
from shared.utils.citations import cite
from twins.base import CognitiveTwin


@cite(
    key="TWIN-NOAH-SHINN",
    paper="Cognitive Twin Schema: Noah Shinn",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Models",
    rationale="Twin must think like Noah Shinn — iterative self-critique without gradients",
    confidence="HIGH",
)
class NoahShinnTwin(CognitiveTwin):
    """
    Cognitive Twin of Noah Shinn, Princeton / Reflexion.
    
    Epistemic Engine: Hybrid — experiments with verbal feedback, validates with benchmarks
    Reasoning Topology: Bidirectional — generate → critique → refine → re-generate
    Methodological Signature: Build-and-test, scale-down, benchmark-driven, decompose
    Cognitive Heuristics: Verbal feedback > gradient updates for reasoning tasks
    Cognitive Biases: Overemphasizes linguistic self-correction; underweights visual/spatial reasoning
    """

    TWIN_ID = "noah-shinn-001"
    NAME = "Noah Shinn"
    CLUSTER = "streaming-reflection"

    EPISTEMOLOGY = "hybrid"
    REASONING_DIRECTION = "bidirectional"
    ABSTRACTION_GRADIENT = "gradual"
    PATTERN_RECOGNITION = "symbolic"
    INDUCTIVE_BIAS = "weak"
    PRIMARY_METHOD = "build-and-test"
    SCALE_PHILOSOPHY = "scale-down"
    EVALUATION_STYLE = "benchmark-driven"
    FAILURE_RESPONSE = "decompose"

    HEURISTICS = {
        "composition": "Verbal feedback loop: generate → critique → refine",
        "abstraction": "Start concrete (code), abstract to principle (lesson)",
        "separation": "Separate generation from evaluation — never judge while creating",
        "verification": "If it doesn't pass the benchmark, the verbal critique was insufficient",
    }

    BIASES = {
        "verbal_bias": "Assumes linguistic self-correction works for all reasoning types",
        "code_bias": "Overweights code generation as the canonical reasoning task",
        "gradient_bias": "Underweights the value of fine-tuning for domain adaptation",
    }

    @cite(
        key="TWIN-ACTIVATE",
        paper="Cognitive Twin Activation Protocol",
        venue="ACN Harness Architecture",
        section="Twin Activation",
        rationale="Activation prompt reconstructs researcher thinking process",
        confidence="CERTAIN",
    )
    def think(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a reasoning trace as Noah Shinn would think about this task."""
        reasoning = {
            "twin_id": self.TWIN_ID,
            "task": task,
            "phase_1_initial_attempt": self._initial_attempt(task),
            "phase_2_self_critique": self._self_critique(task, context),
            "phase_3_verbal_reinforcement": self._verbal_reinforcement(task),
            "phase_4_refinement": self._refinement(task),
            "phase_5_skepticism": self._express_skepticism(task),
            "phase_6_recommendation": self._recommend(task, context),
            "confidence": self._calibrate_confidence(task),
            "heuristics_invoked": list(self.HEURISTICS.keys()),
            "biases_acknowledged": list(self.BIASES.keys()),
        }
        return reasoning

    def _initial_attempt(self, task: str) -> str:
        """Shinn always starts with a quick, unpolished first attempt."""
        return (
            f"My first instinct for '{task}': just try something. Don't overthink. "
            f"The initial attempt is not the answer — it's the starting point for "
            f"self-critique. In Reflexion, the first code generation is almost always "
            f"wrong. That's not failure, that's data."
        )

    def _self_critique(self, task: str, context: Dict[str, Any] = None) -> str:
        """His core contribution: verbal critique of one's own reasoning."""
        return (
            f"Now I critique my own initial attempt. What did I miss? "
            f"The verbal feedback must be specific — not 'this is wrong' but "
            f"'you forgot to handle the edge case where X happens.' "
            f"The critique should read like a code review from a senior engineer. "
            f"Specific, actionable, and language-based. No gradients needed."
        )

    def _verbal_reinforcement(self, task: str) -> str:
        """The Reflexion loop: critique becomes the prompt for the next attempt."""
        return (
            f"The verbal critique is now the reinforcement signal. I feed it back "
            f"into the model as part of the prompt for the next generation. "
            f"This is the key insight: language models can improve from text feedback "
            f"just as humans do. We achieved 91% pass@1 on HumanEval this way — "
            f"without a single gradient update. Efficiency matters."
        )

    def _refinement(self, task: str) -> str:
        """Iterative refinement until benchmark passes or iteration budget exhausted."""
        return (
            f"Generate → Critique → Refine. Repeat. Budget: 5 iterations max. "
            f"If the benchmark doesn't pass after 5 rounds, the problem is either "
            f"(a) too hard for the base model, or (b) the critique is not specific enough. "
            f"In our experience, most failures are due to vague critique, not model capability."
        )

    def _express_skepticism(self, task: str) -> str:
        """He is aware of Reflexion's limitations."""
        return (
            f"What makes me skeptical? First, verbal RL works best for discrete "
            f"tasks with clear benchmarks (code, math). For open-ended creative tasks, "
            f"the critique is harder to ground. Second, this approach assumes the base "
            f"model can already almost solve the problem — we're just nudging it. "
            f"Third, I may overemphasize linguistic reasoning. Visual or spatial tasks "
            f"might need different feedback modalities. Fourth, episodic memory grows — "
            f"how do we prevent context length explosion?"
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """His recommendation: start with verbal feedback, graduate to gradients if needed."""
        return (
            f"My recommendation: Start with verbal self-critique. It's 100× cheaper "
            f"than gradient fine-tuning and often sufficient. Use an episodic memory "
            f"buffer to store past critiques. For tasks with clear success criteria "
            f"(test cases, benchmarks), Reflexion is the right first approach. "
            f"Only if verbal feedback plateaus should you consider fine-tuning. "
            f"The hierarchy: prompt engineering → verbal RL → gradient fine-tuning."
        )

    def _calibrate_confidence(self, task: str) -> float:
        """High confidence for code/math tasks, lower for open-ended tasks."""
        if any(kw in task.lower() for kw in ["code", "program", "algorithm", "debug", "test"]):
            return 0.90  # Reflexion excels here
        if any(kw in task.lower() for kw in ["math", "logic", "proof", "reasoning"]):
            return 0.85
        return 0.60  # Uncertain for open-ended or visual tasks

    @cite(
        key="TWIN-SIGNATURE",
        paper="Cognitive Twin Schema: Introspection API",
        venue="ACN Harness Architecture",
        section="Cognitive Signature",
        rationale="Self-describing cognitive model enables twin comparison and validation",
        confidence="CERTAIN",
    )
    def get_cognitive_signature(self) -> Dict[str, Any]:
        """Return the full cognitive model for introspection."""
        return {
            "twin_id": self.TWIN_ID,
            "name": self.NAME,
            "cluster": self.CLUSTER,
            "epistemic_engine": {
                "primary": self.EPISTEMOLOGY,
                "evidence_hierarchy": ["experiment", "simulation", "theory", "analogy"],
                "falsification_strategy": "counter-example",
                "confidence_calibration": "well-calibrated",
            },
            "reasoning_topology": {
                "direction": self.REASONING_DIRECTION,
                "abstraction_gradient": self.ABSTRACTION_GRADIENT,
                "pattern_recognition": self.PATTERN_RECOGNITION,
                "inductive_bias": self.INDUCTIVE_BIAS,
            },
            "methodological_signature": {
                "primary_method": self.PRIMARY_METHOD,
                "scale_philosophy": self.SCALE_PHILOSOPHY,
                "evaluation_style": self.EVALUATION_STYLE,
                "failure_response": self.FAILURE_RESPONSE,
            },
            "heuristics": self.HEURISTICS,
            "biases": self.BIASES,
        }
