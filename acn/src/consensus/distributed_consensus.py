# src/consensus/distributed_consensus.py
"""
CP-WBFT: Confidence Probe-based Weighted Byzantine Fault Tolerant Consensus.

A two-stage consensus mechanism for distributed agent swarms:
Stage 1 — Confidence Probe Refinement: Each agent re-evaluates its decision
    based on higher-confidence neighbors, leveraging LLM intrinsic skepticism.
Stage 2 — Weighted Aggregation: Refined responses are aggregated using
    confidence-priority ranking with geometric median fallback.

Key properties:
- Tolerates up to 85.7% Byzantine fault rate on complete graphs (CP-WBFT2025)
- Exceeds classical f < n/3 bound for traditional agents
- Uses PCP (Prompt-level Confidence Probe) + HCP (Hidden-level Confidence Probe)
- Weighted by agent reputation from PTKG
- Geometric median aggregation for Byzantine robustness (DecentLLMs2025)

Design inspired by:
- CP-WBFT2025: Confidence probe-based weighted BFT for LLM agents
- DecentLLMs2025: Geometric median aggregation, leaderless worker-evaluator separation
- ReliableMAM2025: Decentralized(Feedback) architecture maximizes reliability
- NSED2026: Quadratic voting with reputation weighting

[CITATION: CP-WBFT2025]
[CITATION: DecentLLMs2025]
[CITATION: ReliableMAM2025]
[CITATION: NSED2026]
"""

import time
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from shared.utils.citations import cite
from consensus.hlc import HLCTimestamp


@cite(
    key="CONSENSUS-PHASE",
    paper="CP-WBFT: Confidence Probe-based Weighted Byzantine Fault Tolerant Consensus",
    venue="ACN Architecture Document",
    section="Consensus Phase Enumeration",
    rationale="Explicit phases enable introspection and debugging of multi-stage consensus",
    confidence="CERTAIN",
)
class ConsensusPhase(Enum):
    """[CITATION: CONSENSUS-ENGINE] Phases of the CP-WBFT consensus protocol."""
    IDLE = "idle"
    PROBE = "probe"              # Stage 1: Confidence probing
    REFINE = "refine"            # Stage 1b: Decision refinement
    AGGREGATE = "aggregate"      # Stage 2: Weighted aggregation
    VERIFY = "verify"            # Post-consensus: Byzantine detection
    FINAL = "final"


@dataclass
class AgentVote:
    """[CITATION: CONSENSUS-ENGINE] A single agent's vote with confidence metadata."""
    agent_id: str
    proposal_id: str
    confidence: float          # 0.0-1.0, from PCP/HCP probes
    raw_score: float           # Original unrefined score
    refined_score: float       # After neighbor influence
    reputation: float          # Agent's current reputation
    hlc_timestamp: Optional[HLCTimestamp] = None


@cite(
    key="CP-WBFT-ENGINE",
    paper="CP-WBFT: Confidence Probe-based Weighted Byzantine Fault Tolerant Consensus",
    venue="ACN Architecture Document",
    section="Distributed Consensus Engine",
    rationale="Two-stage confidence-guided consensus exceeds classical Byzantine bounds for LLM agents",
    confidence="CERTAIN",
)
class DistributedConsensusEngine:
    """
    [CITATION: CONSENSUS-ENGINE] CP-WBFT consensus engine for distributed agent swarms.
    
    Two-stage protocol:
    
    Stage 1 — Confidence Probe Refinement:
    1. Each agent broadcasts its initial proposal and confidence
    2. Agents receive neighbor proposals
    3. Each agent re-evaluates: if neighbor has higher confidence AND reputation,
       adjust own score toward neighbor's position (weighted by confidence delta)
    4. Refined scores are broadcast
    
    Stage 2 — Weighted Aggregation:
    1. Collect all refined votes
    2. Filter out votes from agents with reputation < min_reputation_threshold
    3. If remaining agents < quorum, fall back to geometric median
    4. Compute weighted score: sum(vote.refined_score * weight) / sum(weights)
       where weight = vote.confidence * vote.reputation
    5. Select winner by highest weighted score
    6. Detect potential Byzantine agents (outliers with low confidence but extreme scores)
    
    Parameters:
    - confidence_threshold: Minimum confidence for a vote to count
    - min_reputation_threshold: Agents below this reputation are distrusted
    - quorum_ratio: Minimum fraction of agents required for consensus
    - byzantine_tolerance: Expected max fraction of Byzantine agents
    """

    def __init__(
        self,
        engine_id: str = "cp-wbft-engine",
        confidence_threshold: float = 0.3,
        min_reputation_threshold: float = 0.2,
        quorum_ratio: float = 0.51,
        byzantine_tolerance: float = 0.33,
        max_rounds: int = 3,
    ):
        """[CITATION: CONSENSUS-ENGINE] Initialize the CP-WBFT consensus engine."""
        self.engine_id = engine_id
        self.confidence_threshold = confidence_threshold
        self.min_reputation_threshold = min_reputation_threshold
        self.quorum_ratio = quorum_ratio
        self.byzantine_tolerance = byzantine_tolerance
        self.max_rounds = max_rounds
        
        self._phase = ConsensusPhase.IDLE
        self._round_history: List[Dict[str, Any]] = []
        self._byzantine_suspects: Dict[str, float] = {}  # agent_id -> suspicion_score

    def stage1_probe_and_refine(
        self,
        agent_votes: List[AgentVote],
        neighbor_graph: Optional[Dict[str, List[str]]] = None,
    ) -> List[AgentVote]:
        """
        [CITATION: CONSENSUS-ENGINE] Stage 1: Confidence probe refinement.
        
        Each agent adjusts its vote based on higher-confidence neighbors.
        The adjustment is proportional to the confidence and reputation gap.
        
        Args:
            agent_votes: Initial votes from all agents
            neighbor_graph: adjacency list of agent communication topology
        
        Returns:
            Refined votes after neighbor influence
        """
        self._phase = ConsensusPhase.PROBE
        
        if not agent_votes:
            return []
        
        vote_map = {v.agent_id: v for v in agent_votes}
        refined: List[AgentVote] = []
        
        # Default: complete graph (everyone sees everyone)
        if neighbor_graph is None:
            all_ids = [v.agent_id for v in agent_votes]
            neighbor_graph = {aid: [x for x in all_ids if x != aid] for aid in all_ids}
        
        for vote in agent_votes:
            neighbors = neighbor_graph.get(vote.agent_id, [])
            refined_score = vote.raw_score
            total_influence = 0.0
            
            for neighbor_id in neighbors:
                neighbor_vote = vote_map.get(neighbor_id)
                if not neighbor_vote:
                    continue
                
                # Only influenced by neighbors with higher confidence AND reputation
                if (neighbor_vote.confidence > vote.confidence and
                    neighbor_vote.reputation > vote.reputation):
                    
                    # Influence proportional to confidence gap and reputation
                    conf_gap = neighbor_vote.confidence - vote.confidence
                    rep_weight = neighbor_vote.reputation
                    influence = conf_gap * rep_weight
                    total_influence += influence
                    
                    # Move toward neighbor's score (weighted averaging)
                    neighbor_score = neighbor_vote.raw_score
                    refined_score = refined_score * (1 - influence) + neighbor_score * influence
            
            # Clamp to [0, 1]
            refined_score = max(0.0, min(1.0, refined_score))
            
            refined.append(AgentVote(
                agent_id=vote.agent_id,
                proposal_id=vote.proposal_id,
                confidence=vote.confidence,
                raw_score=vote.raw_score,
                refined_score=refined_score,
                reputation=vote.reputation,
                hlc_timestamp=vote.hlc_timestamp,
            ))
        
        self._phase = ConsensusPhase.REFINE
        return refined

    def stage2_weighted_aggregation(
        self,
        refined_votes: List[AgentVote],
    ) -> Dict[str, Any]:
        """
        [CITATION: CONSENSUS-ENGINE] Stage 2: Weighted aggregation with Byzantine detection.
        
        Computes weighted consensus score and detects outlier agents.
        
        Returns:
        {
            "winner": str,           # winning proposal_id
            "score": float,          # weighted consensus score
            "quorum_reached": bool,
            "byzantine_detected": List[str],
            "entropy": float,        # measure of agreement diversity
            "vote_distribution": Dict[str, float],
        }
        """
        self._phase = ConsensusPhase.AGGREGATE
        
        if not refined_votes:
            return {
                "winner": None,
                "score": 0.0,
                "quorum_reached": False,
                "byzantine_detected": [],
                "entropy": 1.0,
                "vote_distribution": {},
            }
        
        # Filter low-reputation agents
        trusted_votes = [
            v for v in refined_votes
            if v.reputation >= self.min_reputation_threshold
            and v.confidence >= self.confidence_threshold
        ]
        
        total_agents = len(refined_votes)
        quorum = int(total_agents * self.quorum_ratio)
        
        if len(trusted_votes) < quorum:
            # Fall back to geometric median of all votes
            return self._geometric_median_consensus(refined_votes)
        
        # Compute weighted scores per proposal
        proposal_scores: Dict[str, List[Tuple[float, float]]] = {}  # proposal -> [(score, weight), ...]
        for vote in trusted_votes:
            weight = vote.confidence * vote.reputation
            if vote.proposal_id not in proposal_scores:
                proposal_scores[vote.proposal_id] = []
            proposal_scores[vote.proposal_id].append((vote.refined_score, weight))
        
        # Aggregate per proposal
        proposal_aggregates = {}
        for pid, score_weights in proposal_scores.items():
            total_weight = sum(w for _, w in score_weights)
            if total_weight > 0:
                weighted_avg = sum(s * w for s, w in score_weights) / total_weight
            else:
                weighted_avg = 0.0
            proposal_aggregates[pid] = weighted_avg
        
        # Winner
        if proposal_aggregates:
            winner = max(proposal_aggregates, key=proposal_aggregates.get)
            winner_score = proposal_aggregates[winner]
        else:
            winner = None
            winner_score = 0.0
        
        # Entropy (diversity measure)
        scores = list(proposal_aggregates.values())
        entropy = self._compute_entropy(scores)
        
        # Byzantine detection: outliers with extreme scores but low confidence
        byzantine_detected = self._detect_byzantine_agents(refined_votes, winner_score)
        
        self._phase = ConsensusPhase.VERIFY
        
        return {
            "winner": winner,
            "score": winner_score,
            "quorum_reached": len(trusted_votes) >= quorum,
            "byzantine_detected": byzantine_detected,
            "entropy": entropy,
            "vote_distribution": proposal_aggregates,
            "trusted_votes": len(trusted_votes),
            "total_votes": total_agents,
        }

    def _geometric_median_consensus(
        self,
        votes: List[AgentVote],
    ) -> Dict[str, Any]:
        """
        [CITATION: CONSENSUS-ENGINE] Fallback: geometric median aggregation (DecentLLMs2025).
        
        The geometric median is more robust to outliers than arithmetic mean.
        For 1D scores, it approximates to the median.
        """
        scores = [v.refined_score for v in votes]
        proposals = [v.proposal_id for v in votes]
        
        if not scores:
            return {
                "winner": None,
                "score": 0.0,
                "quorum_reached": False,
                "byzantine_detected": [],
                "entropy": 1.0,
                "vote_distribution": {},
                "method": "geometric_median_fallback",
            }
        
        # For 1D, geometric median ≈ median
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        median_score = sorted_scores[n // 2] if n % 2 == 1 else (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        
        # Winner: proposal whose vote is closest to median
        closest_idx = min(range(len(scores)), key=lambda i: abs(scores[i] - median_score))
        winner = proposals[closest_idx]
        
        # Count proposals near median
        proposal_counts: Dict[str, int] = {}
        for i, (pid, s) in enumerate(zip(proposals, scores)):
            if abs(s - median_score) < 0.2:  # within 0.2 of median
                proposal_counts[pid] = proposal_counts.get(pid, 0) + 1
        
        if proposal_counts:
            winner = max(proposal_counts, key=proposal_counts.get)
        
        return {
            "winner": winner,
            "score": median_score,
            "quorum_reached": False,  # Quorum not reached, using fallback
            "byzantine_detected": [],
            "entropy": self._compute_entropy(scores),
            "vote_distribution": {pid: s for pid, s in zip(proposals, scores)},
            "method": "geometric_median_fallback",
        }

    def _detect_byzantine_agents(
        self,
        votes: List[AgentVote],
        consensus_score: float,
    ) -> List[str]:
        """
        [CITATION: CONSENSUS-ENGINE] Detect potential Byzantine agents.
        
        Heuristics:
        1. Very low confidence (< 0.2) but extreme score (far from consensus)
        2. Score > 3 standard deviations from mean
        3. Reputation below threshold but attempting to influence
        """
        suspects = []
        scores = [v.refined_score for v in votes]
        
        if len(scores) < 3:
            return suspects
        
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        for vote in votes:
            is_suspect = False
            
            # Heuristic 1: Low confidence + extreme deviation
            if vote.confidence < 0.2 and abs(vote.refined_score - consensus_score) > 0.5:
                is_suspect = True
            
            # Heuristic 2: Statistical outlier
            if std_dev > 0.01 and abs(vote.refined_score - mean_score) > 3 * std_dev:
                is_suspect = True
            
            # Heuristic 3: Very low reputation but high influence attempt
            if vote.reputation < 0.1 and vote.confidence > 0.8:
                is_suspect = True
            
            if is_suspect:
                suspects.append(vote.agent_id)
                self._byzantine_suspects[vote.agent_id] = self._byzantine_suspects.get(vote.agent_id, 0) + 1
        
        return suspects

    def _compute_entropy(self, scores: List[float]) -> float:
        """[CITATION: CONSENSUS-ENGINE] Compute normalized entropy of score distribution."""
        if not scores:
            return 1.0
        
        # Convert scores to probability distribution
        total = sum(scores)
        if total == 0:
            return 1.0
        
        probs = [s / total for s in scores]
        # Shannon entropy
        entropy = -sum(p * math.log(p + 1e-10) for p in probs)
        # Normalize by max entropy
        max_entropy = math.log(len(probs) + 1e-10)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def reach_consensus(
        self,
        agent_votes: List[AgentVote],
        neighbor_graph: Optional[Dict[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """
        [CITATION: CONSENSUS-ENGINE] Full two-stage CP-WBFT consensus protocol.
        
        Executes Stage 1 (refinement) then Stage 2 (aggregation).
        Returns complete consensus result with metadata.
        """
        start_time = time.time()
        
        # Stage 1
        refined = self.stage1_probe_and_refine(agent_votes, neighbor_graph)
        
        # Stage 2
        result = self.stage2_weighted_aggregation(refined)
        
        self._phase = ConsensusPhase.FINAL
        
        result["engine_id"] = self.engine_id
        result["phase"] = self._phase.value
        result["duration_ms"] = (time.time() - start_time) * 1000
        result["byzantine_tolerance"] = self.byzantine_tolerance
        
        self._round_history.append(result)
        
        return result

    def get_byzantine_suspects(self) -> Dict[str, float]:
        """[CITATION: CONSENSUS-ENGINE] Get agents flagged as potential Byzantine actors."""
        return dict(self._byzantine_suspects)

    def get_consensus_history(self) -> List[Dict[str, Any]]:
        """[CITATION: CONSENSUS-ENGINE] History of all consensus rounds."""
        return self._round_history
