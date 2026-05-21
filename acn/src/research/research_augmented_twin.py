# src/research/research_augmented_twin.py
"""
ResearchAugmentedTwin: A twin that researches before it thinks.

Wraps any CognitiveTwin with live web + arXiv research.
Injects findings into the think() context as `research_context`.

Principle: A twin that only knows what it was born knowing is a twin
that never grows. Research is how twins learn.

[CITATION: SelfInterview2026]
[CITATION: TencentDB2026]
"""

from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from research.web_research_engine import WebResearchEngine, ResearchFinding


@cite(
    key="RESEARCH-TWIN",
    paper="Research-Augmented Digital Twins for Consensus",
    venue="ACN Research Architecture",
    section="Twin Enhancement",
    rationale="Ground twin reasoning in live research before deliberation",
    confidence="HIGH",
)
class ResearchAugmentedTwin:
    """
    Mixin that adds research capability to any CognitiveTwin.

    Usage:
        class MyTwin(ResearchAugmentedTwin, HarrisonChaseTwin):
            pass

        twin = MyTwin()
        result = twin.think("Should we use BFT or PoS for consensus?")
        # result["research_context"] contains live papers + web findings
    """

    def __init__(self, *args, research_engine: Optional[WebResearchEngine] = None, **kwargs):
        self._research_engine = research_engine or WebResearchEngine()
        self._research_budget = 3  # max findings per think()
        super().__init__(*args, **kwargs)

    def think(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Research-augmented think: fetches live research before reasoning.

        1. Research the task topic
        2. Call parent think() with research_context injected
        3. Return enriched reasoning trace
        """
        # Step 1: Research
        research_findings = self._research_task(task)

        # Step 2: Build research context
        research_context = self._build_research_context(research_findings)

        # Step 3: Call parent think with enriched context
        enriched_context = context or {}
        enriched_context["research_context"] = research_context
        enriched_context["research_findings_count"] = len(research_findings)

        result = super().think(task, enriched_context)

        # Step 4: Attach research metadata to result
        result["research_context"] = research_context
        result["research_findings"] = [
            {
                "title": f.title,
                "source": f.source,
                "url": f.url,
                "snippet": f.snippet,
                "confidence": f.confidence,
            }
            for f in research_findings
        ]
        result["research_enabled"] = True

        return result

    def _research_task(self, task: str) -> List[ResearchFinding]:
        """Extract research query from task and search."""
        query = self._extract_research_query(task)
        if not query:
            return []
        return self._research_engine.research(query, top_k=self._research_budget)

    def _extract_research_query(self, task: str) -> str:
        """
        Extract a researchable query from a task description.

        Simple heuristic: take the task as-is, but strip action verbs
        like 'build', 'write', 'create' to get to the topic.
        """
        # Remove common action prefixes
        action_words = ["build", "write", "create", "design", "implement", "evaluate",
                       "analyze", "compare", "integrate", "develop", "test"]
        task_lower = task.lower()
        for word in action_words:
            if task_lower.startswith(word + " "):
                task = task[len(word):].strip()
                break
        # Remove articles at start
        for article in ["a ", "an ", "the "]:
            if task_lower.startswith(article):
                task = task[len(article):].strip()
                break
        return task[:200]  # Cap length

    def _build_research_context(self, findings: List[ResearchFinding]) -> str:
        """Build a concise research context string from findings."""
        if not findings:
            return "No external research found for this topic."

        lines = ["=== LIVE RESEARCH CONTEXT ==="]
        for i, f in enumerate(findings, 1):
            lines.append(f"\n[{i}] {f.title}")
            lines.append(f"    Source: {f.source} (confidence: {f.confidence:.2f})")
            lines.append(f"    {f.snippet[:200]}...")
            if f.citations:
                lines.append(f"    Citations: {', '.join(f.citations[:3])}")
        lines.append("\n=== END RESEARCH CONTEXT ===")
        return "\n".join(lines)
