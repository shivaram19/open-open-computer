# tests/dashboard/test_data_collector.py
"""Tests for DashboardDataCollector."""

import json
import pytest
from unittest.mock import MagicMock

from dashboard.data_collector import DashboardDataCollector
from memory.twin_memory_profile import TwinMemoryProfile


class TestDashboardDataCollector:
    def test_initial_state(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        assert collector._state["version"] == "1.0"
        assert collector._state["swarm"]["total_twins"] == 0

    def test_load_for_dashboard_missing_file(self):
        state = DashboardDataCollector.load_for_dashboard("/tmp/nonexistent_acn_state.json")
        assert state["swarm"]["total_twins"] == 0

    def test_save_and_load(self, tmp_path):
        path = tmp_path / "state.json"
        collector = DashboardDataCollector(str(path))
        collector._state["twins"]["twin-001"] = {"name": "Test", "layer_counts": {"l0": 5}}
        collector.save()

        loaded = DashboardDataCollector.load_for_dashboard(str(path))
        assert loaded["twins"]["twin-001"]["name"] == "Test"
        assert loaded["last_updated"] > 0

    def test_record_consensus(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        collector.record_consensus(score=0.85, round_num=3, academic_support=0.9, dissent=False)
        assert collector._state["consensus"]["score"] == 0.85
        assert collector._state["consensus"]["round"] == 3
        assert len(collector._state["recent_events"]) == 1

    def test_record_event(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        collector.record_event("think", {"twin_id": "twin-001", "task": "debug"})
        events = collector._state["recent_events"]
        assert len(events) == 1
        assert events[0]["type"] == "think"
        assert events[0]["twin_id"] == "twin-001"

    def test_event_history_limit(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        for i in range(60):
            collector.record_event("think", {"index": i})
        assert len(collector._state["recent_events"]) == 50
        assert collector._state["recent_events"][-1]["index"] == 59

    def test_collect_from_flat_memory_agent(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        agent = MagicMock()
        agent.name = "FlatAgent"
        agent.cluster = "multi-agent"
        agent.memory.get_memory_stats.return_value = {
            "episodic_count": 10,
            "semantic_count": 5,
        }
        collector._collect_flat_memory("agent-001", agent)
        twin_data = collector._state["twins"]["agent-001"]
        assert twin_data["name"] == "FlatAgent"
        assert twin_data["layer_counts"]["l0"] == 10
        assert twin_data.get("flat_memory") is True

    def test_swarm_aggregates(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        collector._state["twins"] = {
            "t1": {"layer_counts": {"l0": 10, "l1": 5, "l2": 2, "l3": 1}},
            "t2": {"layer_counts": {"l0": 20, "l1": 8, "l2": 3, "l3": 1}},
        }
        collector._update_swarm_aggregates()
        assert collector._state["swarm"]["total_twins"] == 2
        assert collector._state["swarm"]["total_l0_traces"] == 30
        assert collector._state["swarm"]["total_l1_atoms"] == 13
        assert collector._state["swarm"]["total_l2_scenarios"] == 5
        assert collector._state["swarm"]["total_l3_personas"] == 2

    def test_collect_vm_stats(self):
        collector = DashboardDataCollector("/tmp/test_state.json")
        vm_cluster = MagicMock()
        vm_cluster.get_swarm_stats.return_value = {
            "total_twins": 3,
            "active": 1,
            "hibernated": 2,
            "destroyed": 0,
            "total_thinks": 10,
            "total_hibernates": 5,
            "total_checkpoints": 4,
            "total_compute_time_ms": 1500.0,
            "twins": [
                {"twin_id": "vm-1", "name": "Twin A", "state": "active", "thinks": 4, "hibernates": 2, "checkpoints": 2, "compute_ms": 800.0},
                {"twin_id": "vm-2", "name": "Twin B", "state": "hibernated", "thinks": 3, "hibernates": 1, "checkpoints": 1, "compute_ms": 400.0},
                {"twin_id": "vm-3", "name": "Twin C", "state": "hibernated", "thinks": 3, "hibernates": 2, "checkpoints": 1, "compute_ms": 300.0},
            ],
        }
        collector.collect_vm_stats(vm_cluster)
        vm_state = collector._state["vm_cluster"]
        assert vm_state["total_twins"] == 3
        assert vm_state["active"] == 1
        assert vm_state["hibernated"] == 2
        assert vm_state["total_thinks"] == 10
        assert vm_state["total_compute_time_ms"] == 1500.0
        assert len(vm_state["twins"]) == 3
        assert vm_state["twins"][0]["twin_id"] == "vm-1"
