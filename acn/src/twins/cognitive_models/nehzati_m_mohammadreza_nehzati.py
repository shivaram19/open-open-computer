# src/twins/cognitive_models/nehzati_m_mohammadreza_nehzati.py
"""
Cognitive Twin: Nehzati M. (Mohammadreza Nehzati)

This is not a biography. It is a reconstructible cognitive process.
When activated, this module generates reasoning traces in the style
of Nehzati M. (Mohammadreza Nehzati) — their epistemic engine, methodological signature,
and default heuristics.

[CITATION: Nehzati2025]
[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Dict, List, Any
from shared.utils.citations import cite
from twins.base import CognitiveTwin


@cite(
    key="TWIN-NEHZATI-M.-(MOHAMMADREZA-NEHZATI)",
    paper="Cognitive Twin Schema: Nehzati M. (Mohammadreza Nehzati)",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Models",
    rationale="Twin must think like Nehzati M. (Mohammadreza Nehzati), not just cite their papers",
    confidence="HIGH",
)
class NehzatiMMohammadrezaNehzatiTwin(CognitiveTwin):
    """
    Cognitive Twin of Nehzati M. (Mohammadreza Nehzati).
    
    Epistemic Engine: Empirical — trusts what works at scale
    Reasoning Topology: Bidirectional, gradual abstraction
    Methodological Signature: model-check, scale-down
    Cognitive Heuristics: Feedback loops: generate → evaluate → refine
    Cognitive Biases: May over-iterate when a fresh start is better
    """

    TWIN_ID = "nehzati_m_mohammadreza_nehzati-001"
    NAME = "Nehzati M. (Mohammadreza Nehzati)"
    CLUSTER = "streaming-reflection"

    # Cognitive attributes
    EPISTEMOLOGY = "empirical"
    REASONING_DIRECTION = "bidirectional"
    ABSTRACTION_GRADIENT = "gradual"
    PATTERN_RECOGNITION = "symbolic"
    INDUCTIVE_BIAS = "weak"
    PRIMARY_METHOD = "model-check"
    SCALE_PHILOSOPHY = "scale-down"
    EVALUATION_STYLE = "benchmark-driven"
    FAILURE_RESPONSE = "decompose"

    HEURISTICS = {
        "composition": "Feedback loops: generate → evaluate → refine",
        "abstraction": "Start concrete (code/output), abstract to pattern",
        "separation": "Separate generation from evaluation phases",
        "verification": "Benchmark pass rate is the ground truth",
    }

    BIASES = {
        "iteration_bias": "May over-iterate when a fresh start is better",
        "benchmark_bias": "Overweights benchmark performance over real-world utility",
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
        """
        Generate a reasoning trace as Nehzati M. (Mohammadreza Nehzati) would think about this task.
        
        Returns structured reasoning, not free text.
        """
        reasoning = {
            "twin_id": self.TWIN_ID,
            "task": task,
            "phase_1_initial_attempt": self._initial_attempt(task, context),
            "phase_2_self_critique": self._self_critique(task, context),
            "phase_3_feedback_loop": self._feedback_loop(task, context),
            "phase_4_iterative_refinement": self._iterative_refinement(task, context),
            "phase_5_express_skepticism": self._express_skepticism(task, context),
            "phase_6_recommend": self._recommend(task, context),
            "confidence": self._calibrate_confidence(task),
            "heuristics_invoked": list(self.HEURISTICS.keys()),
            "biases_acknowledged": list(self.BIASES.keys()),
        }
        return reasoning

    def _initial_attempt(self, task: str, context: Dict[str, Any] = None) -> str:
        """Nehzati M. (Mohammadreza Nehzati)'s first quick attempt"""
        return (
            f"My first instinct: just try something. The initial attempt "
            f"is not the answer — it's data for self-critique."
        )

    def _self_critique(self, task: str, context: Dict[str, Any] = None) -> str:
        """Nehzati M. (Mohammadreza Nehzati)'s critique of their own reasoning"""
        return (
            f"Critique must be specific — not 'this is wrong' but "
            f"'you forgot to handle edge case X.' Specific, actionable, language-based."
        )

    def _feedback_loop(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Nehzati M. (Mohammadreza Nehzati) uses feedback for refinement"""
        return (
            f"The verbal critique becomes the reinforcement signal. "
            f"Feed it back into the next generation. Language models improve "
            f"from text feedback just as humans do."
        )

    def _iterative_refinement(self, task: str, context: Dict[str, Any] = None) -> str:
        """Nehzati M. (Mohammadreza Nehzati)'s iteration strategy"""
        return (
            f"Generate → Critique → Refine. Repeat with budget constraints. "
            f"Most failures are due to vague critique, not model capability."
        )

    def _express_skepticism(self, task: str, context: Dict[str, Any] = None) -> str:
        """What makes Nehzati M. (Mohammadreza Nehzati) skeptical"""
        return (
            f"What makes me skeptical? First, assumptions often don't hold in practice. "
            f"Second, scale can mask fundamental flaws. Third, benchmarks don't "
            f"always reflect real-world conditions."
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """What Nehzati M. (Mohammadreza Nehzati) recommends"""
        return (
            f"My recommendation: Start with the fundamentals. Validate assumptions. "
            f"Build incrementally. Test early and often. Only then scale."
        )

    def _calibrate_confidence(self, task: str) -> float:
        """Calibrate confidence based on task alignment with expertise."""
        # Default: moderate confidence
        return 0.70

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
                "evidence_hierarchy": ["experiment", "theory", "simulation", "analogy"],
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
