# tests/harness/test_deerflow_enhanced_swarm.py
"""
Integration test: DeerFlow-enhanced conscious agent swarm.

Demonstrates:
1. SwarmOrchestrator with task decomposition
2. ConsciousAgents with context isolation
3. SandboxAgent code execution
4. CognitiveSkill registration + loading
5. Cross-agent communication + critique
6. Consensus detection (including conformity alert)
7. Final synthesis report

Principle: In God we trust. All others must bring data.
"""

from agents.conscious_agent import ConsciousAgent, AgentGoal
from agents.sandbox_agent import SandboxAgent
from agents.cognitive_skill import SkillRegistry, CognitiveSkill
from agents.swarm_orchestrator import SwarmOrchestrator, SwarmTask
from harness.awareness import AwarenessLevel
from conftest import default_agent_kwargs


def test_deerflow_enhanced_swarm():
    """End-to-end test of the DeerFlow-enhanced conscious agent swarm."""
    print("\n" + "=" * 60)
    print("DEERFLOW-ENHANCED CONSCIOUS AGENT SWARM TEST")
    print("=" * 60)

    # ── Setup ────────────────────────────────────────────────────────
    orchestrator = SwarmOrchestrator()
    skill_registry = SkillRegistry()

    # ── Register Skills ──────────────────────────────────────────────
    research_skill = CognitiveSkill(
        name="deep-research",
        description="Conduct deep research with web search and paper analysis",
        citations=["Shinn2023", "Besta2024"],
        workflow=(
            "1. Search web for latest evidence\n"
            "2. Fetch and analyze top 5 papers\n"
            "3. Extract key findings with citations\n"
            "4. Cross-reference with existing knowledge\n"
            "5. Synthesize structured report"
        ),
        tools=["SearchWeb", "FetchURL", "Shell"],
        inputs={"topic": "str", "depth": "int"},
        outputs={"report": "str", "citations": "list"},
    )
    skill_registry.register(research_skill)

    verification = skill_registry.verify_skill("deep-research")
    assert verification["valid"]
    print(f"✅ Skill registered: {research_skill.name}")
    print(f"   Citations verified: {verification['citations_verified']}")

    # ── Spawn Agents ─────────────────────────────────────────────────
    agent_video = ConsciousAgent(
        agent_id="agent-video-001",
        name="VideoResearcher",
        cluster="video-gnn",
        awareness_level=AwarenessLevel.FULL,
        context_scope={"domain": "video-understanding", "tools": ["SearchWeb"]},
        **default_agent_kwargs("agent-video-001"),
    )

    agent_stream = ConsciousAgent(
        agent_id="agent-stream-001",
        name="StreamResearcher",
        cluster="streaming-reflection",
        awareness_level=AwarenessLevel.FULL,
        context_scope={"domain": "real-time-processing"},
        **default_agent_kwargs("agent-stream-001"),
    )

    agent_sandbox = SandboxAgent(
        agent_id="agent-sandbox-001",
        name="CodeExecutor",
        cluster="multi-agent",
        execution_timeout=30,
        **default_agent_kwargs("agent-sandbox-001"),
    )

    # Register with orchestrator
    orchestrator.register_agent(agent_video)
    orchestrator.register_agent(agent_stream)
    orchestrator.register_agent(agent_sandbox)
    print(f"✅ {len(orchestrator.agents)} agents registered with orchestrator")

    # ── Load Skills into Agents ──────────────────────────────────────
    skill_registry.load_into_agent("deep-research", agent_video)
    skill_registry.load_into_agent("deep-research", agent_stream)
    print("✅ Skills loaded into agents")

    # ── Activate Swarm Task ──────────────────────────────────────────
    task = SwarmTask(
        task_id="task-001",
        description="Build a real-time video understanding system",
        required_clusters=["video-gnn", "streaming-reflection", "multi-agent"],
        success_criteria=[
            "Processes video at 30 FPS",
            "Latency under 100ms",
            "Benchmark results verified",
        ],
        min_agents=2,
        max_agents=5,
    )

    activated = orchestrator.activate_task(task)
    print(f"✅ Task activated: {task.description}")
    print(f"   Agents activated: {activated}")

    # ── Agents Think Independently ───────────────────────────────────
    print("\n--- Agent Reasoning ---")
    video_reasoning = agent_video.think()
    print(f"🧠 {agent_video.name}: {video_reasoning.get('proposed_approach', '')[:80]}...")
    print(f"   Confidence: {video_reasoning.get('confidence', 0):.2f}")

    stream_reasoning = agent_stream.think()
    print(f"🧠 {agent_stream.name}: {stream_reasoning.get('proposed_approach', '')[:80]}...")
    print(f"   Confidence: {stream_reasoning.get('confidence', 0):.2f}")

    # ── Sandbox Execution ────────────────────────────────────────────
    print("\n--- Sandbox Execution ---")
    benchmark_code = """
# Simulate benchmark for video processing
import time
start = time.time()
# Simulate processing 100 frames
frames = 100
fps = frames / 0.05  # 50ms for 100 frames = 2000 FPS (simulated)
latency_ms = 50.0 / frames * 1000  # per-frame latency
print(f"fps: {fps:.1f}")
print(f"latency_ms: {latency_ms:.2f}")
"""
    execution = agent_sandbox.execute(
        code=benchmark_code,
        language="python",
        cited_purpose="Verify video processing performance [CITATION: StreamingVLM2026]",
    )
    print(f"✅ {agent_sandbox.name} executed benchmark")
    print(f"   Return code: {execution.return_code}")
    print(f"   Duration: {execution.duration_ms:.2f}ms")
    print(f"   Output: {execution.stdout.strip()[:100]}...")

    # ── Cross-Agent Communication ────────────────────────────────────
    print("\n--- Cross-Agent Communication ---")
    msg = {
        "type": "findings",
        "content": video_reasoning.get("proposed_approach", ""),
        "reasoning": video_reasoning,
    }
    response = agent_video.communicate("agent-stream-001", msg)
    print(f"💬 {agent_video.name} → {agent_stream.name}")
    print(f"   Response: {response.get('critique', 'No critique')[:100]}...")

    # ── Execute Swarm Round ──────────────────────────────────────────
    print("\n--- Swarm Round Execution ---")
    round_result = orchestrator.execute_round("task-001")

    print(f"🔄 Round {round_result['round']} complete")
    print(f"   Consensus: {round_result['consensus']['status']} (score: {round_result['consensus']['score']:.2f})")
    print(f"   Swarm health: {round_result['swarm_health']:.2f}")

    # ── Final Synthesis ──────────────────────────────────────────────
    print("\n--- Final Synthesis ---")
    report = orchestrator.synthesize_report("task-001")
    print(f"📊 Swarm Report for: {report['task_description']}")
    print(f"   Swarm size: {report['swarm_size']}")
    print(f"   Collective health: {report['collective_health']:.2f}")
    print(f"   Total citations: {report['total_citations']}")
    print(f"   Total reasoning steps: {report['total_reasoning_steps']}")
    print(f"   Recommended next steps: {report['recommended_next_steps']}")

    # ── Assertions ───────────────────────────────────────────────────
    assert len(activated) >= 2, "At least 2 agents should be activated"
    assert execution.return_code == 0, "Sandbox execution should succeed"
    assert "fps:" in execution.stdout, "Benchmark should report FPS"
    assert round_result["swarm_health"] > 0, "Swarm health should be positive"
    assert len(report["agent_reports"]) > 0, "Should have agent reports"

    print("\n✅ ALL ASSERTIONS PASSED")
