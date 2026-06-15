# src/generation/media_tools.py
"""
Security-aware TwinTool wrappers for media generation backends.

Every tool invocation is authenticated, authorized, and audited through
SecurityManager before the underlying adapter is called.

[CITATION: Strands2026]
Agent-as-Tool composition pattern.

[CITATION: ADR-011]
Enterprise Security Baseline — all media generation calls route through
SecurityManager for authentication, authorization, and audit logging.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from agents.twin_tools import TwinTool, TwinToolRegistry
from generation.media_service import ComfyUIClient, HyperFramesRenderer, BerniniRunner, MediaResult
from security import SecurityManager, Identity, IdentityType
from security.rbac import Permission
from security.audit import AuditCategory, AuditSeverity
from shared.utils.citations import cite


class _SecurityContext(BaseModel):
    """Common security context carried by every media tool input."""
    tenant_id: str = Field(..., description="Tenant that owns the request")
    agent_id: str = Field(..., description="Agent or service invoking the tool")
    roles: list[str] = Field(default_factory=lambda: ["service"], description="RBAC roles assigned to the caller")


class ComfyUIImageInput(_SecurityContext):
    prompt: str = Field(..., description="Text prompt for the image")
    width: int = Field(1024, ge=512, le=2048)
    height: int = Field(1024, ge=512, le=2048)
    steps: int = Field(20, ge=1, le=100)
    seed: int = Field(42, ge=0)


class ComfyUIVideoInput(_SecurityContext):
    prompt: str = Field(..., description="Text prompt for the video")
    width: int = Field(832, ge=512, le=1280)
    height: int = Field(480, ge=256, le=720)
    frames: int = Field(24, ge=8, le=128)
    steps: int = Field(20, ge=1, le=100)
    seed: int = Field(42, ge=0)


class HyperFramesVideoInput(_SecurityContext):
    html: str = Field(..., description="HTML composition to render as MP4")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Variables injected into the composition")
    output_name: str = Field("output.mp4", description="Name of the rendered output file")
    timeout: float = Field(300.0, ge=1.0, description="Render timeout in seconds")


class BerniniTextInput(_SecurityContext):
    prompt: str = Field(..., description="Text prompt")
    config: str = Field(..., description="Path to Bernini model config/diffusers directory")
    num_frames: int = Field(16, ge=1, le=128)
    guidance_mode: str = Field("t2v_apg")


class BerniniEditInput(_SecurityContext):
    prompt: str = Field(..., description="Edit instruction")
    input_path: str = Field(..., description="Path to source image or video")
    config: str = Field(..., description="Path to Bernini model config/diffusers directory")
    num_frames: int = Field(16, ge=1, le=128)
    guidance_mode: str = Field("v2v_apg")


class MediaOutput(BaseModel):
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    backend: str
    action: str


@cite(
    key="MEDIA-GENERATION-TOOLS",
    paper="ACN Media Generation Subsystem",
    venue="ACN Architecture Document",
    section="Agent Tools",
    rationale="Typed tool schemas let agents discover and call media generation safely",
    confidence="CERTAIN",
)
class MediaGenerationTools:
    """Factory for registering ComfyUI, HyperFrames, and Bernini tools in a TwinToolRegistry."""

    def __init__(
        self,
        security: SecurityManager,
        comfyui_client: Optional[ComfyUIClient] = None,
        hyperframes_renderer: Optional[HyperFramesRenderer] = None,
        bernini_runner: Optional[BerniniRunner] = None,
    ):
        self.security = security
        self.comfyui = comfyui_client
        self.hyperframes = hyperframes_renderer
        self.bernini = bernini_runner

    def register_all(self, registry: TwinToolRegistry, twin_id: str = "media_agent") -> None:
        """Register all available media tools."""
        if self.comfyui:
            registry.register(TwinTool(
                name="generate_image_comfyui",
                description="Generate an image using ComfyUI from a text prompt",
                twin_id=twin_id,
                handler=self._generate_image_comfyui,
                input_schema=ComfyUIImageInput,
                output_schema=MediaOutput,
                tags=["generation", "image", "comfyui"],
            ))
            registry.register(TwinTool(
                name="generate_video_comfyui",
                description="Generate a video using ComfyUI from a text prompt",
                twin_id=twin_id,
                handler=self._generate_video_comfyui,
                input_schema=ComfyUIVideoInput,
                output_schema=MediaOutput,
                tags=["generation", "video", "comfyui"],
            ))

        if self.hyperframes:
            registry.register(TwinTool(
                name="generate_video_hyperframes",
                description="Render an HTML composition to an MP4 video using HyperFrames",
                twin_id=twin_id,
                handler=self._generate_video_hyperframes,
                input_schema=HyperFramesVideoInput,
                output_schema=MediaOutput,
                tags=["generation", "video", "hyperframes", "html"],
            ))

        if self.bernini:
            registry.register(TwinTool(
                name="generate_image_bernini",
                description="Generate an image using Bernini-R from a text prompt",
                twin_id=twin_id,
                handler=self._generate_image_bernini,
                input_schema=BerniniTextInput,
                output_schema=MediaOutput,
                tags=["generation", "image", "bernini"],
            ))
            registry.register(TwinTool(
                name="generate_video_bernini",
                description="Generate a video using Bernini from a text prompt",
                twin_id=twin_id,
                handler=self._generate_video_bernini,
                input_schema=BerniniTextInput,
                output_schema=MediaOutput,
                tags=["generation", "video", "bernini"],
            ))
            registry.register(TwinTool(
                name="edit_video_bernini",
                description="Edit a video using Bernini from a source video and instruction",
                twin_id=twin_id,
                handler=self._edit_video_bernini,
                input_schema=BerniniEditInput,
                output_schema=MediaOutput,
                tags=["generation", "video", "bernini", "editing"],
            ))

    def _authorize(
        self,
        tool_name: str,
        tenant_id: str,
        agent_id: str,
        roles: list[str],
    ) -> Optional[Dict[str, Any]]:
        """Authorize the caller and return an error dict if denied."""
        identity = Identity(
            id=agent_id,
            type=IdentityType.AGENT,
            name=agent_id,
            tenant_id=tenant_id,
            roles=roles,
            auth_method="tool_call",
        )
        decision = self.security.authorize(
            identity,
            Permission.MEDIA_GENERATE,
            resource_type="media",
            resource_id=tool_name,
            resource_tenant_id=tenant_id,
        )
        if not decision.allowed:
            self.security.audit.log(
                category=AuditCategory.MEDIA,
                severity=AuditSeverity.WARNING,
                action=tool_name,
                actor_id=agent_id,
                actor_type="agent",
                tenant_id=tenant_id,
                outcome="denied",
                resource_type="media",
                resource_id=tool_name,
                details={"reason": decision.reason, "roles": roles},
            )
            return {
                "success": False,
                "error": f"Access denied: {decision.reason}",
                "backend": "security",
                "action": tool_name,
            }
        return None

    def _audit_result(
        self,
        tool_name: str,
        tenant_id: str,
        agent_id: str,
        result: MediaResult,
    ) -> None:
        """Log the outcome of a media generation call."""
        self.security.audit.log(
            category=AuditCategory.MEDIA,
            severity=AuditSeverity.INFO if result.success else AuditSeverity.ERROR,
            action=tool_name,
            actor_id=agent_id,
            actor_type="agent",
            tenant_id=tenant_id,
            outcome="success" if result.success else "failure",
            resource_type="media",
            resource_id=result.task_id,
            details={
                "backend": result.backend,
                "action": result.action,
                "output_path": result.output_path,
                "error": result.error,
                "latency_ms": result.latency_ms,
            },
        )

    @staticmethod
    def _to_media_output(result: MediaResult) -> Dict[str, Any]:
        return {
            "success": result.success,
            "output_path": result.output_path,
            "error": result.error,
            "backend": result.backend,
            "action": result.action,
        }

    def _generate_image_comfyui(self, **inputs) -> Dict[str, Any]:
        denied = self._authorize("generate_image_comfyui", inputs["tenant_id"], inputs["agent_id"], inputs.get("roles", ["service"]))
        if denied:
            return denied
        workflow = self._build_simple_image_workflow(**inputs)
        result = self.comfyui.run_workflow(workflow)
        self._audit_result("generate_image_comfyui", inputs["tenant_id"], inputs["agent_id"], result)
        return self._to_media_output(result)

    def _generate_video_comfyui(self, **inputs) -> Dict[str, Any]:
        denied = self._authorize("generate_video_comfyui", inputs["tenant_id"], inputs["agent_id"], inputs.get("roles", ["service"]))
        if denied:
            return denied
        workflow = self._build_simple_video_workflow(**inputs)
        result = self.comfyui.run_workflow(workflow)
        self._audit_result("generate_video_comfyui", inputs["tenant_id"], inputs["agent_id"], result)
        return self._to_media_output(result)

    def _generate_video_hyperframes(self, **inputs) -> Dict[str, Any]:
        denied = self._authorize("generate_video_hyperframes", inputs["tenant_id"], inputs["agent_id"], inputs.get("roles", ["service"]))
        if denied:
            return denied
        result = self.hyperframes.render(
            html=inputs["html"],
            variables=inputs.get("variables", {}),
            output_name=inputs.get("output_name", "output.mp4"),
            timeout=inputs.get("timeout", 300.0),
        )
        self._audit_result("generate_video_hyperframes", inputs["tenant_id"], inputs["agent_id"], result)
        return self._to_media_output(result)

    def _generate_image_bernini(self, **inputs) -> Dict[str, Any]:
        denied = self._authorize("generate_image_bernini", inputs["tenant_id"], inputs["agent_id"], inputs.get("roles", ["service"]))
        if denied:
            return denied
        result = self.bernini.generate_image(
            prompt=inputs["prompt"],
            config=inputs["config"],
            guidance_mode=inputs.get("guidance_mode", "t2v_apg"),
        )
        self._audit_result("generate_image_bernini", inputs["tenant_id"], inputs["agent_id"], result)
        return self._to_media_output(result)

    def _generate_video_bernini(self, **inputs) -> Dict[str, Any]:
        denied = self._authorize("generate_video_bernini", inputs["tenant_id"], inputs["agent_id"], inputs.get("roles", ["service"]))
        if denied:
            return denied
        result = self.bernini.generate_video(
            prompt=inputs["prompt"],
            config=inputs["config"],
            num_frames=inputs.get("num_frames", 16),
            guidance_mode=inputs.get("guidance_mode", "t2v_apg"),
        )
        self._audit_result("generate_video_bernini", inputs["tenant_id"], inputs["agent_id"], result)
        return self._to_media_output(result)

    def _edit_video_bernini(self, **inputs) -> Dict[str, Any]:
        denied = self._authorize("edit_video_bernini", inputs["tenant_id"], inputs["agent_id"], inputs.get("roles", ["service"]))
        if denied:
            return denied
        result = self.bernini.edit_video(
            prompt=inputs["prompt"],
            input_path=inputs["input_path"],
            config=inputs["config"],
            num_frames=inputs.get("num_frames", 16),
            guidance_mode=inputs.get("guidance_mode", "v2v_apg"),
        )
        self._audit_result("edit_video_bernini", inputs["tenant_id"], inputs["agent_id"], result)
        return self._to_media_output(result)

    @staticmethod
    def _build_simple_image_workflow(
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 20,
        seed: int = 42,
        **kwargs,
    ) -> Dict[str, Any]:
        """Minimal ComfyUI workflow for text-to-image.

        Assumes a checkpoint named 'model.safetensors' exists in ComfyUI/models/checkpoints/.
        In practice the agent would discover available checkpoints via object_info.
        """
        return {
            "1": {
                "inputs": {"ckpt_name": "model.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": "", "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": 7.5,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                },
                "class_type": "KSampler",
            },
            "6": {
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "7": {
                "inputs": {"filename_prefix": "acn_comfyui", "images": ["6", 0]},
                "class_type": "SaveImage",
            },
        }

    @staticmethod
    def _build_simple_video_workflow(
        prompt: str,
        width: int = 832,
        height: int = 480,
        frames: int = 24,
        steps: int = 20,
        seed: int = 42,
        **kwargs,
    ) -> Dict[str, Any]:
        """Placeholder workflow scaffold for ComfyUI video generation."""
        # A real implementation would load an SVD or video checkpoint.
        return {
            "1": {
                "inputs": {"ckpt_name": "svd_xt.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"width": width, "height": height, "video_frames": frames, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "4": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": 7.5,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["2", 0],
                    "latent_image": ["3", 0],
                },
                "class_type": "KSampler",
            },
            "5": {
                "inputs": {"samples": ["4", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "6": {
                "inputs": {"filename_prefix": "acn_comfyui_video", "images": ["5", 0]},
                "class_type": "SaveImage",
            },
        }
