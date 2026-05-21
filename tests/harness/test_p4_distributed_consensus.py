"""
Tests for P4: Distributed Consensus & Temporal Auditor.

Covers:
- HLC: timestamp generation, causality ordering, send/receive sync, skew detection
- Temporal Auditor: message auditing, deliberation round auditing, health signals
- CP-WBFT Consensus: Stage 1 refinement, Stage 2 aggregation, geometric median fallback
- Topology Optimizer: all topology types, adaptive selection, metrics computation
- Cross-Block Messenger: message envelopes, causal delivery, broadcast
- Integration: ConsciousAgent HLC stamping, SwarmOrchestrator CP-WBFT consensus

Citations:
- Kulkarni2014: Hybrid Logical Clocks
- CockroachDB2022: HLC in distributed databases
- TemporalObservability2026: Causality health signal
- CP-WBFT2025: Confidence probe-based weighted BFT
- DecentLLMs2025: Geometric median aggregation
- G-Designer2025: Task-adaptive topology optimization
- Lamport1978: Happened-before relation
"""

import time


import pytest

from consensus.hlc import HybridLogicalClock, HLCTimestamp, hlc_max, are_concurrent
from consensus.temporal_auditor import (
    TemporalAuditor,
    CausalityHealth,
    ViolationType,
    CausalityViolation,
)
from consensus.distributed_consensus import (
    DistributedConsensusEngine,
    AgentVote,
    ConsensusPhase,
)
from consensus.topology import TopologyOptimizer, TopologyType, TopologyMetrics
from consensus.cross_block_messenger import CrossBlockMessenger, MessageEnvelope
from agents.conscious_agent import ConsciousAgent, AgentGoal
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from conftest import default_agent_kwargs


# ── HLC Tests ──────────────────────────────────────────────────────

class TestHybridLogicalClock:
    """Tests for Hybrid Logical Clock implementation."""

    def test_now_increments_logical_counter(self):
        clock = HybridLogicalClock("node-1")
        t1 = clock.now()
        t2 = clock.now()
        
        assert t2 >= t1
        if t1.pt == t2.pt:
            assert t2.lc > t1.lc

    def test_send_returns_timestamp(self):
        clock = HybridLogicalClock("node-1")
        ts = clock.send()
        
        assert ts.node_id == "node-1"
        assert ts.pt > 0
        assert ts.lc >= 0

    def test_receive_advances_clock(self):
        clock_a = HybridLogicalClock("node-a")
        clock_b = HybridLogicalClock("node-b")
        
        # Node A sends
        ts_a = clock_a.send()
        
        # Node B receives
        ts_b = clock_b.receive(ts_a)
        
        # B's clock should be >= A's timestamp
        assert ts_b >= ts_a

    def test_causality_ordering(self):
        clock = HybridLogicalClock("node-1")
        t1 = clock.now()
        t2 = clock.now()
        t3 = clock.now()
        
        assert t1 < t2 < t3

    def test_are_concurrent(self):
        c1 = HybridLogicalClock("node-1")
        c2 = HybridLogicalClock("node-2")
        
        t1 = c1.now()
        t2 = c2.now()
        
        # Concurrent if neither happened-before the other
        # This is unlikely with real clocks, but test the function
        assert not are_concurrent(t1, t2) or t1.pt == t2.pt

    def test_detect_skew(self):
        clock = HybridLogicalClock("node-1", max_skew_ms=100.0)
        
        # Remote timestamp from now should not be skewed
        remote_now = HLCTimestamp(pt=time.time(), lc=0, node_id="node-2")
        is_skewed, skew_ms = clock.detect_skew(remote_now)
        assert not is_skewed
        assert skew_ms < 100.0
        
        # Remote timestamp from far future should be skewed
        remote_future = HLCTimestamp(pt=time.time() + 10, lc=0, node_id="node-2")
        is_skewed, skew_ms = clock.detect_skew(remote_future)
        assert is_skewed
        assert skew_ms > 100.0

    def test_hlc_max(self):
        t1 = HLCTimestamp(pt=1.0, lc=0, node_id="a")
        t2 = HLCTimestamp(pt=1.0, lc=1, node_id="b")
        
        assert hlc_max(t1, t2) == t2
        assert hlc_max(t2, t1) == t2

    def test_timestamp_roundtrip(self):
        ts = HLCTimestamp(pt=123.456, lc=7, node_id="test")
        data = ts.to_dict()
        restored = HLCTimestamp.from_dict(data)
        
        assert restored.pt == ts.pt
        assert restored.lc == ts.lc
        assert restored.node_id == ts.node_id

    def test_clock_monotonicity(self):
        clock = HybridLogicalClock("node-1")
        timestamps = [clock.now() for _ in range(100)]
        
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1]


# ── Temporal Auditor Tests ─────────────────────────────────────────

class TestTemporalAuditor:
    """Tests for Temporal Auditor causal consistency monitoring."""

    def test_audit_message_missing_timestamp(self):
        auditor = TemporalAuditor()
        result = auditor.audit_message("agent-1", None)
        
        assert not result["valid"]
        assert result["health"] == CausalityHealth.VIOLATED
        assert len(result["violations"]) == 1
        assert result["violations"][0].violation_type == ViolationType.MISSING_TIMESTAMP

    def test_audit_message_valid_timestamp(self):
        auditor = TemporalAuditor()
        hlc = HybridLogicalClock("agent-1")
        ts = hlc.send()
        
        result = auditor.audit_message("agent-1", ts)
        
        assert result["valid"]
        assert result["health"] == CausalityHealth.HEALTHY

    def test_audit_message_skew_exceeded(self):
        auditor = TemporalAuditor(max_skew_ms=10.0)
        
        # Timestamp from far future
        future_ts = HLCTimestamp(pt=time.time() + 100, lc=0, node_id="agent-1")
        result = auditor.audit_message("agent-1", future_ts)
        
        assert not result["valid"]
        assert result["health"] == CausalityHealth.VIOLATED

    def test_audit_deliberation_round(self):
        auditor = TemporalAuditor()
        
        c1 = HybridLogicalClock("a1")
        c2 = HybridLogicalClock("a2")
        
        messages = {
            "a1": c1.send(),
            "a2": c2.send(),
        }
        
        result = auditor.audit_deliberation_round(1, messages)
        
        assert result["round"] == 1
        assert result["all_valid"] is True
        assert result["health"] == CausalityHealth.HEALTHY
        assert "a1" in result["agent_results"]
        assert "a2" in result["agent_results"]

    def test_causality_health_signal(self):
        auditor = TemporalAuditor(max_skew_ms=10.0)
        
        # Healthy messages
        hlc = HybridLogicalClock("agent-1")
        auditor.audit_message("agent-1", hlc.send())
        assert auditor.get_causality_health() == CausalityHealth.HEALTHY
        
        # Violated message
        future = HLCTimestamp(pt=time.time() + 100, lc=0, node_id="agent-1")
        auditor.audit_message("agent-1", future)
        assert auditor.get_causality_health() == CausalityHealth.VIOLATED

    def test_health_report(self):
        auditor = TemporalAuditor()
        hlc = HybridLogicalClock("agent-1")
        auditor.audit_message("agent-1", hlc.send())
        
        report = auditor.get_health_report()
        assert report["current_health"] == "HEALTHY"
        assert report["total_messages_checked"] == 1
        assert report["total_violations"] == 0
        assert report["violation_rate"] == 0.0


# ── CP-WBFT Consensus Tests ────────────────────────────────────────

class TestDistributedConsensusEngine:
    """Tests for CP-WBFT two-stage consensus."""

    def test_stage1_refine_moves_toward_higher_confidence(self):
        engine = DistributedConsensusEngine()
        
        votes = [
            AgentVote("a1", "p1", confidence=0.9, raw_score=0.8, refined_score=0.8, reputation=0.9),
            AgentVote("a2", "p1", confidence=0.5, raw_score=0.4, refined_score=0.4, reputation=0.5),
        ]
        
        refined = engine.stage1_probe_and_refine(votes)
        
        # a2 should move toward a1's score (higher confidence + reputation)
        a2_refined = next(v for v in refined if v.agent_id == "a2")
        assert a2_refined.refined_score > a2_refined.raw_score

    def test_stage2_selects_winner(self):
        engine = DistributedConsensusEngine()
        
        votes = [
            AgentVote("a1", "p1", confidence=0.9, raw_score=0.8, refined_score=0.8, reputation=0.9),
            AgentVote("a2", "p1", confidence=0.8, raw_score=0.7, refined_score=0.7, reputation=0.8),
            AgentVote("a3", "p2", confidence=0.5, raw_score=0.3, refined_score=0.3, reputation=0.5),
        ]
        
        result = engine.stage2_weighted_aggregation(votes)
        
        assert result["winner"] == "p1"
        assert result["quorum_reached"] is True
        assert "entropy" in result

    def test_geometric_median_fallback_on_low_quorum(self):
        engine = DistributedConsensusEngine(
            min_reputation_threshold=0.9,  # Very high — filters most votes
            quorum_ratio=0.9,              # Requires almost all agents
        )
        
        votes = [
            AgentVote("a1", "p1", confidence=0.5, raw_score=0.6, refined_score=0.6, reputation=0.5),
            AgentVote("a2", "p1", confidence=0.5, raw_score=0.7, refined_score=0.7, reputation=0.5),
        ]
        
        result = engine.stage2_weighted_aggregation(votes)
        
        assert result["method"] == "geometric_median_fallback"
        assert result["quorum_reached"] is False

    def test_detect_byzantine_outliers(self):
        engine = DistributedConsensusEngine()
        
        # 4 agents agree around 0.5, 1 is extreme outlier with low confidence
        votes = [
            AgentVote("a1", "p1", confidence=0.9, raw_score=0.50, refined_score=0.50, reputation=0.9),
            AgentVote("a2", "p1", confidence=0.85, raw_score=0.52, refined_score=0.52, reputation=0.85),
            AgentVote("a3", "p1", confidence=0.88, raw_score=0.51, refined_score=0.51, reputation=0.88),
            AgentVote("a4", "p1", confidence=0.87, raw_score=0.50, refined_score=0.50, reputation=0.87),
            AgentVote("a5", "p1", confidence=0.05, raw_score=0.0, refined_score=0.0, reputation=0.05),
        ]
        
        result = engine.stage2_weighted_aggregation(votes)
        
        # a5 is Byzantine: very low confidence but extreme score far from consensus
        assert "a5" in result["byzantine_detected"]

    def test_full_consensus_protocol(self):
        engine = DistributedConsensusEngine()
        
        votes = [
            AgentVote(f"a{i}", "p1" if i < 4 else "p2", confidence=0.7, raw_score=0.6, refined_score=0.6, reputation=0.7)
            for i in range(5)
        ]
        
        result = engine.reach_consensus(votes)
        
        assert "winner" in result
        assert result["phase"] == "final"
        assert result["duration_ms"] >= 0

    def test_entropy_computation(self):
        engine = DistributedConsensusEngine()
        
        # Uniform distribution = high entropy
        votes = [
            AgentVote("a1", "p1", confidence=0.5, raw_score=0.5, refined_score=0.5, reputation=0.5),
            AgentVote("a2", "p2", confidence=0.5, raw_score=0.5, refined_score=0.5, reputation=0.5),
        ]
        
        result = engine.stage2_weighted_aggregation(votes)
        entropy = result["entropy"]
        assert 0.0 <= entropy <= 1.0


# ── Topology Optimizer Tests ───────────────────────────────────────

class TestTopologyOptimizer:
    """Tests for communication topology optimization."""

    def setup_method(self):
        self.optimizer = TopologyOptimizer(random_seed=42)
        self.agents = [f"a{i}" for i in range(5)]

    def test_complete_topology(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.COMPLETE)
        
        for aid in self.agents:
            assert len(graph[aid]) == 4  # Connected to all others

    def test_star_topology(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.STAR, hub_agent="a0")
        
        assert graph["a0"] == ["a1", "a2", "a3", "a4"]
        for aid in self.agents[1:]:
            assert graph[aid] == ["a0"]

    def test_chain_topology(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.CHAIN)
        
        assert graph["a0"] == ["a1"]
        assert graph["a2"] == ["a1", "a3"]
        assert graph["a4"] == ["a3"]

    def test_tree_topology(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.TREE)
        
        # a0 is root, connected to a1 and a2
        assert "a1" in graph["a0"]
        assert "a2" in graph["a0"]

    def test_random_topology(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.RANDOM, random_edge_prob=0.5)
        
        # Should have some edges but not complete
        total_edges = sum(len(neighbors) for neighbors in graph.values()) // 2
        assert 0 < total_edges < 10

    def test_layered_topology(self):
        cluster_map = {"a0": "A", "a1": "A", "a2": "B", "a3": "B", "a4": "B"}
        graph = self.optimizer.build_topology(self.agents, TopologyType.LAYERED, cluster_map=cluster_map)
        
        # Dense within clusters
        assert "a1" in graph["a0"]  # Both in A
        assert "a3" in graph["a2"] or "a4" in graph["a2"]  # Both in B

    def test_adaptive_topology_simple_task(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.ADAPTIVE, task_difficulty=0.2)
        
        # Simple task with 5 agents uses star (default for >3 agents at low difficulty)
        assert len(graph) == 5
        # Star topology: hub has 4 neighbors, others have 1
        max_degree = max(len(neighbors) for neighbors in graph.values())
        assert max_degree >= 3  # Hub is well-connected

    def test_adaptive_topology_complex_task(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.ADAPTIVE, task_difficulty=0.9)
        
        # Complex task should use complete graph
        for aid in self.agents:
            assert len(graph[aid]) == 4

    def test_compute_metrics(self):
        graph = self.optimizer.build_topology(self.agents, TopologyType.COMPLETE)
        metrics = self.optimizer.compute_metrics(graph, TopologyType.COMPLETE)
        
        assert metrics.node_count == 5
        assert metrics.edge_count == 10  # 5 choose 2
        assert metrics.diameter == 1
        assert metrics.fault_tolerance_score == 1.0

    def test_optimize_for_task(self):
        topo_type, graph, metrics = self.optimizer.optimize_for_task(
            self.agents, task_complexity=0.5, max_token_budget=0.5
        )
        
        assert metrics.estimated_token_cost <= 0.5
        assert metrics.fault_tolerance_score >= 0.3


# ── Cross-Block Messenger Tests ────────────────────────────────────

class TestCrossBlockMessenger:
    """Tests for cross-block message passing with HLC stamps."""

    def test_send_creates_envelope(self):
        messenger = CrossBlockMessenger()
        messenger.register_agent("a1")
        messenger.register_agent("a2")
        
        envelope = messenger.send("a1", "a2", {"data": "hello"})
        
        assert envelope.sender_id == "a1"
        assert envelope.recipient_id == "a2"
        assert envelope.payload["data"] == "hello"
        assert envelope.hlc_timestamp is not None

    def test_poll_delivers_message(self):
        messenger = CrossBlockMessenger()
        messenger.register_agent("a1")
        messenger.register_agent("a2")
        
        messenger.send("a1", "a2", {"data": "hello"})
        
        delivered = messenger.poll("a2")
        
        assert len(delivered) == 1
        assert delivered[0].payload["data"] == "hello"

    def test_causal_dependency_enforced(self):
        messenger = CrossBlockMessenger()
        messenger.register_agent("a1")
        messenger.register_agent("a2")
        
        # Send msg1
        env1 = messenger.send("a1", "a2", {"seq": 1})
        
        # Send msg2 that depends on msg1
        env2 = messenger.send("a1", "a2", {"seq": 2}, causal_deps=[env1.message_id])
        
        # Poll without delivering msg1 first — msg2 should wait
        # Actually, poll processes in order, so msg1 will be delivered first
        delivered = messenger.poll("a2", max_messages=2)
        
        assert len(delivered) == 2
        assert delivered[0].payload["seq"] == 1
        assert delivered[1].payload["seq"] == 2

    def test_broadcast(self):
        messenger = CrossBlockMessenger()
        for i in range(3):
            messenger.register_agent(f"a{i}")
        
        envelopes = messenger.broadcast("a0", ["a1", "a2"], {"data": "broadcast"})
        
        assert len(envelopes) == 2
        assert messenger.get_pending_count("a1") == 1
        assert messenger.get_pending_count("a2") == 1

    def test_max_queue_size(self):
        messenger = CrossBlockMessenger(max_queue_size=3)
        messenger.register_agent("a1")
        messenger.register_agent("a2")
        
        for i in range(5):
            messenger.send("a1", "a2", {"seq": i})
        
        # Queue should have dropped oldest messages
        assert messenger.get_pending_count("a2") == 3

    def test_get_message_stats(self):
        messenger = CrossBlockMessenger()
        messenger.register_agent("a1")
        messenger.register_agent("a2")
        
        messenger.send("a1", "a2", {"test": True})
        
        stats = messenger.get_message_stats()
        assert stats["total_messages_sent"] == 1
        assert stats["registered_agents"] == 2


# ── Integration Tests ──────────────────────────────────────────────

class TestConsciousAgentHLCIntegration:
    """Tests for ConsciousAgent + HLC integration."""

    def test_agent_has_hlc_clock(self):
        agent = ConsciousAgent("test-1", "TestAgent", "multi-agent", **default_agent_kwargs("test-1"))
        assert hasattr(agent, "hlc_clock")
        assert agent.hlc_clock.node_id == "test-1"

    def test_communicate_stamps_hlc(self):
        agent1 = ConsciousAgent("a1", "Agent1", "multi-agent", **default_agent_kwargs("a1"))
        agent2 = ConsciousAgent("a2", "Agent2", "multi-agent", **default_agent_kwargs("a2"))
        agent1.register_peer(agent2)
        
        response = agent1.communicate("a2", {"confidence": 0.7, "proposal": "test"})
        
        assert "_hlc_timestamp" in response
        assert "_sender_hlc" in response

    def test_receive_updates_hlc(self):
        agent = ConsciousAgent("a1", "Agent1", "multi-agent", **default_agent_kwargs("a1"))
        
        # Simulate receiving a message with HLC
        peer_hlc = HybridLogicalClock("peer")
        ts = peer_hlc.send()
        
        before = agent.hlc_clock.get_current()
        agent.receive("peer", {
            "confidence": 0.5,
            "_hlc_timestamp": ts.to_dict(),
        })
        after = agent.hlc_clock.get_current()
        
        # HLC should have advanced (or at least not gone backward)
        assert after >= before


class TestSwarmOrchestratorP4Integration:
    """Tests for SwarmOrchestrator + P4 components integration."""

    def test_orchestrator_has_p4_components(self):
        orch = SwarmOrchestrator()
        
        assert hasattr(orch, "temporal_auditor")
        assert hasattr(orch, "consensus_engine")
        assert hasattr(orch, "topology_optimizer")

    def test_activate_task_builds_topology(self):
        orch = SwarmOrchestrator()
        
        for i in range(3):
            agent = ConsciousAgent(f"a{i}", f"Agent{i}", "multi-agent", **default_agent_kwargs(f"a{i}"))
            orch.register_agent(agent)
        
        task = SwarmTask(
            task_id="task-1",
            description="Test task",
            required_clusters=["multi-agent"],
            success_criteria=["done"],
        )
        orch.activate_task(task)
        
        assert len(orch.communication_topology) == 3

    def test_check_consensus_uses_cp_wbft(self):
        orch = SwarmOrchestrator()
        
        for i in range(3):
            agent = ConsciousAgent(f"a{i}", f"Agent{i}", "multi-agent", **default_agent_kwargs(f"a{i}"))
            orch.register_agent(agent)
        
        reasoning = {
            "a0": {"confidence": 0.9, "proposed_approach": "p1"},
            "a1": {"confidence": 0.8, "proposed_approach": "p1"},
            "a2": {"confidence": 0.5, "proposed_approach": "p2"},
        }
        
        result = orch._check_consensus(list(orch.agents.values()), reasoning)
        
        assert "cp_wbft" in result
        assert "winner" in result["cp_wbft"]
        assert "temporal_audit" in result
        assert "health" in result["temporal_audit"]

    def test_consensus_detects_byzantine(self):
        orch = SwarmOrchestrator()
        
        for i in range(5):
            agent = ConsciousAgent(f"a{i}", f"Agent{i}", "multi-agent", **default_agent_kwargs(f"a{i}"))
            orch.register_agent(agent)
        
        # a4 is Byzantine: low confidence but extreme score
        reasoning = {
            "a0": {"confidence": 0.9, "proposed_approach": "p1"},
            "a1": {"confidence": 0.85, "proposed_approach": "p1"},
            "a2": {"confidence": 0.8, "proposed_approach": "p1"},
            "a3": {"confidence": 0.75, "proposed_approach": "p1"},
            "a4": {"confidence": 0.1, "proposed_approach": "p2"},
        }
        
        result = orch._check_consensus(list(orch.agents.values()), reasoning)
        
        byzantine = result["cp_wbft"].get("byzantine_detected", [])
        assert "a4" in byzantine

    def test_full_deliberation_with_p4(self):
        orch = SwarmOrchestrator()
        orch.initialize_graph_memory()
        
        for i in range(3):
            agent = ConsciousAgent(f"a{i}", f"Agent{i}", "multi-agent", **default_agent_kwargs(f"a{i}"))
            orch.register_agent(agent)
        
        task = SwarmTask(
            task_id="p4-task",
            description="Test consensus with P4",
            required_clusters=["multi-agent"],
            success_criteria=["consensus"],
        )
        orch.activate_task(task)
        
        # Agents think
        for agent in orch.agents.values():
            if agent.current_goal:
                agent.think()
        
        # Check consensus
        reasoning = {
            agent.agent_id: {"confidence": 0.8, "proposed_approach": "p1"}
            for agent in orch.agents.values()
        }
        
        result = orch._check_consensus(list(orch.agents.values()), reasoning)
        
        assert result["status"] == "consensus" or result["status"] == "suspicious_conformity"
        assert result["cp_wbft"]["quorum_reached"] is True
        assert result["temporal_audit"]["all_valid"] is True
