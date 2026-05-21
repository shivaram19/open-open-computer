# tests/memory/test_persona_distiller.py
"""Tests for PersonaDistiller."""

import pytest
from memory.persona_distiller import PersonaDistiller
from memory.layered_models import ScenarioPattern, PersonaMemory


class TestPersonaDistiller:
    def test_distill_empty_scenarios(self):
        distiller = PersonaDistiller()
        persona = distiller.distill([], base_signature={"twin_id": "twin-001"})
        assert persona.twin_id == "twin-001"
        assert persona.version == 1

    def test_distill_from_scenarios(self):
        distiller = PersonaDistiller()
        scenarios = [
            ScenarioPattern.create(
                template="When consensus, prefers BFT",
                twin_id="twin-001",
                context_keywords=["consensus", "bft", "safety"],
                behavior_summary="Prefers BFT for safety",
                example_atom_ids=["a1", "a2", "a3"],
                confidence=0.9,
            ),
            ScenarioPattern.create(
                template="When code task, high confidence",
                twin_id="twin-001",
                context_keywords=["code", "programming", "debug"],
                behavior_summary="Confident in code tasks",
                example_atom_ids=["a4", "a5"],
                confidence=0.85,
            ),
            ScenarioPattern.create(
                template="When visual task, lower confidence",
                twin_id="twin-001",
                context_keywords=["visual", "image", "ui"],
                behavior_summary="Less confident in visual tasks",
                example_atom_ids=["a6"],
                confidence=0.4,
            ),
        ]
        base_sig = {
            "twin_id": "twin-001",
            "heuristics": {"verification": "Trust proof"},
            "biases": {"pessimism": "Over-engineers"},
        }
        persona = distiller.distill(scenarios, base_signature=base_sig)

        assert persona.twin_id == "twin-001"
        assert persona.version >= 2  # Updated from scenarios
        # Confidence map should have entries
        assert "consensus" in persona.confidence_map
        assert "visual" in persona.confidence_map
        # Expertise boundaries should be built
        assert "strong_in" in persona.expertise_boundaries
        assert "weak_in" in persona.expertise_boundaries

    def test_update_existing_persona(self):
        distiller = PersonaDistiller()
        existing = PersonaMemory.create("twin-001")
        existing.confidence_map = {"old_topic": 0.6}

        scenarios = [
            ScenarioPattern.create(
                template="When testing, uses TDD",
                twin_id="twin-001",
                context_keywords=["testing", "tdd"],
                behavior_summary="Uses TDD",
                example_atom_ids=["a1"],
                confidence=0.8,
            ),
        ]
        updated = distiller.distill(scenarios, existing_persona=existing)
        assert updated.persona_id == existing.persona_id
        assert "old_topic" in updated.confidence_map
        assert "testing" in updated.confidence_map

    def test_heuristic_calibration(self):
        distiller = PersonaDistiller()
        base_sig = {
            "heuristics": {"verification": "Trust = proof + test"},
        }
        scenarios = [
            ScenarioPattern.create(
                template="When verification heuristic applied, success",
                twin_id="twin-001",
                context_keywords=["verification", "proof"],
                behavior_summary="verification heuristic works well",
                example_atom_ids=["a1", "a2", "a3"],
                confidence=0.9,
            ),
        ]
        persona = distiller.distill(scenarios, base_signature=base_sig)
        assert "verification" in persona.heuristic_evidence
        evidence = persona.heuristic_evidence["verification"]
        assert evidence["success_rate"] > 0.5
        assert evidence["support_count"] >= 3

    def test_expertise_boundaries(self):
        distiller = PersonaDistiller()
        scenarios = [
            ScenarioPattern.create(
                template="When math, very confident",
                twin_id="twin-001",
                context_keywords=["math", "logic"],
                behavior_summary="High confidence in math",
                example_atom_ids=["a1", "a2"],
                confidence=0.9,
            ),
            ScenarioPattern.create(
                template="When math problems, solves quickly",
                twin_id="twin-001",
                context_keywords=["math", "algebra"],
                behavior_summary="Fast at math",
                example_atom_ids=["a4", "a5"],
                confidence=0.85,
            ),
            ScenarioPattern.create(
                template="When art, not confident",
                twin_id="twin-001",
                context_keywords=["art", "creative"],
                behavior_summary="Low confidence in art",
                example_atom_ids=["a3"],
                confidence=0.3,
            ),
        ]
        persona = distiller.distill(scenarios)
        boundaries = persona.expertise_boundaries
        assert "math" in boundaries.get("strong_in", [])
        assert "art" in boundaries.get("weak_in", [])

    def test_bias_manifestation_mapping(self):
        distiller = PersonaDistiller()
        base_sig = {
            "biases": {"formalism_bias": "Over-formalizes"},
        }
        scenarios = [
            ScenarioPattern.create(
                template="When formalism_bias manifests in safety tasks",
                twin_id="twin-001",
                context_keywords=["safety", "formalism", "proof"],
                behavior_summary="formalism_bias appears",
                example_atom_ids=["a1"],
                confidence=0.7,
            ),
        ]
        persona = distiller.distill(scenarios, base_signature=base_sig)
        assert "formalism_bias" in persona.bias_manifestations
        assert "safety" in persona.bias_manifestations["formalism_bias"]
