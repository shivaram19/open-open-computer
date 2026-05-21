# src/memory/scenario_miner.py
"""
ScenarioMiner: Cluster L1 atoms into L2 scenario patterns.

Clusters atoms by keyword overlap. For each cluster with sufficient
support, creates a ScenarioPattern describing the recurrent behavior.

Deterministic, no LLM required. Suitable for testing and offline operation.

[CITATION: SCENARIO-MINER]
[CITATION: TencentDB2026]
"""

import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Any

from shared.utils.citations import cite
from memory.layered_models import MemoryAtom, ScenarioPattern, AtomType


@cite(
    key="SCENARIO-MINER",
    paper="Layered Memory Architecture: Pattern Extraction",
    venue="ACN Architecture Document",
    section="L1→L2 Clustering",
    rationale="Keyword-based clustering mines recurrent behavior patterns from atomic facts",
    confidence="HIGH",
)
class ScenarioMiner:
    """
    Mine scenario patterns from collections of MemoryAtoms.

    Usage:
        miner = ScenarioMiner(min_support=3, similarity_threshold=0.3)
        patterns = miner.mine_scenarios(atoms)
    """

    def __init__(
        self,
        min_support: int = 3,
        similarity_threshold: float = 0.3,
        stopwords: Optional[Set[str]] = None,
    ):
        self.min_support = min_support
        self.similarity_threshold = similarity_threshold
        self.stopwords = stopwords or {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "just", "and", "but", "if",
            "or", "because", "until", "while", "this", "that", "these",
            "those", "i", "me", "my", "myself", "we", "our", "you",
            "your", "he", "him", "his", "she", "her", "it", "its",
            "they", "them", "their", "what", "which", "who", "whom",
        }

    def mine_scenarios(self, atoms: List[MemoryAtom]) -> List[ScenarioPattern]:
        """
        Mine scenario patterns from a list of atoms.

        1. Extract keyword vectors from each atom
        2. Group atoms by keyword overlap
        3. Filter groups by min_support
        4. Generate ScenarioPattern for each valid group
        """
        if len(atoms) < self.min_support:
            return []

        # Step 1: Extract keywords
        atom_keywords: Dict[str, Set[str]] = {}
        for atom in atoms:
            keywords = self._extract_keywords(atom.content)
            keywords.update(atom.tags)
            atom_keywords[atom.atom_id] = keywords

        # Step 2: Cluster by keyword overlap (simple greedy clustering)
        clusters = self._cluster_atoms(atoms, atom_keywords)

        # Step 3: Filter and generate patterns
        patterns = []
        for cluster in clusters:
            if len(cluster) >= self.min_support:
                pattern = self._generate_pattern(cluster, atom_keywords)
                if pattern:
                    patterns.append(pattern)

        return patterns

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        text = text.lower()
        # Keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        words = text.split()
        return {w for w in words if len(w) > 2 and w not in self.stopwords}

    def _cluster_atoms(
        self,
        atoms: List[MemoryAtom],
        atom_keywords: Dict[str, Set[str]],
    ) -> List[List[MemoryAtom]]:
        """
        Greedy clustering: start with each atom, merge if overlap > threshold.
        """
        unclustered = set(atom.atom_id for atom in atoms)
        clusters: List[List[str]] = []

        for atom in atoms:
            if atom.atom_id not in unclustered:
                continue

            cluster_ids = [atom.atom_id]
            unclustered.remove(atom.atom_id)
            cluster_keywords = set(atom_keywords[atom.atom_id])

            # Try to add more atoms to this cluster
            changed = True
            while changed and unclustered:
                changed = False
                for other_id in list(unclustered):
                    overlap = self._jaccard_similarity(
                        cluster_keywords, atom_keywords[other_id]
                    )
                    if overlap >= self.similarity_threshold:
                        cluster_ids.append(other_id)
                        unclustered.remove(other_id)
                        cluster_keywords.update(atom_keywords[other_id])
                        changed = True

            clusters.append(cluster_ids)

        # Map IDs back to atoms
        atom_map = {a.atom_id: a for a in atoms}
        return [[atom_map[aid] for aid in c if aid in atom_map] for c in clusters]

    @staticmethod
    def _jaccard_similarity(a: Set[str], b: Set[str]) -> float:
        """Compute Jaccard similarity between two sets."""
        if not a and not b:
            return 1.0
        intersection = len(a & b)
        union = len(a | b)
        return intersection / union if union > 0 else 0.0

    def _generate_pattern(
        self,
        cluster: List[MemoryAtom],
        atom_keywords: Dict[str, Set[str]],
    ) -> Optional[ScenarioPattern]:
        """Generate a ScenarioPattern from a cluster of atoms."""
        if not cluster:
            return None

        # Collect shared keywords across cluster
        all_keywords: Set[str] = set()
        shared_keywords: Optional[Set[str]] = None
        for atom in cluster:
            kw = atom_keywords.get(atom.atom_id, set())
            all_keywords.update(kw)
            if shared_keywords is None:
                shared_keywords = set(kw)
            else:
                shared_keywords &= kw

        # Use shared keywords as context, top non-shared as behavior hints
        context_keywords = list(shared_keywords) if shared_keywords else []
        if not context_keywords and all_keywords:
            context_keywords = sorted(all_keywords, key=lambda k: sum(1 for a in cluster if k in atom_keywords.get(a.atom_id, set())), reverse=True)[:5]

        # Determine dominant atom type
        type_counts = defaultdict(int)
        for atom in cluster:
            type_counts[atom.atom_type] += 1
        dominant_type = max(type_counts, key=type_counts.get)

        # Build template from context + dominant type
        type_templates = {
            AtomType.CLAIM: "When {context}, twin asserts related claims",
            AtomType.INSIGHT: "When {context}, twin generates insights",
            AtomType.CORRECTION: "When {context}, twin makes corrections",
            AtomType.OUTCOME: "When {context}, twin achieves outcomes",
            AtomType.META_COGNITIVE: "When {context}, twin reflects on reasoning",
            AtomType.HYPOTHESIS: "When {context}, twin forms hypotheses",
            AtomType.RECOMMENDATION: "When {context}, twin recommends actions",
        }
        context_str = ", ".join(context_keywords[:5]) if context_keywords else "similar situations"
        template = type_templates.get(
            dominant_type, "When {context}, twin exhibits recurrent behavior"
        ).format(context=context_str)

        # Build behavior summary
        behavior_parts = []
        for atom in cluster[:3]:
            behavior_parts.append(atom.content[:60])
        behavior_summary = "; ".join(behavior_parts) if behavior_parts else "Recurrent behavior"

        # Confidence = average atom confidence, boosted by support
        avg_conf = sum(a.confidence for a in cluster) / len(cluster)
        support_boost = min(0.1, len(cluster) / 100)
        confidence = min(1.0, avg_conf + support_boost)

        return ScenarioPattern.create(
            template=template,
            twin_id=cluster[0].twin_id,
            context_keywords=context_keywords[:10],
            behavior_summary=behavior_summary,
            example_atom_ids=[a.atom_id for a in cluster],
            confidence=confidence,
        )
