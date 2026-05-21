# Autonomous Cognitive Network (ACN) — Architecture

**Version:** 0.1.0 (Research Phase → Architecture Phase)  
**Date:** 2026-05-07  
**Principles:** SOLID, DRY, KISS  
**Status:** Architecture proposed. ADRs pending Council of Ten approval.

---

## 1. Design Principles

### SOLID

| Principle | Application in ACN |
|-----------|-------------------|
| **S**ingle Responsibility | Each block does exactly one thing. Perception senses. Graph Memory stores. Cognition reasons. Generation synthesizes. Consensus validates. Framework routes. |
| **O**pen/Closed | Core ports (interfaces) are stable. New capabilities are added via new adapters implementing existing ports, never by modifying ports. |
| **L**iskov Substitution | Any adapter implementing a port is interchangeable. Swap Deepgram STT for Whisper without changing callers. |
| **I**nterface Segregation | Ports are small and focused. `STTPort` has 3 methods, not 30. Blocks depend only on the ports they need. |
| **D**ependency Inversion | Blocks depend on `ports` (abstractions), never on `infrastructure` (concretions). The assembler wires them together. |

### DRY (Don't Repeat Yourself)

| Duplication Risk | Solution |
|-----------------|----------|
| Message schemas repeated across blocks | Central `shared/protocols/` — one schema definition, all blocks import |
| Error handling patterns | Central `shared/exceptions/` — `ByzantineFault`, `TemporalViolation`, `ConsensusTimeout` |
| Utility functions (logging, serialization) | Central `shared/utils/` — used by all blocks |
| Configuration parsing | Central `config/` — one loader, all blocks read their section |

### KISS (Keep It Simple, Stupid)

| Complexity Risk | KISS Response |
|----------------|---------------|
| 6-layer governance architecture | Start with 2 layers: Core Consensus + Safety Checks. Add layers only when proven necessary. |
| Triple consensus (HACN + CP-WBFT + DecentLLMs) | Phase 1: Simple majority with temporal audit. Phase 2: Add CP-WBFT weighting. Phase 3: Add DecentLLMs trust overlay. |
| 3-tier memory (Working + Episodic + Semantic) | Phase 1: Single PTKG store. Phase 2: Add working memory cache. Phase 3: Add semantic distillation. |
| Dynamic GNN topology rewiring | Phase 1: Static spoke topologies per task type. Phase 2: Add G-Designer optimization. |

---

## 2. Directory Structure

```
acn/
├── src/
│   ├── blocks/                          # SINGLE RESPONSIBILITY: one block = one domain
│   │   ├── perception/                  # Senses: audio, video, text, spatial
│   │   │   ├── __init__.py
│   │   │   ├── ports.py               # PerceptionBlockPort (interface)
│   │   │   ├── domain/                # Domain-specific perception
│   │   │   │   ├── audio/
│   │   │   │   ├── video/
│   │   │   │   └── spatial/
│   │   │   └── service.py             # PerceptionBlock (implements port)
│   │   │
│   │   ├── graph_memory/              # Stores: temporal knowledge graphs
│   │   │   ├── __init__.py
│   │   │   ├── ports.py               # GraphMemoryBlockPort (interface)
│   │   │   ├── domain/                # Storage backends
│   │   │   │   ├── ptkg/              # Periodic Temporal KG
│   │   │   │   ├── wsgg/              # World Scene Graph
│   │   │   │   └── session_forest/    # Per-session snapshot trees
│   │   │   └── service.py             # GraphMemoryBlock (implements port)
│   │   │
│   │   ├── cognition/                 # Reasons: planning, reflection, consensus
│   │   │   ├── __init__.py
│   │   │   ├── ports.py               # CognitionBlockPort (interface)
│   │   │   ├── domain/
│   │   │   │   ├── reasoning/         # ReAct, Tree of Thoughts, CoALA
│   │   │   │   ├── reflection/        # Reflexion, Self-Refine
│   │   │   │   └── consensus/         # CP-WBFT, voting, trust overlay
│   │   │   └── service.py             # CognitionBlock (implements port)
│   │   │
│   │   ├── generation/                # Synthesizes: video, audio, text
│   │   │   ├── __init__.py
│   │   │   ├── ports.py               # GenerationBlockPort (interface)
│   │   │   ├── domain/
│   │   │   │   ├── video/             # Runway, Veo, Wan integrations
│   │   │   │   ├── audio/             # TTS, music generation
│   │   │   │   └── text/              # Summarization, dialogue
│   │   │   └── service.py             # GenerationBlock (implements port)
│   │   │
│   │   ├── consensus/                 # Validates: Byzantine tolerance, safety
│   │   │   ├── __init__.py
│   │   │   ├── ports.py               # ConsensusBlockPort (interface)
│   │   │   ├── domain/
│   │   │   │   ├── byzantine/         # CP-WBFT, PBFT voting
│   │   │   │   ├── safety/            # G-Safeguard, NetSafe pruning
│   │   │   │   ├── deception/         # MAD-Spear, alignment faking detection
│   │   │   │   └── temporal_audit/    # Temporal Auditor (11th persona)
│   │   │   └── service.py             # ConsensusBlock (implements port)
│   │   │
│   │   └── framework/                 # Routes: topology, protocols, execution
│   │       ├── __init__.py
│   │       ├── ports.py               # FrameworkBlockPort (interface)
│   │       ├── domain/
│   │       │   ├── topology/          # Hub-and-spoke, G-Designer
│   │       │   ├── protocols/         # A2A, MCP, custom graph protocol
│   │       │   ├── durable/           # Dapr-style checkpointing
│   │       │   └── discovery/         # Agent Cards, capability registry
│   │       └── service.py             # FrameworkBlock (implements port)
│   │
│   ├── shared/                          # DRY: shared across all blocks
│   │   ├── __init__.py
│   │   ├── ports/                       # All block interfaces (Dependency Inversion)
│   │   │   ├── __init__.py
│   │   │   ├── base_block.py          # Abstract base for all blocks
│   │   │   ├── perception.py          # PerceptionBlockPort
│   │   │   ├── graph_memory.py        # GraphMemoryBlockPort
│   │   │   ├── cognition.py           # CognitionBlockPort
│   │   │   ├── generation.py          # GenerationBlockPort
│   │   │   ├── consensus.py           # ConsensusBlockPort
│   │   │   └── framework.py           # FrameworkBlockPort
│   │   │
│   │   ├── models/                      # Shared data structures
│   │   │   ├── __init__.py
│   │   │   ├── events.py              # Event, EventType, EventStream
│   │   │   ├── graph.py               # GraphNode, GraphEdge, TemporalGraph
│   │   │   ├── consensus.py           # Vote, VoteWeight, ConsensusResult
│   │   │   ├── temporal.py            # HLCTimestamp, CausalChain
│   │   │   └── trust.py               # TrustScore, BeliefState
│   │   │
│   │   ├── protocols/                   # Message schemas (DRY: one definition)
│   │   │   ├── __init__.py
│   │   │   ├── a2a.py                 # Agent-to-Agent protocol
│   │   │   ├── mcp.py                 # Model Context Protocol
│   │   │   ├── evsg.py                # Event-based Video Scene Graph
│   │   │   ├── ptkg.py                # Periodic Temporal Knowledge Graph
│   │   │   └── graph_message.py       # Custom graph protocol envelope
│   │   │
│   │   ├── exceptions/                  # Centralized error taxonomy
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # ACNException
│   │   │   ├── byzantine.py           # ByzantineFault, ConsensusFailure
│   │   │   ├── temporal.py            # TemporalViolation, ClockSkewDetected
│   │   │   ├── safety.py              # SafetyViolation, GuardrailTriggered
│   │   │   └── network.py             # TopologyError, ProtocolMismatch
│   │   │
│   │   └── utils/                       # Shared utilities
│   │       ├── __init__.py
│   │       ├── logging.py             # Structured logging with HLC timestamps
│   │       ├── serialization.py       # JSON + protobuf helpers
│   │       ├── validation.py          # Schema validation
│   │       └── metrics.py             # Prometheus-compatible metrics
│   │
│   ├── infrastructure/                  # Adapters: concrete implementations of ports
│   │   ├── __init__.py
│   │   ├── stt/
│   │   │   ├── __init__.py
│   │   │   ├── deepgram.py            # Implements STTPort (current: voice-revenge)
│   │   │   └── whisper.py             # Alternative STTPort implementation
│   │   ├── tts/
│   │   │   ├── __init__.py
│   │   │   ├── deepgram_aura.py       # Implements TTSPort
│   │   │   └── bulbul.py              # Telugu TTS (voice-revenge)
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── azure_openai.py        # Implements LLMPort
│   │   │   ├── qwen_omni.py           # Omni-modal backbone
│   │   │   └── gemini.py              # Alternative LLMPort
│   │   ├── graph_db/
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_adapter.py       # Graph DB port implementation
│   │   │   └── pglite_adapter.py      # Lightweight graph (current: gbrain)
│   │   ├── streaming/
│   │   │   ├── __init__.py
│   │   │   └── websocket_handler.py   # WebSocket transport
│   │   └── video_gen/
│   │       ├── __init__.py
│   │       ├── runway_gen4.py         # Video generation adapter
│   │       └── veo31.py               # Alternative video generation
│   │
│   └── gateway/                         # Entry point: API, load balancing, routing
│       ├── __init__.py
│       ├── api.py                       # FastAPI/Flask entry point
│       ├── session_manager.py           # Per-session state isolation
│       └── health.py                    # Health checks for all blocks
│
├── tests/
│   ├── __init__.py
│   ├── unit/                            # Single component tests
│   │   ├── blocks/
│   │   ├── shared/
│   │   └── infrastructure/
│   ├── integration/                     # Cross-component tests
│   │   ├── block_to_block/            # e.g., Perception → Graph Memory
│   │   └── protocol/                  # A2A, MCP message round-trips
│   ├── consensus/                       # Byzantine fault tolerance tests
│   │   ├── test_byzantine_1_fault.py  # 1 faulty block in 4
│   │   ├── test_conformity_attack.py  # MAD-Spear scenarios
│   │   ├── test_temporal_drift.py     # Clock skew detection
│   │   └── test_round_block.py        # Round block problem scenarios
│   └── e2e/                             # End-to-end scenarios
│       ├── test_brand_memory.py       # Cross-modal brand memory
│       ├── test_self_healing.py       # Self-healing content pipeline
│       └── test_litigation_graph.py   # Temporal litigation graph
│
├── docs/
│   ├── decisions/                       # ADRs (Architecture Decision Records)
│   │   ├── ADR-001-consensus-protocol.md
│   │   ├── ADR-002-communication-topology.md
│   │   ├── ADR-003-temporal-consistency.md
│   │   ├── ADR-004-memory-architecture.md
│   │   └── ...
│   ├── research/                        # All research outputs
│   │   ├── bfs_landscape/
│   │   ├── digital_twin_profiles/
│   │   └── bidirectional_analysis/
│   ├── architecture/
│   │   ├── ARCHITECTURE.md            # This file
│   │   ├── BLOCKS.md                  # Block-level deep dive
│   │   ├── PORTS.md                   # Interface specifications
│   │   └── PROTOCOLS.md               # Message format specifications
│   └── api/                             # API documentation
│
├── config/
│   ├── default.yaml                     # Default configuration
│   ├── development.yaml                 # Dev overrides
│   ├── production.yaml                  # Prod overrides
│   └── blocks/                          # Per-block config
│       ├── perception.yaml
│       ├── graph_memory.yaml
│       ├── cognition.yaml
│       ├── generation.yaml
│       ├── consensus.yaml
│       └── framework.yaml
│
├── scripts/
│   ├── bootstrap.py                     # Initialize network from config
│   ├── run_tests.py                     # Test runner with consensus scenarios
│   └── deploy.py                        # Deployment orchestration
│
├── pyproject.toml                       # Python dependencies
├── Dockerfile                           # Container definition
└── README.md                            # Project overview
```

---

## 3. Block Interface Design (Ports)

### Design Rule: Each port has ≤5 methods

```python
# shared/ports/base_block.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class BlockPort(ABC):
    """Base interface for all blocks. KISS: every block has lifecycle + health."""
    
    @property
    @abstractmethod
    def block_id(self) -> str:
        """Unique block identifier."""
        ...
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize with configuration."""
        ...
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Return health status: {healthy: bool, latency_ms: float, details: dict}."""
        ...
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Graceful shutdown."""
        ...
```

```python
# shared/ports/perception.py
from typing import AsyncIterator
from shared.models.events import SensoryEvent
from shared.models.graph import TemporalGraph

class PerceptionBlockPort(BlockPort):
    """Interface for the Perception Block.
    
    SINGLE RESPONSIBILITY: Convert raw sensory input into structured events.
    No reasoning. No generation. Just sense and structure.
    """
    
    async def ingest(self, stream: AsyncIterator[bytes]) -> AsyncIterator[SensoryEvent]:
        """Ingest raw sensory stream → emit structured events."""
        ...
    
    async def query_scene(self, query: str, timestamp: HLCTimestamp) -> TemporalGraph:
        """Query the current scene graph at a specific time."""
        ...
```

```python
# shared/ports/graph_memory.py
from typing import Optional
from shared.models.graph import TemporalGraph, GraphQuery
from shared.models.temporal import HLCTimestamp

class GraphMemoryBlockPort(BlockPort):
    """Interface for the Graph Memory Block.
    
    SINGLE RESPONSIBILITY: Store, retrieve, and evolve temporal knowledge graphs.
    """
    
    async def store(self, graph_fragment: TemporalGraph, 
                    timestamp: HLCTimestamp) -> None:
        """Store a graph fragment with temporal annotation."""
        ...
    
    async def query(self, query: GraphQuery, 
                    time_range: tuple[HLCTimestamp, HLCTimestamp]) -> TemporalGraph:
        """Query graph state within a time range."""
        ...
    
    async def unlearn(self, entity_id: str, 
                      reason: str) -> None:
        """Mark entity as unlearned (confidence → 0, not deleted)."""
        ...
```

```python
# shared/ports/cognition.py
from shared.models.consensus import Vote, ConsensusResult
from shared.models.events import Event

class CognitionBlockPort(BlockPort):
    """Interface for the Cognition Block.
    
    SINGLE RESPONSIBILITY: Reason, plan, and coordinate cross-block decisions.
    """
    
    async def reason(self, context: Event) -> Event:
        """Process an event through reasoning pipeline → output decision event."""
        ...
    
    async def propose(self, proposal: Event) -> Vote:
        """Propose a cross-block action → return weighted vote."""
        ...
    
    async def reflect(self, outcome: Event) -> None:
        """Reflect on an outcome → update internal models."""
        ...
```

```python
# shared/ports/generation.py
from typing import AsyncIterator
from shared.models.events import GenerationRequest, GenerationResult

class GenerationBlockPort(BlockPort):
    """Interface for the Generation Block.
    
    SINGLE RESPONSIBILITY: Synthesize multi-modal content from structured requests.
    """
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate content from structured request."""
        ...
    
    async def stream_generate(self, request: GenerationRequest) -> AsyncIterator[bytes]:
        """Stream generation output for real-time scenarios."""
        ...
```

```python
# shared/ports/consensus.py
from typing import List
from shared.models.consensus import Vote, ConsensusResult, TrustReport
from shared.models.temporal import HLCTimestamp

class ConsensusBlockPort(BlockPort):
    """Interface for the Consensus Block.
    
    SINGLE RESPONSIBILITY: Validate decisions, detect bad actors, maintain trust.
    """
    
    async def validate(self, votes: List[Vote], 
                       deadline: HLCTimestamp) -> ConsensusResult:
        """Validate a set of votes → return consensus or rejection."""
        ...
    
    async def audit(self, block_id: str) -> TrustReport:
        """Audit a block's trustworthiness."""
        ...
    
    async def report_temporal(self, violation: TemporalViolation) -> None:
        """Report a temporal violation to the Temporal Auditor."""
        ...
```

```python
# shared/ports/framework.py
from typing import List, Optional
from shared.models.events import Event
from shared.protocols.a2a import AgentCard

class FrameworkBlockPort(BlockPort):
    """Interface for the Framework Block.
    
    SINGLE RESPONSIBILITY: Route messages, manage topology, enable discovery.
    """
    
    async def send(self, event: Event, 
                   destination: str) -> None:
        """Send event to destination block via optimal topology path."""
        ...
    
    async def discover(self, capability: str) -> List[AgentCard]:
        """Discover blocks that provide a given capability."""
        ...
    
    async def rewire(self, task_embedding: bytes) -> None:
        """Rewire topology for a task (Phase 2: G-Designer integration)."""
        ...
```

---

## 4. Message Flow (How Blocks Talk)

### 4.1 Normal Operation: Brand Memory Scenario

```
User: "The burger was cold."

Voice (Perception) ──[SensoryEvent: audio_transcript="burger was cold"]──> Framework
Framework ──routes──> Cognition
Cognition ──[Query: find_video_for_entity("burger", T-5min)]──> Graph Memory
Graph Memory ──[TemporalGraph: video_segment_id="abc123", timestamp=T-5min]──> Cognition
Cognition ──[Proposal: link_complaint_to_video]──> Consensus
Consensus ──[CP-WBFT vote: Voice + Video + Knowledge agree]──> Cognition
Cognition ──[Store: causal_edge(complaint → video_segment)]──> Graph Memory
Graph Memory ──ack──> Cognition
Cognition ──[ResponseEvent: "Noted. Checking kitchen footage."]──> Framework
Framework ──routes──> Voice
Voice ──TTS──> User: "Noted, sir. We'll check what happened."
```

### 4.2 Byzantine Detection: Round Block Scenario

```
Video (Generation) ──[Proposal: template="off_brand_meme"]──> Consensus
Consensus ──[CP-WBFT vote]──> collects votes
    Voice: "reject" (confidence=0.9)
    Knowledge: "reject" (confidence=0.85)
    Temporal: "approve" (confidence=0.99)  ← SUSPICIOUS: always approves
Consensus ──[MAD-Spear: conformity check]──> Temporal agrees too readily
Consensus ──[DecentLLMs: update trust]──> Temporal trust_score -= 0.1
Consensus ──[ConsensusResult: REJECTED]──> Video
Consensus ──[Alert: Temporal block conformity risk]──> Cognition
Cognition ──[Store: alert_edge]──> Graph Memory
```

---

## 5. Configuration Design (KISS)

```yaml
# config/default.yaml — one file, all defaults

network:
  blocks:
    - perception
    - graph_memory
    - cognition
    - generation
    - consensus
    - framework
  
  consensus:
    protocol: "simple_majority"  # Phase 1: KISS
    # protocol: "cp_wbft"       # Phase 2: weighted voting
    fault_tolerance: 1
    timeout_ms: 500
  
  temporal:
    clock_sync: "ntp"
    # clock_sync: "ptp"         # Phase 2: microsecond precision
    health_probe_interval_sec: 10
    auditor_sampling_rate: 0.1  # 10% of decisions
  
  topology:
    mode: "static_hub_spoke"    # Phase 1: KISS
    # mode: "g_designer"        # Phase 2: learned topology
    hub_block: "framework"
    max_spoke_size: 4
  
  memory:
    backend: "ptkg"             # Phase 1: single store
    # tiers:                   # Phase 2: 3-tier Smṛti
    #   working_ttl_sec: 300
    #   episodic_half_life_hours: 6
    #   semantic_reconsensus_threshold: 3

blocks:
  perception:
    stt_provider: "deepgram"
    vad_enabled: true
    audio_format: "mulaw"
    sample_rate: 8000
  
  graph_memory:
    db: "neo4j"
    # db: "pglite"              # gbrain current
    index_temporal: true
  
  cognition:
    llm_provider: "azure_openai"
    model: "gpt-4o-mini"
    # llm_provider: "qwen_omni"  # Phase 2: omni-modal
    max_turns: 50
  
  generation:
    video_provider: "runway_gen4"
    # video_provider: "veo31"   # Alternative
    brand_safety_enabled: true
  
  consensus:
    guardrails_parallel: true
    deception_detection: "stress_test"  # Phase 1: periodic
    # deception_detection: "continuous"   # Phase 2: real-time
  
  framework:
    protocol: "a2a"
    mcp_enabled: true
    durable_execution: true
```

---

## 6. Testing Strategy

### Unit Tests (Fast, Isolated)
```python
# tests/unit/blocks/test_perception.py
def test_perception_ingests_audio():
    block = PerceptionBlock(config={"stt": "mock"})
    events = list(block.ingest(b"fake_audio"))
    assert len(events) == 1
    assert events[0].type == EventType.TRANSCRIPT
```

### Integration Tests (Cross-Block)
```python
# tests/integration/test_perception_to_graph_memory.py
async def test_audio_transcript_stored_in_graph():
    perception = PerceptionBlock(config={...})
    graph_memory = GraphMemoryBlock(config={...})
    
    event = await perception.ingest_one(b"fake_audio")
    await graph_memory.store(event.to_graph_fragment(), event.timestamp)
    
    result = await graph_memory.query(
        GraphQuery(entity="transcript"),
        time_range=(T0, T1)
    )
    assert len(result.nodes) == 1
```

### Consensus Tests (Byzantine Scenarios)
```python
# tests/consensus/test_byzantine_1_fault.py
async def test_network_detects_and_isolates_faulty_block():
    network = TestNetwork(blocks=4, faulty=1)
    
    # Faulty block always proposes "approve"
    network.blocks[2].set_behavior(FaultyBehavior.ALWAYS_APPROVE)
    
    result = await network.consensus.validate(
        votes=network.collect_votes(),
        deadline=hlc_now() + timedelta(ms=500)
    )
    
    assert result.detected_faulty == ["block_2"]
    assert result.decision == "REJECTED"
```

---

## 7. Phase Roadmap (KISS: Start Simple)

| Phase | Goal | What Changes |
|-------|------|-------------|
| **P0** (Now) | Architecture + ADRs | No code. Council deliberation. Port interfaces defined. |
| **P1** (Month 1) | Single block, single flow | Perception → Cognition → Generation for voice-only. No consensus. No graph memory. |
| **P2** (Month 2) | Add Graph Memory + Consensus | Perception → Graph Memory → Cognition → Consensus → Generation. Simple majority voting. |
| **P3** (Month 3) | Add Temporal Auditor + Byzantine | CP-WBFT weighted voting. Temporal Auditor (11th persona). HLC timestamps. |
| **P4** (Month 4) | Add Video + Cross-Modal | Video perception. Cross-modal brand memory. Multi-modal generation. |
| **P5** (Month 5) | Production Hardening | Dapr durable execution. G-Designer topology. DecentLLMs trust overlay. 1M+ session scaling. |

---

## 8. Sanskrit Mapping (For Reference)

| Sanskrit | Component | Port | Phase |
|----------|-----------|------|-------|
| **Śruti** (hearing) | Audio perception | PerceptionBlockPort | P1 |
| **Cakṣus** (sight) | Video perception | PerceptionBlockPort | P4 |
| **Smṛti** (memory) | Graph memory | GraphMemoryBlockPort | P2 |
| **Saṃvedana** (feeling) | Emotion/tone detection | PerceptionBlockPort | P1 |
| **Sphota** (linguistic burst) | LLM reasoning | CognitionBlockPort | P1 |
| **Hṛdaya** (heart) | Rasa-based emotion engine | CognitionBlockPort | P3 |
| **Dhvani** (resonance) | TTS prosody | GenerationBlockPort | P1 |
| **Kāla** (time) | Temporal Auditor | ConsensusBlockPort | P3 |
| **Nyāya** (justice) | Byzantine consensus | ConsensusBlockPort | P3 |
| **Vāhana** (vehicle) | Framework routing | FrameworkBlockPort | P2 |

---

*Architecture Version: 0.1.0*  
*Next: P0 → Council of Ten deliberation on ADRs → Port interface implementation*  
*No production code until ADRs are approved.*
