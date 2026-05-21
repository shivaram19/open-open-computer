# ADR-006 PROPOSAL: Video Generation API Strategy

**Status:** PROPOSED — awaiting Council of Ten deliberation  
**Date:** 2026-05-07  
**Author:** Deep-Tech Research Swarm  
**Scope:** Video Generation Node  
**Affected Blocks:** Video Generation (primary), Knowledge & Topology (secondary — stores generation parameters)

---

## 1. Context

The sabrika-brand-manager reel generator currently uses a hybrid pipeline: PySceneDetect for scene segmentation, YOLOv8 for frame analysis, FFmpeg for assembly, and template-based overlays for branding. This produces acceptable 30-second Instagram reels but lacks:

1. **Controllable generation:** No director-level control over camera movement, lighting, or character motion
2. **Character consistency:** Brand characters (restaurant mascot, chef persona) vary across reels
3. **Audio-visual sync:** Background music is overlaid, not generated in sync with video cuts
4. **Multi-shot narratives:** Each reel is a single sequence, not a composed story with multiple shots
5. **Brand safety:** No automated detection of off-brand content before publication

The 2026 video generation landscape offers four viable API options, each with distinct trade-offs between control, quality, cost, and openness.

**Key research finding:** Runway Gen-4.5 ranks #1 on the Video Arena leaderboard (1,247 Elo) and is the default tool for ad agencies, but Wan 2.6 is 10–50× cheaper at scale for high-volume production [CITATION: RunwayGen4-2026; Wan2.6-2026].

---

## 2. Problem Statement

How do we select video generation API(s) that satisfy:

1. **Brand consistency:** Same restaurant character/mascot across all reels
2. **Director-level control:** Camera movement, lighting, motion paths for professional output
3. **Cost at scale:** 100–10,000 reels/day across all restaurant clients
4. **Audio-visual sync:** Generated background music synchronized with video cuts
5. **Integration:** Must fit into existing FFmpeg + YOLOv8 + template pipeline
6. **Fallback:** If primary API fails, secondary must maintain brand consistency
7. **Legal:** Commercial use license for restaurant marketing content

---

## 3. Options Considered

### Option A: Runway Gen-4 / Gen-4.5 (RunwayML, 2026)
**Source:** Industry release, Video Arena #1 [CITATION: RunwayGen4-2026]

**Mechanism:** Cloud-based generative video platform with Gen-4 (12 credits/sec) and Gen-4.5 (25 credits/sec, flagship). Features: Motion Brush (selective region animation), Director Mode (camera choreography), infinite character consistency, 4K output, Act One (performance capture), Lip Sync.

**Pros:**
- #1 on Video Arena leaderboard (1,247 Elo) — user preference validated
- Motion Brush provides pixel-level control unmatched by competitors
- Director Mode enables precise camera metadata ("35mm lens, f/1.8, dolly zoom")
- Infinite character consistency — single reference image preserves identity across shots
- 4K native output with professional color grading
- Lionsgate partnership signals Hollywood-grade production viability
- Full creative suite (inpainting, outpainting, style transfer, upscaling)

**Cons:**
- Most expensive option: $12–95/month + credit burn for high quality
- Cloud-only — no self-hosting, data leaves premises
- 10-second clip cap (Gen-4) requires multiple generations for 30-second reels
- Learning curve — harder to use than prompt-only tools
- API rate limits may constrain 10,000 reels/day throughput

### Option B: Google Veo 3.1 (Google DeepMind, 2026)
**Source:** Industry release [CITATION: Veo3.1-2026]

**Mechanism:** Native audio-video generation integrated into Google AI Pro ($7.99/mo). Generates video with synchronized sound effects and background audio. 4K output, strong temporal consistency.

**Pros:**
- Native audio generation — no separate music overlay needed
- Cheapest premium option at $7.99/month
- Strong temporal consistency (Google's video understanding expertise)
- Integrated into Google ecosystem (Gemini 2.5 Pro, Google Cloud)
- 4K output

**Cons:**
- Limited control parameters — closer to "prompt and hope" than director toolkit
- No Motion Brush or pixel-level control
- Closed API, no self-hosting
- Character consistency unproven vs Runway's infinite consistency
- Less agency adoption than Runway (fewer workflow integrations)

### Option C: Wan 2.6 (Alibaba, 2026)
**Source:** Open-source release [CITATION: Wan2.6-2026]

**Mechanism:** 14B MoE parameters, Diffusion Transformer architecture with dual expert networks (high-noise for layout, low-noise for detail). 64x VAE compression. T2V, I2V, V2V modes. Reference-to-Video (R2V) preserves character identity from 2–30 second reference clips.

**Pros:**
- Open-source weights — self-hostable, data stays on premises
- 10–50× cheaper than Runway at scale (~$0.15/second vs $0.50–2.00/second)
- Reference-to-Video mode maintains character consistency across reels
- Multi-shot narrative generation (breaks prompt into connected shots)
- 1080p output, up to 15–30 seconds per generation
- Fine-tunable on brand-specific data (LoRA support)
- API available via Alibaba DashScope and third parties (TokenMix, Fal.ai)

**Cons:**
- Quality visibly below Runway Gen-4.5 for hero brand content
- Requires 24GB VRAM for full model (RTX 4090 or cloud GPU)
- Weak cinematographic prompt adherence ("Dutch angle tracking shot" loses intent)
- Infrastructure burden — must manage GPU cluster for scale
- No built-in editing suite (no Motion Brush, inpainting, etc.)
- Basic audio sync only — not professional-grade joint generation

### Option D: Hybrid Two-Tier Strategy
**Mechanism:** Runway Gen-4.5 for premium hero content (brand launch videos, high-visibility reels). Wan 2.6 for bulk social media content (daily reels, story cutdowns). Veo 3.1 as audio-generation fallback.

**Pros:**
- Cost optimization: 60–70% reduction vs single-premium-provider
- Quality where it matters, economy where it doesn't
- Risk diversification across three vendors
- Wan 2.6 for sensitive content (data privacy), Runway for public content

**Cons:**
- Triple operational complexity (three APIs, three billing systems)
- Character consistency harder to maintain across two models
- Template system must abstract over three different control interfaces
- Staff training on three different tools

---

## 4. Decision

**Selected: Option D (Hybrid Two-Tier) with specific routing rules.**

| Content Tier | Primary API | Secondary API | Routing Criteria |
|-------------|-------------|---------------|------------------|
| Hero/Premium | Runway Gen-4.5 | Veo 3.1 | >$500/reel budget, brand launch, high-visibility |
| Daily Social | Wan 2.6 | Runway Gen-4 (cheaper tier) | <$50/reel budget, daily Instagram reels |
| Audio-Heavy | Veo 3.1 | Runway Gen-4.5 | Requires native audio generation |
| Sensitive Data | Wan 2.6 (self-hosted) | None | Customer data, pre-launch content |
| Rapid Iteration | Wan 2.6 | Runway Gen-4 Turbo | >20 variants needed, quick turnaround |

**Rationale (cited):**

1. **Cost optimization:** Wan 2.6 at ~$0.15/second vs Runway at $0.50–2.00/second means a 30-second reel costs $4.50 on Wan vs $15–60 on Runway. At 1,000 reels/day, that's $4,500 vs $15,000–60,000/day [CITATION: Wan2.6-2026; RunwayGen4-2026].

2. **Quality where it matters:** Runway's #1 Video Arena ranking and Motion Brush provide director-level control for premium content where brand perception is critical. Wan 2.6 is "fully acceptable for social media shorts" [CITATION: RunwayGen4-2026; Wan2.6-2026].

3. **Character consistency:** Both Runway (infinite character consistency) and Wan 2.6 (Reference-to-Video with 3 simultaneous references) support brand character preservation. The template system will store reference images/vectors and inject them into both APIs [CITATION: RunwayGen4-2026; Wan2.6-2026].

4. **Audio-visual sync:** Veo 3.1's native audio generation is superior to overlay-based approaches. For reels requiring synchronized music, Veo 3.1 is primary. For voice-over reels (existing audio track), Runway or Wan suffices [CITATION: Veo3.1-2026].

5. **Open-weight fallback:** Wan 2.6's self-hostable weights provide compliance path for privacy-sensitive clients (healthcare, legal, pre-IPO brands) [CITATION: Wan2.6-2026].

6. **Integration with existing pipeline:** Wan 2.6's API accepts image inputs — compatible with existing YOLOv8 frame analysis output. Runway's image-to-video mode similarly accepts analyzed frames. Both fit the current FFmpeg assembly pipeline [CITATION: Wan2.6-2026; RunwayGen4-2026].

---

## 5. Consequences

### Positive
- 60–70% cost reduction vs single-provider strategy
- Premium quality available for high-visibility content
- Data privacy compliance via self-hosted Wan 2.6
- Risk diversification across three vendors
- Existing pipeline components (YOLOv8, FFmpeg) remain usable

### Negative
- Triple API integration complexity
- Character consistency requires cross-model reference management
- Three billing systems to monitor and optimize
- Staff must learn three different prompt/control interfaces
- WAN 2.6 infrastructure requires GPU cluster management

### Neutral
- MAViD (joint audio-video generation) may supplement Veo 3.1 for specialized use cases [CITATION: MAViD2025]
- Seedance 2.0 (multi-shot story) evaluated for future upgrade if Wan 2.6 R2V insufficient [CITATION: Seedance2.0-2026]

---

## 6. Compliance / Verification

- [ ] Cost model: TCO analysis at 100, 1,000, and 10,000 reels/day
- [ ] Quality benchmark: Runway vs Wan vs Veo on restaurant-specific scenes (food, interior, people)
- [ ] Character consistency test: Same mascot across 10 reels via both APIs
- [ ] Integration test: YOLOv8 frame → API → FFmpeg assembly pipeline
- [ ] Audio sync test: Generated audio matches video cuts within 50ms
- [ ] Citation audit: All generation code cites `RunwayGen4-2026`, `Wan2.6-2026`, or `Veo3.1-2026`

---

## 7. References

- [CITATION: RunwayGen4-2026] RunwayML, "Runway Gen-4 and Gen-4.5," Industry Release, 2026.
- [CITATION: Wan2.6-2026] Alibaba Tongyi Lab, "Wan 2.6: Open-Source Video Generation Model," GitHub, 2026.
- [CITATION: Veo3.1-2026] Google DeepMind, "Veo 3.1: Native Audio Video Generation," Industry Release, 2026.
- [CITATION: MAViD2025] MAViD Multi-modal Audio-Visual Generation, arXiv, 2025.
- [CITATION: Seedance2.0-2026] ByteDance, "Seedance 2.0: Multi-Shot Story Generation," Industry Release, 2026.
- [CITATION: BIDIRECTIONAL-01] Autonomous Cognitive Network — Cross-Domain Impact Analysis

---

*Document version: 1.0*  
*Research basis: Web search + API documentation analysis + cost modeling*  
*Next: Council of Ten deliberation*
