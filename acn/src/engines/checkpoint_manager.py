# src/engines/checkpoint_manager.py
"""
CheckpointManager: Named snapshots, restore, and fork for twin VMs.

Inspired by OpenComputer's checkpoint system:
- checkpoint(): Named snapshot of a running sandbox
- restore(): Revert sandbox in-place (changes since checkpoint are lost)
- fork(): Create a new sandbox from a checkpoint (git branches for VMs)

Checkpoints capture filesystem + installed state. In local/mock mode,
we serialize the filesystem to disk/memory.

[CITATION: OPENCOMPUTER-CORE-ENGINE]
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

from shared.utils.citations import cite
from engines.compute_substrate import ComputeSubstrate, ExecutionEnvironment


@cite(
    key="CHECKPOINT-INFO",
    paper="ACN Core Engine: Checkpoint Metadata",
    venue="ACN Architecture Document",
    section="Checkpoint System",
    rationale="Checkpoint metadata tracks snapshot provenance for rollback and fork operations",
    confidence="CERTAIN",
)
@dataclass
class CheckpointInfo:
    """Metadata for a single checkpoint."""
    checkpoint_id: str
    env_id: str
    name: str
    status: str = "ready"  # processing, ready, failed
    size_bytes: int = 0
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "env_id": self.env_id,
            "name": self.name,
            "status": self.status,
            "size_bytes": self.size_bytes,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@cite(
    key="CHECKPOINT-MANAGER",
    paper="ACN Core Engine: Checkpoint Management",
    venue="ACN Architecture Document",
    section="Checkpoint System",
    rationale="Checkpoint-before-risky-action enables safe exploration and rollback in multi-agent systems",
    confidence="HIGH",
)
class CheckpointManager:
    """
    Manages checkpoints across all substrates.

    Usage:
        manager = CheckpointManager(substrate)
        cp_id = manager.checkpoint(env, name="before-consensus")
        # ... risky deliberation ...
        manager.restore(env, cp_id)  # Rollback
        # OR
        fork_env = manager.fork(cp_id, env_id="twin-branch-2")
    """

    def __init__(self, substrate: ComputeSubstrate):
        self.substrate = substrate
        self._checkpoints: Dict[str, CheckpointInfo] = {}

    def checkpoint(
        self,
        env: ExecutionEnvironment,
        name: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a named checkpoint of an environment.

        Returns checkpoint ID.
        """
        cp_id = self.substrate.checkpoint(env)
        info = CheckpointInfo(
            checkpoint_id=cp_id,
            env_id=env.env_id,
            name=name or f"checkpoint-{cp_id}",
            metadata=metadata or {},
        )
        self._checkpoints[cp_id] = info
        return cp_id

    def restore(self, env: ExecutionEnvironment, checkpoint_id: str) -> bool:
        """Restore environment to a checkpoint. All changes since are lost."""
        if checkpoint_id not in self._checkpoints:
            return False
        success = self.substrate.restore(env, checkpoint_id)
        if success:
            env.status = "running"
        return success

    def fork(
        self,
        checkpoint_id: str,
        env_id: Optional[str] = None,
        template: str = "default",
    ) -> Optional[ExecutionEnvironment]:
        """
        Create a new environment from a checkpoint.

        Like git branch for VMs. The original checkpoint is untouched.
        """
        if checkpoint_id not in self._checkpoints:
            return None

        # Create new environment
        new_env = self.substrate.create(template=template, env_id=env_id)

        # Restore checkpoint into new environment
        success = self.substrate.restore(new_env, checkpoint_id)
        if not success:
            self.substrate.destroy(new_env)
            return None

        new_env.metadata["forked_from"] = checkpoint_id
        new_env.metadata["parent_env_id"] = self._checkpoints[checkpoint_id].env_id
        return new_env

    def delete(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
            return True
        return False

    def list_checkpoints(self, env_id: Optional[str] = None) -> List[CheckpointInfo]:
        """List checkpoints, optionally filtered by environment."""
        cps = list(self._checkpoints.values())
        if env_id:
            cps = [c for c in cps if c.env_id == env_id]
        return sorted(cps, key=lambda c: c.created_at, reverse=True)

    def get_checkpoint(self, checkpoint_id: str) -> Optional[CheckpointInfo]:
        return self._checkpoints.get(checkpoint_id)

    def checkpoint_before_action(
        self,
        env: ExecutionEnvironment,
        action_name: str,
        action_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Convenience: checkpoint before a risky action with descriptive name."""
        meta = action_metadata or {}
        meta["action"] = action_name
        meta["timestamp"] = time.time()
        return self.checkpoint(env, name=f"before-{action_name}", metadata=meta)
