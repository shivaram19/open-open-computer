# acn/tests/generation/test_mcp_bridge.py
"""Tests for the Model Context Protocol bridge over ACN media tools."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mcp.shared.memory import create_connected_server_and_client_session
from mcp import types

# Ensure src/ is on path when running this file directly.
_SRC_DIR = Path(__file__).parent.parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from agents.twin_tools import TwinToolRegistry
from generation.media_service import ComfyUIClient, HyperFramesRenderer, BerniniRunner, MediaResult
from generation.media_tools import MediaGenerationTools
from generation.mcp_server import MediaMcpServer
from security import SecurityManager
from security.config import SecurityConfig


@pytest.fixture
def security():
    return SecurityManager(config=SecurityConfig(rate_limit_enabled=False))


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
def registry(media_tools):
    reg = TwinToolRegistry()
    media_tools.register_all(reg)
    return reg


@pytest.fixture
def mcp_server(registry, security):
    return MediaMcpServer(
        tool_registry=registry,
        security=security,
        default_tenant_id="tenant-mcp",
        default_agent_id="agent-mcp",
    )


@pytest.mark.anyio
async def test_mcp_list_tools(mcp_server):
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        tools_result = await client.list_tools()
        tool_names = {tool.name for tool in tools_result.tools}
        assert tool_names == {
            "generate_image_comfyui",
            "generate_video_comfyui",
            "generate_video_hyperframes",
            "generate_image_bernini",
            "generate_video_bernini",
            "edit_video_bernini",
        }
        for tool in tools_result.tools:
            assert "tenant_id" in tool.inputSchema["properties"]
            assert "agent_id" in tool.inputSchema["properties"]
            # Defaults are injected by the bridge, so they are not strictly required.
            assert "tenant_id" not in tool.inputSchema.get("required", [])
            assert "agent_id" not in tool.inputSchema.get("required", [])


@pytest.mark.anyio
async def test_mcp_call_hyperframes_tool(mcp_server, media_tools):
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        result = await client.call_tool(
            "generate_video_hyperframes",
            {
                "tenant_id": "tenant-1",
                "agent_id": "agent-1",
                "html": "<h1>Hello</h1>",
                "output_name": "hello.mp4",
            },
        )
        assert len(result.content) == 1
        payload = json.loads(result.content[0].text)
        assert payload["success"] is True
        assert payload["output"]["backend"] == "hyperframes"
        media_tools.hyperframes.render.assert_called_once()


@pytest.mark.anyio
async def test_mcp_call_comfyui_image_tool(mcp_server, media_tools):
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        result = await client.call_tool(
            "generate_image_comfyui",
            {
                "tenant_id": "tenant-1",
                "agent_id": "agent-1",
                "prompt": "a red cube",
            },
        )
        payload = json.loads(result.content[0].text)
        assert payload["success"] is True
        assert payload["output"]["backend"] == "comfyui"
        media_tools.comfyui.run_workflow.assert_called_once()


@pytest.mark.anyio
async def test_mcp_call_bernini_tools(mcp_server, media_tools):
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        result = await client.call_tool(
            "generate_video_bernini",
            {
                "tenant_id": "tenant-1",
                "agent_id": "agent-1",
                "prompt": "a dancing robot",
                "config": "/models/bernini",
                "num_frames": 8,
            },
        )
        payload = json.loads(result.content[0].text)
        assert payload["success"] is True
        assert payload["output"]["backend"] == "bernini"
        media_tools.bernini.generate_video.assert_called_once()


@pytest.mark.anyio
async def test_mcp_security_denial_is_returned(mcp_server, media_tools):
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        result = await client.call_tool(
            "generate_image_comfyui",
            {
                "tenant_id": "tenant-1",
                "agent_id": "agent-1",
                "roles": ["readonly"],
                "prompt": "a red cube",
            },
        )
        payload = json.loads(result.content[0].text)
        assert payload["success"] is True
        # Registry invocation succeeds; business-level denial is in output.
        assert payload["output"]["success"] is False
        assert "Access denied" in payload["output"]["error"]
        media_tools.comfyui.run_workflow.assert_not_called()


@pytest.mark.anyio
async def test_mcp_audit_records_media_call(mcp_server, media_tools):
    before = len(mcp_server.security.audit.get_records())
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        await client.call_tool(
            "generate_video_hyperframes",
            {
                "tenant_id": "tenant-audit",
                "agent_id": "agent-audit",
                "html": "<h1>Audit</h1>",
            },
        )
    after = len(mcp_server.security.audit.get_records())
    assert after > before
    from security.audit import AuditCategory

    media_records = mcp_server.security.audit.get_records(category=AuditCategory.MEDIA)
    assert len(media_records) >= 1
    assert media_records[-1].tenant_id == "tenant-audit"


@pytest.mark.anyio
async def test_mcp_default_tenant_agent_injected(mcp_server, media_tools):
    async with create_connected_server_and_client_session(mcp_server.get_server()) as client:
        # Omit tenant_id/agent_id; defaults should be injected.
        result = await client.call_tool(
            "generate_video_hyperframes",
            {"html": "<h1>Defaults</h1>"},
        )
        payload = json.loads(result.content[0].text)
        assert payload["success"] is True
