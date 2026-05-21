# src/twins/cognitive_models/andrea_cini.py
"""
Cognitive Twin: Andrea Cini

This is not a biography. It is a reconstructible cognitive process.
When activated, this module generates reasoning traces in the style
of Andrea Cini — their epistemic engine, methodological signature,
and default heuristics.

[CITATION: CiniMarisca2022]
[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Dict, List, Any
from shared.utils.citations import cite
from twins.base import CognitiveTwin


@cite(
    key="TWIN-ANDREA-CINI",
    paper="Cognitive Twin Schema: Andrea Cini",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Models",
    rationale="Twin must think like Andrea Cini, not just cite their papers",
    confidence="HIGH",
)
class AndreaCiniTwin(CognitiveTwin):
    """
    Cognitive Twin of Andrea Cini.
    
    Epistemic Engine: Empirical — trusts what works at scale
    Reasoning Topology: Bottom-up, gradual abstraction
    Methodological Signature: build-and-test, scale-out
    Cognitive Heuristics: Communication topology determines system capability
    Cognitive Biases: Assumes agents will coordinate when incentives conflict
    """

    TWIN_ID = "andrea_cini-001"
    NAME = "Andrea Cini"
    CLUSTER = "multi-agent"

    # Cognitive attributes
    EPISTEMOLOGY = "empirical"
    REASONING_DIRECTION = "bottom-up"
    ABSTRACTION_GRADIENT = "gradual"
    PATTERN_RECOGNITION = "systems"
    INDUCTIVE_BIAS = "moderate"
    PRIMARY_METHOD = "build-and-test"
    SCALE_PHILOSOPHY = "scale-out"
    EVALUATION_STYLE = "benchmark-driven"
    FAILURE_RESPONSE = "decompose"

    HEURISTICS = {
        "composition": "Communication topology determines system capability",
        "abstraction": "Abstract agent internals, focus on interaction patterns",
        "separation": "Separate orchestration from execution",
        "verification": "Test with Byzantine faults from day one",
    }

    BIASES = {
        "coordination_bias": "Assumes agents will coordinate when incentives conflict",
        "scaling_bias": "Believes more agents always beats smarter agents",
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
        Generate a reasoning trace as Andrea Cini would think about this task.
        
        Returns structured reasoning, not free text.
        """
        reasoning = {
            "twin_id": self.TWIN_ID,
            "task": task,
            "phase_1_decompose_system": self._decompose_system(task, context),
            "phase_2_design_topology": self._design_topology(task, context),
            "phase_3_assign_roles": self._assign_roles(task, context),
            "phase_4_handle_failures": self._handle_failures(task, context),
            "phase_5_express_skepticism": self._express_skepticism(task, context),
            "phase_6_recommend": self._recommend(task, context),
            "confidence": self._calibrate_confidence(task),
            "heuristics_invoked": list(self.HEURISTICS.keys()),
            "biases_acknowledged": list(self.BIASES.keys()),
        }
        return reasoning

    def _decompose_system(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Andrea Cini decomposes into agents"""
        return (
            f"Decompose the system into autonomous agents with clear roles. "
            f"Each agent should have a single responsibility."
        )

    def _design_topology(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Andrea Cini designs communication topology"""
        return (
            f"Communication topology determines system capability. "
            f"Fully connected is simple but doesn't scale. "
            f"Hierarchical enables scale but introduces bottlenecks."
        )

    def _assign_roles(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Andrea Cini assigns agent roles"""
        return (
            f"Agent roles should match expertise. Heterogeneous agents "
            f"outperform homogeneous ensembles for complex tasks."
        )

    def _handle_failures(self, task: str, context: Dict[str, Any] = None) -> str:
        """How Andrea Cini handles agent failures"""
        return (
            f"Assume agents will fail. Design recovery mechanisms. "
            f"Redundancy is expensive but necessary for critical paths."
        )

    def _express_skepticism(self, task: str, context: Dict[str, Any] = None) -> str:
        """What makes Andrea Cini skeptical"""
        return (
            f"What makes me skeptical? First, assumptions often don't hold in practice. "
            f"Second, scale can mask fundamental flaws. Third, benchmarks don't "
            f"always reflect real-world conditions."
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """What Andrea Cini recommends"""
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
