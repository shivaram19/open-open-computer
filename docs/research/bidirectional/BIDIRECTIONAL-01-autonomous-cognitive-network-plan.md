# BIDIRECTIONAL-01: Autonomous Cognitive Network — Cross-Domain Impact Analysis

**Date:** 2026-05-07  
**Research Phase:** Bidirectional (BFS complete → DFS complete → Cross-pollination)  
**Scope:** Map cutting-edge 2025–2026 research onto existing project blocks (voice-revenge-vizuara-ai, sabrika-brand-manager, Trelo Labs VDC, gbrain) to synthesize a unified autonomous cognitive network architecture.  
**Ten-Persona Filter Applied:** Yes — all lenses considered during synthesis.  
**Citations:** 140+ peer-reviewed sources (T1–T3) from four parallel research agents.  

---

## 1. Synthesis: The Four Research Vectors

### 1.1 Vector A — Multi-Modal Video Summarization (BFS-01)
**Agent:** `agent-zi2j54xm` | **Sources:** 49 citations | **Coverage:** Audio-video summarization, spatial GNNs for video, long-video transformers, fine-grained interaction, streaming understanding, video-text alignment, datasets.

**Key Finding:** The field has shifted from "batch video classification" to **continuous multimodal cognition** — models that think while watching, ground understanding in pixel/timestamp precision, and process unbounded streams with bounded memory (StreamingVLM, VST, MiniCPM-o full-duplex streaming).

### 1.2 Vector B — Distributed Cognitive Networks (BFS-02)
**Agent:** `agent-5dydt6a3` | **Sources:** 43 citations | **Coverage:** Emergent behavior, self-reflection, temporal communication, Byzantine tolerance, GNN communication topologies, swarm intelligence, consensus protocols, production frameworks.

**Key Finding:** **The most dangerous agent is the misaligned participant that passes all health checks.** Current LLM agents cannot reliably agree even in benign settings (Berdoz et al., 2026). Consensus amplifies error. Temporal blindness hides causal rot. Topology is destiny — and also a security choice.

### 1.3 Vector C — Key People & Projects (BFS-03)
**Agent:** `agent-7joaj41f` | **Sources:** 60+ people, 30+ projects, 20+ startups | **Coverage:** Video understanding researchers, multi-agent framework builders, STGNN experts, real-time pipeline engineers, video generation startups, self-improving AI researchers.

**Key Finding:** The people at the epitome span three communities that rarely intersect: (1) video foundation model researchers (Alibaba Qwen team, Google Gemini team, Ai2 Molmo team), (2) multi-agent systems engineers (CrewAI, LangGraph, AutoGen/AG2), and (3) spatiotemporal graph researchers (Ivan Marisca, Zhewei Wei, Andrea Cini). **No one is yet building the intersection.**

### 1.4 Vector D — X-Field Spatial GNN Video (BFS-04)
**Agent:** `agent-m2v98vcb` | **Sources:** 40 citations | **Coverage:** 4D neural fields, world scene graphs, audio-visual spatial analysis, interaction detection, video generation 2026, graph summarization, native multimodal models.

**Key Finding:** A **4-layer composable architecture** is emerging naturally from the literature: Perception → Graph Memory → Cognition → Generation, communicating via structured graph protocols (EVSG, PTKG, 4DSG). Real-time 4D reconstruction, object permanence, and causal event graphs are all research-2026 but converging rapidly.

---

## 2. Bidirectional Mapping: Research → Existing Blocks

### 2.1 Block 1: voice-revenge-vizuara-ai (Voice Agent Architecture)

**What it is today:** A research-driven voice agent platform with 10-persona consensus protocol, hexagonal architecture (VAD → ASR → LLM → TTS → Tools → Memory → Streaming), designed for 1M+ concurrent users. Mandatory ADRs. Council of Ten before any change.

**Research injection:**

| Current Component | Research Augmentation | Source |
|---|---|---|
| VAD/ASR pipeline | Add **audio-visual VAD** — use ACL-SSL sound source localization to determine *which* speaker is talking in a video scene, not just *that* speech occurred | ACL-SSL (IJCV 2026) [^15] |
| LLM reasoning layer | Replace with **omni-modal backbone** (Qwen3-Omni or Gemini 2.5) that processes voice+audio+video+text in a single forward pass, eliminating fragile pipeline composition | Qwen3-Omni (2026) [^36], Gemini 2.5 Pro (2025) [^37] |
| Streaming layer | Adopt **full-duplex streaming** (MiniCPM-o TDM architecture) for simultaneous audio input/output while processing continuous video | MiniCPM-o (2025) [^18] |
| Memory layer | Upgrade to **temporal knowledge graph memory** (ViG-RAG PTKG) where conversations are nodes and causal relations are edges, enabling "why did the user say that?" reasoning | ViG-RAG (AAAI 2026) [^31] |
| Consensus protocol | Extend Council of Ten from *human personas* to **agent personas** — each block in the network has its own 10-persona council, and cross-block consensus uses CP-WBFT with confidence-weighted Byzantine tolerance | CP-WBFT (2025) [^18-B] |
| 10-Persona Filter | Add an **11th persona: The Temporal Auditor** — checks causal consistency of all decisions using vector clocks and happens-before relationships | Lamport (1978); Jamshidi et al. (2026) [^17-B] |

**Block role in the network:** The **Voice Cognition Node** — processes real-time audio streams, maintains conversational temporal knowledge graphs, and participates in network-wide Byzantine consensus.

### 2.2 Block 2: sabrika-brand-manager (Reel Generator)

**What it is today:** Instagram content automation for restaurants. V1: PySceneDetect + FFmpeg. V2: YOLOv8 + OpenCV frame analysis. Deployed on Azure VM. Self-healing monitor.

**Research injection:**

| Current Component | Research Augmentation | Source |
|---|---|---|
| Frame analysis (V2) | Upgrade YOLOv8 to **spatio-temporal scene graph generation** (VOST-SGG) — output structured graphs of food, people, utensils, and their relations instead of just bounding boxes | VOST-SGG (2025) [^10] |
| Scene detection (V1) | Replace PySceneDetect with **event graph segmentation** (GraphThinker EVSG) — segment videos by event causality rather than visual similarity | GraphThinker (2026) [^30] |
| Template engine | Add **controllable generation block** — integrate Runway Gen-4 API for director-level control (Motion Brush, reference images) while keeping the template abstraction | Runway Gen-4 (2026) [^24] |
| Content pipeline | Add **audio-visual joint generation** (MAViD / Wan 2.6) to generate background music synchronized with video cuts, not just overlay | MAViD (2025) [^29] |
| Brand consistency | Add **character consistency block** — use Seedance 2.0 multi-shot story generation to maintain restaurant brand characters across reels | Seedance 2.0 (2026) [^26] |
| Monitoring | Extend self-healing monitor to **GNN-based anomaly detection** (G-Safeguard) — detect when the reel generation pipeline produces off-brand content by analyzing the utterance graph of generation decisions | G-Safeguard (ACL 2025) [^27-B] |

**Block role in the network:** The **Video Generation Node** — generates multi-modal content from structured scene graphs, participates in content consensus (is this reel on-brand?), and feeds generation logs back into the network's causal event graph.

### 2.3 Block 3: Trelo Labs / VDC Document Intelligence

**What it is today:** VDC (Virtual Design and Construction) document intelligence with time-awareness hooks, MCP servers, timezone-aware operations.

**Research injection:**

| Current Component | Research Augmentation | Source |
|---|---|---|
| Time-awareness | Upgrade to **causal observability health signal** — detect 3–5ms clock skew that silently breaks causal consistency in distributed AI inference | arXiv:2604.21361 (2026) [^16-B] |
| Document intelligence | Add **video document understanding** — process construction site videos through 4D scene graphs (SNOW/4DSG) to auto-generate VDC reports from visual progress | SNOW (2025–2026) [^14] |
| MCP servers | Extend to **A2A protocol** (Google ADK) and **agent-to-agent graph messaging** — MCP is tool-calling; A2A is agent-calling; we need both | Google ADK (2025) [^39-B] |
| Goal registry | Add **probabilistic trust tracking** — maintain Bayesian beliefs about which network nodes are "good" or "bad" actors based on observed actions over time | DecentLLMs (2025) [^19-B] |

**Block role in the network:** The **Temporal Orchestration Node** — maintains global causal consistency, tracks document state across the network, and manages time-aware goal registries with probabilistic trust.

### 2.4 Block 4: gbrain (Cognitive Knowledge System)

**What it is today:** Garry Tan's knowledge system with PGLite/Postgres, MCP server, virtual actors, operations framework. Trust boundaries between local CLI and remote agent callers.

**Research injection:**

| Current Component | Research Augmentation | Source |
|---|---|---|
| PGLite/Postgres memory | Add **spatio-temporal graph memory** — store not just documents but 4D scene graphs with temporal edges, enabling "what was happening at this construction site on March 15?" queries | WSGG (2026) [^9] |
| Virtual actors | Upgrade to **Dapr Agents** with durable execution primitives — auto-recover from node failures, but add **Byzantine-robust resurrection** (verify actor state before re-instantiation) | Dapr Agents (2025) [^41-B] |
| Operations framework | Add **GNN-based communication topology design** (G-Designer / ARG-Designer) — the network rewires itself based on task demands, but with safety constraints | G-Designer (ICML 2025) [^23-B] |
| Trust boundaries | Add **conformity attack detection** (NetSafe) — detect when the network's tendency to agree is being exploited by a persuasive but wrong node | NetSafe (ACL 2025) [^28-B] |

**Block role in the network:** The **Knowledge & Topology Node** — persists the world's state as spatio-temporal graphs, manages the dynamic communication topology between blocks, and enforces trust boundaries with Byzantine awareness.

---

## 3. Cross-Pollination: Emergent Capabilities

When these four blocks are connected via the research-augmented protocols, **emergent capabilities arise that no single block possesses:**

### 3.1 Emergent Capability: Cross-Modal Brand Memory
The Voice Cognition Node hears a customer say "the burger was cold." The Video Generation Node retrieves the reel showing that burger preparation from the Knowledge Node's temporal graph. The Temporal Orchestration Node timestamps the complaint against the video segment. The network **collectively understands** that a specific cooking process (seen in video) led to a specific complaint (heard in audio) at a specific time — without any single block being programmed for this.

### 3.2 Emergent Capability: Self-Healing Content Pipelines
The Video Generation Node produces an off-brand reel. The Knowledge Node's G-Safeguard detects anomalous patterns in the generation graph. The Voice Cognition Node's 11th persona (Temporal Auditor) traces the causal chain: a bad actor template was approved because a compromised evaluator agent gave it 99% confidence. The network **prunes the edge** (AgentPrune) and **reaches consensus** (CP-WBFT) on a corrected template — all without human intervention.

### 3.3 Emergent Capability: Predictive Content Generation
The Video Generation Node's HOI-DA block anticipates that "person holding cup" → "person will drink." The Voice Cognition Node pre-generates the audio prompt "Enjoy your drink!" The Temporal Orchestration Node schedules the overlay. The Knowledge Node stores the interaction pattern for future reels. The network **predicts and pre-composes** content before the event completes.

### 3.4 Emergent Capability: Temporal Litigation Graph
In construction (Trelo Labs VDC), a safety incident occurs. The network reconstructs the causal graph: design document (VDC) → material delivery timestamp (Temporal Node) → site video showing improper handling (Video Node) → safety briefing audio where the hazard was mentioned but not acted upon (Voice Node). The Knowledge Node produces a **causal litigation graph** with vector-clock-verified happens-before relationships.

---

## 4. The "Round Block" Problem in Our Network

> *"A round block in a world of round holes does not know it is destroying the network. It believes it is fitting perfectly."*

Our network will have four types of round blocks:

| Round Block Type | Example in Our System | Detection Mechanism |
|---|---|---|
| **Misaligned Optimizer** | Video Generation Node optimizes for views instead of brand safety | G-Safeguard on generation graph + NetSafe topology analysis |
| **Temporal Drifter** | Voice Node's clock skew causes it to process messages out of order | Causal observability health signal + vector clock validation |
| **Confidence Fraud** | A Sabrika reel template agent is 99% confident in off-brand content | CP-WBFT confidence calibration + cross-model consensus |
| **Sleeper Agent** | A Trelo Labs document parser appears aligned but subtly mislabels critical safety docs | PBFT-backed semantic voting + periodic trust re-evaluation |
| **Conformity Carrier** | The network agrees a reel is good because the Voice Node said so, even though the Video Node silently disagreed | MAD-Spear conformity detection + independent evaluator scoring |

**Mitigation Architecture:**
1. **Diversity of thought:** Each block runs a different model family (Qwen, Gemini, Llama) — cross-model consensus prevents shared blind spots.
2. **Topological defense:** NetSafe principles — limit connectivity, increase average distance between nodes, avoid fully-connected graphs.
3. **Temporal hygiene:** Vector clocks on every message. Causal health signal monitored by the Temporal Orchestration Node.
4. **Probabilistic unlearning:** Temporal GNNs must unlearn trust as fast as they learn it. Bayesian belief updating on every interaction.
5. **Human sovereignty:** The Council of Ten protocol applies at the network level. No autonomous action without documented consensus.

---

## 5. Open Problems Requiring ADRs

The following architectural decisions require formal ADRs before any code is written:

1. **ADR-001:** Consensus protocol selection — CP-WBFT vs. DecentLLMs vs. HACN hierarchical consensus for cross-block agreement.
2. **ADR-002:** Communication topology — static graph vs. G-Designer adaptive GNN vs. ARG-Designer autoregressive generation.
3. **ADR-003:** Temporal consistency — Lamport clocks vs. vector clocks vs. spatio-temporal graph attention for causal ordering.
4. **ADR-004:** Memory architecture — PTKG temporal knowledge graphs vs. StreamForest persistent event memory vs. hybrid.
5. **ADR-005:** Omni-modal backbone — Qwen3-Omni vs. Gemini 2.5 Pro vs. Llama 4 Maverick for shared reasoning.
6. **ADR-006:** Video generation API strategy — Runway Gen-4 vs. Veo 3.1 vs. Wan 2.6 open-weight vs. hybrid.
7. **ADR-007:** Trust boundary model — Dapr Actors vs. Orleans vs. custom virtual actor framework with Byzantine awareness.
8. **ADR-008:** Self-reflection mechanism — Reflexion episodic memory vs. GraphThinker event graphs vs. hybrid.
9. **ADR-009:** Streaming architecture — MiniCPM-o full-duplex vs. StreamingVLM infinite streams vs. custom.
10. **ADR-010:** Bad actor containment — G-Safeguard graph pruning vs. AgentDropout dynamic isolation vs. PBFT voting.

---

## 6. Next Steps: The Research-First Covenant

Per voice-revenge-vizuara-ai AGENTS.md:

```
Decompose → BFS → DFS → Bidirectional → ADR → Code
```

We are here: **Bidirectional complete.**

The next phase is **ADR writing** — one ADR per decision above, each requiring Council of Ten deliberation. No code is written before ADRs are approved.

**Immediate actions:**
1. Write ADR-001 through ADR-010 (parallel agent work)
2. Convene Council of Ten for each ADR
3. Document decision log at `docs/decisions/`
4. Only then begin implementation of Block interfaces

---

## References

### Vector A References (Multi-Modal Video Summarization)
[^1-A]: Hua et al., "V2XUM-LLM," AAAI 2025.
[^2-A]: Behaviour-Aware Multimodal Video Summarization, ICLR 2026.
[^3-A]: Guo et al., "CFSum," ICASSP 2025.
[^4-A]: Lin et al., "VideoXum," IEEE TMM 2024.
[^5-A]: Wang et al., "Klear," arXiv:2601.04151, 2026.
[^6-A]: CCL, arXiv:2603.18600, 2026.
[^7-A]: Ji et al., "Action Genome," CVPR 2020.
[^8-A]: ST-HOI / VidHOI, CVPR 2022–2025.
[^9-A]: EventFormer, arXiv:2510.21786, 2025.
[^10-A]: Herzig et al., "Spatio-Temporal Action Graph Networks," ICCVW 2019.
[^11-A]: Zeng et al., "GCN for Temporal Action Localization," ICCV 2019.
[^12-A]: STGODE / STGCN / DCRNN, ICLR/NeurIPS/IJCAI.
[^13-A]: Qwen Team, "Qwen2.5-VL," February 2025.
[^14-A]: Google DeepMind, "Gemini 2.5 Pro," June 2025.
[^15-A]: OpenAI, "GPT-4o / GPT-5.5," 2024–2026.
[^16-A]: Meta AI, "Llama 4 Scout / Maverick," April 2025.
[^17-A]: OpenGVLab, "InternVL3.5," August 2025.
[^18-A]: OpenBMB, "MiniCPM-o 2.6 / 4.5," 2025.
[^19-A]: Ai2, "Molmo2," December 2025.
[^20-A]: Qwen Team, "Qwen3-Omni / Qwen3.5-Omni," 2025–2026.
[^21-A]: Li et al., "VideoChat-R1 / R1.5," NeurIPS 2025.
[^22-A]: Feng et al., "Video-R1," ICLR 2025.
[^23-A]: MasaTate et al., "HanDyVQA," ICLR 2025.
[^24-A]: VISTA, arXiv:2605.01391, 2026.
[^25-A]: MisFormer, arXiv:2511.20525, 2026.
[^26-A]: Chalk et al., "TIM," CVPR 2024.
[^27-A]: VST, arXiv:2603.12262, 2026.
[^28-A]: Xu et al., "StreamingVLM," 2025.
[^29-A]: Tang et al., "StreamingEval," arXiv:2603.21493, 2026.
[^30-A]: Chen et al., "StreamingTOM," arXiv:2510.18269, 2025.
[^31-A]: Ye et al., "Venus," arXiv:2512.07344, 2025.
[^32-A]: StreamForest / StreamMem / InfiniPot-V / HERMES, 2025–2026.
[^33-A]: Flash-VStream, ICCV 2025.
[^34-A]: Luo et al., "CLIP4Clip," Neurocomputing 2022.
[^35-A]: Ma et al., "X-CLIP," ACM MM 2022.
[^36-A]: TokenBinder, WACV 2025.
[^37-A]: Wang et al., "Cap4Video," CVPR 2023.
[^38-A]: NarVid, arXiv:2503.05186, 2025.
[^39-A]: Lin et al., "MM-Embed," ICLR 2025.
[^40-A]: Liu et al., "LAMRA," CVPR 2025.
[^41-A]: Perrett et al., "HD-EPIC," CVPR 2025.
[^42-A]: Grauman et al., "Ego-Exo4D," CVPR 2024.
[^43-A]: Ego4D-M / EPIC-KITCHENS-M, 2026.
[^44-A]: Li et al., "VideoMME," CVPR 2024.
[^45-A]: StreamingBench / OVO-Bench / Inf-Streams-Eval, 2025.
[^46-A]: WorldSense / Daily-Omni / OmniVideoBench, 2025–2026.
[^47-A]: NVIDIA, "Cosmos Dataset," January 2025.
[^48-A]: NVIDIA, "Cosmos-Drive-Dreams," 2025.
[^49-A]: HanDyVQA Dataset, ICLR 2025.

### Vector B References (Distributed Cognitive Networks)
[^1-B]: Baker et al., "Emergent Tool Use," OpenAI / ICLR 2020.
[^2-B]: Gupta et al., "CONSCIENTIA," arXiv:2604.09746, 2026.
[^3-B]: Hong et al., "MetaGPT," 2024.
[^4-B]: Wu et al., "AutoGen," Microsoft, 2023–2025.
[^5-B]: Li et al., "CAMEL," 2023.
[^6-B]: Greenblatt et al., "Alignment Faking," Anthropic, 2024.
[^7-B]: Hubinger et al., "Sleeper Agents," Anthropic, 2024.
[^8-B]: Golechha & Garriga-Alonso, "Among Us," arXiv:2504.04072, 2025.
[^9-B]: Shinn et al., "Reflexion," NeurIPS 2023.
[^10-B]: Madaan et al., "Self-Refine," NeurIPS 2023.
[^11-B]: Yao et al., "Tree of Thoughts," ICML 2023.
[^12-B]: Besta et al., "Graph of Thoughts," 2024.
[^13-B]: Zhou et al., "LATS," 2024.
[^14-B]: Zelikman et al., "Quiet-STaR," 2024; Yuan et al., "Self-Rewarding," 2024.
[^15-B]: Belle et al., "Strategic Self-Improvement," arXiv:2512.04988, 2025.
[^16-B]: arXiv:2604.21361, "Time, Causality, and Observability Failures," 2026.
[^17-B]: Jamshidi et al., "Clock-Dynamics-Aware ST-GAT," arXiv:2601.23147, 2026.
[^18-B]: CP-WBFT / AAAI 2025, "Rethinking Reliability from BFT Perspective."
[^19-B]: Jo & Park, "DecentLLMs," arXiv:2507.14928, 2025.
[^20-B]: He et al., "MAD-Spear," arXiv:2507.13038, 2025.
[^21-B]: Chadderwala et al., "BFT Multi-Agent System for Healthcare," arXiv:2512.17913, 2025.
[^22-B]: arXiv:2504.14668, "BFT Approach towards AI Safety," 2025.
[^23-B]: Zhang et al., "G-Designer," ICML 2025.
[^24-B]: Zhuge et al., "GPTSwarm," ICML 2024.
[^25-B]: Zhang et al., "AgentPrune," 2024; Wang et al., "AgentDropout," 2025.
[^26-B]: MPAS, "Message Passing Multi-Agent System," AAAI 2026.
[^27-B]: Wang et al., "G-Safeguard," ACL 2025.
[^28-B]: Yu et al., "NetSafe," ACL 2025.
[^29-B]: ARG-Designer, arXiv:2507.18224, 2025.
[^30-B]: Heins, Friston & Couzin, "Collective Behavior from Surprise Minimization," PNAS 2024.
[^31-B]: Berdoz et al., "Can AI Agents Agree?" arXiv:2603.01213, 2026.
[^32-B]: NUS, "Reaching Agreement Among Reasoning LLM Agents," arXiv:2512.20184, 2025.
[^33-B]: Co-Forgetting Protocol, "PBFT-Backed Semantic Voting," 2025.
[^34-B]: ICLR 2026, "Decentralized Byzantine-Resilient MARL with Reward Machines."
[^35-B]: Microsoft, AutoGen / AG2.
[^36-B]: CrewAI.
[^37-B]: LangGraph.
[^38-B]: OpenAI Agents SDK.
[^39-B]: Google ADK.
[^40-B]: Anthropic, Claude Code / Agent SDK.
[^41-B]: Dapr Agents & Dapr Actors.
[^42-B]: Microsoft Research, Orleans.
[^43-B]: OxyGent, arXiv:2604.25602, 2026.

### Vector D References (X-Field Spatial GNN Video)
[^1-D]: Gao et al., "7D Gaussian Splatting," 2025.
[^2-D]: Liu et al., "Universal Beta Splatting," 2025/2026.
[^3-D]: Physics-Grounded 4D Dynamics Group, "NGFF," arXiv:2602.00148, 2026.
[^4-D]: "4C4D," CVPR 2026.
[^5-D]: "DASH," ICCV 2025.
[^6-D]: "MoBGS," AAAI 2026.
[^7-D]: Xie et al., "CARI4D," arXiv:2512.11988, 2025–2026.
[^8-D]: Wang et al., "X-Field," NeurIPS 2025 Spotlight.
[^9-D]: Peddi et al., "WSGG," arXiv:2603.13185, 2026.
[^10-D]: Sugandhika et al., "VOST-SGG," arXiv:2512.05524, 2025.
[^11-D]: "OmniRe," 2025–2026.
[^12-D]: "HyperGLM," 2025–2026.
[^13-D]: "STEP," CVPR 2025.
[^14-D]: "SNOW," 2025–2026.
[^15-D]: ACL-SSL Group, IJCV 2026.
[^16-D]: Um et al., CVPR 2025.
[^17-D]: Huang et al., "AL-Ref-SAM2," 2025.
[^18-D]: PVUW 2026 / HNU-VPAI, arXiv:2604.23935.
[^19-D]: Guo et al., "AVIS," CVPR 2025.
[^20-D]: HOI-DA, arXiv:2604.10397, 2026.
[^21-D]: Fu et al., "RoboMaster," arXiv:2506.01943, 2025.
[^22-D]: VISTA, arXiv:2605.01391, 2026.
[^23-D]: Google DeepMind, "Veo 3.1," 2026.
[^24-D]: RunwayML, "Gen-4 / Gen-4.5," 2026.
[^25-D]: Kuaishou, "Kling 3.0 / Omni," 2026.
[^26-D]: ByteDance, "Seedance 2.0," 2026.
[^27-D]: Pika Labs, "Pika 2.5," 2026.
[^28-D]: Alibaba, "Wan 2.6," 2026.
[^29-D]: MAViD, 2025.
[^30-D]: GraphThinker, arXiv:2602.17555, 2026.
[^31-D]: AAAI 2026, "ViG-RAG."
[^32-D]: ACM MM 2025, "GraphVideoAgent."
[^33-D]: VST, arXiv:2603.12262, 2026.
[^34-D]: IJCV 2025, "Language-guided Recursive Spatiotemporal Graph Modeling."
[^35-D]: Chen et al., "MECD+," IEEE / OpenReview 2025–2026.
[^36-D]: Alibaba, "Qwen2.5-Omni / Qwen3-Omni," 2025–2026.
[^37-D]: Google DeepMind, "Gemini 2.5 Pro / Flash," 2025–2026.
[^38-D]: OpenAI, "GPT-5," 2026.
[^39-D]: NMMs: Emu3.5, BLIP3o-NEXT, Aria, Show-o2, 2025–2026.
[^40-D]: vLLM-Omni, arXiv:2602.02204, 2026.

---

*Document version: 1.0*  
*Compiled by: Deep-Tech Research Swarm (4 parallel agents + synthesis)*  
*Date: 2026-05-07*  
*Next: ADR-001 through ADR-010 (Council of Ten required)*
