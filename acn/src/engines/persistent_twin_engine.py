# src/engines/persistent_twin_engine.py
"""
PersistentTwinEngine: Run digital twins in isolated, persistent VMs.

Core principles from OpenComputer:
- Each twin gets its own VM (isolation)
- Twins hibernate between deliberations (cost savings, persistence)
- Checkpoints before risky actions (safe exploration)
- L0-L3 memory survives hibernation cycles

Lifecycle:
  create → activate → think → [hibernate → wake → think]* → destroy

The engine handles:
1. VM provisioning per twin
2. Twin cognitive loop execution inside VM
3. Hibernation/wake with memory persistence
4. Checkpoint-before-risky-action pattern
5. Idle timeout auto-hibernation

[CITATION: OPENCOMPUTER-CORE-ENGINE]
[CITATION: LAYERED-MEMORY]
"""

import time
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from shared.utils.citations import cite
from engines.compute_substrate import ComputeSubstrate, ExecutionEnvironment
from engines.checkpoint_manager import CheckpointManager


@cite(
    key="TWIN-VM-STATE",
    paper="ACN Core Engine: Twin VM State Machine",
    venue="ACN Architecture Document",
    section="Persistent Twin Engine",
    rationale="Explicit state machine enables hibernation, checkpointing, and safe recovery",
    confidence="CERTAIN",
)
class TwinVMState(Enum):
    """Lifecycle states of a twin's VM."""
    CREATED = "created"
    ACTIVE = "active"           # Running, processing
    HIBERNATED = "hibernated"   # Memory saved, VM stopped
    CHECKPOINTED = "checkpointed"  # Has active checkpoint
    DESTROYED = "destroyed"


@dataclass
class TwinVMRecord:
    """Running record of a twin VM session."""
    twin_id: str
    twin_name: str
    env: ExecutionEnvironment
    state: TwinVMState = TwinVMState.CREATED
    activation_count: int = 0
    think_count: int = 0
    hibernate_count: int = 0
    checkpoint_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_think_at: Optional[float] = None
    idle_timeout_seconds: float = 0.0  # 0 = never auto-hibernate
    total_compute_time_ms: float = 0.0


@cite(
    key="PERSISTENT-TWIN-ENGINE",
    paper="ACN Core Engine: Persistent Twin Execution",
    venue="ACN Architecture Document",
    section="Core Engine",
    rationale="Persistent VM substrate enables twins to survive process restarts and scale horizontally",
    confidence="HIGH",
)
class PersistentTwinEngine:
    """
    Orchestrate twin execution in persistent VMs.

    Usage:
        engine = PersistentTwinEngine(MockVMSubstrate())
        record = engine.create_twin_vm("noah-shinn-001", "Noah Shinn")
        engine.activate(record)
        result = engine.think(record, "Should we use BFT?")
        engine.hibernate(record)  # VM stops, memory saved
        engine.wake(record)       # VM resumes
        result2 = engine.think(record, "What about PoS?")
        engine.destroy(record)
    """

    def __init__(
        self,
        substrate: ComputeSubstrate,
        idle_timeout_seconds: float = 300.0,
        checkpoint_before_think: bool = False,
    ):
        self.substrate = substrate
        self.checkpoint_manager = CheckpointManager(substrate)
        self.idle_timeout_seconds = idle_timeout_seconds
        self.checkpoint_before_think = checkpoint_before_think
        self._records: Dict[str, TwinVMRecord] = {}

    def create_twin_vm(
        self,
        twin_id: str,
        twin_name: str,
        template: str = "default",
        idle_timeout: Optional[float] = None,
    ) -> TwinVMRecord:
        """Provision a new VM for a twin."""
        env = self.substrate.create(template=template, env_id=f"twin-vm-{twin_id}")

        # Write twin identity into VM
        identity = {
            "twin_id": twin_id,
            "twin_name": twin_name,
            "created_by": "acn-persistent-twin-engine",
            "created_at": time.time(),
        }
        self.substrate.write_file(env, "/workspace/.acn-twin-identity.json", json.dumps(identity))

        record = TwinVMRecord(
            twin_id=twin_id,
            twin_name=twin_name,
            env=env,
            state=TwinVMState.CREATED,
            idle_timeout_seconds=idle_timeout if idle_timeout is not None else self.idle_timeout_seconds,
        )
        self._records[twin_id] = record
        return record

    def activate(self, record: TwinVMRecord) -> None:
        """Activate a twin VM (wake if hibernated, or mark active)."""
        if record.state == TwinVMState.HIBERNATED:
            self.wake(record)
        record.state = TwinVMState.ACTIVE
        record.activation_count += 1
        record.env.touch()

    def think(
        self,
        record: TwinVMRecord,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a think cycle inside the twin's VM.

        In mock/local mode, this simulates twin reasoning.
        In OpenComputer mode, this would serialize the twin and
        run it inside the VM via agent loop.
        """
        self._ensure_active(record)

        # Optional: checkpoint before risky think
        if self.checkpoint_before_think:
            cp_id = self.checkpoint_manager.checkpoint_before_action(
                record.env, action_name="think", action_metadata={"task": task}
            )
            record.checkpoint_ids.append(cp_id)

        start = time.time()

        # Increment think count BEFORE simulation so result has correct number
        record.think_count += 1

        # Simulate twin reasoning inside VM
        result = self._simulate_think_in_vm(record, task, context)

        duration = (time.time() - start) * 1000
        record.total_compute_time_ms += duration
        record.last_think_at = time.time()
        record.env.touch()

        return result

    def _simulate_think_in_vm(
        self,
        record: TwinVMRecord,
        task: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Simulate a think cycle. In real mode, this runs the twin inside the VM."""
        # Write task to VM filesystem (as if twin received it)
        task_record = {
            "task": task,
            "context": context or {},
            "timestamp": time.time(),
            "twin_id": record.twin_id,
        }
        self.substrate.write_file(
            record.env,
            f"/workspace/thinks/{record.think_count:04d}-task.json",
            json.dumps(task_record, default=str),
        )

        # Simulate execution
        exec_result = self.substrate.execute(
            record.env,
            f"echo 'Twin {record.twin_name} thinking about: {task[:50]}...'",
            timeout=30,
        )

        return {
            "twin_id": record.twin_id,
            "task": task,
            "status": "completed",
            "vm_stdout": exec_result.get("stdout", ""),
            "vm_stderr": exec_result.get("stderr", ""),
            "duration_ms": exec_result.get("duration_ms", 0),
            "think_number": record.think_count,
        }

    def hibernate(self, record: TwinVMRecord) -> bool:
        """
        Hibernate the twin VM.

        Saves L0-L3 memory state and stops the VM. No compute cost while hibernated.
        """
        if record.state in (TwinVMState.HIBERNATED, TwinVMState.DESTROYED):
            return False

        # Serialize twin memory state to VM filesystem before hibernation
        memory_manifest = {
            "twin_id": record.twin_id,
            "hibernated_at": time.time(),
            "think_count": record.think_count,
            "activation_count": record.activation_count,
            "total_compute_time_ms": record.total_compute_time_ms,
        }
        self.substrate.write_file(
            record.env,
            "/workspace/.acn-memory-state.json",
            json.dumps(memory_manifest),
        )

        success = self.substrate.hibernate(record.env)
        if success:
            record.state = TwinVMState.HIBERNATED
            record.hibernate_count += 1
        return success

    def wake(self, record: TwinVMRecord) -> bool:
        """Wake a hibernated twin VM."""
        if record.state != TwinVMState.HIBERNATED:
            return False

        success = self.substrate.wake(record.env)
        if success:
            record.state = TwinVMState.ACTIVE
            record.env.touch()

            # Restore memory state if present
            try:
                mem_json = self.substrate.read_file(record.env, "/workspace/.acn-memory-state.json")
                mem_state = json.loads(mem_json)
                record.think_count = mem_state.get("think_count", record.think_count)
                record.activation_count = mem_state.get("activation_count", record.activation_count)
            except Exception:
                pass
        return success

    def auto_hibernate_if_idle(self, record: TwinVMRecord) -> bool:
        """
        Check idle timeout and hibernate if expired.

        Returns True if hibernation occurred.
        """
        if record.idle_timeout_seconds <= 0:
            return False
        if record.state != TwinVMState.ACTIVE:
            return False

        idle = time.time() - record.env.last_activity
        if idle >= record.idle_timeout_seconds:
            return self.hibernate(record)
        return False

    def checkpoint(self, record: TwinVMRecord, name: str = "") -> str:
        """Create a named checkpoint of the twin VM."""
        cp_id = self.checkpoint_manager.checkpoint(record.env, name=name)
        record.checkpoint_ids.append(cp_id)
        record.state = TwinVMState.CHECKPOINTED
        return cp_id

    def restore(self, record: TwinVMRecord, checkpoint_id: str) -> bool:
        """Restore twin VM to a checkpoint."""
        success = self.checkpoint_manager.restore(record.env, checkpoint_id)
        if success:
            record.state = TwinVMState.ACTIVE
        return success

    def fork(self, record: TwinVMRecord, checkpoint_id: str, new_twin_id: str) -> Optional[TwinVMRecord]:
        """Fork a new twin VM from a checkpoint."""
        new_env = self.checkpoint_manager.fork(checkpoint_id, env_id=f"twin-vm-{new_twin_id}")
        if new_env is None:
            return None

        new_record = TwinVMRecord(
            twin_id=new_twin_id,
            twin_name=f"{record.twin_name}-fork",
            env=new_env,
            state=TwinVMState.CREATED,
        )
        self._records[new_twin_id] = new_record
        return new_record

    def destroy(self, record: TwinVMRecord) -> bool:
        """Terminate and clean up a twin VM."""
        success = self.substrate.destroy(record.env)
        if success:
            record.state = TwinVMState.DESTROYED
            # Keep record in _records for stats, but mark destroyed
        return success

    def get_record(self, twin_id: str) -> Optional[TwinVMRecord]:
        return self._records.get(twin_id)

    def list_records(self) -> List[TwinVMRecord]:
        return list(self._records.values())

    def get_stats(self) -> Dict[str, Any]:
        """Engine-wide statistics."""
        records = self.list_records()
        return {
            "total_twins": len(records),
            "active": sum(1 for r in records if r.state == TwinVMState.ACTIVE),
            "hibernated": sum(1 for r in records if r.state == TwinVMState.HIBERNATED),
            "destroyed": sum(1 for r in records if r.state == TwinVMState.DESTROYED),
            "total_thinks": sum(r.think_count for r in records),
            "total_hibernates": sum(r.hibernate_count for r in records),
            "total_checkpoints": sum(len(r.checkpoint_ids) for r in records),
            "total_compute_time_ms": sum(r.total_compute_time_ms for r in records),
        }

    def _ensure_active(self, record: TwinVMRecord) -> None:
        """Ensure VM is active before operation."""
        if record.state == TwinVMState.HIBERNATED:
            self.wake(record)
        if record.state == TwinVMState.DESTROYED:
            raise RuntimeError(f"Cannot operate on destroyed VM: {record.twin_id}")
