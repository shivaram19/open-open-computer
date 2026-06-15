"""Quick sensor: run ACN's Bernini tool with the real GPU runner."""
import sys
sys.path.insert(0, "/home/Ubuntu/deeptech/acn/src")
sys.path.insert(0, "/home/Ubuntu/deeptech")

from pathlib import Path
from generation.media_service import BerniniRunner
from generation.media_tools import MediaGenerationTools
from security import SecurityManager
from security.config import SecurityConfig
from agents.twin_tools import TwinToolRegistry

repo = Path("/home/Ubuntu/deeptech/experiments/Bernini")
runner = BerniniRunner(
    repo_path=str(repo),
    venv_python=str(repo / ".venv" / "bin" / "python"),
    output_dir="/home/Ubuntu/deeptech/outputs/bernini_real",
    dry_run=False,
)

security = SecurityManager(config=SecurityConfig(rate_limit_enabled=False))

tools = MediaGenerationTools(
    security=security,
    comfyui_client=None,
    hyperframes_renderer=None,
    bernini_runner=runner,
)

registry = TwinToolRegistry()
tools.register_all(registry)

result = registry.invoke("generate_image_bernini", {
    "tenant_id": "test",
    "agent_id": "test",
    "prompt": "A futuristic Indian city at sunset",
    "config": "/home/Ubuntu/models/Bernini-R-1.3B-Diffusers",
    "num_frames": 1,
})

print("success:", result.success)
print("result:", result)
if hasattr(result, "data"):
    print("data:", result.data)
if not result.success:
    print("error:", getattr(result, "error", None))
