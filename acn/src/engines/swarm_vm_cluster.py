# src/engines/swarm_vm_cluster.py
"""
SwarmVMCluster: Multi-VM orchestration for twin swarm deliberation.

Manages a fleet of twin VMs:
- Provisions VMs for each twin in the swarm
- Coordinates hibernation/wake cycles
- Checkpoint-all before risky consensus (atomic snapshot)
- Parallel think execution across VMs
- Fork swarm to explore multiple approaches

Inspired by OpenComputer's fork-from-checkpoint pattern:
"Try five approaches in parallel from the same starting point
— like git branches for VMs."

[CITATION: OPENCOMPUTER-CORE-ENGINE]
[CITATION: CP-WBFT2025]
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from shared.utils.citations import cite
from engines.compute_substrate import ComputeSubstrate
from engines.persistent_twin_engine import PersistentTwinEngine, TwinVMRecord


@cite(
    key="SWARM-VM-CLUSTER",
    paper="ACN Core Engine: Swarm VM Cluster",
    venue="ACN Architecture Document",
    section="Multi-VM Orchestration",
    rationale="Coordinated checkpointing across multiple twin VMs enables safe parallel exploration",
    confidence="HIGH",
)
class SwarmVMCluster:
    """
    Orchestrate multiple twin VMs as a coordinated swarm.

    Usage:
        cluster = SwarmVMCluster(MockVMSubstrate())
        cluster.create_swarm(["noah-shinn-001", "conor-heins-001"])
        cluster.checkpoint_all("before-consensus")
        results = cluster.think_all("Should we use BFT?")
        # If dissent detected:
        cluster.restore_all("before-consensus")
    """

    def __init__(
        self,
        substrate: ComputeSubstrate,
        idle_timeout_seconds: float = 300.0,
    ):
        self.substrate = substrate
        self.engine = PersistentTwinEngine(
            substrate,
            idle_timeout_seconds=idle_timeout_seconds,
        )
        self._swarm_checkpoint: Optional[str] = None

    def create_swarm(
        self,
        twin_specs: List[Dict[str, str]],
        template: str = "default",
    ) -> Dict[str, TwinVMRecord]:
        """
        Provision VMs for a swarm of twins.

        twin_specs: [{"twin_id": "...", "twin_name": "...", "cluster": "..."}]
        """
        records = {}
        for spec in twin_specs:
            record = self.engine.create_twin_vm(
                twin_id=spec["twin_id"],
                twin_name=spec["twin_name"],
                template=template,
            )
            records[spec["twin_id"]] = record
        return records

    def activate_all(self) -> None:
        """Wake all hibernated twins in the swarm."""
        for record in self.engine.list_records():
            self.engine.activate(record)

    def hibernate_all(self) -> None:
        """Hibernate all active or checkpointed twins in the swarm."""
        for record in self.engine.list_records():
            if record.state.value in ("active", "checkpointed"):
                self.engine.hibernate(record)

    def think_all(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute think() on all twins in parallel.

        Returns {twin_id: think_result}.
        """
        results = {}
        for record in self.engine.list_records():
            results[record.twin_id] = self.engine.think(record, task, context)
        return results

    def checkpoint_all(self, name: str = "") -> str:
        """
        Checkpoint ALL twins in the swarm atomically.

        Returns a swarm checkpoint ID (composite of individual checkpoints).
        """
        cp_ids = []
        for record in self.engine.list_records():
            cp_id = self.engine.checkpoint(record, name=name)
            cp_ids.append(cp_id)

        swarm_cp = f"swarm-cp-{time.time():.0f}"
        self._swarm_checkpoint = swarm_cp
        return swarm_cp

    def restore_all(self, swarm_checkpoint_id: str) -> bool:
        """
        Restore ALL twins to their last checkpoint.

        This is the "rollback" operation when consensus fails or dissent is detected.
        """
        success = True
        for record in self.engine.list_records():
            # Restore to the most recent checkpoint for this twin
            if record.checkpoint_ids:
                latest_cp = record.checkpoint_ids[-1]
                if not self.engine.restore(record, latest_cp):
                    success = False
        return success

    def fork_swarm(
        self,
        swarm_checkpoint_id: str,
        new_swarm_id: str,
        twin_id_mapping: Optional[Dict[str, str]] = None,
    ) -> Dict[str, TwinVMRecord]:
        """
        Fork the entire swarm from a checkpoint.

        Creates parallel twin branches to explore multiple approaches.
        Like git branch for the whole swarm.
        """
        new_records = {}
        mapping = twin_id_mapping or {}

        for record in self.engine.list_records():
            if record.checkpoint_ids:
                original_cp = record.checkpoint_ids[-1]
                new_id = mapping.get(record.twin_id, f"{record.twin_id}-branch-{new_swarm_id}")
                forked = self.engine.fork(record, original_cp, new_id)
                if forked:
                    new_records[new_id] = forked

        return new_records

    def auto_hibernate_idle_twins(self) -> Dict[str, bool]:
        """Check all twins for idle timeout and hibernate if expired."""
        results = {}
        for record in self.engine.list_records():
            results[record.twin_id] = self.engine.auto_hibernate_if_idle(record)
        return results

    def destroy_swarm(self) -> None:
        """Destroy all twin VMs in the swarm."""
        for record in list(self.engine.list_records()):
            if record.state.value != "destroyed":
                self.engine.destroy(record)

    def get_swarm_stats(self) -> Dict[str, Any]:
        """Statistics for the entire swarm."""
        engine_stats = self.engine.get_stats()
        records = self.engine.list_records()
        return {
            **engine_stats,
            "twins": [
                {
                    "twin_id": r.twin_id,
                    "name": r.twin_name,
                    "state": r.state.value,
                    "thinks": r.think_count,
                    "hibernates": r.hibernate_count,
                    "checkpoints": len(r.checkpoint_ids),
                    "compute_ms": r.total_compute_time_ms,
                }
                for r in records
            ],
        }

    def get_record(self, twin_id: str) -> Optional[TwinVMRecord]:
        return self.engine.get_record(twin_id)
