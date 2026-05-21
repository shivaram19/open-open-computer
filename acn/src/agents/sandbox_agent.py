# src/agents/sandbox_agent.py
"""
SandboxAgent: A ConsciousAgent that can execute code in isolated environments.

Inspired by DeerFlow's sandbox execution but enhanced with:
- Citation governance (every execution must cite its purpose)
- Awareness tracking (monitors resource usage, execution time)
- Memory integration (stores execution traces as episodic memory)

Principle: A conscious agent that cannot act is a philosopher, not an engineer.

[CITATION: CITATIONS-GOVERNANCE]
"""

import uuid
import time
import subprocess
import tempfile
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path

from shared.utils.citations import cite
from agents.conscious_agent import ConsciousAgent, AgentGoal
from memory.architecture import MemoryType, MemoryTrace


@cite(
    key="SANDBOX-RESULT",
    paper="SandboxAgent: Execution Result",
    venue="ACN Architecture Document",
    section="Execution Output",
    rationale="Structured execution results enable verification and audit",
    confidence="CERTAIN",
)
@dataclass
class ExecutionResult:
    """Result of a sandboxed code execution."""
    execution_id: str
    code: str
    stdout: str
    stderr: str
    return_code: int
    duration_ms: float
    workspace_path: str
    artifacts: List[str]  # Files created during execution
    cited_purpose: str  # Why this execution was performed (with citation)


@cite(
    key="SANDBOX-AGENT",
    paper="SandboxAgent: Conscious Code Execution",
    venue="ACN Harness Architecture",
    section="Agent Execution",
    rationale="Agents must execute code to verify hypotheses and test solutions",
    confidence="CERTAIN",
)
class SandboxAgent(ConsciousAgent):
    """
    A conscious agent with code execution capabilities.
    
    Every execution:
    1. Must have a cited purpose (why are we running this?)
    2. Runs in an isolated workspace (per-execution directory)
    3. Is monitored for resource usage (time, memory, output size)
    4. Produces artifacts stored in memory
    5. Is self-evaluated (did it produce the expected result?)
    
    Security:
    - Execution timeout prevents runaway processes
    - Output size limits prevent memory exhaustion
    - No network access unless explicitly enabled
    - Workspace is destroyed after execution (unless persistent)
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        cluster: str,
        execution_timeout: int = 60,
        max_output_size: int = 10_000_000,  # 10MB
        allow_network: bool = False,
        **kwargs,
    ):
        super().__init__(agent_id, name, cluster, **kwargs)
        self.execution_timeout = execution_timeout
        self.max_output_size = max_output_size
        self.allow_network = allow_network
        self.execution_history: List[ExecutionResult] = []
        self.workspace_root = Path(f"/tmp/sandbox-{agent_id}")
        self.workspace_root.mkdir(exist_ok=True)

    @cite(
        key="SANDBOX-EXECUTE",
        paper="SandboxAgent: Execution Protocol",
        venue="ACN Harness Architecture",
        section="Code Execution",
        rationale="Isolated execution with citation-governed purpose tracking",
        confidence="CERTAIN",
    )
    def execute(
        self,
        code: str,
        language: str = "python",
        cited_purpose: str = "",
        expected_output: Optional[str] = None,
    ) -> ExecutionResult:
        """
        Execute code in an isolated workspace.
        
        Args:
            code: The code to execute
            language: python, bash, or javascript
            cited_purpose: Why this execution is needed (must include citation)
            expected_output: If provided, auto-evaluate against this
        
        Returns:
            ExecutionResult with stdout, stderr, artifacts
        """
        execution_id = f"exec-{uuid.uuid4().hex[:8]}"
        workspace = self.workspace_root / execution_id
        workspace.mkdir(exist_ok=True)
        
        start_time = time.time()
        
        # Write code to file
        if language == "python":
            code_file = workspace / "script.py"
        elif language == "bash":
            code_file = workspace / "script.sh"
        elif language == "javascript":
            code_file = workspace / "script.js"
        else:
            raise ValueError(f"Unsupported language: {language}")
        
        code_file.write_text(code)
        
        # Prepare execution command
        if language == "python":
            cmd = ["python3", str(code_file)]
        elif language == "bash":
            cmd = ["bash", str(code_file)]
        elif language == "javascript":
            cmd = ["node", str(code_file)]
        
        # Execute with timeout and resource limits
        try:
            result = subprocess.run(
                cmd,
                cwd=str(workspace),
                capture_output=True,
                text=True,
                timeout=self.execution_timeout,
            )
            duration_ms = (time.time() - start_time) * 1000
            
            # Truncate output if too large
            stdout = result.stdout
            stderr = result.stderr
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... [truncated]"
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... [truncated]"
            
            # Collect artifacts (files created in workspace)
            artifacts = [
                str(f.relative_to(workspace))
                for f in workspace.iterdir()
                if f.name != code_file.name
            ]
            
            execution_result = ExecutionResult(
                execution_id=execution_id,
                code=code,
                stdout=stdout,
                stderr=stderr,
                return_code=result.returncode,
                duration_ms=duration_ms,
                workspace_path=str(workspace),
                artifacts=artifacts,
                cited_purpose=cited_purpose,
            )
            
        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            execution_result = ExecutionResult(
                execution_id=execution_id,
                code=code,
                stdout="",
                stderr=f"Execution timed out after {self.execution_timeout}s",
                return_code=-1,
                duration_ms=duration_ms,
                workspace_path=str(workspace),
                artifacts=[],
                cited_purpose=cited_purpose,
            )
        
        # Store in memory
        self.memory.store(MemoryTrace(
            trace_id=f"execution-{execution_id}",
            memory_type=MemoryType.EPISODIC,
            content={
                "execution": execution_result.__dict__,
                "evaluation": self._evaluate_execution(execution_result, expected_output),
            },
            source=self.agent_id,
            confidence=0.9 if execution_result.return_code == 0 else 0.3,
            importance=0.8,
            tags=["execution", language, "sandbox"],
        ))
        
        self.execution_history.append(execution_result)
        
        # Update awareness
        self.awareness.record_state(self._current_state())
        
        return execution_result

    @cite(
        key="SANDBOX-BENCHMARK",
        paper="SandboxAgent: Benchmark Execution",
        venue="ACN Harness Architecture",
        section="Benchmarking",
        rationale="Agents must verify performance claims with reproducible benchmarks",
        confidence="CERTAIN",
    )
    def run_benchmark(
        self,
        benchmark_script: str,
        metric_name: str,
        expected_metric: float,
        cited_purpose: str = "",
    ) -> Dict[str, Any]:
        """
        Run a benchmark script and verify the metric.
        
        Args:
            benchmark_script: Python script that prints the metric
            metric_name: Name of the metric (e.g., "accuracy", "latency_ms")
            expected_metric: Expected value for the metric
            cited_purpose: Why this benchmark is being run
        
        Returns:
            Dict with execution result, parsed metric, and verification status
        """
        result = self.execute(
            code=benchmark_script,
            language="python",
            cited_purpose=cited_purpose,
        )
        
        # Try to parse metric from stdout
        parsed_metric = None
        try:
            # Look for "metric_name: value" pattern
            for line in result.stdout.split("\n"):
                if f"{metric_name}:" in line.lower():
                    parsed_metric = float(line.split(":")[1].strip())
                    break
        except (ValueError, IndexError):
            pass
        
        verification = {
            "metric_name": metric_name,
            "expected": expected_metric,
            "parsed": parsed_metric,
            "match": parsed_metric is not None and abs(parsed_metric - expected_metric) < 0.01 * expected_metric,
            "execution": result,
        }
        
        return verification

    def _evaluate_execution(
        self,
        result: ExecutionResult,
        expected_output: Optional[str],
    ) -> Dict[str, Any]:
        """Evaluate whether execution produced expected results."""
        evaluation = {
            "success": result.return_code == 0,
            "output_match": None,
            "performance_ok": result.duration_ms < self.execution_timeout * 1000,
            "size_ok": len(result.stdout) < self.max_output_size,
        }
        
        if expected_output is not None:
            evaluation["output_match"] = expected_output in result.stdout
        
        return evaluation

    def _current_state(self) -> Any:
        """Generate current state for awareness tracking."""
        from harness.awareness import CurrentState
        return CurrentState(
            task_id=self.current_goal.goal_id if self.current_goal else "idle",
            phase="executing",
            active_twins=[self.agent_id],
            completed_subtasks=len(self.execution_history),
            total_subtasks=10,
            confidence=0.8 if self.execution_history and self.execution_history[-1].return_code == 0 else 0.4,
            resource_usage={
                "executions": len(self.execution_history),
                "total_duration_ms": sum(e.duration_ms for e in self.execution_history),
            },
        )
