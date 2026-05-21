# src/harness/code_generator.py
"""
Code Generation Substrate for P5-5 Autonomous Executor.

Provides multiple generation strategies:
- TemplateCodeGenerator: deterministic, testable, no external dependencies
- LLMCodeGenerator: OpenAI API-based generation for arbitrary tasks
- FallbackCodeGenerator: tries LLM first, falls back to templates

Principle: In God we trust. All others must bring data.
Every generated code block must be executable and verifiable.

[CITATION: AGoT2025]
[CITATION: Besta2024]
"""

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite


@dataclass
class GenerationResult:
    """Result of a code generation attempt."""
    code: str
    success: bool
    strategy: str  # "llm" | "template" | "fallback"
    latency_ms: float
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    attempts: int = 1  # Number of generation attempts (includes retries)
    validation_passed: bool = True  # Did post-conditions pass


@cite(
    key="CODE-GEN-PROTOCOL",
    paper="Autonomous Executor: Code Generation Protocol",
    venue="ACN Harness Architecture",
    section="P5-5 Code Generation",
    rationale="Abstract interface enables swapping generation strategies without changing callers",
    confidence="CERTAIN",
)
class CodeGenerator(ABC):
    """Abstract interface for code generation strategies."""

    @abstractmethod
    def generate_code(
        self,
        approach: str,
        language: str = "python",
        test_cases: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        """Generate executable code from a natural language approach."""
        ...


@cite(
    key="CODE-GEN-TEMPLATE",
    paper="Autonomous Executor: Template-Based Code Generation",
    venue="ACN Harness Architecture",
    section="P5-5 Code Generation",
    rationale="Deterministic, zero-cost generation for common patterns; essential for tests",
    confidence="CERTAIN",
)
class TemplateCodeGenerator(CodeGenerator):
    """
    Deterministic template-based code generation.

    Zero external dependencies. Predictable output. Perfect for tests.
    """

    def generate_code(
        self,
        approach: str,
        language: str = "python",
        test_cases: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        start = time.time()
        test_cases = test_cases or []

        if language != "python":
            return GenerationResult(
                code="",
                success=False,
                strategy="template",
                latency_ms=(time.time() - start) * 1000,
                error=f"Template generation for {language} not supported",
            )

        approach_lower = approach.lower()

        if "fibonacci" in approach_lower:
            code = self._template_fibonacci(test_cases)
        elif "hello" in approach_lower or "printer" in approach_lower:
            code = self._template_hello_world(test_cases)
        elif "add" in approach_lower or "sum" in approach_lower:
            code = self._template_add_function(test_cases)
        else:
            code = self._template_generic(approach, test_cases)

        return GenerationResult(
            code=code,
            success=True,
            strategy="template",
            latency_ms=(time.time() - start) * 1000,
        )

    def _template_fibonacci(self, test_cases: List[Dict[str, str]]) -> str:
        code = '''def fibonacci(n):
    """Return the nth Fibonacci number iteratively."""
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

'''
        for tc in test_cases:
            inp = tc.get("input", "")
            if inp:
                code += f"print({inp})\n"
        if not test_cases:
            code += "print(fibonacci(10))\n"
        return code

    def _template_hello_world(self, test_cases: List[Dict[str, str]]) -> str:
        code = '''def hello_world():
    """Print a greeting."""
    return "Hello, World!"

'''
        for tc in test_cases:
            inp = tc.get("input", "")
            if inp:
                code += f"print({inp})\n"
        if not test_cases:
            code += "print(hello_world())\n"
        return code

    def _template_add_function(self, test_cases: List[Dict[str, str]]) -> str:
        code = '''def add(a, b):
    """Return the sum of a and b."""
    return a + b

'''
        for tc in test_cases:
            inp = tc.get("input", "")
            if inp:
                code += f"print({inp})\n"
        if not test_cases:
            code += "print(add(2, 3))\n"
        return code

    def _template_generic(self, approach: str, test_cases: List[Dict[str, str]]) -> str:
        code = f'''# Approach: {approach}
def generated_function():
    """Auto-generated from consensus approach."""
    return "generated"

'''
        for tc in test_cases:
            inp = tc.get("input", "")
            if inp:
                code += f"print({inp})\n"
        if not test_cases:
            code += "print(generated_function())\n"
        return code


@cite(
    key="CODE-GEN-LLM",
    paper="Autonomous Executor: LLM-Based Code Generation",
    venue="ACN Harness Architecture",
    section="P5-5 Code Generation",
    rationale="LLM enables arbitrary code generation beyond hardcoded templates",
    confidence="HIGH",
)
class LLMCodeGenerator(CodeGenerator):
    """
    OpenAI API-based code generation.

    Uses GPT-4o-mini for fast, cost-effective generation.
    Structured via system prompt with citation governance.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client: Optional[Any] = None

    def _get_client(self) -> Any:
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError as exc:
                raise RuntimeError("openai package not installed. Run: pip install openai") from exc
        return self._client

    def generate_code(
        self,
        approach: str,
        language: str = "python",
        test_cases: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        start = time.time()
        test_cases = test_cases or []

        if not self.api_key:
            return GenerationResult(
                code="",
                success=False,
                strategy="llm",
                latency_ms=(time.time() - start) * 1000,
                error="No OpenAI API key configured",
            )

        # Build structured prompt
        test_section = ""
        if test_cases:
            test_lines = "\n".join(
                f"- {tc.get('input', '')} → {tc.get('expected_output', '')}"
                for tc in test_cases
            )
            test_section = f"\nThe code must satisfy these test cases:\n{test_lines}\n"

        prompt = f"""Generate {language} code for the following approach.

Approach: {approach}{test_section}

Requirements:
- Output ONLY the code, no markdown fences, no explanations
- Include a docstring for the main function
- Include print statements that demonstrate the function working
- The code must be runnable as a standalone script
"""

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert software engineer. "
                            "You write clean, correct, runnable code. "
                            "You never include explanations outside the code."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            code = response.choices[0].message.content or ""
            # Strip markdown fences if the model included them
            code = code.strip()
            if code.startswith("```"):
                code = "\n".join(code.split("\n")[1:])
            if code.endswith("```"):
                code = "\n".join(code.split("\n")[:-1])
            code = code.strip()

            tokens = response.usage.total_tokens if response.usage else None

            return GenerationResult(
                code=code,
                success=len(code) > 0,
                strategy="llm",
                latency_ms=(time.time() - start) * 1000,
                tokens_used=tokens,
            )

        except Exception as exc:
            return GenerationResult(
                code="",
                success=False,
                strategy="llm",
                latency_ms=(time.time() - start) * 1000,
                error=str(exc),
            )


@cite(
    key="CODE-GEN-FALLBACK",
    paper="Autonomous Executor: Fallback Code Generation",
    venue="ACN Harness Architecture",
    section="P5-5 Code Generation",
    rationale="Reliability through graceful degradation: LLM preferred, templates guaranteed",
    confidence="CERTAIN",
)
class FallbackCodeGenerator(CodeGenerator):
    """
    Tries LLM first; falls back to templates on failure.

    Optionally validates generated code with post-conditions
    and auto-retries with feedback (Strands-inspired).

    Production default: maximizes capability while guaranteeing output.
    """

    def __init__(
        self,
        llm_generator: Optional[LLMCodeGenerator] = None,
        template_generator: Optional[TemplateCodeGenerator] = None,
        post_conditions: Optional[List[Any]] = None,
        max_validation_attempts: int = 3,
    ):
        self.llm = llm_generator or LLMCodeGenerator()
        self.template = template_generator or TemplateCodeGenerator()
        self.post_conditions = post_conditions or []
        self.max_validation_attempts = max_validation_attempts
        self._validator: Optional[Any] = None

    def _get_validator(self) -> Any:
        if self._validator is None and self.post_conditions:
            from harness.post_conditions import PostConditionValidator
            self._validator = PostConditionValidator(self.max_validation_attempts)
        return self._validator

    def generate_code(
        self,
        approach: str,
        language: str = "python",
        test_cases: Optional[List[Dict[str, str]]] = None,
    ) -> GenerationResult:
        # Try LLM first
        llm_result = self.llm.generate_code(approach, language, test_cases)
        if llm_result.success:
            result = llm_result
        else:
            # Fall back to templates
            template_result = self.template.generate_code(approach, language, test_cases)
            if template_result.success:
                result = GenerationResult(
                    code=template_result.code,
                    success=True,
                    strategy="fallback",
                    latency_ms=llm_result.latency_ms + template_result.latency_ms,
                    error=f"LLM failed ({llm_result.error}); used template fallback",
                )
            else:
                # Both failed
                return GenerationResult(
                    code="",
                    success=False,
                    strategy="fallback",
                    latency_ms=llm_result.latency_ms + template_result.latency_ms,
                    error=f"LLM: {llm_result.error}; Template: {template_result.error}",
                )

        # Post-condition validation with auto-retry
        validator = self._get_validator()
        if validator is not None:
            v = validator.validate(
                result=result,
                conditions=self.post_conditions,
                generator=self,
                approach=approach,
                language=language,
                test_cases=test_cases,
            )
            result = v.result

        return result
