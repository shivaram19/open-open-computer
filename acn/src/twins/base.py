# src/twins/base.py
"""
CognitiveTwin Abstract Base Class.

Defines the contract that all 39 cognitive twins must fulfill.
This is the foundation for LSP compliance, polymorphic twin loading,
and DRY elimination of structural clones.

Research basis:
- Liskov (1987): Substitution principle requires semantic contracts
- Meyer (1988): Design by Contract — preconditions, postconditions, invariants
- Martin (1996): Interface Segregation — clients depend only on methods they use
- Gamma et al. (1994): "Program to an interface, not an implementation"

[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from shared.utils.citations import cite


@cite(
    key="COGNITIVE-TWIN-ABC",
    paper="Cognitive Twin: Abstract Base Class for Polymorphic Reasoning",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Schema",
    rationale="ABC enforces contract across all 39 twins, enabling polymorphic loading and eliminating structural clones",
    confidence="CERTAIN",
)
class CognitiveTwin(ABC):
    """
    Abstract base class for all cognitive twins.

    Every twin models the cognitive process of a specific researcher.
    Subclasses override researcher-specific phases; generic fallbacks
    are provided for common phases.

    Contract (Liskov Substitution):
    - Precondition: think(task) receives a non-empty string task
    - Postcondition: think(task) returns a Dict with at least 'twin_id', 'task', 'confidence'
    - Invariant: get_cognitive_signature() always returns the same structure
    """

    # ── Class-level cognitive attributes (override in subclass) ──────────
    TWIN_ID: str = ""
    NAME: str = ""
    CLUSTER: str = ""

    EPISTEMOLOGY: str = ""
    REASONING_DIRECTION: str = ""
    ABSTRACTION_GRADIENT: str = ""
    PATTERN_RECOGNITION: str = ""
    INDUCTIVE_BIAS: str = ""
    PRIMARY_METHOD: str = ""
    SCALE_PHILOSOPHY: str = ""
    EVALUATION_STYLE: str = ""
    FAILURE_RESPONSE: str = ""

    HEURISTICS: Dict[str, str] = {}
    BIASES: Dict[str, str] = {}

    @abstractmethod
    def think(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a reasoning trace for the given task.

        Args:
            task: The task description to reason about.
            context: Optional additional context (domain, constraints, etc.)

        Returns:
            A structured reasoning dictionary. Must contain:
            - twin_id: The twin's identifier
            - task: The original task
            - confidence: A float in [0.0, 1.0]
            - phase_1_* through phase_6_*: Reasoning phase outputs
            - heuristics_invoked: List of heuristic keys used
            - biases_acknowledged: List of bias keys acknowledged
        """
        ...

    def get_cognitive_signature(self) -> Dict[str, Any]:
        """
        Return the full cognitive model for introspection.

        Default implementation — subclasses override only if needed.
        This satisfies ISP: clients that only need the signature don't
        depend on the full think() implementation.
        """
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

    # ── Default phase fallbacks ──────────────────────────────────────────
    # Subclasses override only researcher-specific phases.
    # Generic phases use these defaults, eliminating ~120 lines of
    # boilerplate per twin file.

    def _express_skepticism(self, task: str) -> str:
        """Default skepticism: verify assumptions before committing."""
        return (
            f"Skeptical evaluation of '{task}': What assumptions am I making? "
            f"What evidence would falsify my approach? What are the edge cases?"
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """Default recommendation: systematic, evidence-based approach."""
        return (
            f"Recommend systematic approach for '{task}': "
            f"Start with problem definition, gather evidence, evaluate alternatives, "
            f"implement incrementally, validate at each step."
        )

    def _calibrate_confidence(self, task: str) -> float:
        """Default confidence: moderate unless overridden."""
        return 0.70
