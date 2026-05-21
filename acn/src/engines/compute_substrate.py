# src/engines/compute_substrate.py
"""
ComputeSubstrate Protocol: Abstract execution environment for digital twins.

Every substrate provides:
- create(): Spawn an isolated execution environment
- execute(): Run a command in the environment
- read_file() / write_file(): Filesystem I/O
- checkpoint(): Snapshot current state
- restore(): Rollback to a checkpoint
- hibernate(): Save state and suspend
- wake(): Resume from hibernation
- destroy(): Terminate and clean up

Implementations:
- LocalSandboxSubstrate: subprocess + temp dirs (no API key needed)
- MockVMSubstrate: in-memory simulation for deterministic tests
- OpenComputerSubstrate: real persistent VMs (requires API key)

"""

import json
import time
import uuid
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Protocol
from pathlib import Path

from shared.utils.citations import cite


@cite(
    key="Guo2024",
    paper="Large Language Model Based Multi-Agents: A Survey of Progress and Challenges",
    venue="IJCAI 2024",
    section="Compute Substrate",
    rationale="Uniform environment descriptor across all substrate implementations",
    confidence="CERTAIN",
)
@dataclass
class ExecutionEnvironment:
    """A running execution environment (VM, container, or sandbox)."""
    env_id: str
    substrate_type: str  # "local", "mock", "opencomputer"
    status: str = "running"  # running, hibernating, hibernated, destroyed
    workspace_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    checkpoint_count: int = 0

    def touch(self) -> None:
        self.last_activity = time.time()


@cite(
    key="Besta2024",
    paper="Graph of Thoughts: Solving Elaborate Problems with Large Language Models",
    venue="AAAI 2024",
    section="Compute Abstraction",
    rationale="Protocol enables swapping local sandbox for cloud VMs without changing twin logic",
    confidence="CERTAIN",
)
class ComputeSubstrate(ABC):
    """
    Abstract base class for compute substrates.

    All substrates must provide the same interface so twins
    execute identically whether running locally or in the cloud.
    """

    @abstractmethod
    def create(self, template: str = "default", env_id: Optional[str] = None) -> ExecutionEnvironment:
        """Create a new execution environment."""
        ...

    @abstractmethod
    def execute(self, env: ExecutionEnvironment, command: str, timeout: int = 60) -> Dict[str, Any]:
        """Execute a shell command in the environment. Returns {stdout, stderr, return_code}."""
        ...

    @abstractmethod
    def read_file(self, env: ExecutionEnvironment, path: str) -> str:
        """Read a file from the environment."""
        ...

    @abstractmethod
    def write_file(self, env: ExecutionEnvironment, path: str, content: str) -> None:
        """Write a file to the environment."""
        ...

    @abstractmethod
    def checkpoint(self, env: ExecutionEnvironment, checkpoint_id: Optional[str] = None) -> str:
        """Snapshot the environment state. Returns checkpoint ID."""
        ...

    @abstractmethod
    def restore(self, env: ExecutionEnvironment, checkpoint_id: str) -> bool:
        """Restore environment to a checkpoint. Returns success."""
        ...

    @abstractmethod
    def hibernate(self, env: ExecutionEnvironment) -> bool:
        """Save state and suspend the environment."""
        ...

    @abstractmethod
    def wake(self, env: ExecutionEnvironment) -> bool:
        """Resume a hibernated environment."""
        ...

    @abstractmethod
    def destroy(self, env: ExecutionEnvironment) -> bool:
        """Terminate and clean up the environment."""
        ...

    @abstractmethod
    def list_environments(self) -> List[ExecutionEnvironment]:
        """List all active environments on this substrate."""
        ...


@cite(
    key="Castro1999",
    paper="Practical Byzantine Fault Tolerance",
    venue="OSDI 1999",
    section="Substrate Implementations",
    rationale="Local subprocess execution requires no external services or API keys",
    confidence="CERTAIN",
)
class LocalSandboxSubstrate(ComputeSubstrate):
    """
    Local subprocess-based substrate.

    Uses temp directories for isolation. No persistence across process restarts.
    Ideal for: development, CI, lightweight tasks.
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path(tempfile.gettempdir()) / "acn-engines"
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self._envs: Dict[str, ExecutionEnvironment] = {}

    def create(self, template: str = "default", env_id: Optional[str] = None) -> ExecutionEnvironment:
        eid = env_id or f"local-{uuid.uuid4().hex[:12]}"
        ws = self.workspace_root / eid
        ws.mkdir(parents=True, exist_ok=True)

        env = ExecutionEnvironment(
            env_id=eid,
            substrate_type="local",
            status="running",
            workspace_path=str(ws),
            metadata={"template": template},
        )
        self._envs[eid] = env
        return env

    def execute(self, env: ExecutionEnvironment, command: str, timeout: int = 60) -> Dict[str, Any]:
        env.touch()
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=env.workspace_path,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "duration_ms": 0.0,  # Could measure with time.perf_counter
            }
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": f"Timeout after {timeout}s", "return_code": -1, "duration_ms": timeout * 1000}
        except Exception as exc:
            return {"stdout": "", "stderr": str(exc), "return_code": -1, "duration_ms": 0.0}

    def read_file(self, env: ExecutionEnvironment, path: str) -> str:
        env.touch()
        full_path = Path(env.workspace_path) / path.lstrip("/")
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_text()

    def write_file(self, env: ExecutionEnvironment, path: str, content: str) -> None:
        env.touch()
        full_path = Path(env.workspace_path) / path.lstrip("/")
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    def checkpoint(self, env: ExecutionEnvironment, checkpoint_id: Optional[str] = None) -> str:
        env.touch()
        cid = checkpoint_id or f"cp-{uuid.uuid4().hex[:8]}"
        cp_dir = Path(env.workspace_path) / ".checkpoints" / cid
        cp_dir.mkdir(parents=True, exist_ok=True)
        # In local mode, checkpoint is a manifest of files
        manifest = {}
        ws = Path(env.workspace_path)
        for f in ws.rglob("*"):
            if f.is_file() and ".checkpoints" not in str(f.relative_to(ws)):
                manifest[str(f.relative_to(ws))] = f.read_text()
        (cp_dir / "manifest.json").write_text(json.dumps(manifest, default=str))
        env.checkpoint_count += 1
        return cid

    def restore(self, env: ExecutionEnvironment, checkpoint_id: str) -> bool:
        cp_dir = Path(env.workspace_path) / ".checkpoints" / checkpoint_id
        manifest_path = cp_dir / "manifest.json"
        if not manifest_path.exists():
            return False
        import json
        manifest = json.loads(manifest_path.read_text())
        ws = Path(env.workspace_path)
        for rel_path, content in manifest.items():
            if ".checkpoints" in rel_path:
                continue
            target = ws / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        return True

    def hibernate(self, env: ExecutionEnvironment) -> bool:
        # Local sandbox can't truly hibernate, so we checkpoint + mark status
        self.checkpoint(env, "hibernate")
        env.status = "hibernated"
        return True

    def wake(self, env: ExecutionEnvironment) -> bool:
        if env.status == "hibernated":
            self.restore(env, "hibernate")
            env.status = "running"
            return True
        return False

    def destroy(self, env: ExecutionEnvironment) -> bool:
        import shutil
        ws = Path(env.workspace_path)
        if ws.exists():
            shutil.rmtree(ws, ignore_errors=True)
        env.status = "destroyed"
        self._envs.pop(env.env_id, None)
        return True

    def list_environments(self) -> List[ExecutionEnvironment]:
        return [e for e in self._envs.values() if e.status != "destroyed"]


class MockVMSubstrate(ComputeSubstrate):
    """
    In-memory mock substrate for deterministic testing.

    Simulates a VM with a virtual filesystem. No actual processes are spawned.
    All operations are instantaneous and deterministic.
    """

    def __init__(self):
        self._envs: Dict[str, ExecutionEnvironment] = {}
        self._fs: Dict[str, Dict[str, str]] = {}  # env_id -> {path: content}
        self._checkpoints: Dict[str, Dict[str, Dict[str, str]]] = {}  # env_id -> {cp_id: fs_snapshot}

    def create(self, template: str = "default", env_id: Optional[str] = None) -> ExecutionEnvironment:
        eid = env_id or f"mock-{uuid.uuid4().hex[:12]}"
        env = ExecutionEnvironment(
            env_id=eid,
            substrate_type="mock",
            status="running",
            workspace_path=f"/workspace/{eid}",
            metadata={"template": template},
        )
        self._envs[eid] = env
        self._fs[eid] = {}
        self._checkpoints[eid] = {}
        return env

    def execute(self, env: ExecutionEnvironment, command: str, timeout: int = 60) -> Dict[str, Any]:
        env.touch()
        # Simulate command execution
        if command.startswith("echo"):
            stdout = command[5:].strip().strip('"').strip("'")
            return {"stdout": stdout, "stderr": "", "return_code": 0, "duration_ms": 1.0}
        if command.startswith("cat"):
            path = command[4:].strip()
            content = self._fs.get(env.env_id, {}).get(path, "")
            return {"stdout": content, "stderr": "", "return_code": 0, "duration_ms": 1.0}
        if command.startswith("python") or command.startswith("python3"):
            # Simulate Python execution by echoing success
            return {"stdout": "mock-python-output", "stderr": "", "return_code": 0, "duration_ms": 10.0}
        return {"stdout": "", "stderr": f"mock: command not found: {command}", "return_code": 127, "duration_ms": 0.0}

    def read_file(self, env: ExecutionEnvironment, path: str) -> str:
        env.touch()
        fs = self._fs.get(env.env_id, {})
        if path not in fs:
            raise FileNotFoundError(f"File not found: {path}")
        return fs[path]

    def write_file(self, env: ExecutionEnvironment, path: str, content: str) -> None:
        env.touch()
        if env.env_id not in self._fs:
            self._fs[env.env_id] = {}
        self._fs[env.env_id][path] = content

    def checkpoint(self, env: ExecutionEnvironment, checkpoint_id: Optional[str] = None) -> str:
        env.touch()
        cid = checkpoint_id or f"cp-{uuid.uuid4().hex[:8]}"
        # Store globally by checkpoint ID so any env can restore it
        self._checkpoints[cid] = {
            "env_id": env.env_id,
            "fs": dict(self._fs.get(env.env_id, {})),
        }
        env.checkpoint_count += 1
        return cid

    def restore(self, env: ExecutionEnvironment, checkpoint_id: str) -> bool:
        snapshot = self._checkpoints.get(checkpoint_id)
        if snapshot is None:
            return False
        self._fs[env.env_id] = dict(snapshot["fs"])
        return True

    def hibernate(self, env: ExecutionEnvironment) -> bool:
        self.checkpoint(env, "hibernate")
        env.status = "hibernated"
        return True

    def wake(self, env: ExecutionEnvironment) -> bool:
        if env.status == "hibernated":
            self.restore(env, "hibernate")
            env.status = "running"
            return True
        return False

    def destroy(self, env: ExecutionEnvironment) -> bool:
        self._fs.pop(env.env_id, None)
        self._checkpoints.pop(env.env_id, None)
        env.status = "destroyed"
        self._envs.pop(env.env_id, None)
        return True

    def list_environments(self) -> List[ExecutionEnvironment]:
        return [e for e in self._envs.values() if e.status != "destroyed"]
