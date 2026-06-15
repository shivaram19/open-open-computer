# src/generation/__init__.py
"""
Media generation subsystem for ACN agents.

Provides adapters for:
- ComfyUI (node-based diffusion workflow engine)
- Bernini (MLLM semantic planner + DiT renderer for video)

Agents invoke these through TwinTool registrations.

[CITATION: ADR-011]
Enterprise Security Baseline — all media generation calls are
auditable and tenant-scoped.
"""

from generation.media_service import ComfyUIClient, BerniniRunner, MediaResult
from generation.media_tools import MediaGenerationTools

__all__ = [
    "ComfyUIClient",
    "BerniniRunner",
    "MediaResult",
    "MediaGenerationTools",
]
