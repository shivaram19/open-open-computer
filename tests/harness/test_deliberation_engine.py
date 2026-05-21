"""
Tests for the Deliberation Engine: Weighted Consensus, Recursive Rounds, Argument Persistence.

Citations:
- NSED2026: Quadratic voting, semantic decay, consensus collapse prevention
- ReliableMAM2025: Decentralized(Feedback) architecture for reliability
- SWARP2026: Argument maps with cognitive closure detection
- GraphMemory2026: Retrieval precedes reasoning
"""



from agents.deliberation import (
    DeliberationEngine,
    Vote,
    Proposal,
    ArgumentMap,
)


def test_quadratic_voting_dampens_extremes():
    """Quadratic voting should reduce the influence of extreme scores."""
    engine = DeliberationEngine()
    
    vote_extreme = Vote(agent_id="a1", proposal_id="p1", raw_score=100)
    vote_moderate = Vote(agent_id="a2", proposal_id="p1", raw_score=50)
    
    # Quadratic transformation: sqrt(100)/10 = 1.0, sqrt(50)/10 ≈ 0.707
    assert vote_extreme.quadratic_score == 1.0
    assert abs(vote_moderate.quadratic_score - 0.707) < 0.01
    
    # The ratio of raw scores is 2:1, but quadratic ratio is ~1.41:1
    raw_ratio = vote_extreme.raw_score / vote_moderate.raw_score
    quad_ratio = vote_extreme.quadratic_score / vote_moderate.quadratic_score
    assert quad_ratio < raw_ratio, "Quadratic voting should dampen extremes"


def test_weighted_vote_selects_winner():
    """Weighted vote must select a winner based on quadratic scores."""
    engine = DeliberationEngine()
    
    votes = [
        Vote(agent_id="a1", proposal_id="p1", raw_score=80),
        Vote(agent_id="a2", proposal_id="p1", raw_score=75),
        Vote(agent_id="a3", proposal_id="p2", raw_score=60),
    ]
    
    result = engine.weighted_vote(votes)
    
    assert result["winner"] == "p1"
    assert result["score"] > 0
    assert result["quorum_reached"] is True
    assert result["total_votes"] == 3
    assert "entropy" in result


def test_weighted_vote_with_reputation():
    """Agent reputation should influence vote weighting on same proposal."""
    engine = DeliberationEngine()
    engine.agent_reputation = {"a1": 0.9, "a2": 0.5}
    
    # Both agents vote on the SAME proposal — reputation determines effective weight
    votes = [
        Vote(agent_id="a1", proposal_id="p1", raw_score=60),  # High rep
        Vote(agent_id="a2", proposal_id="p1", raw_score=80),  # Low rep, but higher raw
    ]
    
    result = engine.weighted_vote(votes)
    
    # With quadratic voting + rep weighting:
    # a1: sqrt(60)/10 = 0.775, weight = 0.9 * 0.75 = 0.675, contribution = 0.523
    # a2: sqrt(80)/10 = 0.894, weight = 0.5 * 0.75 = 0.375, contribution = 0.335
    # Weighted average = (0.523 + 0.335) / (0.675 + 0.375) = 0.858 / 1.05 = 0.817
    # Winner is still p1 (only proposal), but the score reflects reputation-weighted blend
    assert result["winner"] == "p1"
    assert result["score"] > 0.7  # Reputation-weighted score should be high


def test_recursive_deliberation_round():
    """Execute one round of recursive deliberation."""
    engine = DeliberationEngine(max_rounds=5, semantic_decay=0.85)
    
    agent_reasoning = {
        "a1": {"proposal_id": "p1", "confidence": 0.8},
        "a2": {"proposal_id": "p1", "confidence": 0.7},
        "a3": {"proposal_id": "p2", "confidence": 0.5},
    }
    
    result = engine.execute_round("task-001", agent_reasoning)
    
    assert result["round"] == 1
    assert result["consensus"]["winner"] == "p1"
    assert "consensus" in result
    assert "collapse_warning" in result
    # With 2 agents voting p1 at high confidence, consensus score exceeds 0.75 threshold
    assert result["converged"] is True


def test_semantic_decay_applied():
    """Semantic decay should reduce influence of previous consensus over rounds."""
    engine = DeliberationEngine(max_rounds=5, semantic_decay=0.85)
    
    # Round 1
    result1 = engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.9},
        "a2": {"proposal_id": "p1", "confidence": 0.85},
    })
    
    # Round 2 with previous consensus
    result2 = engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.9},
        "a2": {"proposal_id": "p1", "confidence": 0.85},
    }, previous_consensus=result1["consensus"])
    
    assert result2["decayed_consensus"] is not None
    assert result2["decayed_consensus"]["decay_factor"] == 0.85
    assert result2["decayed_consensus"]["score"] < result1["consensus"]["score"]


def test_consensus_collapse_warning():
    """Detect consensus collapse when agents agree too easily with near-zero entropy."""
    engine = DeliberationEngine(max_rounds=5, semantic_decay=0.85)
    
    # Round 1: some disagreement
    engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.8},
        "a2": {"proposal_id": "p2", "confidence": 0.7},
    })
    
    # Round 2: more agreement
    engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.95},
        "a2": {"proposal_id": "p1", "confidence": 0.92},
    })
    
    # Round 3: suspicious conformity
    result3 = engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.99},
        "a2": {"proposal_id": "p1", "confidence": 0.98},
    })
    
    assert result3["collapse_warning"] is True


def test_argument_map_initialization():
    """Argument map must track proposals and critiques."""
    engine = DeliberationEngine()
    arg_map = engine.initialize_argument_map("task-001")
    
    assert arg_map.task_id == "task-001"
    assert arg_map.closure_reached is False
    assert len(arg_map.proposals) == 0


def test_argument_map_proposal_and_critique():
    """Proposals and critiques must be tracked in the argument map."""
    engine = DeliberationEngine()
    engine.initialize_argument_map("task-001")
    
    proposal = engine.add_proposal_to_map(
        proposal_id="p1",
        agent_id="a1",
        content="Use GNN for topology design",
        reasoning="GNNs learn optimal communication patterns",
        confidence=0.8,
    )
    
    assert proposal.proposal_id == "p1"
    assert proposal.agent_id == "a1"
    assert proposal.revision_count == 0
    
    engine.argument_map.add_critique("p1", "a2", "GNNs may overfit to training topology")
    
    assert len(engine.argument_map.proposals["p1"].critiques_received) == 1
    assert engine.argument_map.proposals["p1"].critiques_received[0]["addressed"] is False


def test_argument_map_closure_by_addressed_critiques():
    """Closure reached when all critiques on a proposal are addressed."""
    engine = DeliberationEngine()
    engine.initialize_argument_map("task-001")
    
    engine.add_proposal_to_map("p1", "a1", "Content", "Reasoning", 0.8)
    engine.argument_map.add_critique("p1", "a2", "Critique 1")
    engine.argument_map.add_critique("p1", "a3", "Critique 2")
    
    # Simulate deliberation rounds directly in argument_map
    # (bypassing execute_round to avoid auto-population of rounds)
    engine.argument_map.rounds = [
        {"round": 1, "proposals": ["p1"], "votes": {"a1": "p1"}},
        {"round": 2, "proposals": ["p1", "p2"], "votes": {"a1": "p2", "a2": "p1"}},
    ]
    
    # Before addressing: no closure (critiques exist but are unaddressed)
    assert engine.argument_map.check_closure(min_rounds=2) is False
    
    # Address critiques
    engine.argument_map.mark_critique_addressed("p1", 0)
    engine.argument_map.mark_critique_addressed("p1", 1)
    
    # After addressing: closure reached (all critiques on p1 addressed + min_rounds met)
    assert engine.argument_map.check_closure(min_rounds=2) is True
    assert engine.argument_map.closure_reached is True


def test_argument_map_closure_by_stagnation():
    """Closure reached when no new proposals and stable voting across rounds."""
    engine = DeliberationEngine()
    engine.initialize_argument_map("task-001")
    
    engine.add_proposal_to_map("p1", "a1", "Content", "Reasoning", 0.8)
    
    # Simulate two rounds with same proposals via execute_round
    engine.execute_round("task-001", {"a1": {"proposal_id": "p1", "confidence": 0.8}})
    engine.execute_round("task-001", {"a1": {"proposal_id": "p1", "confidence": 0.8}})
    
    assert engine.argument_map.check_closure(min_rounds=2) is True
    assert "Stagnation" in engine.argument_map.closure_reason


def test_unaddressed_critiques_tracking():
    """Unaddressed critiques are the open questions in the deliberation."""
    engine = DeliberationEngine()
    engine.initialize_argument_map("task-001")
    
    engine.add_proposal_to_map("p1", "a1", "Content", "Reasoning", 0.8)
    engine.argument_map.add_critique("p1", "a2", "Unaddressed critique")
    engine.argument_map.mark_critique_addressed("p1", 0)  # Address it
    
    engine.add_proposal_to_map("p2", "a3", "Content2", "Reasoning2", 0.7)
    engine.argument_map.add_critique("p2", "a1", "Open question")
    
    unaddressed = engine.argument_map.get_unaddressed_critiques()
    assert len(unaddressed) == 1
    assert unaddressed[0]["proposal_id"] == "p2"


def test_deliberation_summary():
    """Deliberation summary must report status accurately."""
    engine = DeliberationEngine(max_rounds=5)
    
    # Empty deliberation
    summary = engine.get_deliberation_summary()
    assert summary["status"] == "no_deliberation"
    
    # Execute rounds
    engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.8},
    })
    
    engine.initialize_argument_map("task-001")
    engine.add_proposal_to_map("p1", "a1", "Content", "Reasoning", 0.8)
    
    summary = engine.get_deliberation_summary()
    assert summary["status"] == "ongoing"
    assert summary["total_rounds"] == 1
    assert summary["semantic_decay_applied"] is True


def test_end_to_end_deliberation_with_closure():
    """Full deliberation: 3 rounds, proposals, critiques, closure."""
    engine = DeliberationEngine(max_rounds=5, semantic_decay=0.85)
    engine.initialize_argument_map("task-001")
    
    # Round 1: Initial proposals
    result1 = engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.8},
        "a2": {"proposal_id": "p2", "confidence": 0.7},
        "a3": {"proposal_id": "p3", "confidence": 0.6},
    })
    
    engine.add_proposal_to_map("p1", "a1", "Use GNN topology", "GNNs learn patterns", 0.8)
    engine.add_proposal_to_map("p2", "a2", "Use fully-connected", "Simple and robust", 0.7)
    
    # Round 2: Convergence + critiques
    result2 = engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.85},
        "a2": {"proposal_id": "p1", "confidence": 0.80},
        "a3": {"proposal_id": "p2", "confidence": 0.65},
    }, previous_consensus=result1["consensus"])
    
    engine.argument_map.add_critique("p1", "a3", "GNN training cost is high")
    engine.argument_map.add_critique("p1", "a2", "Needs Byzantine fault tolerance proof")
    
    # Round 3: Address critiques + final convergence
    result3 = engine.execute_round("task-001", {
        "a1": {"proposal_id": "p1", "confidence": 0.90},
        "a2": {"proposal_id": "p1", "confidence": 0.88},
        "a3": {"proposal_id": "p1", "confidence": 0.85},
    }, previous_consensus=result2["consensus"])
    
    engine.argument_map.mark_critique_addressed("p1", 0)
    engine.argument_map.mark_critique_addressed("p1", 1)
    
    # Check closure
    closure = engine.check_closure()
    assert closure["closure_reached"] is True
    assert closure["total_proposals"] == 2
    assert closure["unaddressed_critiques"] == 0
    
    # Summary
    summary = engine.get_deliberation_summary()
    assert summary["status"] == "completed"
    assert summary["total_rounds"] == 3
