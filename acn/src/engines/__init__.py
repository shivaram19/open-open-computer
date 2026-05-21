# acn/src/engines/__init__.py
"""
ACN Core Engine: Compute substrate abstraction for digital twins.

Provides persistent, checkpointable execution environments for twins:
- LocalSandboxSubstrate: subprocess-based (existing SandboxAgent)
- MockVMSubstrate: deterministic testing substrate
- OpenComputerSubstrate: persistent cloud VMs (requires API key)

[CITATION: OPENCOMPUTER-CORE-ENGINE]
"""

from engines.compute_substrate import (
    ComputeSubstrate,
    LocalSandboxSubstrate,
    MockVMSubstrate,
    ExecutionEnvironment,
)
from engines.opencomputer_client import OpenComputerSubstrate
from engines.persistent_twin_engine import PersistentTwinEngine
from engines.checkpoint_manager import CheckpointManager

__all__ = [
    "ComputeSubstrate",
    "LocalSandboxSubstrate",
    "MockVMSubstrate",
    "OpenComputerSubstrate",
    "PersistentTwinEngine",
    "CheckpointManager",
    "ExecutionEnvironment",
]
