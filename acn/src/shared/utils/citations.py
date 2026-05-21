# src/shared/utils/citations.py
"""
Citation governance for the Autonomous Cognitive Network.

Every module, class, function, and non-trivial constant MUST cite its source.
This module provides infrastructure for declaring, validating, and auditing
citations throughout the codebase.

Principle: In God we trust. All others must bring data.
"""

import json
import inspect
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List, Callable, Dict, Any
from functools import wraps

# ── Constants ──────────────────────────────────────────────────────────
# [CITATION: CITATIONS-GOVERNANCE]
# Rationale: Central registry ensures all citations are validated against
# a single source of truth.
_REGISTRY_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "docs"
    / "research"
    / "citation_registry.json"
)

# [CITATION: CITATIONS-GOVERNANCE]
# Rationale: Standardized confidence levels for citation quality.
_CONFIDENCE_LEVELS = ["CERTAIN", "HIGH", "MEDIUM", "LOW", "PROPOSED", "ASSUMED"]

# ── Registry Loader ────────────────────────────────────────────────────
_registry_cache: Optional[Dict[str, Any]] = None


def _load_registry() -> Dict[str, Any]:
    """Load and cache the central citation registry."""
    global _registry_cache
    if _registry_cache is None:
        if _REGISTRY_PATH.exists():
            _registry_cache = json.loads(_REGISTRY_PATH.read_text())
        else:
            _registry_cache = {"citations": {}}
    return _registry_cache


# ── Data Model ─────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Citation:
    """
    A single citation binding code to research evidence.

    [CITATION: CITATIONS-DATAMODEL]
    Source: Deep-Tech Research Swarm, Citation Governance System
    Rationale: Immutable dataclass ensures citation integrity.
    """

    key: str
    paper: str
    venue: str
    section: Optional[str] = None
    rationale: Optional[str] = None
    verified: bool = False
    replication: Optional[str] = None
    confidence: str = "PROPOSED"

    def __post_init__(self) -> None:
        if self.confidence not in _CONFIDENCE_LEVELS:
            raise ValueError(
                f"Invalid confidence '{self.confidence}'. "
                f"Must be one of: {_CONFIDENCE_LEVELS}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize citation to dictionary.

        [CITATION: CITATIONS-DATAMODEL]
        Rationale: Immutable serialization for audit trails.
        """
        return asdict(self)


# ── Decorator ──────────────────────────────────────────────────────────
def cite(**kwargs) -> Callable:
    """
    Bind a citation to a class or function.

    Usage:
        @cite(
            key="CP-WBFT2025",
            paper="Rethinking Reliability from BFT Perspective",
            venue="AAAI 2025",
            section="Method: Confidence-Probed Weighted Consensus",
            rationale="Weighted voting prevents bad actors from dominating",
            verified=True,
            confidence="HIGH"
        )
        async def validate_votes(votes: List[Vote]) -> ConsensusResult:
            ...

    [CITATION: CITATIONS-GOVERNANCE]
    Source: Deep-Tech Research Swarm, Citation Governance System
    Rationale: Decorator pattern provides machine-readable citation metadata.
    """
    citation = Citation(**kwargs)

    def decorator(func: Callable) -> Callable:
        func._acn_citation = citation  # type: ignore[attr-defined]
        func._acn_cited = True  # type: ignore[attr-defined]
        return func

    return decorator


# ── Introspection ──────────────────────────────────────────────────────
@cite(
    key="CITATIONS-INTROSPECTION",
    paper="Citation Governance for Autonomous Cognitive Networks",
    venue="ACN Architecture Document",
    section="Introspection API",
    rationale="Runtime citation retrieval for audit and verification",
    confidence="CERTAIN",
)
def get_citation(func: Callable) -> Optional[Citation]:
    """Retrieve the citation attached to a function or class."""
    return getattr(func, "_acn_citation", None)


@cite(
    key="CITATIONS-INTROSPECTION",
    paper="Citation Governance for Autonomous Cognitive Networks",
    venue="ACN Architecture Document",
    section="Introspection API",
    rationale="Boolean check for citation presence",
    confidence="CERTAIN",
)
def is_cited(func: Callable) -> bool:
    """Check whether a function or class has a citation."""
    return getattr(func, "_acn_cited", False)


# ── Verification ───────────────────────────────────────────────────────
@cite(
    key="CITATIONS-VERIFICATION",
    paper="Citation Governance for Autonomous Cognitive Networks",
    venue="ACN Architecture Document",
    section="Registry Verification",
    rationale="Cross-reference citation keys against central registry of truth",
    confidence="CERTAIN",
)
def verify_citation(key: str) -> Dict[str, Any]:
    """
    Verify a citation key against the real literature registry first,
    then fall back to the central project registry.

    Returns verification report with found/not-found status,
    peer-review status, reproducibility, and confidence level.
    """
    # First check real academic literature registry
    try:
        from research.literature_registry import validate_citation, get_paper
        if validate_citation(key):
            paper = get_paper(key)
            if paper is not None:
                return {
                    "key": key,
                    "found": True,
                    "peer_reviewed": paper.venue in ("NeurIPS", "ICML", "ICLR", "AAAI", "IJCAI", "OSDI", "SOSP", "PODC", "ACM TURC"),
                    "reproducible": True,
                    "confidence": paper.confidence,
                    "verification_date": str(paper.year),
                    "verified_by": "literature_registry",
                    "warnings": [],
                    "paper": paper.title,
                    "authors": paper.authors,
                    "venue": paper.venue,
                    "url": paper.url,
                }
    except Exception:
        pass

    # Fall back to project registry
    registry = _load_registry()
    entry = registry.get("citations", {}).get(key)

    if entry is None:
        return {
            "key": key,
            "found": False,
            "error": (
                f"Citation key '{key}' not found in literature registry or project registry. "
                f"Verify it is a real peer-reviewed paper."
            ),
        }

    return {
        "key": key,
        "found": True,
        "peer_reviewed": entry.get("peer_reviewed", False),
        "reproducible": entry.get("reproducible", False),
        "confidence": entry.get("confidence", "UNKNOWN"),
        "verification_date": entry.get("verification_date"),
        "verified_by": entry.get("verified_by"),
        "warnings": ["Not found in peer-reviewed literature registry"],
    }


# ── Audit ──────────────────────────────────────────────────────────────
@cite(
    key="CITATIONS-AUDIT",
    paper="Citation Governance for Autonomous Cognitive Networks",
    venue="ACN Architecture Document",
    section="Audit System",
    rationale="Explicit exception type for citation policy violations",
    confidence="CERTAIN",
)
class CitationAuditError(Exception):
    """Raised when code lacks required citations."""

    pass


@cite(
    key="CITATIONS-AUDIT",
    paper="Citation Governance for Autonomous Cognitive Networks",
    venue="ACN Architecture Document",
    section="Audit System",
    rationale="Automated module-level citation compliance scanning",
    confidence="CERTAIN",
)
def audit_module(module: Any, strict: bool = True) -> List[Dict[str, Any]]:
    """
    Audit all classes and functions in a module for citations.

    Args:
        module: Python module to audit.
        strict: If True, raises CitationAuditError for uncited public APIs.

    Returns:
        List of audit reports for each public class/function.
    """
    violations: List[Dict[str, Any]] = []

    for name, obj in inspect.getmembers(module):
        if name.startswith("_"):
            continue

        if inspect.isclass(obj) or inspect.isfunction(obj):
            if not is_cited(obj):
                violations.append(
                    {
                        "module": module.__name__,
                        "name": name,
                        "type": "class" if inspect.isclass(obj) else "function",
                        "cited": False,
                        "severity": "ERROR" if strict else "WARNING",
                    }
                )

    if strict and violations:
        raise CitationAuditError(
            f"Citation audit failed for {module.__name__}: "
            f"{len(violations)} uncited public APIs. "
            f"In God we trust. All others must bring data."
        )

    return violations


# ── Trust Score ────────────────────────────────────────────────────────
def compute_trust_score(module: Any) -> Dict[str, Any]:
    """
    Compute a trust score for a module based on its citations.

    Higher score = more citations + higher confidence citations.

    Formula: Σ(confidence_weight × peer_reviewed_bonus × reproducible_bonus)
             ─────────────────────────────────────────────────────────────
                         total_public_apis

    [CITATION: CITATIONS-AUDIT]
    Source: Deep-Tech Research Swarm
    Rationale: Quantitative trust metric for code auditability.
    """
    confidence_weights = {
        "CERTAIN": 1.0,
        "HIGH": 0.85,
        "MEDIUM": 0.6,
        "LOW": 0.35,
        "PROPOSED": 0.2,
        "ASSUMED": 0.1,
    }

    total_score = 0.0
    total_apis = 0
    cited_apis = 0

    for name, obj in inspect.getmembers(module):
        if name.startswith("_"):
            continue
        if not (inspect.isclass(obj) or inspect.isfunction(obj)):
            continue

        total_apis += 1

        if is_cited(obj):
            cited_apis += 1
            citation = get_citation(obj)
            if citation:
                weight = confidence_weights.get(citation.confidence, 0.1)
                registry_entry = _load_registry().get("citations", {}).get(
                    citation.key, {}
                )
                if registry_entry.get("peer_reviewed"):
                    weight *= 1.2
                if registry_entry.get("reproducible"):
                    weight *= 1.1
                total_score += weight

    coverage = cited_apis / total_apis if total_apis > 0 else 0.0
    avg_score = total_score / total_apis if total_apis > 0 else 0.0

    return {
        "module": module.__name__,
        "total_apis": total_apis,
        "cited_apis": cited_apis,
        "coverage": coverage,
        "average_score": avg_score,
        "trust_grade": _grade(avg_score * coverage),
    }


def _grade(score: float) -> str:
    if score >= 0.9:
        return "A+"
    if score >= 0.8:
        return "A"
    if score >= 0.7:
        return "B"
    if score >= 0.5:
        return "C"
    if score >= 0.3:
        return "D"
    return "F"
