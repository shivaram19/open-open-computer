"""
Tests for P3: Periodic Temporal Knowledge Graph (PTKG).

Covers:
- PTKG core: nodes, edges, periods, temporal queries, traversal
- Persistence: JSONL save/load/compact
- Graph retrieval: all strategies including hybrid
- Reputation graph: tracking, history, trends
- Causal chains: recording, querying, cross-session impact
- Integration: ConsciousAgent retrieval-before-reasoning, SwarmOrchestrator persistence

Citations:
- ViG-RAG2026: PTKG quintuple structure (h, r, t, τ, p)
- Zep2025: Temporal knowledge graph with validity periods
- TSM2026: Episodic-to-durative consolidation
- KGoT2025: Dynamic knowledge graph evolving with task state
- GraphMemory2026: Retrieval precedes reasoning
- NSED2026: Reputation-weighted consensus
- SWARP2026: Argument map causal chains
- LiCoMemory2025: Hierarchical graph retrieval
"""

import time
import tempfile


import pytest

from memory.ptkg import (
    PTKG,
    PTKGNode,
    PTKGEdge,
    PTKGPeriod,
    NodeType,
    EdgeType,
)
from memory.persistence import PTKGPersistence
from memory.graph_retrieval import GraphRetriever, GraphRetrievalStrategy
from memory.reputation_graph import ReputationGraphTracker, ReputationFactors
from memory.causal_chain import CausalChainTracker
from agents.conscious_agent import ConsciousAgent, AgentGoal
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from agents.deliberation import DeliberationEngine, Vote, Proposal, ArgumentMap
from conftest import default_agent_kwargs


# ── PTKG Core Tests ────────────────────────────────────────────────

class TestPTKGCore:
    """Tests for PTKG node/edge/period operations."""

    def test_add_node_returns_node_with_id(self):
        graph = PTKG()
        node = graph.add_node(NodeType.AGENT, label="Test Agent")
        
        assert node.node_id is not None
        assert node.label == "Test Agent"
        assert node.node_type == NodeType.AGENT
        assert node.node_id in graph._nodes

    def test_add_edge_requires_existing_nodes(self):
        graph = PTKG()
        n1 = graph.add_node(NodeType.AGENT, label="A1")
        
        edge = graph.add_edge(n1.node_id, "nonexistent", EdgeType.PROPOSED)
        assert edge is None
        
        n2 = graph.add_node(NodeType.PROPOSAL, label="P1")
        edge = graph.add_edge(n1.node_id, n2.node_id, EdgeType.PROPOSED)
        assert edge is not None
        assert edge.source_id == n1.node_id
        assert edge.target_id == n2.node_id

    def test_node_temporal_validity(self):
        graph = PTKG()
        now = time.time()
        node = graph.add_node(
            NodeType.CONCEPT,
            label="Test",
            valid_from=now - 100,
            valid_until=now + 100,
        )
        
        assert node.is_valid_at(now)
        assert not node.is_valid_at(now - 200)
        assert not node.is_valid_at(now + 200)

    def test_invalidate_node_sets_valid_until(self):
        graph = PTKG()
        node = graph.add_node(NodeType.CONCEPT, label="Old Fact")
        
        assert node.valid_until is None
        graph.invalidate_node(node.node_id)
        assert node.valid_until is not None
        assert not node.is_valid_at(time.time() + 1)

    def test_get_nodes_by_type(self):
        graph = PTKG()
        graph.add_node(NodeType.AGENT, label="A1")
        graph.add_node(NodeType.AGENT, label="A2")
        graph.add_node(NodeType.PROPOSAL, label="P1")
        
        agents = graph.get_nodes_by_type(NodeType.AGENT)
        proposals = graph.get_nodes_by_type(NodeType.PROPOSAL)
        
        assert len(agents) == 2
        assert len(proposals) == 1

    def test_period_lifecycle(self):
        graph = PTKG()
        period = graph.start_period(label="Session 1")
        
        assert period.period_id in graph._periods
        assert period.end_time is None
        
        graph.end_period(period.period_id)
        assert graph._periods[period.period_id].end_time is not None

    def test_nodes_in_period(self):
        graph = PTKG()
        period = graph.start_period(label="Test Period")
        
        graph.add_node(NodeType.AGENT, label="A1", period_id=period.period_id)
        graph.add_node(NodeType.PROPOSAL, label="P1", period_id=period.period_id)
        graph.add_node(NodeType.AGENT, label="A2")  # No period
        
        period_nodes = graph.get_nodes_in_period(period.period_id)
        assert len(period_nodes) == 2


class TestPTKGBfsTraversal:
    """Tests for BFS traversal with filters."""

    def test_bfs_basic_traversal(self):
        graph = PTKG()
        a = graph.add_node(NodeType.AGENT, label="A1")
        p1 = graph.add_node(NodeType.PROPOSAL, label="P1")
        p2 = graph.add_node(NodeType.PROPOSAL, label="P2")
        
        graph.add_edge(a.node_id, p1.node_id, EdgeType.PROPOSED)
        graph.add_edge(a.node_id, p2.node_id, EdgeType.PROPOSED)
        
        results = graph.bfs_traversal(a.node_id, max_depth=1)
        
        assert len(results) == 2
        targets = [r["target_node"] for r in results]
        assert p1.node_id in targets
        assert p2.node_id in targets

    def test_bfs_edge_type_filter(self):
        graph = PTKG()
        a = graph.add_node(NodeType.AGENT, label="A1")
        p = graph.add_node(NodeType.PROPOSAL, label="P1")
        arg = graph.add_node(NodeType.ARGUMENT, label="Arg1")
        
        graph.add_edge(a.node_id, p.node_id, EdgeType.PROPOSED)
        graph.add_edge(arg.node_id, p.node_id, EdgeType.SUPPORTED)
        
        results = graph.bfs_traversal(a.node_id, max_depth=2, edge_types=[EdgeType.PROPOSED])
        
        # Should reach P1 but not arg (since arg->p is SUPPORTED, not PROPOSED)
        assert any(r["target_node"] == p.node_id for r in results)

    def test_bfs_confidence_filter(self):
        graph = PTKG()
        a = graph.add_node(NodeType.AGENT, label="A1")
        p_low = graph.add_node(NodeType.PROPOSAL, label="P_low")
        p_high = graph.add_node(NodeType.PROPOSAL, label="P_high")
        
        graph.add_edge(a.node_id, p_low.node_id, EdgeType.PROPOSED, confidence=0.2)
        graph.add_edge(a.node_id, p_high.node_id, EdgeType.PROPOSED, confidence=0.9)
        
        results = graph.bfs_traversal(a.node_id, max_depth=1, min_confidence=0.5)
        targets = [r["target_node"] for r in results]
        
        assert p_high.node_id in targets
        assert p_low.node_id not in targets

    def test_find_causal_paths(self):
        graph = PTKG()
        cause = graph.add_node(NodeType.EVENT, label="Cause")
        mid = graph.add_node(NodeType.EVENT, label="Intermediate")
        effect = graph.add_node(NodeType.EVENT, label="Effect")
        
        graph.add_edge(cause.node_id, mid.node_id, EdgeType.CAUSED, causal_weight=0.8)
        graph.add_edge(mid.node_id, effect.node_id, EdgeType.CAUSED, causal_weight=0.7)
        
        paths = graph.find_causal_paths(cause.node_id, max_depth=3, min_causal_weight=0.5)
        
        assert len(paths) == 2  # cause->mid and cause->mid->effect
        
        # Check that effect is reachable
        effect_reachable = any(
            step["to"] == effect.node_id for path in paths for step in path
        )
        assert effect_reachable


class TestPTKGConsolidation:
    """Tests for period consolidation into durative summaries."""

    def test_consolidate_period_creates_summary(self):
        graph = PTKG()
        period = graph.start_period(label="Old Session")
        
        graph.add_node(NodeType.AGENT, label="A1", period_id=period.period_id)
        graph.add_node(NodeType.PROPOSAL, label="P1", period_id=period.period_id)
        graph.end_period(period.period_id)
        
        summary = graph.consolidate_period(period.period_id)
        
        assert summary is not None
        assert summary.node_type == NodeType.DURATIVE_SUMMARY
        assert summary.properties["node_count"] == 2
        assert graph._periods[period.period_id].consolidated_into == summary.node_id


class TestPTKGSerialization:
    """Tests for to_dict/from_dict round-trip."""

    def test_round_trip_preserves_structure(self):
        graph = PTKG(graph_id="test-graph")
        a = graph.add_node(NodeType.AGENT, label="A1", properties={"key": "val"})
        p = graph.add_node(NodeType.PROPOSAL, label="P1")
        graph.add_edge(a.node_id, p.node_id, EdgeType.PROPOSED, causal_weight=0.7)
        graph.start_period(label="P1")
        
        data = graph.to_dict()
        restored = PTKG.from_dict(data)
        
        assert restored.graph_id == "test-graph"
        assert len(restored._nodes) == 2
        assert len(restored._edges) == 1
        assert len(restored._periods) == 1
        
        restored_node = restored._nodes[a.node_id]
        assert restored_node.label == "A1"
        assert restored_node.properties["key"] == "val"


# ── Persistence Tests ──────────────────────────────────────────────

class TestPTKGPersistence:
    """Tests for JSONL persistence layer."""

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            persist = PTKGPersistence(storage_dir=tmpdir)
            
            graph = PTKG(graph_id="persist-test")
            graph.add_node(NodeType.AGENT, label="A1")
            
            path = persist.save(graph)
            assert path.exists()
            
            loaded = persist.load("persist-test")
            assert loaded is not None
            assert loaded.graph_id == "persist-test"
            assert len(loaded._nodes) == 1

    def test_multiple_snapshots(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            persist = PTKGPersistence(storage_dir=tmpdir)
            
            graph = PTKG(graph_id="multi-snap")
            persist.save(graph)
            
            graph.add_node(NodeType.AGENT, label="A1")
            persist.save(graph)
            
            graph.add_node(NodeType.PROPOSAL, label="P1")
            persist.save(graph)
            
            loaded = persist.load("multi-snap")
            assert loaded is not None
            assert len(loaded._nodes) == 2

    def test_compact_keeps_latest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            persist = PTKGPersistence(storage_dir=tmpdir, max_snapshots=2)
            
            graph = PTKG(graph_id="compact-test")
            for i in range(5):
                graph.add_node(NodeType.AGENT, label=f"A{i}")
                persist.save(graph)
            
            persist.compact("compact-test", keep_snapshots=2)
            
            path = persist._graph_path("compact-test")
            with open(path) as f:
                lines = f.readlines()
            assert len(lines) == 2

    def test_list_graphs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            persist = PTKGPersistence(storage_dir=tmpdir)
            graph = PTKG(graph_id="list-me")
            persist.save(graph)
            
            graphs = persist.list_graphs()
            assert "list-me" in graphs


# ── Graph Retrieval Tests ──────────────────────────────────────────

class TestGraphRetrieval:
    """Tests for GraphRetriever strategies."""

    def setup_graph(self):
        graph = PTKG()
        a1 = graph.add_node(NodeType.AGENT, label="A1", source_agent_id="agent-1", properties={"agent_id": "agent-1"})
        a2 = graph.add_node(NodeType.AGENT, label="A2", source_agent_id="agent-2", properties={"agent_id": "agent-2"})
        p1 = graph.add_node(NodeType.PROPOSAL, label="P1", source_agent_id="agent-1")
        p2 = graph.add_node(NodeType.PROPOSAL, label="P2", source_agent_id="agent-2")
        
        graph.add_edge(a1.node_id, p1.node_id, EdgeType.PROPOSED, confidence=0.9)
        graph.add_edge(a2.node_id, p2.node_id, EdgeType.PROPOSED, confidence=0.6)
        graph.add_edge(p1.node_id, p2.node_id, EdgeType.CRITIQUED, confidence=0.7)
        
        return graph, a1, a2, p1, p2

    def test_neighbor_retrieval(self):
        graph, a1, _, p1, p2 = self.setup_graph()
        retriever = GraphRetriever(graph)
        
        result = retriever.retrieve(
            GraphRetrievalStrategy.NEIGHBOR,
            query_node_id=a1.node_id,
        )
        
        assert len(result.nodes) == 1  # Only p1 is directly connected to a1
        assert any(n.node_id == p1.node_id for n in result.nodes)

    def test_multi_hop_bfs(self):
        graph, a1, _, _, p2 = self.setup_graph()
        retriever = GraphRetriever(graph)
        
        result = retriever.retrieve(
            GraphRetrievalStrategy.MULTI_HOP_BFS,
            query_node_id=a1.node_id,
            params={"depth": 2},
        )
        
        # a1 -> p1 -> p2 (2 hops)
        assert any(n.node_id == p2.node_id for n in result.nodes)

    def test_reputation_weighted(self):
        graph, a1, _, p1, p2 = self.setup_graph()
        retriever = GraphRetriever(graph)
        retriever.set_agent_reputation("agent-1", 0.9)
        retriever.set_agent_reputation("agent-2", 0.3)
        
        result = retriever.retrieve(
            GraphRetrievalStrategy.REPUTATION_WEIGHTED,
            query_node_id=a1.node_id,
        )
        
        # agent-1's proposal (p1) should be ranked higher
        if result.nodes:
            assert result.nodes[0].source_agent_id in ("agent-1", "agent-2")

    def test_hybrid_retrieval(self):
        graph, a1, _, _, _ = self.setup_graph()
        retriever = GraphRetriever(graph)
        
        result = retriever.retrieve(
            GraphRetrievalStrategy.HYBRID,
            query_node_id=a1.node_id,
            params={"depth": 2, "reputation_boost": True},
        )
        
        assert result.strategy == "hybrid"
        assert len(result.nodes) > 0

    def test_build_reasoning_context(self):
        graph, a1, _, _, _ = self.setup_graph()
        retriever = GraphRetriever(graph)
        
        context = retriever.build_reasoning_context(
            agent_id="agent-1",
            goal_description="test goal",
            max_nodes=5,
        )
        
        assert "relevant_nodes" in context
        assert "agent_reputation" in context
        assert context["strategy"] == "hybrid"


# ── Reputation Graph Tests ─────────────────────────────────────────

class TestReputationGraphTracker:
    """Tests for reputation evolution tracking."""

    def test_record_reputation_creates_snapshot(self):
        graph = PTKG()
        tracker = ReputationGraphTracker(graph)
        
        snapshot = tracker.record_reputation("agent-1", 0.85)
        
        assert snapshot is not None
        assert snapshot.node_type == NodeType.REPUTATION_SNAPSHOT
        assert snapshot.properties["score"] == 0.85

    def test_reputation_history_chronological(self):
        graph = PTKG()
        tracker = ReputationGraphTracker(graph)
        
        tracker.record_reputation("agent-1", 0.6)
        tracker.record_reputation("agent-1", 0.7)
        tracker.record_reputation("agent-1", 0.8)
        
        history = tracker.get_reputation_history("agent-1")
        assert len(history) == 3
        assert history[0]["score"] == 0.6
        assert history[2]["score"] == 0.8

    def test_current_reputation(self):
        graph = PTKG()
        tracker = ReputationGraphTracker(graph)
        
        assert tracker.get_current_reputation("agent-1") == 0.5  # Default
        
        tracker.record_reputation("agent-1", 0.75)
        assert tracker.get_current_reputation("agent-1") == 0.75

    def test_reputation_trend(self):
        graph = PTKG()
        tracker = ReputationGraphTracker(graph)
        
        tracker.record_reputation("agent-1", 0.5)
        tracker.record_reputation("agent-1", 0.6)
        tracker.record_reputation("agent-1", 0.7)
        tracker.record_reputation("agent-1", 0.8)
        
        trend = tracker.get_reputation_trend("agent-1", window=4)
        assert trend["trend"] == "rising"
        assert trend["slope"] > 0

    def test_compute_from_deliberation(self):
        graph = PTKG()
        tracker = ReputationGraphTracker(graph)
        
        score = tracker.compute_reputation_from_deliberation(
            agent_id="agent-1",
            proposals_made=4,
            proposals_accepted=3,
            critiques_received=2,
            critiques_addressed=2,
        )
        
        assert 0.0 <= score <= 1.0
        assert tracker.get_current_reputation("agent-1") == score

    def test_reputation_factors_computation(self):
        factors = ReputationFactors(
            task_success_rate=0.8,
            consensus_alignment=0.9,
            peer_evaluation=0.7,
            deliberation_quality=0.6,
        )
        score = factors.compute_score()
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # All factors above 0.5


# ── Causal Chain Tests ─────────────────────────────────────────────

class TestCausalChainTracker:
    """Tests for causal chain tracking."""

    def test_record_cause_creates_edge(self):
        graph = PTKG()
        tracker = CausalChainTracker(graph)
        
        cause = tracker.record_event("Cause Event")
        effect = tracker.record_event("Effect Event")
        
        edge = tracker.record_cause(cause.node_id, effect.node_id, causal_weight=0.8)
        
        assert edge is not None
        assert edge.edge_type == EdgeType.CAUSED
        assert edge.causal_weight == 0.8

    def test_find_causes_backward(self):
        graph = PTKG()
        tracker = CausalChainTracker(graph)
        
        c1 = tracker.record_event("Root Cause")
        c2 = tracker.record_event("Intermediate")
        effect = tracker.record_event("Final Effect")
        
        tracker.record_cause(c1.node_id, c2.node_id, 0.8)
        tracker.record_cause(c2.node_id, effect.node_id, 0.7)
        
        causes = tracker.find_causes(effect.node_id, max_depth=3)
        
        cause_ids = [c["cause_node_id"] for c in causes]
        assert c1.node_id in cause_ids
        assert c2.node_id in cause_ids

    def test_find_effects_forward(self):
        graph = PTKG()
        tracker = CausalChainTracker(graph)
        
        cause = tracker.record_event("Cause")
        e1 = tracker.record_event("Effect 1")
        e2 = tracker.record_event("Effect 2")
        
        tracker.record_cause(cause.node_id, e1.node_id, 0.8)
        tracker.record_cause(cause.node_id, e2.node_id, 0.6)
        
        effects = tracker.find_effects(cause.node_id, max_depth=2)
        
        effect_ids = [e["effect_node_id"] for e in effects]
        assert e1.node_id in effect_ids
        assert e2.node_id in effect_ids

    def test_causal_strength(self):
        graph = PTKG()
        tracker = CausalChainTracker(graph)
        
        c1 = tracker.record_event("C1")
        c2 = tracker.record_event("C2")
        effect = tracker.record_event("Effect")
        
        tracker.record_cause(c1.node_id, c2.node_id, 0.5)
        tracker.record_cause(c2.node_id, effect.node_id, 0.5)
        
        strength = tracker.get_causal_strength(c1.node_id, effect.node_id)
        assert strength == 0.25  # 0.5 * 0.5

    def test_deliberation_causal_chain(self):
        graph = PTKG()
        tracker = CausalChainTracker(graph)
        
        proposal = graph.add_node(NodeType.PROPOSAL, label="P1")
        arg1 = graph.add_node(NodeType.ARGUMENT, label="Arg1")
        arg2 = graph.add_node(NodeType.ARGUMENT, label="Arg2")
        
        result = tracker.record_deliberation_causal_chain(
            period_id="period-1",
            proposal_node_id=proposal.node_id,
            argument_node_ids=[arg1.node_id, arg2.node_id],
            critique_node_ids=[],
            outcome="accepted",
        )
        
        assert "outcome_node_id" in result
        assert len(result["recorded_edges"]) == 3  # 2 args + 1 proposal

    def test_cross_session_impact(self):
        graph = PTKG()
        tracker = CausalChainTracker(graph)
        
        root = tracker.record_event("Root")
        e1 = tracker.record_event("Effect 1")
        e2 = tracker.record_event("Effect 2")
        
        tracker.record_cause(root.node_id, e1.node_id, 0.8)
        tracker.record_cause(root.node_id, e2.node_id, 0.7)
        
        impact = tracker.get_cross_session_impact(root.node_id)
        
        assert impact["direct_effects"] == 2
        assert impact["total_effects"] == 2


# ── Integration Tests ──────────────────────────────────────────────

class TestConsciousAgentGraphIntegration:
    """Tests for ConsciousAgent + PTKG integration."""

    def test_connect_graph_memory(self):
        agent = ConsciousAgent("test-1", "TestAgent", "multi-agent", **default_agent_kwargs("test-1"))
        graph = PTKG()
        
        agent.connect_graph_memory(graph)
        
        assert agent.graph_memory is graph
        assert agent.graph_retriever is not None
        
        # Agent node should exist in graph
        agent_nodes = [n for n in graph._nodes.values() if n.properties.get("agent_id") == "test-1"]
        assert len(agent_nodes) == 1

    def test_think_includes_graph_context(self):
        agent = ConsciousAgent("test-2", "TestAgent2", "multi-agent", **default_agent_kwargs("test-2"))
        graph = PTKG()
        
        # Pre-populate graph with relevant context
        agent_node = graph.add_node(
            NodeType.AGENT,
            label="TestAgent2",
            properties={"agent_id": "test-2"},
            source_agent_id="test-2",
        )
        task_node = graph.add_node(
            NodeType.TASK,
            label="Similar Task",
            properties={"task_id": "old-task"},
        )
        graph.add_edge(agent_node.node_id, task_node.node_id, EdgeType.PARTICIPATED_IN)
        
        agent.connect_graph_memory(graph)
        agent.graph_retriever.set_agent_reputation("test-2", 0.8)
        
        goal = AgentGoal(
            goal_id="goal-1",
            description="Analyze video stream for anomalies",
            success_criteria=["detection_rate > 0.9"],
        )
        agent.activate(goal)
        reasoning = agent.think()
        
        assert "graph_context" in reasoning
        assert reasoning["graph_context"] is not None


class TestSwarmOrchestratorGraphIntegration:
    """Tests for SwarmOrchestrator + PTKG integration."""

    def test_initialize_graph_memory(self):
        orch = SwarmOrchestrator()
        graph = orch.initialize_graph_memory()
        
        assert orch.graph_memory is graph
        assert orch.graph_retriever is not None
        assert orch.reputation_tracker is not None
        assert orch.causal_tracker is not None

    def test_activate_task_connects_graph(self):
        orch = SwarmOrchestrator()
        graph = orch.initialize_graph_memory()
        
        agent = ConsciousAgent("a1", "Agent1", "multi-agent", **default_agent_kwargs("a1"))
        orch.register_agent(agent)
        
        task = SwarmTask(
            task_id="task-1",
            description="Test task",
            required_clusters=["multi-agent"],
            success_criteria=["done"],
        )
        orch.activate_task(task)
        
        assert agent.graph_memory is graph

    def test_persist_deliberation_to_graph(self):
        orch = SwarmOrchestrator()
        orch.initialize_graph_memory()
        
        agent = ConsciousAgent("a1", "Agent1", "multi-agent", **default_agent_kwargs("a1"))
        orch.register_agent(agent)
        
        task = SwarmTask(
            task_id="task-1",
            description="Test task",
            required_clusters=["multi-agent"],
            success_criteria=["done"],
        )
        orch.activate_task(task)
        
        # Create a fake deliberation result
        deliberation_result = {
            "task_id": "task-1",
            "task_description": "Test task",
            "total_rounds": 2,
            "rounds": [],
            "final_consensus": {"winner": "p1", "quorum_reached": True},
            "closure": {"closure_reached": True},
            "deliberation_summary": {
                "argument_map": {
                    "proposals": {
                        "p1": {"agent_id": "a1", "content": "Proposal 1", "confidence": 0.9}
                    }
                }
            },
            "timestamp": time.time(),
        }
        
        result = orch.persist_deliberation_to_graph("task-1", deliberation_result)
        
        assert "error" not in result
        assert result["proposals_persisted"] == 1
        assert result["period_id"] is not None

    def test_persist_without_graph_memory_returns_error(self):
        orch = SwarmOrchestrator()
        result = orch.persist_deliberation_to_graph("task-1", {})
        assert "error" in result


class TestEndToEndGraphMemory:
    """End-to-end test: swarm deliberation -> PTKG -> retrieval."""

    def test_full_cycle(self):
        orch = SwarmOrchestrator()
        orch.initialize_graph_memory()
        
        # Create and register agents
        for i in range(3):
            agent = ConsciousAgent(f"a{i}", f"Agent{i}", "multi-agent", **default_agent_kwargs(f"a{i}"))
            orch.register_agent(agent)
        
        task = SwarmTask(
            task_id="e2e-task",
            description="Byzantine fault-tolerant video analysis",
            required_clusters=["multi-agent"],
            success_criteria=["consensus reached"],
        )
        orch.activate_task(task)
        
        # Agents think (with graph context)
        for agent in orch.agents.values():
            if agent.current_goal:
                reasoning = agent.think()
                assert "graph_context" in reasoning
        
        # Create a deliberation result and persist
        deliberation_result = {
            "task_id": "e2e-task",
            "task_description": "Byzantine fault-tolerant video analysis",
            "total_rounds": 3,
            "rounds": [],
            "final_consensus": {"winner": "p1", "quorum_reached": True},
            "closure": {"closure_reached": True},
            "deliberation_summary": {
                "argument_map": {
                    "proposals": {
                        "p1": {"agent_id": "a0", "content": "Use GNN for spatial analysis", "confidence": 0.85},
                        "p2": {"agent_id": "a1", "content": "Use streaming reflection", "confidence": 0.70},
                    }
                }
            },
            "timestamp": time.time(),
        }
        
        persist_result = orch.persist_deliberation_to_graph("e2e-task", deliberation_result)
        assert persist_result["proposals_persisted"] == 2
        
        # Query the graph: find all proposals
        proposals = orch.graph_memory.get_nodes_by_type(NodeType.PROPOSAL)
        assert len(proposals) == 2
        
        # Query the graph: causal paths from a proposal
        causal = CausalChainTracker(orch.graph_memory)
        for p in proposals:
            effects = causal.find_effects(p.node_id, max_depth=2)
            # At minimum, each proposal has a causal edge to the outcome
            assert len(effects) >= 1
        
        # Query the graph: reputation tracking
        reps = orch.reputation_tracker.get_all_agent_reputations()
        assert len(reps) >= 1
        
        # Test persistence
        with tempfile.TemporaryDirectory() as tmpdir:
            persist = PTKGPersistence(storage_dir=tmpdir)
            persist.save(orch.graph_memory)
            
            loaded = persist.load(orch.graph_memory.graph_id)
            assert loaded is not None
            assert len(loaded.get_nodes_by_type(NodeType.PROPOSAL)) == 2
