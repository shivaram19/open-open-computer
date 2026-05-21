# src/twins/cognitive_models/jiebo_luo.py
"""
Cognitive Twin: Jiebo Luo

This is not a biography. It is a reconstructible cognitive process.
When activated, this module generates reasoning traces in the style
of Jiebo Luo — their epistemic engine, methodological signature,
and default heuristics.

[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Dict, List, Any
from shared.utils.citations import cite
from twins.base import CognitiveTwin


@cite(
    key="TWIN-JIEBO-LUO",
    paper="Cognitive Twin Schema: Jiebo Luo",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Models",
    rationale="Twin must think like Jiebo Luo, not just cite their papers",
    confidence="HIGH",
)
class JieboLuoTwin(CognitiveTwin):
    """
    Cognitive Twin of Jiebo Luo.
    
    Epistemic Engine: Deductive — trusts formal proofs and axioms
    Reasoning Topology: Bottom-up, gradual abstraction
    Methodological Signature: build-and-test, scale-up
    Cognitive Heuristics: Visual structure + temporal dynamics = understanding
    Cognitive Biases: May overestimate the value of larger datasets
    """

    TWIN_ID = "jiebo_luo-001"
    NAME = "Jiebo Luo"
    CLUSTER = "video-gnn"

    # Cognitive attributes
    EPISTEMOLOGY = "deductive"
    REASONING_DIRECTION = "bottom-up"
    ABSTRACTION_GRADIENT = "gradual"
    PATTERN_RECOGNITION = "visual-statistical"
    INDUCTIVE_BIAS = "strong"
    PRIMARY_METHOD = "build-and-test"
    SCALE_PHILOSOPHY = "scale-up"
    EVALUATION_STYLE = "benchmark-driven"
    FAILURE_RESPONSE = "decompose"

    HEURISTICS = {
        "composition": "Visual structure + temporal dynamics = understanding",
        "abstraction": "Scene graphs before semantics; objects before concepts",
        "separation": "Separate spatial reasoning from temporal reasoning",
        "verification": "If it doesn't work on real video, it doesn't work",
    }

    BIASES = {
        "scale_bias": "May overestimate the value of larger datasets",
        "visual_bias": "Assumes visual understanding transfers to non-visual domains",
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
        Generate a reasoning trace as Jiebo Luo would think about this task.
        
        Returns structured reasoning, not free text.
        """
        reasoning = {
            "twin_id": self.TWIN_ID,
            "task": task,
            "phase_1_identify_problem": self._identify_problem(task, context),
            "phase_2_assess_structure": self._assess_structure(task, context),
            "phase_3_evaluate_scale": self._evaluate_scale(task, context),
            "phase_4_design_benchmark": self._design_benchmark(task, context),
            "phase_5_express_skepticism": self._express_skepticism(task, context),
            "phase_6_recommend": self._recommend(task, context),
            "confidence": self._calibrate_confidence(task),
            "heuristics_invoked": list(self.HEURISTICS.keys()),
            "biases_acknowledged": list(self.BIASES.keys()),
        }
        return reasoning

    def _identify_problem(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Jiebo Luo frames the visual challenge"""
        return (
            f"From my perspective, the core challenge in '{task}' is: "
            f"what is the visual or structural representation that captures the essence? "
            f"We need to define the visual ontology before algorithm design."
        )

    def _assess_structure(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Jiebo Luo analyzes spatial and temporal structure"""
        return (
            f"How do objects and their relationships evolve over time? "
            f"Scene graphs provide the structured representation. "
            f"Temporal dynamics add the critical time dimension."
        )

    def _evaluate_scale(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Jiebo Luo thinks about data and compute scale"""
        return (
            f"Scale matters. Start small, validate, then scale up. "
            f"The breakthrough often happens at the intersection of "
            f"sufficient data and the right structural representation."
        )

    def _design_benchmark(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Jiebo Luo designs evaluation"""
        return (
            f"A good benchmark needs: clear metrics, realistic difficulty, "
            f"and room for improvement. Without community adoption, "
            f"a benchmark is just a dataset."
        )

    def _express_skepticism(self, task: str, context: Dict[str, Any] = None) -> str:
        """What makes Jiebo Luo skeptical"""
        return (
            f"What makes me skeptical? First, assumptions often don't hold in practice. "
            f"Second, scale can mask fundamental flaws. Third, benchmarks don't "
            f"always reflect real-world conditions."
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """What Jiebo Luo recommends"""
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
