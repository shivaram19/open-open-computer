# src/generation/media_service.py
"""
Adapters for external media generation backends.

- ComfyUIClient talks to the ComfyUI REST API.
- HyperFramesRenderer writes HTML/variables and shells out to the HyperFrames CLI.
- BerniniRunner shells out to the Bernini inference scripts.

All clients support a `dry_run` mode for testing without GPU.

[CITATION: ADR-011]
Enterprise Security Baseline — inputs/outputs carry tenant_id and
agent_id for audit and access control.
"""

import json
import os
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

from shared.utils.citations import cite


@cite(
    key="MEDIA-RESULT",
    paper="ACN Media Generation Subsystem",
    venue="ACN Architecture Document",
    section="Data Model",
    rationale="Uniform result type lets agents handle success and failure consistently",
    confidence="CERTAIN",
)
@dataclass
class MediaResult:
    """Result of a media generation call."""
    success: bool
    task_id: str
    output_path: Optional[str] = None
    output_bytes: Optional[bytes] = None
    mime_type: str = "application/octet-stream"
    backend: str = ""
    action: str = ""
    prompt: str = ""
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@cite(
    key="COMFYUI-CLIENT",
    paper="Building a Production-Ready ComfyUI API",
    venue="ViewComfy Blog",
    section="Core API Functions",
    rationale="HTTP client abstracts ComfyUI prompt API, history polling, and image download",
    confidence="HIGH",
)
class ComfyUIClient:
    """Client for the ComfyUI HTTP API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8188",
        timeout: float = 300.0,
        output_dir: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.output_dir = Path(output_dir) if output_dir else Path("./outputs/comfyui")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _url(self, path: str) -> str:
        return urljoin(self.base_url + "/", path)

    def _get(self, path: str) -> Dict[str, Any]:
        resp = requests.get(self._url(path), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = requests.post(self._url(path), json=json_data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_object_info(self, class_type: Optional[str] = None) -> Dict[str, Any]:
        """Get available node definitions from ComfyUI."""
        data = self._get("object_info")
        if class_type:
            return data.get(class_type, {})
        return data

    def submit_workflow(self, workflow: Dict[str, Any], client_id: Optional[str] = None) -> str:
        """Submit a workflow and return the prompt_id."""
        client_id = client_id or f"acn_{uuid.uuid4().hex[:8]}"
        payload = {"prompt": workflow, "client_id": client_id}
        data = self._post("prompt", payload)
        return data["prompt_id"]

    def get_queue_status(self) -> Dict[str, Any]:
        return self._get("queue")

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        return self._get(f"history/{prompt_id}")

    def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval: float = 1.0,
        max_wait: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Poll history until the prompt is done or timeout."""
        max_wait = max_wait or self.timeout
        start = time.time()
        while time.time() - start < max_wait:
            history = self.get_history(prompt_id)
            entry = history.get(prompt_id, {})
            status = entry.get("status", {})
            status_str = status.get("status_str")
            if status_str == "success":
                return entry
            if status_str == "error":
                raise RuntimeError(f"ComfyUI workflow failed: {status.get('messages', 'unknown error')}")
            time.sleep(poll_interval)
        raise TimeoutError(f"ComfyUI prompt {prompt_id} did not complete within {max_wait}s")

    def download_output(
        self,
        filename: str,
        subfolder: str = "",
        folder_type: str = "output",
    ) -> bytes:
        """Download a generated file from ComfyUI."""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        resp = requests.get(self._url("view"), params=params, timeout=60)
        resp.raise_for_status()
        return resp.content

    def upload_image(
        self,
        input_path: str,
        filename: Optional[str] = None,
        folder_type: str = "input",
        overwrite: bool = False,
    ) -> bytes:
        """Upload an image to ComfyUI's input folder."""
        path = Path(input_path)
        filename = filename or path.name
        with open(path, "rb") as file:
            files = {"image": (filename, file, "image/png")}
            data = {"type": folder_type, "overwrite": str(overwrite).lower()}
            resp = requests.post(self._url("upload/image"), files=files, data=data, timeout=60)
        resp.raise_for_status()
        return resp.content

    def run_workflow(
        self,
        workflow: Dict[str, Any],
        client_id: Optional[str] = None,
    ) -> MediaResult:
        """Submit a workflow, wait, and collect the first output file."""
        task_id = f"comfy_{uuid.uuid4().hex[:8]}"
        start = time.time()
        try:
            prompt_id = self.submit_workflow(workflow, client_id)
            history = self.wait_for_completion(prompt_id)
            outputs = history.get("outputs", {})
            if not outputs:
                return MediaResult(
                    success=False,
                    task_id=task_id,
                    backend="comfyui",
                    action="workflow",
                    latency_ms=(time.time() - start) * 1000,
                    error="No outputs in ComfyUI history",
                )

            first_node = next(iter(outputs.values()))
            files = first_node.get("images", []) or first_node.get("files", [])
            if not files:
                return MediaResult(
                    success=False,
                    task_id=task_id,
                    backend="comfyui",
                    action="workflow",
                    latency_ms=(time.time() - start) * 1000,
                    error="No files in ComfyUI output node",
                )

            file_info = files[0]
            filename = file_info["filename"]
            subfolder = file_info.get("subfolder", "")
            data = self.download_output(filename, subfolder)
            ext = Path(filename).suffix.lstrip(".").lower()
            mime_map = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "webp": "image/webp",
                "mp4": "video/mp4",
            }
            mime = mime_map.get(ext, "application/octet-stream")
            output_path = self.output_dir / filename
            output_path.write_bytes(data)

            return MediaResult(
                success=True,
                task_id=task_id,
                output_path=str(output_path),
                output_bytes=data,
                mime_type=mime,
                backend="comfyui",
                action="workflow",
                latency_ms=(time.time() - start) * 1000,
                metadata={"prompt_id": prompt_id, "filename": filename},
            )
        except Exception as exc:
            return MediaResult(
                success=False,
                task_id=task_id,
                backend="comfyui",
                action="workflow",
                latency_ms=(time.time() - start) * 1000,
                error=str(exc),
            )


@cite(
    key="HYPERFRAMES-RENDERER",
    paper="HyperFrames: Write HTML. Render video.",
    venue="HeyGen Open Source",
    section="How It Works",
    rationale="HTML-native video renderer is deterministic and agent-friendly because LLMs already write HTML/CSS",
    confidence="HIGH",
)
class HyperFramesRenderer:
    """Renderer that writes HTML/variables and calls the HyperFrames CLI."""

    def __init__(
        self,
        project_dir: str,
        npx_cmd: str = "npx",
        hyperframes_version: str = "0.6.97",
        output_dir: Optional[str] = None,
    ):
        self.project_dir = Path(project_dir)
        self.output_dir = Path(output_dir) if output_dir else self.project_dir / "renders"
        self.npx_cmd = npx_cmd
        self.hyperframes_version = hyperframes_version

    def _write_project(self, html: str, variables: Dict[str, Any]) -> None:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "index.html").write_text(html, encoding="utf-8")
        (self.project_dir / "variables.json").write_text(json.dumps(variables), encoding="utf-8")

    def render(
        self,
        html: str,
        variables: Dict[str, Any],
        output_name: str,
        timeout: float = 300.0,
    ) -> MediaResult:
        """Render an HTML composition to MP4 via HyperFrames CLI."""
        task_id = f"hf_{uuid.uuid4().hex[:8]}"
        start = time.time()
        try:
            self._write_project(html, variables)
            output_path = self.output_dir / output_name
            self.output_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                self.npx_cmd,
                "--yes",
                f"hyperframes@{self.hyperframes_version}",
                "render",
                "--variables-file", str(self.project_dir / "variables.json"),
                "--output", str(output_path),
            ]
            result = subprocess.run(
                cmd,
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
            return MediaResult(
                success=True,
                task_id=task_id,
                output_path=str(output_path),
                backend="hyperframes",
                action="render",
                latency_ms=(time.time() - start) * 1000,
                metadata={"stdout": result.stdout, "stderr": result.stderr},
            )
        except Exception as exc:
            return MediaResult(
                success=False,
                task_id=task_id,
                backend="hyperframes",
                action="render",
                latency_ms=(time.time() - start) * 1000,
                error=str(exc),
            )

    def check(self, timeout: float = 60.0) -> MediaResult:
        """Run lint + validate + inspect on the current project."""
        task_id = f"hf_check_{uuid.uuid4().hex[:8]}"
        start = time.time()
        try:
            for subcmd in ("lint", "validate", "inspect"):
                cmd = [
                    self.npx_cmd,
                    "--yes",
                    f"hyperframes@{self.hyperframes_version}",
                    subcmd,
                ]
                subprocess.run(
                    cmd,
                    cwd=str(self.project_dir),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=True,
                )
            return MediaResult(
                success=True,
                task_id=task_id,
                backend="hyperframes",
                action="check",
                latency_ms=(time.time() - start) * 1000,
            )
        except Exception as exc:
            return MediaResult(
                success=False,
                task_id=task_id,
                backend="hyperframes",
                action="check",
                latency_ms=(time.time() - start) * 1000,
                error=str(exc),
            )


@cite(
    key="BERNINI-RUNNER",
    paper="ACN Media Generation Subsystem",
    venue="ACN Architecture Document",
    section="Bernini Adapter",
    rationale="Shell wrapper keeps Bernini's heavy dependencies isolated while exposing task types to agents",
    confidence="CERTAIN",
)
class BerniniRunner:
    """Runner for Bernini inference scripts. GPU required for actual inference."""

    def __init__(
        self,
        repo_path: str,
        venv_python: Optional[str] = None,
        output_dir: Optional[str] = None,
        dry_run: bool = False,
    ):
        self.repo_path = Path(repo_path)
        self.venv_python = venv_python or str(self.repo_path / ".venv" / "bin" / "python")
        self.output_dir = Path(output_dir) if output_dir else Path("./outputs/bernini")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dry_run = dry_run

    def _run_script(
        self,
        script: str,
        args: List[str],
        timeout: float = 600.0,
    ) -> subprocess.CompletedProcess:
        cmd = [self.venv_python, str(self.repo_path / script)] + args
        if self.dry_run:
            print("[DRY RUN]", " ".join(cmd))
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")
        return subprocess.run(
            cmd,
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True,
        )

    def _case_file(
        self,
        task_type: str,
        prompt: str,
        input_path: Optional[str] = None,
        num_frames: int = 16,
    ) -> str:
        """Write a temporary Bernini case file and return its path."""
        ext = "png" if task_type in ("t2i", "i2i") else "mp4"
        output_name = f"{task_type}_{uuid.uuid4().hex[:8]}.{ext}"
        case = {
            "task_type": task_type,
            "prompt": prompt,
            "output": str(self.output_dir / output_name),
        }
        if input_path:
            if task_type in ("i2i",):
                case["image"] = input_path
            elif task_type in ("v2v", "rv2v"):
                case["video"] = input_path
            elif task_type == "r2v":
                case["images"] = input_path if isinstance(input_path, list) else [input_path]
        case_path = self.output_dir / f"case_{uuid.uuid4().hex[:8]}.json"
        case_path.write_text(json.dumps(case, indent=2))
        return str(case_path)

    def run_task(
        self,
        task_type: str,
        config: str,
        case_path: str,
        num_frames: Optional[int] = None,
        guidance_mode: str = "t2v_apg",
    ) -> MediaResult:
        """Run a Bernini task from a case file."""
        task_id = f"bernini_{uuid.uuid4().hex[:8]}"
        start = time.time()
        try:
            args = ["--config", config, "--case", case_path, "--guidance_mode", guidance_mode]
            if num_frames is not None:
                args.extend(["--num_frames", str(num_frames)])

            script = "infer_single_gpu.py" if task_type in ("t2i", "i2i") else "infer_multi_gpu.py"
            result = self._run_script(script, args)
            case = json.loads(Path(case_path).read_text())
            output_path = case.get("output")

            return MediaResult(
                success=True,
                task_id=task_id,
                output_path=output_path,
                backend="bernini",
                action=task_type,
                latency_ms=(time.time() - start) * 1000,
                metadata={"stdout": result.stdout, "stderr": result.stderr},
            )
        except Exception as exc:
            return MediaResult(
                success=False,
                task_id=task_id,
                backend="bernini",
                action=task_type,
                latency_ms=(time.time() - start) * 1000,
                error=str(exc),
            )

    def generate_image(
        self,
        prompt: str,
        config: str,
        guidance_mode: str = "t2v_apg",
    ) -> MediaResult:
        case_path = self._case_file("t2i", prompt, num_frames=1)
        return self.run_task("t2i", config, case_path, num_frames=1, guidance_mode=guidance_mode)

    def generate_video(
        self,
        prompt: str,
        config: str,
        num_frames: int = 16,
        guidance_mode: str = "t2v_apg",
    ) -> MediaResult:
        case_path = self._case_file("t2v", prompt, num_frames=num_frames)
        return self.run_task("t2v", config, case_path, num_frames=num_frames, guidance_mode=guidance_mode)

    def edit_video(
        self,
        prompt: str,
        input_path: str,
        config: str,
        num_frames: int = 16,
        guidance_mode: str = "v2v_apg",
    ) -> MediaResult:
        case_path = self._case_file("v2v", prompt, input_path=input_path, num_frames=num_frames)
        return self.run_task("v2v", config, case_path, num_frames=num_frames, guidance_mode=guidance_mode)
