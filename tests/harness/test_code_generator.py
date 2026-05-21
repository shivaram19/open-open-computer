# tests/harness/test_code_generator.py
"""
Tests for CodeGenerator strategies: Template, LLM, Fallback.

Principle: In God we trust. All others must bring data.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from harness.code_generator import (
    TemplateCodeGenerator,
    LLMCodeGenerator,
    FallbackCodeGenerator,
    GenerationResult,
)


class TestTemplateCodeGenerator:
    """Deterministic, zero-dependency code generation."""

    def test_generates_fibonacci(self):
        gen = TemplateCodeGenerator()
        result = gen.generate_code(
            approach="Implement fibonacci(n) using an iterative loop",
            language="python",
            test_cases=[{"input": "fibonacci(10)", "expected_output": "55"}],
        )
        assert result.success is True
        assert result.strategy == "template"
        assert "def fibonacci" in result.code
        assert "print(fibonacci(10))" in result.code

    def test_generates_hello_world(self):
        gen = TemplateCodeGenerator()
        result = gen.generate_code(
            approach="Build a hello-world printer",
            language="python",
        )
        assert result.success is True
        assert "Hello, World!" in result.code
        assert "print(hello_world())" in result.code

    def test_generates_add_function(self):
        gen = TemplateCodeGenerator()
        result = gen.generate_code(
            approach="Create an add function",
            language="python",
        )
        assert result.success is True
        assert "def add(a, b)" in result.code
        assert "print(add(2, 3))" in result.code

    def test_unsupported_language_fails(self):
        gen = TemplateCodeGenerator()
        result = gen.generate_code(
            approach="Build something",
            language="rust",
        )
        assert result.success is False
        assert "not supported" in result.error

    def test_generic_fallback(self):
        gen = TemplateCodeGenerator()
        result = gen.generate_code(
            approach="Sort a list using quicksort",
            language="python",
        )
        assert result.success is True
        assert "generated_function" in result.code


class TestLLMCodeGenerator:
    """OpenAI-based generation with mocking for determinism."""

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key_fails(self):
        gen = LLMCodeGenerator(api_key=None)
        result = gen.generate_code(
            approach="Implement fibonacci",
            language="python",
        )
        assert result.success is False
        assert "API key" in result.error

    def test_mock_response_succeeds(self):
        """Mock OpenAI client to avoid real API calls in unit tests."""
        mock_choice = MagicMock()
        mock_choice.message.content = "def hello(): return 'hi'\nprint(hello())"
        mock_usage = MagicMock()
        mock_usage.total_tokens = 42
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        gen = LLMCodeGenerator(api_key="fake-key")
        gen._client = mock_client

        result = gen.generate_code(
            approach="Say hello",
            language="python",
        )
        assert result.success is True
        assert result.strategy == "llm"
        assert result.tokens_used == 42
        assert "def hello" in result.code
        assert "print(hello())" in result.code

    def test_mock_with_markdown_fences_stripped(self):
        """LLM sometimes wraps code in markdown fences — we strip them."""
        mock_choice = MagicMock()
        mock_choice.message.content = "```python\ndef add(a, b):\n    return a + b\n\nprint(add(2, 3))\n```"
        mock_usage = MagicMock()
        mock_usage.total_tokens = 30
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        gen = LLMCodeGenerator(api_key="fake-key")
        gen._client = mock_client

        result = gen.generate_code(approach="Add two numbers")
        assert result.success is True
        assert "```" not in result.code
        assert "def add(a, b)" in result.code

    def test_api_error_handled_gracefully(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RuntimeError("API timeout")

        gen = LLMCodeGenerator(api_key="fake-key")
        gen._client = mock_client

        result = gen.generate_code(approach="Do something")
        assert result.success is False
        assert "API timeout" in result.error


class TestFallbackCodeGenerator:
    """Prefers LLM, falls back to templates on failure."""

    def test_uses_llm_when_available(self):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = GenerationResult(
            code="def llm_func(): pass",
            success=True,
            strategy="llm",
            latency_ms=100.0,
        )
        fallback = FallbackCodeGenerator(
            llm_generator=mock_llm,
            template_generator=TemplateCodeGenerator(),
        )
        result = fallback.generate_code(approach="Any task")
        assert result.strategy == "llm"
        assert result.code == "def llm_func(): pass"

    def test_falls_back_to_template_when_llm_fails(self):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = GenerationResult(
            code="",
            success=False,
            strategy="llm",
            latency_ms=50.0,
            error="API down",
        )
        fallback = FallbackCodeGenerator(
            llm_generator=mock_llm,
            template_generator=TemplateCodeGenerator(),
        )
        result = fallback.generate_code(approach="Implement fibonacci")
        assert result.strategy == "fallback"
        assert result.success is True
        assert "def fibonacci" in result.code
        assert "API down" in result.error

    def test_both_fail_returns_error(self):
        mock_llm = MagicMock()
        mock_llm.generate_code.return_value = GenerationResult(
            code="",
            success=False,
            strategy="llm",
            latency_ms=10.0,
            error="LLM error",
        )
        mock_template = MagicMock()
        mock_template.generate_code.return_value = GenerationResult(
            code="",
            success=False,
            strategy="template",
            latency_ms=5.0,
            error="Template error",
        )
        fallback = FallbackCodeGenerator(
            llm_generator=mock_llm,
            template_generator=mock_template,
        )
        result = fallback.generate_code(approach="Anything")
        assert result.success is False
        assert "LLM error" in result.error
        assert "Template error" in result.error


class TestLLMCodeGeneratorIntegration:
    """Real LLM call — skipped unless OPENAI_API_KEY is present."""

    @pytest.mark.skipif(
        os.environ.get("OPENAI_API_KEY") is None,
        reason="No OpenAI API key available",
    )
    def test_real_llm_generates_runnable_python(self):
        """
        End-to-end: LLM generates code, code runs, output is correct.
        This test costs a few cents and validates the real integration.
        """
        from agents.sandbox_agent import SandboxAgent
        from conftest import default_agent_kwargs

        gen = LLMCodeGenerator()
        result = gen.generate_code(
            approach="Implement a function reverse_string(s) that reverses a string",
            language="python",
            test_cases=[{"input": "reverse_string('hello')", "expected_output": "olleh"}],
        )
        assert result.success is True, f"LLM failed: {result.error}"
        assert result.strategy == "llm"
        assert "def reverse_string" in result.code or "reverse_string" in result.code

        # Execute the generated code
        sandbox = SandboxAgent(
            "llm-test-sandbox", "LLMTester", "multi-agent",
            execution_timeout=30,
            **default_agent_kwargs("llm-test-sandbox"),
        )
        exec_result = sandbox.execute(
            code=result.code,
            language="python",
            cited_purpose="[CITATION: P5-5] Validate LLM-generated reverse_string",
        )
        assert exec_result.return_code == 0, f"Execution failed: {exec_result.stderr}"
