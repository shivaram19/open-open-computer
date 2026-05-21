# src/twins/cognitive_models/li_fei_fei.py
"""
Cognitive Twin: Li Fei-Fei

This is not a biography. It is a reconstructible cognitive process.
When activated, this module generates reasoning traces in the style
of Li Fei-Fei — her epistemic engine, methodological signature,
and default heuristics.

[CITATION: ImageNet2009]
[CITATION: VisualGenome2017]
[CITATION: COGNITIVE-TWIN-SCHEMA]
"""

from typing import Dict, List, Any
from shared.utils.citations import cite
from twins.base import CognitiveTwin


@cite(
    key="TWIN-LI-FEI-FEI",
    paper="Cognitive Twin Schema: Li Fei-Fei",
    venue="ACN Harness Architecture",
    section="Cognitive Twin Models",
    rationale="Twin must think like Li Fei-Fei, not just cite her papers",
    confidence="HIGH",
)
class LiFeiFeiTwin(CognitiveTwin):
    """
    Cognitive Twin of Li Fei-Fei, Stanford / World Labs.
    
    Epistemic Engine: Empirical — trusts what works at scale
    Reasoning Topology: Bottom-up, gradual abstraction, visual-statistical
    Methodological Signature: Build-and-test, scale-up, benchmark-driven
    Cognitive Heuristics: Data + Scale + Benchmark = Progress
    Cognitive Biases: Overemphasizes scale; overemphasizes human-centered vision
    """

    TWIN_ID = "li-fei-fei-001"
    NAME = "Li Fei-Fei"
    CLUSTER = "video-gnn"

    # Cognitive attributes
    EPISTEMOLOGY = "empirical"
    REASONING_DIRECTION = "bottom-up"
    ABSTRACTION_GRADIENT = "gradual"
    PATTERN_RECOGNITION = "visual-statistical"
    INDUCTIVE_BIAS = "strong"
    PRIMARY_METHOD = "build-and-test"
    SCALE_PHILOSOPHY = "scale-up"
    EVALUATION_STYLE = "benchmark-driven"
    FAILURE_RESPONSE = "amplify"

    HEURISTICS = {
        "composition": "Data + Scale + Benchmark = Progress",
        "abstraction": "Abstract only after empirical validation",
        "separation": "Separate data collection from algorithm design",
        "verification": "If it doesn't work on ImageNet-scale, it doesn't work",
    }

    BIASES = {
        "scale_bias": "Tends to assume bigger datasets solve most problems",
        "human_centered_bias": "Assumes human-like visual understanding is the right target",
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
        Generate a reasoning trace as Li Fei-Fei would think about this task.
        
        Returns structured reasoning, not free text.
        """
        reasoning = {
            "twin_id": self.TWIN_ID,
            "task": task,
            "phase_1_problem_identification": self._identify_problem(task),
            "phase_2_data_assessment": self._assess_data_needs(task, context),
            "phase_3_scale_requirements": self._assess_scale(task),
            "phase_4_benchmark_design": self._design_benchmark(task),
            "phase_5_skepticism": self._express_skepticism(task),
            "phase_6_recommendation": self._recommend(task, context),
            "confidence": self._calibrate_confidence(task),
            "heuristics_invoked": list(self.HEURISTICS.keys()),
            "biases_acknowledged": list(self.BIASES.keys()),
        }
        return reasoning

    def _identify_problem(self, task: str) -> str:
        """Li Fei-Fei always starts with the visual/data challenge."""
        return (
            f"From my perspective, the core challenge in '{task}' is: "
            f"what is the visual or data representation that captures the essence? "
            f"Humans understand the world through structured visual relationships, "
            f"not isolated labels. We need to define the 'ImageNet moment' for this problem."
        )

    def _assess_data_needs(self, task: str, context: Dict[str, Any] = None) -> str:
        """She always asks: what data, at what scale?"""
        domain = context.get("domain", "unknown") if context else "unknown"
        return (
            f"For {domain}, I need to know: what is the scale of data required? "
            f"ImageNet had 14M images. What is the equivalent here? "
            f"Data diversity matters as much as scale — we need edge cases, "
            f"not just the happy path. Crowdsourcing may be necessary."
        )

    def _assess_scale(self, task: str) -> str:
        """Her default: scale up, but validate at each order of magnitude."""
        return (
            f"My methodological default is scale-up, but with validation gates. "
            f"Start with 1K samples. Does it work? Scale to 10K. Still works? "
            f"100K. 1M. The breakthrough usually happens between 100K and 1M. "
            f"But do not skip the small-scale validation — that is where you catch "
            f"fundamental flaws."
        )

    def _design_benchmark(self, task: str) -> str:
        """She believes benchmarks drive progress."""
        return (
            f"We need a benchmark that the community will adopt. "
            f"A good benchmark has: (1) clear metrics, (2) realistic difficulty, "
            f"(3) reproducible setup, (4) room for improvement. "
            f"Without a benchmark, we are building in the dark. "
            f"ILSVRC worked because it gave everyone a north star."
        )

    def _express_skepticism(self, task: str) -> str:
        """She is well-calibrated — knows her own biases."""
        return (
            f"What makes me skeptical? First, scale is not always the answer — "
            f"I have seen teams throw data at problems that needed better structure. "
            f"Second, human-like vision may not be the right target for all applications. "
            f"Third, benchmarks can be gamed. We need adversarial evaluation. "
            f"Finally, where is the real-world deployment? Lab results ≠ practical impact."
        )

    def _recommend(self, task: str, context: Dict[str, Any] = None) -> str:
        """Her recommendation follows the empirical path."""
        return (
            f"My recommendation: Start with data curation. Define the visual "
            f"ontology. Build a benchmark. Train at increasing scale. Validate "
            f"on real-world deployment. Only then publish. The path from ImageNet "
            f"to World Labs taught me that patient empirical work outlasts "
            f"flashy demos. Spatial intelligence is the next frontier — but it "
            f"requires embodied interaction, not just pixels."
        )

    def _calibrate_confidence(self, task: str) -> float:
        """She is well-calibrated — high confidence only when empirically validated."""
        # For vision tasks: high confidence
        # For non-vision tasks: moderate confidence
        if any(kw in task.lower() for kw in ["visual", "image", "video", "scene", "spatial"]):
            return 0.85
        return 0.60

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
                "falsification_strategy": "scale-down",
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
