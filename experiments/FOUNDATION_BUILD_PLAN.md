# Foundation Build Plan: ACN Agent-Driven Media Generation

**Goal:** Build an end-to-end foundation where ACN agents can generate media via ComfyUI, HyperFrames, and (later) Bernini. Foundation must be tested locally without GPU. Bernini is the last engine to wire in.

**Method:** Build in locked phases. Each phase has a **sensor** — a concrete check that must pass before moving on. This prevents drift.

---

## Research-backed blocks we will use

### Block A: ComfyUI API client
From [ViewComfy production ComfyUI API guide](https://www.viewcomfy.com/blog/building-a-production-ready-comfyui-api):

```python
def queue_prompt(prompt, client_id, server_address):
    data = {"prompt": prompt, "client_id": client_id}
    response = requests.post(f"http://{server_address}/prompt", json=data)
    return response.json()

def get_history(prompt_id, server_address):
    response = requests.get(f"http://{server_address}/history/{prompt_id}")
    return response.json()

def get_image(filename, subfolder, folder_type, server_address):
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    response = requests.get(f"http://{server_address}/view", params=params)
    return response.content

def upload_image(input_path, filename, server_address, folder_type="input"):
    with open(input_path, 'rb') as file:
        files = {"image": (filename, file, 'image/png')}
        data = {"type": folder_type, "overwrite": "false"}
        url = f"http://{server_address}/upload/image"
        response = requests.post(url, files=files, data=data)
        return response.content
```

We will wrap this into a `ComfyUIClient` class with WebSocket progress tracking and dry-run mode.

### Block B: HyperFrames composition template
From [HyperFrames README](https://github.com/heygen-com/hyperframes):

```html
<div id="stage" data-composition-id="launch" data-start="0" data-width="1920" data-height="1080">
  <h1 id="title" class="clip" data-start="1" data-duration="4" data-track-index="1">Launch day</h1>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.from("#title", { opacity: 0, y: 40, duration: 0.8 }, 1);
    window.__timelines = window.__timelines || {};
    window.__timelines.launch = tl;
  </script>
</div>
```

Rendered with:

```bash
npx hyperframes render --variables '{"title":"Q4 Report"}' --output q4.mp4
```

We will build a Python `HyperFramesRenderer` that writes `index.html` + `variables.json`, shells out to `npx hyperframes render`, and returns the MP4 path.

### Block C: Agent tool registration
From existing `acn/src/agents/twin_tools.py`:

```python
registry.register(TwinTool(
    name="generate_image_comfyui",
    description="Generate an image using ComfyUI",
    twin_id="media_agent",
    handler=handler,
    input_schema=InputSchema,
    output_schema=OutputSchema,
    tags=["generation", "image"],
))
```

We will register one tool per backend capability and let a `ToolCallingTwin` agent pick the right one.

---

## Phase 1 — Refactor media_service.py ✅ COMPLETE

**What:** Split into three focused adapters:
- `ComfyUIClient` (HTTP API, workflow runner)
- `HyperFramesRenderer` (HTML → MP4)
- `BerniniRunner` (already drafted; mark as GPU-only)

**Sensor:**
```bash
python -c "from generation.media_service import ComfyUIClient, HyperFramesRenderer, BerniniRunner; print('imports ok')"
```

**Result:** `Phase 1 sensor: imports OK`

**Code block placed:**
```python
class HyperFramesRenderer:
    def __init__(self, project_dir: str, npx_cmd: str = "npx"):
        self.project_dir = Path(project_dir)
        self.npx_cmd = npx_cmd

    def render(self, html: str, variables: dict, output_name: str) -> MediaResult:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        (self.project_dir / "index.html").write_text(html, encoding="utf-8")
        (self.project_dir / "variables.json").write_text(json.dumps(variables), encoding="utf-8")
        cmd = [
            self.npx_cmd, "--yes", "hyperframes@0.6.97", "render",
            "--variables-file", str(self.project_dir / "variables.json"),
            "--output", str(self.project_dir / output_name),
        ]
        subprocess.run(cmd, cwd=self.project_dir, check=True)
        return MediaResult(success=True, output_path=str(self.project_dir / output_name), backend="hyperframes")
```

---

## Phase 2 — Add security-aware media tools ✅ COMPLETE

**What:** Create `generation/media_tools.py` tools:
- `generate_image_comfyui`
- `generate_video_hyperframes`
- `generate_video_comfyui` (scaffold)
- `generate_image_bernini` (dry-run only until GPU)
- `generate_video_bernini` (dry-run only until GPU)

Each tool accepts `tenant_id`, `agent_id`, and calls `SecurityManager.authorize` + `audit.log`.

**Sensor:**
```bash
python3 -m pytest acn/tests/generation/test_media_tools.py -v
```

**Result:** 13 passed.

**Code block placed:**
```python
class MediaGenerationTools:
    def __init__(self, security, comfyui_client, hyperframes_renderer, bernini_runner):
        self.security = security
        self.comfyui = comfyui_client
        self.hyperframes = hyperframes_renderer
        self.bernini = bernini_runner

    def register_all(self, registry, twin_id="media_agent"):
        ...
```

---

## Phase 2b — Model Context Protocol (MCP) bridge (MANDATORY) ✅ COMPLETE

**What:** Expose ACN media tools via the Model Context Protocol so any MCP-compatible client (Claude, GPT, etc.) can invoke them. Use **gopher-mcp** as the reference MCP implementation.

**Research source:** [GopherSecurity/gopher-mcp](https://github.com/GopherSecurity/gopher-mcp.git) — C++ MCP SDK with Go/Python bindings, transport support (stdio/SSE/WebSocket/TCP), and production features.

**Deliverables:**
1. ✅ Clone `gopher-mcp` into `experiments/gopher-mcp/`.
2. ✅ Add `generation/mcp_server.py` that:
   - Creates an MCP server (stdio or HTTP+SSE transport)
   - Reads `TwinToolRegistry` definitions
   - Exposes each media tool as an MCP tool with JSON schema
   - Routes every call through `SecurityManager.authorize` + audit
3. ✅ Tests in `acn/tests/generation/test_mcp_bridge.py`.

**Sensor:**
```bash
python3 -m pytest acn/tests/generation/test_mcp_bridge.py -v
```

**Result:** 14 passed.

**Code block placed:**
```python
class MediaMcpServer:
    def __init__(self, tool_registry: TwinToolRegistry, security: SecurityManager, ...):
        self.registry = tool_registry
        self.security = security
        self.server = Server(name="acn-media-server")

    async def _list_tools_handler(self, request) -> types.ListToolsResult:
        ...

    async def _call_tool_handler(self, tool_name: str, arguments: dict):
        arguments.setdefault("tenant_id", self.default_tenant_id)
        arguments.setdefault("agent_id", self.default_agent_id)
        return self.registry.invoke(tool_name, arguments)
```

**Note:** The actual implementation uses the official Anthropic `mcp` Python SDK for the protocol layer while gopher-mcp serves as the architectural reference.

---

## Phase 3 — Build agent orchestration demo

**What:** Create `examples/agent_generates_media.py` that:
1. Creates a `TwinToolRegistry`
2. Registers media tools
3. Creates a `ToolCallingTwin` agent
4. Agent receives a task: "Make a 10-second product intro for Sukha"
5. Agent picks `generate_video_hyperframes`
6. Tool runs and renders a real MP4 locally

**Sensor:**
```bash
python examples/agent_generates_media.py
# Output: a real MP4 file in outputs/agent_media/
```

**Code block to place:**
```python
agent = ToolCallingTwin(
    agent_id="media_agent_1",
    name="Media Producer",
    cluster="generation",
    twin_module_path="twins.cognitive_models.noah_shinn",
    twin_class_name="NoahShinnTwin",
    tool_registry=registry,
)

result = agent.call_tool("generate_video_hyperframes", prompt="Sukha — AI that doesn't give you anxiety")
assert result.success
```

---

## Phase 4 — Add tests and documentation

**What:**
- Unit tests for each adapter with mocked subprocess / HTTP
- Integration test that actually renders HyperFrames
- `docs/generation/AGENT_MEDIA_INTEGRATION.md`
- Updated checklist for Bernini GPU phase

**Sensor:**
```bash
python -m pytest acn/tests/generation -v
# expect: all pass, including real HyperFrames render test
```

---

## Phase 5 — Bernini engine (GPU, last) — PLANNED ✅

Only after Phases 1–4 sensors are green.

**Plan:** See [`GPU_VM_DEPLOYMENT_PLAN.md`](GPU_VM_DEPLOYMENT_PLAN.md) for full inventory, cost estimates, launch command, and validation sensors.

**What:**
- Launch GPU VM (`gpu_1x_a6000` recommended for 1.3B, `gpu_1x_a100` for 14B)
- Run `experiments/vm_setup.sh`
- Download Bernini-R 1.3B, IndicConformer, IndicTrans2
- Add Bernini tool tests on GPU
- Update `MediaGenerationTools` to use real Bernini runner

**Sensor:**
```bash
python infer_single_gpu.py --config pretrained_models/Bernini-R-1.3B-Diffusers \
    --case assets/testcases/t2i/t2i.json --num_frames 1 --guidance_mode t2v_apg
# expect: image file produced
```

---

## Anti-drift rules

1. **No GPU spending until Phase 5.**
2. **Every phase ends with a sensor command that must pass.**
3. **No adding new backends mid-phase.**
4. **Each code block comes from a researched source and is cited.**
5. **Tests first for every new public API.**
6. **MCP bridge (Phase 2b) is mandatory before agent demo (Phase 3).**

---

## Approval

Confirm:
1. Start Phase 2b (MCP bridge) now, or proceed directly to Phase 3 agent demo and fold MCP in later?
2. Any backend priority change?
3. Any feature to drop from scope?
