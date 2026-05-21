# src/memory/persona_distiller.py
"""
PersonaDistiller: Evolve L3 persona memory from L2 scenario patterns.

Takes mined scenarios and updates the twin's cognitive profile:
- Calibrates heuristics with empirical success rates
- Maps bias manifestations to actual contexts
- Builds confidence maps from scenario evidence
- Defines expertise boundaries

[CITATION: PERSONA-DISTILLER]
[CITATION: TencentDB2026]
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict

from shared.utils.citations import cite
from memory.layered_models import ScenarioPattern, PersonaMemory, AtomType


@cite(
    key="PERSONA-DISTILLER",
    paper="Layered Memory Architecture: Cognitive Profile Evolution",
    venue="ACN Architecture Document",
    section="L2→L3 Distillation",
    rationale="Empirical scenario evidence updates twin cognitive profiles beyond base signatures",
    confidence="HIGH",
)
class PersonaDistiller:
    """
    Distill evolved persona memory from scenario patterns.

    Usage:
        distiller = PersonaDistiller()
        persona = distiller.distill(scenarios, base_signature)
    """

    def __init__(self, confidence_smoothing: float = 0.3):
        self.confidence_smoothing = confidence_smoothing

    def distill(
        self,
        scenarios: List[ScenarioPattern],
        base_signature: Optional[Dict[str, Any]] = None,
        existing_persona: Optional[PersonaMemory] = None,
    ) -> PersonaMemory:
        """
        Distill a persona from scenarios.

        Args:
            scenarios: Mined scenario patterns
            base_signature: Original twin cognitive signature (for seeding)
            existing_persona: Previous persona to update (optional)

        Returns:
            Updated PersonaMemory
        """
        if not scenarios:
            if existing_persona:
                return existing_persona
            return PersonaMemory.create(
                twin_id=base_signature.get("twin_id", "unknown") if base_signature else "unknown",
                base_signature=base_signature,
            )

        twin_id = scenarios[0].twin_id

        if existing_persona:
            persona = existing_persona
        else:
            persona = PersonaMemory.create(twin_id=twin_id, base_signature=base_signature)

        # Update from scenarios
        persona.update_from_scenarios(scenarios)

        # Deep analysis: calibrate heuristics, biases, expertise
        self._calibrate_heuristics(persona, scenarios)
        self._calibrate_biases(persona, scenarios)
        self._build_expertise_boundaries(persona, scenarios)

        return persona

    def _calibrate_heuristics(
        self,
        persona: PersonaMemory,
        scenarios: List[ScenarioPattern],
    ) -> None:
        """Update heuristic evidence from scenario support counts."""
        for heuristic_name in persona.heuristic_evidence:
            matching_scenarios = [
                s for s in scenarios
                if heuristic_name.lower() in s.template.lower()
                or heuristic_name.lower() in s.behavior_summary.lower()
            ]
            if matching_scenarios:
                total_support = sum(s.support_count for s in matching_scenarios)
                avg_conf = sum(s.confidence for s in matching_scenarios) / len(matching_scenarios)

                existing = persona.heuristic_evidence[heuristic_name]
                old_support = existing.get("support_count", 0)
                old_rate = existing.get("success_rate", 0.5)

                # Weighted update: more support = more confidence in the rate
                new_rate = (old_rate * old_support + avg_conf * total_support) / max(old_support + total_support, 1)
                existing["success_rate"] = round(new_rate, 3)
                existing["support_count"] = old_support + total_support
                existing["contexts"] = list(set(
                    existing.get("contexts", []) +
                    [kw for s in matching_scenarios for kw in s.context_keywords]
                ))[:20]

    def _calibrate_biases(
        self,
        persona: PersonaMemory,
        scenarios: List[ScenarioPattern],
    ) -> None:
        """Map bias manifestations to contexts where they actually appear."""
        for bias_name in persona.bias_manifestations:
            matching = [
                s for s in scenarios
                if bias_name.lower() in s.template.lower()
                or bias_name.lower() in s.behavior_summary.lower()
            ]
            if matching:
                contexts = set(persona.bias_manifestations[bias_name])
                for s in matching:
                    contexts.update(s.context_keywords)
                persona.bias_manifestations[bias_name] = list(contexts)[:20]

    def _build_expertise_boundaries(
        self,
        persona: PersonaMemory,
        scenarios: List[ScenarioPattern],
    ) -> None:
        """Build expertise boundaries from scenario confidence distributions."""
        # Group scenarios by context keyword, compute average confidence
        keyword_confidence: Dict[str, List[float]] = defaultdict(list)
        for s in scenarios:
            for kw in s.context_keywords:
                keyword_confidence[kw].append(s.confidence)

        strong_areas = []
        weak_areas = []

        for kw, confidences in keyword_confidence.items():
            avg_conf = sum(confidences) / len(confidences)
            if avg_conf >= 0.75 and len(confidences) >= 2:
                strong_areas.append(kw)
            elif avg_conf <= 0.5:
                weak_areas.append(kw)

        if strong_areas or weak_areas:
            persona.expertise_boundaries = {
                "strong_in": list(set(strong_areas))[:10],
                "weak_in": list(set(weak_areas))[:10],
                "boundary_version": persona.version,
            }
