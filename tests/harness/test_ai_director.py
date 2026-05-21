# tests/harness/test_ai_director.py
"""Tests for the AI Director meta-cognitive orchestration layer."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from harness.ai_director import AIDirector, DirectorObservation, Direction


class TestAIDirectorInstantiation:
    """Test construction and defaults."""

    def test_default_instantiation(self):
        director = AIDirector()
        assert "AI Director" in director.system_prompt
        assert "Task: {task_id}" in director.user_prompt_template
        assert director.model == "gpt-4o-mini"
        assert director._direction_history == []

    def test_custom_prompts(self):
        director = AIDirector(
            system_prompt="Custom system",
            user_prompt_template="Custom user: {task_id}",
        )
        assert director.system_prompt == "Custom system"
        assert director.user_prompt_template == "Custom user: {task_id}"

    def test_api_key_from_env(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}):
            director = AIDirector()
            assert director.api_key == "sk-test"

    def test_api_key_from_argument(self):
        director = AIDirector(api_key="sk-arg")
        assert director.api_key == "sk-arg"


class TestAIDirectorFallbackLogic:
    """Test rule-based fallback when no LLM is available."""

    def test_failed_status_redirects_retry(self):
        director = AIDirector(api_key=None)
        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="X", consensus_score=0.8,
            execution_status="failed",
        )
        direction = director.direct(obs)
        assert direction.action == "retry"
        assert "Retry" in direction.revised_task_description
        assert direction.reasoning == "Rule-based fallback (no LLM available)"

    def test_low_consensus_triggers_critique(self):
        director = AIDirector(api_key=None)
        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="X", consensus_score=0.3,
            execution_status="completed",
        )
        direction = director.direct(obs)
        assert direction.action == "critique"
        assert "Critique" in direction.revised_task_description

    def test_high_consensus_continue(self):
        director = AIDirector(api_key=None)
        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="X", consensus_score=0.95,
            execution_status="completed",
        )
        direction = director.direct(obs)
        assert direction.action == "continue"
        assert direction.confidence == 0.95

    def test_direction_history_tracked(self):
        director = AIDirector(api_key=None)
        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="X", consensus_score=0.95,
            execution_status="completed",
        )
        director.direct(obs)
        assert len(director.get_direction_history()) == 1
        director.direct(obs)
        assert len(director.get_direction_history()) == 2

    def test_narcissistic_report_empty(self):
        director = AIDirector(api_key=None)
        report = director.get_narcissistic_report()
        assert report["interventions"] == 0
        assert report["avg_confidence"] == 0.0

    def test_narcissistic_report_with_directions(self):
        director = AIDirector(api_key=None)
        obs_ok = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="X", consensus_score=0.95,
            execution_status="completed",
        )
        obs_fail = DirectorObservation(
            task_id="T1", subtask_id="S2",
            consensus_approach="X", consensus_score=0.4,
            execution_status="failed",
        )
        director.direct(obs_ok)
        director.direct(obs_fail)
        report = director.get_narcissistic_report()
        assert report["total_directions"] == 2
        assert report["intervention_rate"] == 0.5  # retry is intervention
        assert report["action_distribution"]["continue"] == 1
        assert report["action_distribution"]["retry"] == 1


class TestAIDirectorLLMPath:
    """Test LLM-based direction generation (mocked)."""

    def test_llm_direct_success(self):
        director = AIDirector(api_key="sk-test")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = (
            '{"action": "redirect", '
            '"revised_task_description": "New approach", '
            '"reasoning": "Consensus was weak", '
            '"confidence": 0.7}'
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        director._client = mock_client

        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="A", consensus_score=0.4,
            execution_status="completed",
        )
        direction = director.direct(obs)
        assert direction.action == "redirect"
        assert direction.revised_task_description == "New approach"
        assert direction.confidence == 0.7
        assert direction.meta_prompt_used == director.system_prompt[:100]
        assert direction.latency_ms > 0

    def test_llm_direct_api_error_falls_back(self):
        director = AIDirector(api_key="sk-test")
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("API down")
        director._client = mock_client

        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="A", consensus_score=0.5,
            execution_status="completed",
        )
        direction = director.direct(obs)
        assert direction.action == "continue"
        assert "API down" in direction.revised_task_description
        assert direction.confidence == 0.3

    def test_llm_direct_malformed_json(self):
        director = AIDirector(api_key="sk-test")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "not json"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        director._client = mock_client

        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="A", consensus_score=0.5,
            execution_status="completed",
        )
        direction = director.direct(obs)
        assert direction.action == "continue"
        assert "continue with caution" in direction.revised_task_description.lower()


class TestAIDirectorCustomDirector:
    """Test custom director callable injection."""

    def test_custom_director_takes_precedence(self):
        def my_director(obs: DirectorObservation) -> Direction:
            return Direction(
                action="complete",
                revised_task_description="All done",
                reasoning="Custom logic",
                confidence=1.0,
            )

        director = AIDirector(api_key=None, custom_director=my_director)
        obs = DirectorObservation(
            task_id="T1", subtask_id="S1",
            consensus_approach="A", consensus_score=0.1,
            execution_status="failed",
        )
        direction = director.direct(obs)
        assert direction.action == "complete"
        assert direction.revised_task_description == "All done"


class TestAIDirectorMetaPromptFiles:
    """Test loading prompts from WeirdDream-style text files."""

    def test_load_from_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            sys_path = Path(tmp) / "system.txt"
            user_path = Path(tmp) / "user.txt"
            sys_path.write_text("You are a strict director.")
            user_path.write_text("Decide: {task_id}")

            director = AIDirector()
            director.load_meta_prompts_from_files(sys_path, user_path)
            assert director.system_prompt == "You are a strict director."
            assert director.user_prompt_template == "Decide: {task_id}"

    def test_load_partial_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            sys_path = Path(tmp) / "system.txt"
            sys_path.write_text("Only system.")
            user_path = Path(tmp) / "missing.txt"

            director = AIDirector()
            director.load_meta_prompts_from_files(sys_path, user_path)
            assert director.system_prompt == "Only system."
            assert "Task: {task_id}" in director.user_prompt_template  # unchanged


class TestAIDirectorObservationDefaults:
    """Test observation dataclass defaults."""

    def test_defaults(self):
        obs = DirectorObservation(
            task_id="T", subtask_id="S",
            consensus_approach=None, consensus_score=0.0,
            execution_status="completed",
        )
        assert obs.artifacts == []
        assert obs.previous_directions == []
        assert obs.swarm_health == 1.0
        assert obs.memory_context == ""
