# acn/tests/generation/test_media_tools.py
"""Tests for security-aware media generation tools."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agents.twin_tools import TwinToolRegistry
from generation.media_service import ComfyUIClient, HyperFramesRenderer, BerniniRunner, MediaResult
from generation.media_tools import MediaGenerationTools
from security import SecurityManager
from security.config import SecurityConfig


@pytest.fixture
def security():
    return SecurityManager(config=SecurityConfig(rate_limit_enabled=False))


@pytest.fixture
def registry():
    return TwinToolRegistry()


@pytest.fixture
def comfyui_client(tmp_path):
    client = ComfyUIClient(output_dir=str(tmp_path / "comfyui"))
    client.run_workflow = MagicMock(
        return_value=MediaResult(
            success=True,
            task_id="comfy_test_1",
            output_path=str(tmp_path / "comfyui" / "test.png"),
            backend="comfyui",
            action="workflow",
        )
    )
    return client


@pytest.fixture
def hyperframes_renderer(tmp_path):
    renderer = HyperFramesRenderer(project_dir=str(tmp_path / "hyperframes"))
    renderer.render = MagicMock(
        return_value=MediaResult(
            success=True,
            task_id="hf_test_1",
            output_path=str(tmp_path / "hyperframes" / "renders" / "output.mp4"),
            backend="hyperframes",
            action="render",
        )
    )
    return renderer


@pytest.fixture
def bernini_runner(tmp_path):
    runner = BerniniRunner(repo_path=str(tmp_path / "bernini"), dry_run=True)
    runner.generate_image = MagicMock(
        return_value=MediaResult(
            success=True,
            task_id="bernini_i2i_1",
            output_path=str(tmp_path / "bernini" / "output.png"),
            backend="bernini",
            action="t2i",
        )
    )
    runner.generate_video = MagicMock(
        return_value=MediaResult(
            success=True,
            task_id="bernini_t2v_1",
            output_path=str(tmp_path / "bernini" / "output.mp4"),
            backend="bernini",
            action="t2v",
        )
    )
    runner.edit_video = MagicMock(
        return_value=MediaResult(
            success=True,
            task_id="bernini_v2v_1",
            output_path=str(tmp_path / "bernini" / "edited.mp4"),
            backend="bernini",
            action="v2v",
        )
    )
    return runner


@pytest.fixture
def media_tools(security, comfyui_client, hyperframes_renderer, bernini_runner):
    return MediaGenerationTools(
        security=security,
        comfyui_client=comfyui_client,
        hyperframes_renderer=hyperframes_renderer,
        bernini_runner=bernini_runner,
    )


@pytest.fixture
def media_tools_no_clients(security):
    return MediaGenerationTools(security=security)


def _base_inputs(**overrides):
    defaults = {
        "tenant_id": "tenant-1",
        "agent_id": "agent-1",
        "roles": ["service"],
    }
    defaults.update(overrides)
    return defaults


def test_register_all_tools(media_tools, registry):
    media_tools.register_all(registry)
    tool_names = {tool.name for tool in registry.list_tools()}
    assert tool_names == {
        "generate_image_comfyui",
        "generate_video_comfyui",
        "generate_video_hyperframes",
        "generate_image_bernini",
        "generate_video_bernini",
        "edit_video_bernini",
    }


def test_register_only_provided_clients(media_tools_no_clients, registry):
    media_tools_no_clients.register_all(registry)
    assert len(registry.list_tools()) == 0


def test_input_validation_fails_on_missing_security_context(media_tools, registry):
    media_tools.register_all(registry)
    result = registry.invoke("generate_video_hyperframes", {"html": "<h1>Hi</h1>"})
    assert not result.success
    assert "tenant_id" in result.error or "agent_id" in result.error


def test_comfyui_image_tool_authorizes_and_runs(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(prompt="a red cube on a blue table")
    result = registry.invoke("generate_image_comfyui", inputs)
    assert result.success
    assert result.output["backend"] == "comfyui"
    assert result.output["action"] == "workflow"
    assert Path(result.output["output_path"]).name == "test.png"
    media_tools.comfyui.run_workflow.assert_called_once()


def test_comfyui_video_tool_authorizes_and_runs(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(prompt="a rotating red cube")
    result = registry.invoke("generate_video_comfyui", inputs)
    assert result.success
    assert result.output["backend"] == "comfyui"


def test_hyperframes_tool_authorizes_and_runs(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(html="<h1>Hello</h1>", output_name="hello.mp4")
    result = registry.invoke("generate_video_hyperframes", inputs)
    assert result.success
    assert result.output["backend"] == "hyperframes"
    assert result.output["action"] == "render"
    media_tools.hyperframes.render.assert_called_once_with(
        html="<h1>Hello</h1>",
        variables={},
        output_name="hello.mp4",
        timeout=300.0,
    )


def test_bernini_image_tool_authorizes_and_runs(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(prompt="a marble statue", config="/models/bernini")
    result = registry.invoke("generate_image_bernini", inputs)
    assert result.success
    assert result.output["backend"] == "bernini"
    assert result.output["action"] == "t2i"


def test_bernini_video_tool_authorizes_and_runs(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(prompt="a dancing robot", config="/models/bernini", num_frames=8)
    result = registry.invoke("generate_video_bernini", inputs)
    assert result.success
    assert result.output["backend"] == "bernini"
    assert result.output["action"] == "t2v"


def test_bernini_edit_tool_authorizes_and_runs(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(
        prompt="make it sunset",
        input_path="/tmp/input.mp4",
        config="/models/bernini",
    )
    result = registry.invoke("edit_video_bernini", inputs)
    assert result.success
    assert result.output["backend"] == "bernini"
    assert result.output["action"] == "v2v"


def test_unauthorized_role_is_denied_and_audited(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(roles=["readonly"], prompt="a red cube")
    result = registry.invoke("generate_image_comfyui", inputs)
    # Registry invocation succeeds because the handler returned gracefully;
    # the business-level failure is in the output payload.
    assert result.success
    assert not result.output["success"]
    assert "Access denied" in result.output["error"]
    # Audit: authorize denied + media denied.
    media_records = media_tools.security.audit.get_records()
    denied_records = [r for r in media_records if r.outcome == "denied"]
    assert len(denied_records) >= 1


def test_cross_tenant_access_denied(media_tools, registry):
    media_tools.register_all(registry)
    # readonly role lacks MEDIA_GENERATE and is tenant-scoped, but use service role
    # with explicit cross-tenant mismatch by overriding tenant in resource is not possible
    # via tool inputs. Instead simulate an identity that belongs to tenant-2 calling
    # a tool whose tenant_id is tenant-1. The tool authorizes against tenant-1.
    inputs = {
        "tenant_id": "tenant-1",
        "agent_id": "agent-2",
        "roles": ["service"],
        "prompt": "a red cube",
    }
    # Force the authorizer to see tenant-2 by tampering is not possible; instead we
    # construct a scenario where the caller's identity tenant differs from resource tenant.
    # The tool always uses inputs["tenant_id"] as both identity and resource tenant,
    # so it will pass. To test cross-tenant denial we directly call the authorizer.
    from security.identity import Identity, IdentityType
    from security.rbac import Permission

    identity = Identity(
        id="agent-2",
        type=IdentityType.AGENT,
        name="agent-2",
        tenant_id="tenant-2",
        roles=["service"],
        auth_method="tool_call",
    )
    decision = media_tools.security.authorize(
        identity,
        Permission.MEDIA_GENERATE,
        resource_type="media",
        resource_id="generate_image_comfyui",
        resource_tenant_id="tenant-1",
    )
    assert not decision.allowed
    assert "cross-tenant" in decision.reason.lower()


def test_audit_records_media_success(media_tools, registry):
    media_tools.register_all(registry)
    before = len(media_tools.security.audit.get_records())
    inputs = _base_inputs(html="<p>ok</p>", output_name="ok.mp4")
    result = registry.invoke("generate_video_hyperframes", inputs)
    assert result.success
    after = len(media_tools.security.audit.get_records())
    assert after > before
    media_records = media_tools.security.audit.get_records()
    success_records = [r for r in media_records if r.outcome == "success" and r.category == "media"]
    assert len(success_records) >= 1
    assert success_records[-1].resource_id.startswith("hf_")


def test_audit_chain_verifies(media_tools, registry):
    media_tools.register_all(registry)
    inputs = _base_inputs(prompt="a red cube")
    registry.invoke("generate_image_comfyui", inputs)
    verification = media_tools.security.audit.verify_chain()
    assert verification["valid"]
    assert verification["records"] >= 2
