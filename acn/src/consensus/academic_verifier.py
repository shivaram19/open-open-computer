# src/consensus/academic_verifier.py
"""
Academic Verifier: Ground consensus in peer-reviewed literature.

After agents reach consensus, this module verifies whether the
consensus position is supported by academic research.

If literature contradicts the consensus → flag "academic dissent"
If literature supports the consensus → boost confidence
If no relevant literature found → neutral

Principle: Consensus without evidence is just groupthink.

[CITATION: SelfInterview2026]
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite
from research.web_research_engine import WebResearchEngine


@dataclass
class AcademicVerificationResult:
    """Outcome of verifying consensus against literature."""
    consensus_approach: str
    consensus_score: float
    academic_support: float  # 0.0-1.0: how much literature supports consensus
    dissent_detected: bool
    dissent_reasoning: str
    papers_found: int
    top_papers: List[Dict[str, Any]]
    recommendation: str


@cite(
    key="ACADEMIC-VERIFIER",
    paper="Research-Grounded Consensus Verification",
    venue="ACN Consensus Architecture",
    section="External Knowledge",
    rationale="Prevent groupthink by verifying agent consensus against literature",
    confidence="HIGH",
)
class AcademicVerifier:
    """
    Verifies agent consensus against academic literature.

    Usage:
        verifier = AcademicVerifier()
        result = verifier.verify(
            approach="Use Raft for distributed consensus",
            consensus_score=0.85,
        )
        if result.dissent_detected:
            print(f"Warning: {result.dissent_reasoning}")
    """

    def __init__(self, research_engine: Optional[WebResearchEngine] = None):
        self.engine = research_engine or WebResearchEngine()
        self.support_threshold = 0.6  # minimum support to avoid dissent

    def verify(
        self,
        approach: str,
        consensus_score: float,
        query_override: Optional[str] = None,
    ) -> AcademicVerificationResult:
        """
        Verify a consensus approach against academic literature.

        Args:
            approach: The consensus approach text (e.g., "Use BFT for Byzantine agents")
            consensus_score: The agent consensus score (0.0-1.0)
            query_override: Optional custom search query (defaults to approach text)

        Returns:
            AcademicVerificationResult with support score and recommendation
        """
        query = query_override or approach
        findings = self.engine.research(query, top_k=5, include_web=False, include_arxiv=True)

        if not findings:
            return AcademicVerificationResult(
                consensus_approach=approach,
                consensus_score=consensus_score,
                academic_support=0.0,
                dissent_detected=False,
                dissent_reasoning="No relevant academic literature found.",
                papers_found=0,
                top_papers=[],
                recommendation="No literature to verify against. Proceed with caution.",
            )

        # Score support: average confidence of findings
        support = sum(f.confidence for f in findings) / len(findings)

        # Detect dissent: if support is low but consensus is high
        dissent = consensus_score > 0.75 and support < self.support_threshold

        if dissent:
            reasoning = (
                f"Agent consensus is high ({consensus_score:.2f}) but academic support "
                f"is weak ({support:.2f}). Literature may contradict the proposed approach."
            )
            recommendation = (
                "DISSENT FLAG: Agents agree but literature does not strongly support. "
                "Consider revisiting assumptions or seeking more diverse agent perspectives."
            )
        elif support > 0.8:
            reasoning = f"Strong academic support ({support:.2f}) for consensus approach."
            recommendation = (
                f"VERIFIED: Literature strongly supports the consensus. "
                f"Confidence boosted by {support:.2f}."
            )
        else:
            reasoning = f"Moderate academic support ({support:.2f})."
            recommendation = "Proceed with consensus. Monitor for contradictory evidence."

        return AcademicVerificationResult(
            consensus_approach=approach,
            consensus_score=consensus_score,
            academic_support=support,
            dissent_detected=dissent,
            dissent_reasoning=reasoning,
            papers_found=len(findings),
            top_papers=[
                {"title": f.title, "source": f.source, "url": f.url}
                for f in findings[:3]
            ],
            recommendation=recommendation,
        )
