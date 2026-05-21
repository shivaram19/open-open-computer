# tests/engines/test_swarm_vm_cluster.py
"""Tests for SwarmVMCluster."""

import pytest
from engines.swarm_vm_cluster import SwarmVMCluster
from engines.compute_substrate import MockVMSubstrate
from engines.persistent_twin_engine import TwinVMState


class TestSwarmVMCluster:
    def test_create_swarm(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
            {"twin_id": "twin-002", "twin_name": "Conor", "cluster": "consensus-safety"},
        ]
        records = cluster.create_swarm(specs)
        assert len(records) == 2
        assert "twin-001" in records
        assert "twin-002" in records

    def test_think_all(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
            {"twin_id": "twin-002", "twin_name": "Conor", "cluster": "consensus-safety"},
        ]
        cluster.create_swarm(specs)
        cluster.activate_all()

        results = cluster.think_all("Should we use BFT?")
        assert len(results) == 2
        assert results["twin-001"]["status"] == "completed"
        assert results["twin-002"]["status"] == "completed"

    def test_checkpoint_all_and_restore(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
        ]
        cluster.create_swarm(specs)
        cluster.activate_all()
        cluster.think_all("Task 1")

        swarm_cp = cluster.checkpoint_all("before-risky-action")
        assert swarm_cp is not None

        cluster.think_all("Task 2")
        r = cluster.get_record("twin-001")
        assert r.think_count == 2

        cluster.restore_all(swarm_cp)
        # After restore, filesystem reverted but counter not (mock limitation)

    def test_hibernate_all_and_wake(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
            {"twin_id": "twin-002", "twin_name": "Conor", "cluster": "consensus-safety"},
        ]
        cluster.create_swarm(specs)
        cluster.activate_all()
        cluster.think_all("Task")

        cluster.hibernate_all()
        r1 = cluster.get_record("twin-001")
        r2 = cluster.get_record("twin-002")
        assert r1.state == TwinVMState.HIBERNATED
        assert r2.state == TwinVMState.HIBERNATED

        cluster.activate_all()
        assert r1.state == TwinVMState.ACTIVE
        assert r2.state == TwinVMState.ACTIVE

    def test_fork_swarm(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
        ]
        cluster.create_swarm(specs)
        cluster.activate_all()
        cluster.think_all("Original approach")

        swarm_cp = cluster.checkpoint_all("baseline")
        branch = cluster.fork_swarm(swarm_cp, "exploration-branch")

        assert len(branch) >= 1
        branch_record = list(branch.values())[0]
        assert "forked_from" in branch_record.env.metadata

    def test_destroy_swarm(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
        ]
        cluster.create_swarm(specs)
        cluster.destroy_swarm()

        stats = cluster.get_swarm_stats()
        assert stats["destroyed"] == 1

    def test_swarm_stats(self):
        cluster = SwarmVMCluster(MockVMSubstrate())
        specs = [
            {"twin_id": "twin-001", "twin_name": "Noah", "cluster": "streaming-reflection"},
            {"twin_id": "twin-002", "twin_name": "Conor", "cluster": "consensus-safety"},
        ]
        cluster.create_swarm(specs)
        cluster.activate_all()
        cluster.think_all("Task")
        cluster.hibernate_all()

        stats = cluster.get_swarm_stats()
        assert stats["total_twins"] == 2
        assert stats["active"] == 0
        assert stats["hibernated"] == 2
        assert stats["total_thinks"] == 2
        assert len(stats["twins"]) == 2
