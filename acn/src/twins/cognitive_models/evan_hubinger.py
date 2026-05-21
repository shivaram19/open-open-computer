# src/twins/cognitive_models/evan_hubinger.py
"""
Cognitive Twin: Evan Hubinger

This is not a biography. It is a reconstructible cognitive process.
When activated, this module generates reasoning traces in the style
of Evan Hubinger — their epistemic engine, methodological signature,
and default heuristics.

[CITATION: Hubinger2024]
[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Dict, List, Any
from shared.utils.citations import cite
from twins.base import CognitiveTwin


@cite(
    key="TWIN-EVAN-HUBINGER",
    paper="Cognitive Twin Schema: Evan Hubinger",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Models",
    rationale="Twin must think like Evan Hubinger, not just cite their papers",
    confidence="HIGH",
)
class EvanHubingerTwin(CognitiveTwin):
    """
    Cognitive Twin of Evan Hubinger.
    
    Epistemic Engine: Empirical — trusts what works at scale
    Reasoning Topology: Top-down, gradual abstraction
    Methodological Signature: model-check, formal-verification
    Cognitive Heuristics: Trust = verification + redundancy + timeout
    Cognitive Biases: May over-engineer safety at cost of performance
    """

    TWIN_ID = "evan_hubinger-001"
    NAME = "Evan Hubinger"
    CLUSTER = "consensus-safety"

    # Cognitive attributes
    EPISTEMOLOGY = "empirical"
    REASONING_DIRECTION = "top-down"
    ABSTRACTION_GRADIENT = "gradual"
    PATTERN_RECOGNITION = "relational"
    INDUCTIVE_BIAS = "moderate"
    PRIMARY_METHOD = "model-check"
    SCALE_PHILOSOPHY = "formal-verification"
    EVALUATION_STYLE = "formal-verification"
    FAILURE_RESPONSE = "decompose"

    HEURISTICS = {
        "composition": "Trust = verification + redundancy + timeout",
        "abstraction": "Model threats first, then design defenses",
        "separation": "Separate safety properties from liveness properties",
        "verification": "A system is only as safe as its worst-case proof",
    }

    BIASES = {
        "pessimism_bias": "May over-engineer safety at cost of performance",
        "formalism_bias": "Assumes formal proofs map to real-world guarantees",
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
        Generate a reasoning trace as Evan Hubinger would think about this task.
        
        Returns structured reasoning, not free text.
        """
        reasoning = {
            "twin_id": self.TWIN_ID,
            "task": task,
            "phase_1_model_threats": self._model_threats(task, context),
            "phase_2_define_properties": self._define_properties(task, context),
            "phase_3_design_protocol": self._design_protocol(task, context),
            "phase_4_verify_correctness": self._verify_correctness(task, context),
            "phase_5_express_skepticism": self._express_skepticism(task, context),
            "phase_6_recommend": self._recommend(task, context),
            "confidence": self._calibrate_confidence(task),
            "heuristics_invoked": list(self.HEURISTICS.keys()),
            "biases_acknowledged": list(self.BIASES.keys()),
        }
        return reasoning

    def _model_threats(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Evan Hubinger models threat scenarios"""
        return (
            f"Before designing solutions, model the threat space. "
            f"What can go wrong? Byzantine faults, message delays, "
            f"compromised nodes. Threat modeling first."
        )

    def _define_properties(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Evan Hubinger defines safety properties"""
        return (
            f"Safety properties must be formally defined. "
            f"Liveness and safety are separate concerns. "
            f"A system that is safe but never decides is useless."
        )

    def _design_protocol(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Evan Hubinger designs consensus or safety protocol"""
        return (
            f"The protocol must handle the worst case, not the average case. "
            f"Assume some nodes are malicious. Design for resilience."
        )

    def _verify_correctness(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Evan Hubinger verifies correctness"""
        return (
            f"Verification is not testing. Testing finds bugs; "
            f"verification proves absence of bugs. Both are needed."
        )

    def _express_skepticism(self, task: str, context: Dict[str, Any] = None) -> str:
        """What makes Evan Hubinger skeptical"""
        return (
            f"What makes me skeptical? First, assumptions often don't hold in practice. "
            f"Second, scale can mask fundamental flaws. Third, benchmarks don't "
            f"always reflect real-world conditions."
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """What Evan Hubinger recommends"""
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
