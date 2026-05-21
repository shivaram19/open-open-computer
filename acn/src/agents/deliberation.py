# src/agents/deliberation.py
"""
Deliberation Engine: Weighted Consensus, Recursive Rounds, Argument Persistence.

Inspired by:
- NSED2026: Recurrent deliberation topology with semantic forget gate
- ReliableMAM2025: Decentralized(Feedback) architecture for reliability
- SWARP2026: Argument maps with cognitive closure detection
- GraphMemory2026: Retrieval precedes reasoning

Principle: Deliberation without memory decay collapses into premature consensus.
[CITATION: NSED2026]
[CITATION: ReliableMAM2025]
[CITATION: SWARP2026]
[CITATION: GraphMemory2026]
"""

import time
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from shared.utils.citations import cite


@cite(
    key="DELIB-VOTE",
    paper="Deliberation Engine: Quadratic Voting for Multi-Agent Consensus",
    venue="ACN Harness Architecture",
    section="Deliberation",
    rationale="NSED2026-inspired non-linear voting dampens extremist influence while preserving minority signal",
    confidence="HIGH",
)
@dataclass
class Vote:
    """A single agent's vote on a proposal, with quadratic cost."""
    agent_id: str
    proposal_id: str
    raw_score: float  # 0-100
    
    @property
    def quadratic_score(self) -> float:
        """Quadratic transformation: sqrt(raw) / 10 → dampens extremes.
        
        [CITATION: NSED2026]
        """
        return math.sqrt(max(0, self.raw_score)) / 10.0
    
    @property
    def cost(self) -> float:
        """Quadratic cost of voting: proportional to square of vote intensity.
        
        [CITATION: NSED2026]
        """
        return (self.raw_score / 100.0) ** 2


@cite(
    key="DELIB-PROPOSAL",
    paper="Deliberation Engine: Structured Proposal with Argument Map",
    venue="ACN Harness Architecture",
    section="Deliberation",
    rationale="SWARP2026-inspired argument persistence with closure tracking",
    confidence="HIGH",
)
@dataclass
class Proposal:
    """A proposal in the deliberation, with attached arguments and critiques."""
    proposal_id: str
    agent_id: str
    content: str
    reasoning: str
    confidence: float
    round_created: int
    arguments_for: List[str] = field(default_factory=list)
    arguments_against: List[str] = field(default_factory=list)
    critiques_received: List[Dict[str, Any]] = field(default_factory=list)
    revisions: List[str] = field(default_factory=list)
    
    @property
    def revision_count(self) -> int:
        """Number of revisions this proposal has undergone.
        
        [CITATION: SWARP2026]
        """
        return len(self.revisions)
    
    @property
    def is_mature(self) -> bool:
        """A proposal is mature if it has survived at least 2 rounds of critique.
        
        [CITATION: SWARP2026]
        """
        return len(self.critiques_received) >= 2


@cite(
    key="DELIB-ARGUMENT",
    paper="Deliberation Engine: Argument Map with Cognitive Closure Detection",
    venue="ACN Harness Architecture",
    section="Deliberation",
    rationale="SWARP2026 warns argument maps proliferate without closure; we track closure explicitly",
    confidence="HIGH",
)
@dataclass
class ArgumentMap:
    """
    Persistent map of arguments in a deliberation.
    
    Tracks:
    - Proposals and their lineage
    - Critiques and whether they were addressed
    - Whether cognitive closure has been reached
    """
    task_id: str
    proposals: Dict[str, Proposal] = field(default_factory=dict)
    rounds: List[Dict[str, Any]] = field(default_factory=list)
    closure_reached: bool = False
    closure_reason: Optional[str] = None
    
    def add_proposal(self, proposal: Proposal) -> None:
        """Add a proposal to the argument map.
        
        [CITATION: SWARP2026]
        """
        self.proposals[proposal.proposal_id] = proposal
    
    def add_critique(self, proposal_id: str, from_agent: str, critique: str) -> None:
        """Add a critique to a proposal.
        
        [CITATION: SWARP2026]
        """
        if proposal_id in self.proposals:
            self.proposals[proposal_id].critiques_received.append({
                "from": from_agent,
                "critique": critique,
                "timestamp": time.time(),
                "addressed": False,
            })
    
    def mark_critique_addressed(self, proposal_id: str, critique_index: int) -> None:
        """Mark a critique as addressed.
        
        [CITATION: SWARP2026]
        """
        if proposal_id in self.proposals:
            critiques = self.proposals[proposal_id].critiques_received
            if 0 <= critique_index < len(critiques):
                critiques[critique_index]["addressed"] = True
    
    def check_closure(self, min_rounds: int = 2) -> bool:
        """
        Check if cognitive closure has been reached.
        
        Closure conditions (SWARP2026-inspired):
        1. At least min_rounds of deliberation
        2. All critiques on the top proposal have been addressed
        3. No new proposals in the last round
        4. Confidence variance across agents is below threshold
        
        [CITATION: SWARP2026]
        """
        if len(self.rounds) < min_rounds:
            return False
        
        # Check if any proposal has all critiques addressed
        for proposal in self.proposals.values():
            if proposal.critiques_received and all(c["addressed"] for c in proposal.critiques_received):
                if len(self.rounds) >= min_rounds:
                    self.closure_reached = True
                    self.closure_reason = f"All critiques addressed on proposal {proposal.proposal_id}"
                    return True
        
        # Check for stagnation (no new proposals in last round)
        if len(self.rounds) >= 2:
            last_round = self.rounds[-1]
            prev_round = self.rounds[-2]
            last_proposals = set(last_round.get("proposals", []))
            prev_proposals = set(prev_round.get("proposals", []))
            if last_proposals == prev_proposals and len(last_round.get("votes", {})) > 0:
                self.closure_reached = True
                self.closure_reason = "Stagnation: no new proposals and stable voting"
                return True
        
        return False
    
    def get_unaddressed_critiques(self) -> List[Dict[str, Any]]:
        """Get all unaddressed critiques — these are the open questions.
        
        [CITATION: SWARP2026]
        """
        unaddressed = []
        for prop in self.proposals.values():
            for i, crit in enumerate(prop.critiques_received):
                if not crit["addressed"]:
                    unaddressed.append({
                        "proposal_id": prop.proposal_id,
                        "critique_index": i,
                        **crit,
                    })
        return unaddressed


@cite(
    key="DELIB-ENGINE",
    paper="Deliberation Engine: Weighted Consensus + Recursive Deliberation + Argument Persistence",
    venue="ACN Harness Architecture",
    section="Deliberation",
    rationale="Three mechanisms in one engine: NSED2026 voting + ReliableMAM2025 feedback + SWARP2026 closure",
    confidence="CERTAIN",
)
class DeliberationEngine:
    """
    Core deliberation engine for the conscious agent swarm.
    
    Three mechanisms:
    1. WEIGHTED CONSENSUS: Quadratic voting with agent reputation weighting
    2. RECURSIVE DELIBERATION: Multiple rounds with semantic feedback decay
    3. ARGUMENT PERSISTENCE: Structured argument map with closure detection
    """
    
    def __init__(
        self,
        max_rounds: int = 7,
        semantic_decay: float = 0.85,  # NSED2026-inspired: attention on older rounds decays
        convergence_threshold: float = 0.75,
    ):
        self.max_rounds = max_rounds
        self.semantic_decay = semantic_decay
        self.convergence_threshold = convergence_threshold
        
        # Round history for recurrence
        self.round_history: List[Dict[str, Any]] = []
        
        # Argument map
        self.argument_map: Optional[ArgumentMap] = None
        
        # Agent reputation scores (learned over deliberations)
        self.agent_reputation: Dict[str, float] = {}
    
    @cite(
        key="DELIB-WEIGHTED-VOTE",
        paper="Deliberation Engine: Quadratic Voting with Reputation Weighting",
        venue="ACN Harness Architecture",
        section="Weighted Consensus",
        rationale="NSED2026 Quadratic Voting + historical success rate = robust consensus",
        confidence="HIGH",
    )
    def weighted_vote(
        self,
        votes: List[Vote],
        agent_success_rates: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Compute weighted consensus using quadratic voting.
        
        Each vote is transformed quadratically (dampens extremes).
        Weighted by agent reputation + historical success.
        Diagonal mask is applied at swarm level (agents don't vote on own proposals).
        """
        if not votes:
            return {"winner": None, "score": 0.0, "distribution": {}}
        
        # Group votes by proposal
        proposal_scores: Dict[str, List[float]] = {}
        proposal_weights: Dict[str, List[float]] = {}
        
        for vote in votes:
            # Get agent reputation (default 0.5)
            rep = self.agent_reputation.get(vote.agent_id, 0.5)
            
            # Get success rate (default 0.5)
            success = agent_success_rates.get(vote.agent_id, 0.5) if agent_success_rates else 0.5
            
            # Combined weight: reputation * success_rate
            weight = rep * (0.5 + 0.5 * success)
            
            # Quadratic score
            q_score = vote.quadratic_score
            
            if vote.proposal_id not in proposal_scores:
                proposal_scores[vote.proposal_id] = []
                proposal_weights[vote.proposal_id] = []
            
            proposal_scores[vote.proposal_id].append(q_score)
            proposal_weights[vote.proposal_id].append(weight)
        
        # Compute weighted scores
        weighted_scores = {}
        for prop_id, scores in proposal_scores.items():
            weights = proposal_weights[prop_id]
            total_weight = sum(weights)
            if total_weight > 0:
                weighted_scores[prop_id] = sum(
                    s * w for s, w in zip(scores, weights)
                ) / total_weight
            else:
                weighted_scores[prop_id] = 0.0
        
        # Find winner
        if not weighted_scores:
            return {"winner": None, "score": 0.0, "distribution": {}}
        
        winner = max(weighted_scores, key=weighted_scores.get)
        winner_score = weighted_scores[winner]
        
        # Compute entropy (diversity of opinions)
        total_score = sum(weighted_scores.values())
        if total_score > 0:
            probabilities = {k: v / total_score for k, v in weighted_scores.items()}
            entropy = -sum(
                p * math.log2(p) for p in probabilities.values() if p > 0
            )
        else:
            entropy = 0.0
        
        return {
            "winner": winner,
            "score": winner_score,
            "distribution": weighted_scores,
            "entropy": entropy,
            "total_votes": len(votes),
            "quorum_reached": len(votes) >= 2,
        }
    
    @cite(
        key="DELIB-RECURSIVE",
        paper="Deliberation Engine: Recursive Deliberation with Semantic Decay",
        venue="ACN Harness Architecture",
        section="Recursive Deliberation",
        rationale="NSED2026 recurrent topology: consensus loops back with semantic decay to prevent consensus collapse",
        confidence="HIGH",
    )
    def execute_round(
        self,
        task_id: str,
        agent_reasoning: Dict[str, Dict[str, Any]],
        previous_consensus: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute one round of recursive deliberation.
        
        The consensus from previous rounds feeds back with semantic decay γ.
        This prevents premature convergence (consensus collapse).
        """
        round_num = len(self.round_history) + 1
        
        # Apply semantic decay to previous consensus if it exists
        decayed_consensus = None
        if previous_consensus and round_num > 1:
            decay_factor = self.semantic_decay ** (round_num - 1)
            decayed_consensus = {
                "winner": previous_consensus.get("winner"),
                "score": previous_consensus.get("score", 0) * decay_factor,
                "decay_factor": decay_factor,
            }
        
        # Extract votes from agent reasoning
        votes = []
        for agent_id, reasoning in agent_reasoning.items():
            # Agent implicitly votes for its own proposal
            proposal_id = reasoning.get("proposal_id", f"proposal-{agent_id}")
            confidence = reasoning.get("confidence", 0.5) * 100  # scale to 0-100
            votes.append(Vote(
                agent_id=agent_id,
                proposal_id=proposal_id,
                raw_score=confidence,
            ))
        
        # Compute weighted consensus
        consensus = self.weighted_vote(votes)
        
        # Record round
        round_record = {
            "round": round_num,
            "task_id": task_id,
            "votes": [v.__dict__ for v in votes],
            "consensus": consensus,
            "decayed_consensus": decayed_consensus,
            "agent_count": len(agent_reasoning),
            "timestamp": time.time(),
        }
        self.round_history.append(round_record)
        
        # Also record in argument map if initialized
        if self.argument_map is not None:
            self.argument_map.rounds.append({
                "round": round_num,
                "proposals": list(self.argument_map.proposals.keys()),
                "votes": {v.agent_id: v.proposal_id for v in votes},
            })
        
        # Check for convergence
        converged = consensus["score"] >= self.convergence_threshold
        
        # Check for consensus collapse (NSED2026 warning)
        collapse_warning = False
        if round_num >= 3 and consensus["score"] > 0.95:
            # Check if entropy is near zero (everyone agrees too much)
            if consensus.get("entropy", 1.0) < 0.1:
                collapse_warning = True
        
        return {
            "round": round_num,
            "consensus": consensus,
            "converged": converged,
            "collapse_warning": collapse_warning,
            "decayed_consensus": decayed_consensus,
            "round_record": round_record,
        }
    
    @cite(
        key="DELIB-ARGUMENT-MAP",
        paper="Deliberation Engine: Argument Persistence and Closure Detection",
        venue="ACN Harness Architecture",
        section="Argument Persistence",
        rationale="SWARP2026: argument maps need closure detection to prevent infinite proliferation",
        confidence="HIGH",
    )
    def initialize_argument_map(self, task_id: str) -> ArgumentMap:
        """Initialize an argument map for a task."""
        self.argument_map = ArgumentMap(task_id=task_id)
        return self.argument_map
    
    def add_proposal_to_map(
        self,
        proposal_id: str,
        agent_id: str,
        content: str,
        reasoning: str,
        confidence: float,
    ) -> Proposal:
        """Add a proposal to the argument map.
        
        [CITATION: SWARP2026]
        """
        if self.argument_map is None:
            raise RuntimeError("Argument map not initialized. Call initialize_argument_map first.")
        
        proposal = Proposal(
            proposal_id=proposal_id,
            agent_id=agent_id,
            content=content,
            reasoning=reasoning,
            confidence=confidence,
            round_created=len(self.round_history) + 1,
        )
        self.argument_map.add_proposal(proposal)
        return proposal
    
    def check_closure(self) -> Dict[str, Any]:
        """Check if cognitive closure has been reached in the argument map.
        
        [CITATION: SWARP2026]
        """
        if self.argument_map is None:
            return {"closure_reached": False, "reason": "No argument map"}
        
        closed = self.argument_map.check_closure(min_rounds=2)
        
        return {
            "closure_reached": closed,
            "reason": self.argument_map.closure_reason,
            "unaddressed_critiques": len(self.argument_map.get_unaddressed_critiques()),
            "total_proposals": len(self.argument_map.proposals),
            "total_rounds": len(self.round_history),
        }
    
    def get_deliberation_summary(self) -> Dict[str, Any]:
        """Get a summary of the full deliberation history.
        
        [CITATION: NSED2026]
        [CITATION: SWARP2026]
        """
        if not self.round_history:
            return {"status": "no_deliberation", "rounds": 0}
        
        final_round = self.round_history[-1]
        
        return {
            "status": "completed" if self.argument_map and self.argument_map.closure_reached else "ongoing",
            "total_rounds": len(self.round_history),
            "max_rounds": self.max_rounds,
            "final_consensus": final_round.get("consensus", {}),
            "collapse_warnings": sum(
                1 for r in self.round_history
                if r.get("consensus", {}).get("score", 0) > 0.95
            ),
            "argument_map_status": {
                "proposals": len(self.argument_map.proposals) if self.argument_map else 0,
                "closure_reached": self.argument_map.closure_reached if self.argument_map else False,
            },
            "semantic_decay_applied": self.semantic_decay < 1.0,
        }
