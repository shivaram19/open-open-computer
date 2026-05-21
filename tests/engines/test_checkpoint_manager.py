# tests/engines/test_checkpoint_manager.py
"""Tests for CheckpointManager."""

import pytest
from engines.checkpoint_manager import CheckpointManager, CheckpointInfo
from engines.compute_substrate import MockVMSubstrate


class TestCheckpointManager:
    def test_checkpoint_and_list(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()
        sub.write_file(env, "/data.txt", "v1")

        cp_id = mgr.checkpoint(env, name="test-checkpoint")
        assert cp_id is not None

        cps = mgr.list_checkpoints(env.env_id)
        assert len(cps) == 1
        assert cps[0].name == "test-checkpoint"

    def test_restore(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()
        sub.write_file(env, "/data.txt", "v1")

        cp_id = mgr.checkpoint(env)
        sub.write_file(env, "/data.txt", "v2")

        assert mgr.restore(env, cp_id) is True
        assert sub.read_file(env, "/data.txt") == "v1"

    def test_restore_missing_checkpoint(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()
        assert mgr.restore(env, "nonexistent") is False

    def test_fork(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()
        sub.write_file(env, "/data.txt", "original")

        cp_id = mgr.checkpoint(env)
        new_env = mgr.fork(cp_id, env_id="forked-001")

        assert new_env is not None
        assert new_env.env_id == "forked-001"
        assert sub.read_file(new_env, "/data.txt") == "original"
        assert new_env.metadata.get("forked_from") == cp_id

    def test_fork_missing_checkpoint(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        result = mgr.fork("nonexistent")
        assert result is None

    def test_checkpoint_before_action(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()
        cp_id = mgr.checkpoint_before_action(env, "consensus", {"round": 3})

        info = mgr.get_checkpoint(cp_id)
        assert info is not None
        assert "before-consensus" in info.name
        assert info.metadata["action"] == "consensus"

    def test_delete_checkpoint(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()
        cp_id = mgr.checkpoint(env)

        assert mgr.delete(cp_id) is True
        assert mgr.get_checkpoint(cp_id) is None
        assert mgr.delete("nonexistent") is False

    def test_multiple_checkpoints(self):
        sub = MockVMSubstrate()
        mgr = CheckpointManager(sub)
        env = sub.create()

        cp1 = mgr.checkpoint(env, name="cp1")
        sub.write_file(env, "/step.txt", "1")
        cp2 = mgr.checkpoint(env, name="cp2")
        sub.write_file(env, "/step.txt", "2")
        cp3 = mgr.checkpoint(env, name="cp3")

        cps = mgr.list_checkpoints(env.env_id)
        assert len(cps) == 3

        # Restore to middle checkpoint
        mgr.restore(env, cp2)
        assert sub.read_file(env, "/step.txt") == "1"
