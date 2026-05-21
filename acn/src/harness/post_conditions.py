# src/harness/post_conditions.py
"""
Post-Conditions: Declarative validation layer for code generation.

Inspired by Strands AI Functions (strands-labs/ai-functions, 2026):
- Post-conditions validate outputs before they propagate downstream
- Failed conditions trigger self-correcting retry loops
- Avoids cascading errors from bad code generation

Principle: Trust but verify. Then verify again.

[CITATION: Strands2026]
"""

import ast
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

from shared.utils.citations import cite
from harness.code_generator import CodeGenerator, GenerationResult


@dataclass
class PostConditionResult:
    """Outcome of a single post-condition check."""
    passed: bool
    message: str = ""


@cite(
    key="POST-COND-IFACE",
    paper="Strands AI Functions: Post-Condition Validation",
    venue="ACN Harness Architecture",
    section="P5-5 Post-Conditions",
    rationale="Declarative validation interface inspired by Strands",
    confidence="HIGH",
)
class PostCondition(ABC):
    """Abstract post-condition: validates a GenerationResult."""

    @abstractmethod
    def validate(self, result: GenerationResult) -> PostConditionResult:
        """Return PostConditionResult(passed=True) if condition satisfied."""
        ...


class SyntaxPostCondition(PostCondition):
    """Validate that generated code is syntactically valid Python."""

    def validate(self, result: GenerationResult) -> PostConditionResult:
        if not result.code or not result.code.strip():
            return PostConditionResult(
                passed=False,
                message="Code is empty",
            )
        try:
            ast.parse(result.code)
            return PostConditionResult(
                passed=True,
                message="Syntax valid",
            )
        except SyntaxError as exc:
            return PostConditionResult(
                passed=False,
                message=f"Syntax error: {exc}",
            )


class SignaturePostCondition(PostCondition):
    """Validate that generated code contains an expected function signature."""

    def __init__(self, expected_signature: str):
        self.expected_signature = expected_signature

    def validate(self, result: GenerationResult) -> PostConditionResult:
        pattern = rf"def\s+{re.escape(self.expected_signature)}\s*\("
        if re.search(pattern, result.code):
            return PostConditionResult(
                passed=True,
                message=f"Signature '{self.expected_signature}' found",
            )
        return PostConditionResult(
            passed=False,
            message=f"Expected signature '{self.expected_signature}' not found in code",
        )


class RegexPostCondition(PostCondition):
    """Validate that generated code matches a regex pattern."""

    def __init__(self, pattern: str, description: str = ""):
        self.pattern = re.compile(pattern)
        self.description = description or pattern

    def validate(self, result: GenerationResult) -> PostConditionResult:
        if self.pattern.search(result.code):
            return PostConditionResult(
                passed=True,
                message=f"Pattern '{self.description}' matched",
            )
        return PostConditionResult(
            passed=False,
            message=f"Pattern '{self.description}' not found in code",
        )


@dataclass
class ValidationResult:
    """Outcome of a full validation run with potential retries."""
    result: GenerationResult
    passed: bool
    attempts: int = 0
    failures: List[PostConditionResult] = field(default_factory=list)
    final_feedback: str = ""


@cite(
    key="POST-COND-VALIDATOR",
    paper="Strands AI Functions: Self-Correcting Validation",
    venue="ACN Harness Architecture",
    section="P5-5 Post-Condition Validator",
    rationale="Auto-retry loop with feedback injection inspired by Strands",
    confidence="HIGH",
)
class PostConditionValidator:
    """
    Runs post-conditions on generated code with auto-retry.

    If conditions fail, re-invokes the generator with feedback
    appended to the approach prompt. Respects max_attempts.
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts

    def validate(
        self,
        result: GenerationResult,
        conditions: List[PostCondition],
        generator: CodeGenerator,
        approach: str,
        language: str = "python",
        test_cases: Optional[List[Dict[str, str]]] = None,
    ) -> ValidationResult:
        """
        Validate result against conditions. Retry with feedback on failure.

        Args:
            result: Initial generation result to validate.
            conditions: Post-conditions to enforce.
            generator: CodeGenerator to use for retries.
            approach: Original approach description (enriched with feedback on retry).
            language: Target programming language.
            test_cases: Optional test cases for generation.

        Returns:
            ValidationResult with final result, pass/fail, attempts, and failures.
        """
        if not conditions:
            return ValidationResult(
                result=result,
                passed=True,
                attempts=1,
            )

        attempts = 0
        current_result = result
        all_failures: List[PostConditionResult] = []
        final_feedback = ""

        while attempts < self.max_attempts:
            attempts += 1
            wave_failures: List[PostConditionResult] = []

            for condition in conditions:
                try:
                    pcr = condition.validate(current_result)
                except Exception as exc:
                    pcr = PostConditionResult(
                        passed=False,
                        message=f"Condition raised exception: {exc}",
                    )
                if not pcr.passed:
                    wave_failures.append(pcr)

            if not wave_failures:
                # All conditions passed
                current_result.attempts = attempts
                current_result.validation_passed = True
                return ValidationResult(
                    result=current_result,
                    passed=True,
                    attempts=attempts,
                    failures=all_failures,
                    final_feedback="",
                )

            all_failures.extend(wave_failures)

            if attempts < self.max_attempts:
                # Build feedback and retry
                feedback_lines = ["[VALIDATION FEEDBACK]"]
                for f in wave_failures:
                    feedback_lines.append(f"- {f.message}")
                feedback = "\n".join(feedback_lines)
                final_feedback = feedback

                enriched_approach = approach + "\n\n" + feedback
                current_result = generator.generate_code(
                    enriched_approach, language, test_cases
                )

        # Max attempts exceeded
        current_result.attempts = attempts
        current_result.validation_passed = False
        return ValidationResult(
            result=current_result,
            passed=False,
            attempts=attempts,
            failures=all_failures,
            final_feedback=final_feedback,
        )
