# ADR-005 PROPOSAL: Omni-Modal Backbone Selection

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Scope:** Network-wide reasoning backbone  
**Affected Blocks:** Voice Cognition (primary), Video Generation (secondary), Temporal Orchestration (tertiary), Knowledge & Topology (tertiary)

---

## 1. Context

The autonomous cognitive network requires a shared reasoning backbone capable of processing text, audio, video, and structured graph data in a single forward pass. The current voice-revenge-vizuara-ai pipeline uses a cascaded architecture (Deepgram ASR → Azure OpenAI GPT-4o-mini → Deepgram Aura TTS) with separate models for each modality. This creates:

1. **Error accumulation:** Each stage introduces independent failure modes
2. **Latency stacking:** ASR + LLM + TTS latency exceeds emotional disclosure budget (<600ms per ADR-013)
3. **Context loss:** Cross-modal relationships (e.g., facial expression + tone of voice) are lost at modality boundaries
4. **Pipeline fragility:** Changing one component (e.g., ASR model) requires retuning all downstream components

The research landscape has shifted from "modality-specific pipelines" to "native omni-modal models" that process all inputs in a unified representation space. MiniCPM-o 4.5 (April 2026), Gemini 2.5 Pro (March 2025), and Qwen3-Omni (2025) represent the leading candidates.

**Key research finding:** MiniCPM-o 4.5 achieves 80.2 on Daily-Omni vs Qwen3-Omni-30B's 70.7 — a 9B-parameter model outperforming a 30B-parameter model on omni-modal understanding, demonstrating that architecture (end-to-end token-level connectivity) matters more than scale for multimodal integration [CITATION: MiniCPM-o2026].

---

## 2. Problem Statement

How do we select an omni-modal backbone that satisfies:

1. **Full-duplex audio streaming:** Simultaneous audio input/output while processing video (MiniCPM-o's Omni-Flow TDM achieves this; Gemini 2.5 Flash Native Audio achieves this)
2. **Latency budget:** <600ms for emotional disclosures (ADR-013), <1500ms for standard responses
3. **Video understanding:** Process construction site videos, restaurant reels, and streaming content with temporal grounding
4. **Telugu language support:** Native Indic language optimization (Gemini 2.5 has dedicated Indic optimizations)
5. **Cost at scale:** 1M+ concurrent sessions must be economically viable
6. **Deployment flexibility:** Must run on Azure infrastructure (existing voice-revenge deployment)
7. **Open-weight fallback:** For sensitive brand content, on-premise inference may be required

---

## 3. Options Considered

### Option A: MiniCPM-o 4.5 (OpenBMB, April 2026)
**Source:** arXiv:2604.27393 [CITATION: MiniCPM-o2026]

**Mechanism:** 9B-parameter end-to-end omni-modal architecture with token-level hidden state connectivity across SigLIP ViT visual encoder (0.4B), Whisper Medium audio encoder (0.3B), Qwen3-8B LLM backbone, and streaming flow-matching speech decoder. Omni-Flow TDM aligns all input/output streams on a shared millisecond-level timeline.

**Pros:**
- Outperforms Qwen3-Omni-30B on Daily-Omni (80.2 vs 70.7), WorldSense (55.7 vs 54.0), Video-Holmes (64.3 vs 50.4)
- Full-duplex streaming via Omni-Flow TDM (simultaneous audio I/O + video processing)
- Runs on edge devices with <12GB RAM (critical for Suryapet-parent demographic on low-bandwidth)
- Open-weight — full model weights available for on-premise deployment
- 9B parameters = faster inference than 30B alternatives
- 40,960 max context length sufficient for 2-hour video sessions

**Cons:**
- Newer model (April 2026) — less production validation than Gemini 2.5 Pro
- Smaller ecosystem — fewer fine-tuning tools, smaller community than Llama
- Audio quality from flow-matching decoder unproven at scale vs commercial TTS (Aura, Bulbul)
- Requires custom inference infrastructure (not available on Azure OpenAI)
- Chinese team (OpenBMB) — potential geopolitical risk for US/EU deployments

### Option B: Gemini 2.5 Pro (Google DeepMind, March 2025)
**Source:** arXiv:2507.06261 [CITATION: Gemini2.5Pro2025]

**Mechanism:** Sparse mixture-of-experts (MoE) with 1M token context window, native multimodal support for text, image, audio, and video. Dynamic thinking mode for complex reasoning. Live API with native audio I/O and causal audio representations for streaming.

**Pros:**
- 1M token context (2M coming) — can ingest entire codebases, 3-hour videos, or complete document corpora
- SOTA on video understanding benchmarks (VideoMME, LOFT hard retrieval)
- Native audio generation with affective dialogue and proactive audio
- Dedicated Indic language optimizations (Telugu, Hindi) — critical for Suryapet demographic
- Integrated with Google ecosystem (Workspace, Photos, Search)
- $1.25/1M input tokens — ~60% cheaper than OpenAI o3
- Production validated at Google scale
- MCP (Model Context Protocol) native support for agentic workflows

**Cons:**
- Closed API — vendor lock-in, no on-premise deployment
- Requires Google Cloud infrastructure (migration from Azure)
- 64K max output tokens may limit long-form generation
- Latency for "thinking mode" may exceed emotional disclosure budget
- Sparse MoE routing overhead adds inference latency
- No full-duplex audio streaming in Pro variant (Flash Native Audio has this, but lower quality)

### Option C: Qwen3-Omni / Qwen3.5-Omni (Alibaba, 2025–2026)
**Source:** Qwen Team technical reports [CITATION: Qwen3-Omni — referenced in BIDIRECTIONAL-01]

**Mechanism:** 30B-A3B architecture (30B active parameters, 3B attention) with native audio-visual-text processing. Part of the Qwen3 model family with unified multimodal training.

**Pros:**
- Strong omni-modal performance (54.0 on WorldSense, 62.1 on FutureOmni)
- Open-weight ecosystem — extensive fine-tuning community
- Alibaba Cloud integration for Asia-Pacific deployment
- Strong Chinese + English bilingual capabilities

**Cons:**
- Outperformed by MiniCPM-o 4.5 (9B) on 5 of 7 omni-modal benchmarks — scale inefficiency
- 30B parameters = higher inference cost and latency than 9B MiniCPM-o
- No full-duplex streaming architecture (turn-based only)
- Limited Indic language support compared to Gemini 2.5
- Geopolitical concerns for US/EU deployments

### Option D: Hybrid — Gemini 2.5 Pro for cloud, MiniCPM-o 4.5 for edge
**Mechanism:** Use Gemini 2.5 Pro as primary backbone for cloud-hosted nodes (Video Generation, Knowledge & Topology) where latency is less critical and context length matters. Use MiniCPM-o 4.5 for edge-deployed Voice Cognition Nodes where full-duplex streaming and low latency are critical.

**Pros:**
- Best of both worlds: Gemini's context length + MiniCPM-o's streaming
- Reduces vendor lock-in via diversification
- Edge deployment for voice aligns with Suryapet-parent low-bandwidth scenario

**Cons:**
- Two-model ecosystem = doubled operational complexity
- Cross-model consistency issues (same prompt produces different outputs)
- Unified memory graph (PTKG) must be model-agnostic — adds abstraction layer
- Cost optimization harder with two billing systems (Google Cloud + self-hosted)

---

## 4. Decision

**Selected: Option A (MiniCPM-o 4.5) as primary backbone, with Gemini 2.5 Pro as secondary for long-context tasks.**

This is a **conditional hybrid** — not a full Option D, but a tiered approach:

| Task Type | Primary Model | Reason |
|-----------|--------------|--------|
| Real-time voice streaming | MiniCPM-o 4.5 | Omni-Flow TDM full-duplex, <12GB RAM, edge deployable |
| Video understanding (>1 hour) | Gemini 2.5 Pro | 1M context, SOTA on VideoMME |
| Cross-modal brand memory | MiniCPM-o 4.5 | End-to-end token connectivity preserves cross-modal relationships |
| Document intelligence (VDC) | Gemini 2.5 Pro | 1M context for entire codebase analysis |
| Telugu voice interactions | Gemini 2.5 Pro Flash Native Audio | Dedicated Indic optimizations |
| Offline/sensitive content | MiniCPM-o 4.5 | Open-weight, on-premise possible |

**Rationale (cited):**

1. **Latency constraint:** MiniCPM-o 4.5's 9B parameters + end-to-end architecture enable faster inference than 30B Qwen3-Omni or sparse MoE Gemini 2.5 Pro. The Omni-Flow TDM mechanism specifically targets real-time streaming [CITATION: MiniCPM-o2026].

2. **Full-duplex requirement:** Only MiniCPM-o 4.5 demonstrates full-duplex audio+video streaming with proactive interaction (1Hz decision frequency). Gemini 2.5 Flash Native Audio supports streaming audio I/O but lacks the integrated video stream alignment [CITATION: MiniCPM-o2026; Gemini2.5Pro2025].

3. **Edge deployment:** Suryapet-parent demographic requires low-bandwidth, low-compute edge deployment. MiniCPM-o 4.5 runs on <12GB RAM — deployable on consumer hardware. Gemini 2.5 Pro requires cloud API [CITATION: MiniCPM-o2026].

4. **Open-weight for trust:** Per ADR-010 (bad actor containment), we need the ability to audit model weights. MiniCPM-o 4.5 provides full weight access. Gemini 2.5 Pro is a black box [CITATION: MiniCPM-o2026].

5. **Performance per parameter:** MiniCPM-o 4.5 (9B) outperforms Qwen3-Omni (30B) on 5 of 7 benchmarks, demonstrating superior architecture efficiency [CITATION: MiniCPM-o2026].

6. **Gemini 2.5 Pro for long context:** When the network needs to analyze 3-hour construction site videos or entire codebases, Gemini 2.5 Pro's 1M context is unmatched. This is a secondary use case, not the primary streaming path [CITATION: Gemini2.5Pro2025].

---

## 5. Consequences

### Positive
- Single end-to-end model replaces 3-stage pipeline (ASR → LLM → TTS), reducing latency and error accumulation
- Full-duplex streaming enables proactive voice agent behavior (interruptions, confirmations, emotional mirroring)
- Edge deployment possible for rural/low-bandwidth users
- Model weight auditability for safety compliance

### Negative
- Custom inference infrastructure required (not available on Azure OpenAI — must self-host or use Alibaba Cloud)
- Migration effort from current Azure OpenAI GPT-4o-mini + Deepgram stack
- Gemini 2.5 Pro integration adds secondary operational complexity
- MiniCPM-o 4.5 is newer (April 2026) — production stability unproven at our scale
- Two-model ecosystem requires careful abstraction layer design

### Neutral
- Telugu support will use Gemini 2.5 Pro Flash Native Audio for cloud path, MiniCPM-o for edge path
- Cost model shifts from per-token API billing to per-GPU-hour self-hosting

---

## 6. Compliance / Verification

- [ ] All Voice Cognition Node adapters must implement `OmniModalPort` interface
- [ ] Latency tests: 95th percentile <600ms for Telugu emotional disclosures
- [ ] Latency tests: 95th percentile <1500ms for standard responses
- [ ] Full-duplex test: Simultaneous audio input + output + video processing for 5 minutes without degradation
- [ ] Edge deployment test: Run on GPU with ≤12GB VRAM at ≥8 FPS
- [ ] Citation audit: All code using omni-modal backbone must cite `MiniCPM-o2026` or `Gemini2.5Pro2025`

---

## 7. References

- [CITATION: MiniCPM-o2026] OpenBMB Team, "MiniCPM-o 4.5: Towards Real-Time Full-Duplex Omni-Modal Interaction," arXiv:2604.27393, 2026.
- [CITATION: Gemini2.5Pro2025] Google DeepMind, "Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities," arXiv:2507.06261, 2025.
- [CITATION: ADR-013] Patience-Aware Conversation Thresholds, voice-revenge-vizuara-ai/docs/decisions/ADR-013-patience-aware-thresholds.md
- [CITATION: ADR-010] Sanskrit Architecture — Śruti, Saṃvedana, Smṛti, Sphota, Dhvani
- [CITATION: BIDIRECTIONAL-01] Autonomous Cognitive Network — Cross-Domain Impact Analysis

---

*Document version: 1.0*  
*Research basis: Web search + arXiv paper analysis + benchmark comparison*  
*Next: Council of Ten deliberation*
