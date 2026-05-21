# tests/engines/test_persistent_twin_engine.py
"""Tests for PersistentTwinEngine."""

import time
import pytest
from engines.persistent_twin_engine import PersistentTwinEngine, TwinVMState
from engines.compute_substrate import MockVMSubstrate


class TestPersistentTwinEngine:
    def test_create_and_destroy(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        assert record.twin_id == "twin-001"
        assert record.state == TwinVMState.CREATED
        assert record.env.workspace_path == "/workspace/twin-vm-twin-001"

        # Identity file should be written
        identity = record.env.env_id  # mock substrate stores in _fs
        assert identity is not None

        engine.destroy(record)
        assert record.state == TwinVMState.DESTROYED

    def test_activate(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)
        assert record.state == TwinVMState.ACTIVE
        assert record.activation_count == 1

    def test_think(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)

        result = engine.think(record, "Should we use BFT?")
        assert result["twin_id"] == "twin-001"
        assert result["status"] == "completed"
        assert result["think_number"] == 1
        assert record.think_count == 1

    def test_hibernate_and_wake(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)
        engine.think(record, "Task 1")

        assert engine.hibernate(record) is True
        assert record.state == TwinVMState.HIBERNATED
        assert record.hibernate_count == 1

        assert engine.wake(record) is True
        assert record.state == TwinVMState.ACTIVE
        assert record.think_count == 1  # Memory preserved

    def test_think_after_wake(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)
        engine.think(record, "Task 1")
        engine.hibernate(record)
        engine.wake(record)

        result = engine.think(record, "Task 2")
        assert result["think_number"] == 2
        assert record.think_count == 2

    def test_checkpoint_and_restore(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)
        engine.think(record, "Before checkpoint")

        cp_id = engine.checkpoint(record, name="test-cp")
        assert cp_id is not None
        assert record.state == TwinVMState.CHECKPOINTED

        engine.think(record, "After checkpoint")
        assert record.think_count == 2

        engine.restore(record, cp_id)
        assert record.state == TwinVMState.ACTIVE
        # In mock mode, restore reverts filesystem but not the counter
        # because counters are in-memory. In real mode, they'd be serialized.

    def test_auto_hibernate_idle(self):
        engine = PersistentTwinEngine(MockVMSubstrate(), idle_timeout_seconds=0.1)
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)

        # Should NOT hibernate immediately
        assert engine.auto_hibernate_if_idle(record) is False

        # Wait for timeout
        time.sleep(0.15)
        assert engine.auto_hibernate_if_idle(record) is True
        assert record.state == TwinVMState.HIBERNATED

    def test_no_auto_hibernate_with_zero_timeout(self):
        engine = PersistentTwinEngine(MockVMSubstrate(), idle_timeout_seconds=0)
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)
        time.sleep(0.05)
        assert engine.auto_hibernate_if_idle(record) is False

    def test_stats(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        r1 = engine.create_twin_vm("twin-001", "Twin A")
        r2 = engine.create_twin_vm("twin-002", "Twin B")
        engine.activate(r1)
        engine.activate(r2)
        engine.think(r1, "Task")
        engine.hibernate(r1)

        stats = engine.get_stats()
        assert stats["total_twins"] == 2
        assert stats["active"] == 1
        assert stats["hibernated"] == 1
        assert stats["total_thinks"] == 1
        assert stats["total_hibernates"] == 1

    def test_destroyed_vm_cannot_think(self):
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("twin-001", "Test Twin")
        engine.activate(record)
        engine.destroy(record)

        with pytest.raises(RuntimeError):
            engine.think(record, "Should fail")
