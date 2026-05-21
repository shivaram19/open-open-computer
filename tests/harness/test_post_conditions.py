# tests/harness/test_post_conditions.py
"""Tests for post-conditions with auto-retry (Strands-inspired)."""

import pytest

from harness.post_conditions import (
    PostConditionResult,
    SyntaxPostCondition,
    SignaturePostCondition,
    RegexPostCondition,
    PostConditionValidator,
    ValidationResult,
)
from harness.code_generator import GenerationResult, TemplateCodeGenerator, FallbackCodeGenerator


class TestSyntaxPostCondition:
    """Validate Python syntax checking."""

    def test_valid_python_passes(self):
        cond = SyntaxPostCondition()
        result = GenerationResult(
            code="def foo():\n    return 42\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is True
        assert "Syntax valid" in pcr.message

    def test_invalid_python_fails(self):
        cond = SyntaxPostCondition()
        result = GenerationResult(
            code="def foo(\n    return 42\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is False
        assert "Syntax error" in pcr.message

    def test_empty_code_fails(self):
        cond = SyntaxPostCondition()
        result = GenerationResult(
            code="",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is False
        assert "empty" in pcr.message.lower()


class TestSignaturePostCondition:
    """Validate function signature detection."""

    def test_signature_found(self):
        cond = SignaturePostCondition("fibonacci")
        result = GenerationResult(
            code="def fibonacci(n):\n    return n\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is True
        assert "found" in pcr.message

    def test_signature_not_found(self):
        cond = SignaturePostCondition("factorial")
        result = GenerationResult(
            code="def fibonacci(n):\n    return n\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is False
        assert "not found" in pcr.message

    def test_signature_with_args(self):
        cond = SignaturePostCondition("add")
        result = GenerationResult(
            code="def add(a, b):\n    return a + b\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is True


class TestRegexPostCondition:
    """Validate regex pattern matching."""

    def test_pattern_matches(self):
        cond = RegexPostCondition(r"return\s+42", "returns 42")
        result = GenerationResult(
            code="def foo():\n    return 42\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is True

    def test_pattern_missing(self):
        cond = RegexPostCondition(r"import numpy", "uses numpy")
        result = GenerationResult(
            code="def foo():\n    return 42\n",
            success=True,
            strategy="template",
            latency_ms=1.0,
        )
        pcr = cond.validate(result)
        assert pcr.passed is False
        assert "not found" in pcr.message


class TestPostConditionValidator:
    """Test the auto-retry validator."""

    def test_no_conditions_always_passes(self):
        validator = PostConditionValidator(max_attempts=3)
        result = GenerationResult(
            code="x = 1", success=True, strategy="template", latency_ms=1.0,
        )
        v = validator.validate(result, [], TemplateCodeGenerator(), "test")
        assert v.passed is True
        assert v.attempts == 1

    def test_all_pass_first_try(self):
        validator = PostConditionValidator(max_attempts=3)
        result = GenerationResult(
            code="def foo():\n    return 42\n",
            success=True, strategy="template", latency_ms=1.0,
        )
        conditions = [SyntaxPostCondition()]
        v = validator.validate(
            result, conditions, TemplateCodeGenerator(), "test",
        )
        assert v.passed is True
        assert v.attempts == 1
        assert v.result.validation_passed is True

    def test_retry_succeeds(self):
        """First attempt fails syntax, retry with feedback fixes it."""
        validator = PostConditionValidator(max_attempts=3)
        # Start with bad syntax
        bad_result = GenerationResult(
            code="def foo(\n    return 42\n",
            success=True, strategy="template", latency_ms=1.0,
        )
        conditions = [SyntaxPostCondition()]
        v = validator.validate(
            bad_result, conditions, TemplateCodeGenerator(), "write hello world function",
        )
        # Template generator will produce valid code on retry
        assert v.attempts >= 1
        assert v.result.validation_passed is True
        assert v.passed is True

    def test_max_attempts_exceeded(self):
        """A condition that always fails should exhaust attempts."""
        validator = PostConditionValidator(max_attempts=2)
        result = GenerationResult(
            code="def foo():\n    return 42\n",
            success=True, strategy="template", latency_ms=1.0,
        )
        # A condition that always fails, even on retry
        class AlwaysFail:
            def validate(self, result):
                return PostConditionResult(passed=False, message="Always fails")

        conditions = [AlwaysFail()]
        v = validator.validate(
            result, conditions, TemplateCodeGenerator(), "test",
        )
        assert v.passed is False
        assert v.attempts == 2
        assert v.result.validation_passed is False
        assert len(v.failures) > 0

    def test_exception_in_condition_caught(self):
        validator = PostConditionValidator(max_attempts=2)
        result = GenerationResult(
            code="def foo(): pass", success=True, strategy="template", latency_ms=1.0,
        )

        class ExplodingCondition:
            def validate(self, result):
                raise RuntimeError("boom")

        conditions = [ExplodingCondition()]
        v = validator.validate(
            result, conditions, TemplateCodeGenerator(), "test",
        )
        assert v.passed is False
        assert "boom" in v.failures[0].message


class TestPostConditionIntegration:
    """Test post-conditions wired into FallbackCodeGenerator."""

    def test_generator_with_post_conditions(self):
        conditions = [SyntaxPostCondition()]
        gen = FallbackCodeGenerator(
            llm_generator=None,
            template_generator=TemplateCodeGenerator(),
            post_conditions=conditions,
            max_validation_attempts=3,
        )
        result = gen.generate_code("Write a hello world function")
        assert result.success is True
        assert result.validation_passed is True
        assert result.attempts >= 1

    def test_generator_without_post_conditions(self):
        gen = FallbackCodeGenerator(
            llm_generator=None,
            template_generator=TemplateCodeGenerator(),
        )
        result = gen.generate_code("Write a hello world function")
        assert result.success is True
        assert result.attempts == 1  # Default, no validation

    def test_generator_signature_condition(self):
        conditions = [
            SyntaxPostCondition(),
            SignaturePostCondition("hello"),
        ]
        gen = FallbackCodeGenerator(
            llm_generator=None,
            template_generator=TemplateCodeGenerator(),
            post_conditions=conditions,
            max_validation_attempts=3,
        )
        result = gen.generate_code("Write a hello world function")
        assert result.success is True
        assert result.validation_passed is True
