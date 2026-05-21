# Digital Twin Profiles: Architects of Cognitive Video Intelligence

## A Comprehensive Archaeological Study of Ten Foundational Researchers

---

## Table of Contents
1. [Noah Shinn](#1-noah-shinn)
2. [Aman Madaan](#2-aman-madaan)
3. [Shunyu Yao](#3-shunyu-yao)
4. [Maciej Besta](#4-maciej-besta)
5. [Xinhao Li](#5-xinhao-li)
6. [Ruyi Xu](#6-ruyi-xu)
7. [Shengyuan Ye](#7-shengyuan-ye)
8. [Jacob Chalk](#8-jacob-chalk)
9. [Jenny Zhang](#9-jenny-zhang)
10. [Nehzati M. (Mohammadreza Nehzati)](#10-nehzati-m)
11. [Interconnection Matrix](#interconnection-matrix)
12. [Council Composition](#council-composition)

---

## 1. Noah Shinn

### Identity & Trajectory
- **Current Affiliation**: Research Scientist at Sierra (conversational AI company co-founded by Bret Taylor and Clay Bavor)
- **Education**: Undergraduate at Northeastern University (Khoury College); Research at MIT with Prof. Ashwin Gopinath
- **Advisor Lineage**: Ashwin Gopinath (MIT) → Karthik Narasimhan (Princeton, co-author and mentor)
- **Career Arc**: Northeastern undergrad → MIT research → Sierra (early employee) → Leading agent evaluation research

### Core Methodology
**Verbal Reinforcement Learning without Weight Updates**. Shinn's defining insight is that language agents can learn from failure through *linguistic feedback* rather than gradient descent. This decouples learning from the expensive pretraining/fine-tuning loop, enabling rapid trial-and-error adaptation.

### Key Papers

#### 1. Reflexion: Language Agents with Verbal Reinforcement Learning (NeurIPS 2023)
- **Core Problem**: LLM agents struggle to learn from trial-and-error because traditional RL requires extensive training samples and model fine-tuning
- **Methodological Innovation**: Agents verbally reflect on task feedback, maintain reflective text in episodic memory buffer, and use this to induce better decision-making in subsequent trials
- **Philosophical Approach**: "Use the model's strengths to address its shortcomings" — leverage LLMs' ability to critique and verify outputs, not just generate them
- **Lasting Impact**: 91% pass@1 on HumanEval (surpassing GPT-4's 80%). Foundation for all subsequent self-reflecting agent architectures. Cited by Google DeepMind and OpenAI.

#### 2. τ-bench: A Benchmark for Tool-Agent-User Interaction (ICLR 2025, with Shunyu Yao & Karthik Narasimhan)
- **Core Problem**: Existing benchmarks test single-turn problems; real-world agents need multi-turn dynamic interaction with humans and APIs
- **Methodological Innovation**: Multi-party interaction benchmark with policy compliance requirements and reliability metrics (pass^k)
- **Philosophical Approach**: "Evaluation will be more important than training" — rigorous measurement of real-world agent behavior
- **Lasting Impact**: Industry-standard benchmark for customer service and tool-use agent evaluation

#### 3. Can It Edit? Evaluating the Ability of LLMs to Follow Code Editing Instructions (COLM 2024)
- **Core Problem**: Code generation is different from code editing — models need to understand diffs and contextual modifications
- **Methodological Innovation**: Systematic evaluation framework for code editing capabilities
- **Philosophical Approach**: Practical capability assessment over theoretical benchmarks

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Verbal reinforcement learning, self-reflection, agent evaluation |
| **Key Intellectual Contributions** | 1) Language-as-reward-signal paradigm<br>2) Episodic memory for agent self-improvement<br>3) Dynamic multi-party agent benchmarking<br>4) Code editing as distinct capability |
| **Research Philosophy** | *"Build systems that learn from their own mistakes in the same language they use to solve problems."* Pragmatic, engineering-first, focused on real-world deployment reliability |
| **Signature Techniques** | Reflexion loop (generate → evaluate → reflect → retry), episodic memory buffers, pass^k reliability metrics |
| **Advised Students / Lineage** | Federico Cassano (co-author, Northeastern undergrad); Part of Karthik Narasimhan's Princeton→Sierra lineage |
| **Council Guidance** | Would advocate for *memory-first architectures* where every cognitive process leaves a trace that can be reflected upon. Believes the bottleneck is not model capability but reliable evaluation and feedback loops |
| **Assigned Block** | **Self-Reflection** |

---

## 2. Aman Madaan

### Identity & Trajectory
- **Current Affiliation**: AI Researcher & Engineer at xAI (Elon Musk's AI company, since March 2024)
- **Education**: PhD (2024) & MS (2021) in Language Technologies, Carnegie Mellon University (GPA: 4.20/4.33); Advisor: Prof. Yiming Yang
- **Prior Education**: M.Tech. IIT Bombay (CPI: 10.0/10.0, Department Rank 1); B.Tech. Guru Gobind Singh Indraprastha University, Delhi (Department Rank 1)
- **Career Arc**: Visa (Senior Software Engineer) → Oracle (Principal Member of Technical Staff) → CMU PhD → Google Brain / Google Bard Team (intern) → Allen Institute for AI (AI2) → xAI
- **Advisor Lineage**: Yiming Yang (CMU, renowned for text mining and machine learning) → Graham Neubig (CMU/NLP)

### Core Methodology
**Inference-Time Compute for Enhanced Reasoning**. Madaan's work demonstrates that even state-of-the-art LLMs can be dramatically improved *at test time* through structured iterative refinement, without any weight updates. His research bridges code generation, natural language reasoning, and self-feedback loops.

### Key Papers

#### 1. Self-Refine: Iterative Refinement with Self-Feedback (NeurIPS 2023)
- **Core Problem**: LLMs generate initial outputs that contain errors; how can the same model critique and improve its own work?
- **Methodological Innovation**: A single LLM acts as generator, critic, and refiner in a loop — generating feedback on its own outputs and using that feedback to iteratively improve
- **Philosophical Approach**: "LLMs can be their own teachers" — self-supervision through iterative critique without external training data
- **Lasting Impact**: Demonstrated across code, dialogue, math, and creative writing. Foundation for test-time scaling approaches

#### 2. PAL: Program-Aided Language Models (ICML 2023)
- **Core Problem**: LLMs make arithmetic and logical errors even when they correctly decompose problems
- **Methodological Innovation**: LLM generates programs as intermediate reasoning steps, but offloads *execution* to a Python interpreter — neural-symbolic hybrid
- **Philosophical Approach**: "Separate reasoning from calculation" — use each tool for what it's good at
- **Lasting Impact**: Surpassed PaLM-540B on GSM8K with Codex. Inspired wave of tool-augmented reasoning systems

#### 3. Language Models of Code are Few-Shot Commonsense Learners (EMNLP 2022)
- **Core Problem**: Structured commonsense reasoning tasks (event graphs, reasoning graphs) are hard for natural language LMs
- **Methodological Innovation**: Frame structured reasoning as *code generation* — code LMs outperform natural language LMs even on non-code tasks
- **Philosophical Approach**: The *representation format* (code vs. text) fundamentally shapes reasoning capability

#### 4. What Makes Chain-of-Thought Prompting Effective? A Counterfactual Study (EMNLP Findings 2023)
- **Core Problem**: CoT "just works" but nobody understands why
- **Methodological Innovation**: Systematic manipulation of prompt elements (symbols, patterns, equations) to isolate what matters
- **Philosophical Approach**: Rigorous empirical deconstruction of emergent phenomena
- **Key Finding**: Patterns and text style matter more than exact symbols; intermediate steps convey *task understanding* rather than teaching how to solve

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Iterative self-refinement, neural-symbolic hybrids, test-time compute scaling |
| **Key Intellectual Contributions** | 1) Self-Refine loop (generator-critic-refiner in one model)<br>2) PAL: program-as-reasoning-intermediary<br>3) Code models for commonsense reasoning<br>4) Counterfactual analysis of prompting phenomena |
| **Research Philosophy** | *"The answer is not in the weights — it's in the loop."* Believes in systematic, empirical decomposition of AI capabilities. Engineering precision meets scientific rigor |
| **Signature Techniques** | Self-feedback loops, program-aided reasoning, counterfactual prompting analysis |
| **Advised Students / Lineage** | Part of Yiming Yang's CMU LTI lineage; Collaborates extensively with AI2 (Peter Clark, Niket Tandon) |
| **Council Guidance** | Would advocate for *separation of concerns* — reasoning, execution, and verification should be distinct, composable modules. Emphasizes empirical measurement over intuition |
| **Assigned Block** | **Self-Reflection** |

---

## 3. Shunyu Yao

### Identity & Trajectory
- **Current Status**: Left OpenAI (August 2024 – September 2025); rumored to be starting new venture. Previously Research Scientist at OpenAI.
- **Education**: PhD in Computer Science, Princeton University (2019–2024); Advisor: Prof. Karthik Narasimhan. Dissertation: *"Language Agents: From Next-Token Prediction to Digital Automation"*
- **Undergraduate**: Tsinghua University, Yao Class (2015–2019). Silver medal at National Olympiad in Informatics (NOI) 2014. Ranked 3rd in Anhui Province in Gaokao.
- **PhD Committee**: Karthik Narasimhan (advisor), Tom Griffiths, Benjamin Eysenbach; Readers: Sanjeev Arora, Tatsunori Hashimoto (Stanford)
- **Career Arc**: Tsinghua Yao Class → Princeton PhD → OpenAI (led Computer-Using Agent / CUA, Deep Research) → Industry transition
- **Total Citations**: >15,000 (as of 2025)

### Core Methodology
**Language Agents as a New Category of AI Systems**. Yao's work establishes LLM-based agents as a rigorous, distinct field — moving from "prompt engineering" to principled cognitive architectures. His approach interleaves reasoning and acting, uses tree search for deliberation, and grounds agents in real-world environments.

### Key Papers

#### 1. ReAct: Synergizing Reasoning and Acting in Language Models (ICLR 2023, Oral Top 5%)
- **Core Problem**: Reasoning (chain-of-thought) and acting (tool use) were studied separately; LLMs need both synergistically
- **Methodological Innovation**: Interleaved generation of reasoning traces and task-specific actions — reasoning traces help induce/update action plans, while actions gather external information
- **Philosophical Approach**: "Reasoning and acting are not separate modules — they are two aspects of the same cognitive process"
- **Lasting Impact**: Foundation paradigm for all modern agent systems (LangChain, AutoGPT, etc.). Applied across healthcare, robotics, education, disaster control

#### 2. Tree of Thoughts: Deliberate Problem Solving with Large Language Models (NeurIPS 2023, Oral)
- **Core Problem**: LLMs are confined to token-level, left-to-right decision-making; they cannot explore, backtrack, or plan globally
- **Methodological Innovation**: Generalize chain-of-thought to a tree structure where each "thought" is a coherent language unit; use BFS/DFS to explore multiple reasoning paths with self-evaluation
- **Philosophical Approach**: "Human problem-solving searches through combinatorial problem spaces — LLMs should too"
- **Lasting Impact**: Enabled LLMs to solve Game of 24, creative writing planning, and crosswords. Directly influenced OpenAI's o1 reasoning model

#### 3. Cognitive Architectures for Language Agents / CoALA (TMLR 2024)
- **Core Problem**: Hundreds of agent methods exist but no unified framework to understand or compare them
- **Methodological Innovation**: Modular cognitive architecture with working memory, long-term memory, internal actions (reasoning, planning, reflection), and external actions (tool use, communication)
- **Philosophical Approach**: Ground agent design in classical cognitive science (ACT-R, SOAR) rather than ad-hoc engineering
- **Lasting Impact**: First principled framework for language agents. Actionable insights for agent design

#### 4. SWE-bench / SWE-agent (ICLR 2024 Oral, NeurIPS 2024)
- **Core Problem**: Can LLMs resolve real GitHub issues?
- **Methodological Innovation**: Benchmark of 2,000+ real GitHub issues from 12 Python repos; SWE-agent introduces agent-computer interfaces
- **Philosophical Approach**: "Evaluation must mirror real-world complexity" — synthetic benchmarks mislead

#### 5. WebShop (NeurIPS 2022)
- **Core Problem**: E-commerce agents need to navigate websites, search products, and make decisions in natural language
- **Methodological Innovation**: 1.18M real Amazon products, simulated web environment, goal-driven evaluation
- **Philosophical Approach**: Digital automation tasks are the proving ground for general agents

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Language agents, reasoning-acting synergy, tree search over thoughts, cognitive architectures |
| **Key Intellectual Contributions** | 1) ReAct paradigm (reasoning ↔ acting interleaving)<br>2) Tree of Thoughts (deliberate search in reasoning space)<br>3) CoALA (principled cognitive architecture for agents)<br>4) Real-world benchmarks (WebShop, SWE-bench, τ-bench)<br>5) CUA / Deep Research at OpenAI |
| **Research Philosophy** | *"From next-token prediction to digital automation."* Believes language models are not just text predictors but the foundation of a new category of autonomous agents. Evaluation-driven research |
| **Signature Techniques** | ReAct loops, Tree search over reasoning traces, cognitive architecture modularity, real-environment benchmarking |
| **Advised Students / Lineage** | Karthik Narasimhan's lineage (Princeton NLP Group); Mentored Noah Shinn (Reflexion); Collaborated with Tom Griffiths (cognitive science). Best man at Yao's wedding |
| **Council Guidance** | Would advocate for *benchmark-grounded development* — every capability must be measurable against real-world tasks. Emphasizes the agent-environment loop as the core of intelligence |
| **Assigned Block** | **Temporal Reasoning** (with cross-over to Self-Reflection and Streaming Cognition) |

---

## 4. Maciej Besta

### Identity & Trajectory
- **Current Affiliation**: Research Lead at Scalable Parallel Computing Lab (SPCL) and ETH Future Computing Lab, ETH Zurich
- **Education**: PhD, ETH Zurich (2021); Advisor: Prof. Torsten Hoefler. Dissertation on irregular computations
- **Awards**: IEEE TCHPC Award for Excellence in HPC Early Career (2024), HiPEAC Tech Transfer Award (2024), ETH Medal for outstanding doctoral thesis (2021), ACM/IEEE-CS HPC Fellowship (2015), Google Fellowship in Parallel Computing (2013), Best Student of Poland (2012)
- **Career Arc**: Poland's Best Student → Google Fellow → ETH PhD with Torsten Hoefler → Research Lead at ETH. Background in high-performance graph computing before pivoting to LLM reasoning
- **Lab**: SPCL (Scalable Parallel Computing Lab) — world-leading systems research group

### Core Methodology
**Graph-Structured Reasoning for LLMs**. Besta's foundational insight is that human thinking and brain mechanisms operate through *complex networks*, not linear chains or trees. His work models LLM reasoning as arbitrary graphs where thoughts are vertices and dependencies are edges — enabling aggregation, feedback loops, and distillation.

### Key Papers

#### 1. Graph of Thoughts: Solving Elaborate Problems with Large Language Models (AAAI 2024)
- **Core Problem**: Chain-of-Thought and Tree of Thoughts are limited to linear/tree structures; human reasoning forms complex networks
- **Methodological Innovation**: Model LLM-generated information as arbitrary graphs; thoughts are vertices, dependencies are edges. Enables aggregation, feedback loops, and distillation of thought networks
- **Philosophical Approach**: "LLM reasoning should mirror human thinking and brain mechanisms — recurrence, feedback, complex networks"
- **Lasting Impact**: 62% quality improvement over ToT on sorting, 31% cost reduction. Extensible framework for new prompting schemes

#### 2. Knowledge Graph of Thoughts / KGoT (2025)
- **Core Problem**: LLM-driven agents are expensive and have limited success on complex benchmarks like GAIA
- **Methodological Innovation**: Integrate LLM reasoning with dynamically constructed knowledge graphs; extract and structure task-relevant knowledge into KG representations iteratively enhanced by external tools
- **Philosophical Approach**: Structured knowledge representation enables smaller models to solve complex tasks — *cognitive scaffolding*
- **Lasting Impact**: 29% improvement on GAIA benchmark, 36× cost reduction vs GPT-4o

#### 3. The Graph Database Interface (SC 2023) & Hardware Acceleration for KG Processing (2024)
- **Core Problem**: Knowledge graph processing at scale requires extreme parallelism
- **Methodological Innovation**: GDI standard for scaling graph workloads to hundreds of thousands of cores; hardware-software co-design for KG processing
- **Philosophical Approach**: Reasoning systems must be co-designed with their execution substrate

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Graph-structured reasoning, knowledge graphs, high-performance computing, neuro-inspired architectures |
| **Key Intellectual Contributions** | 1) Graph of Thoughts (arbitrary graph reasoning for LLMs)<br>2) Knowledge Graph of Thoughts (structured reasoning with external tools)<br>3) Hardware-software co-design for cognitive workloads<br>4) Graph database interfaces at extreme scale |
| **Research Philosophy** | *"Bring LLM reasoning closer to brain mechanisms — recurrence, feedback, complex networks."* Systems-thinking approach: reasoning architecture and execution substrate must be co-designed. Values extensibility and theoretical grounding |
| **Signature Techniques** | Graph-of-thought transformations, knowledge graph construction, feedback loops in reasoning, HPC-scale graph processing |
| **Advised Students / Lineage** | Torsten Hoefler's SPCL lineage (ETH Zurich); Supervised Nils Blach, Robert Gerstenberger, Lukas Gianinazzi, and many others. Mentored Andrea Jiang (KGoT thesis) |
| **Council Guidance** | Would advocate for *graph-structured cognition* — every thought should be a node in an evolving network, not a step in a sequence. Emphasizes the importance of feedback loops and aggregation in collective reasoning |
| **Assigned Block** | **Temporal Reasoning** (graph-based event dependencies) |

---

## 5. Xinhao Li

### Identity & Trajectory
- **Current Affiliation**: Research Intern at ByteDance Seed (becoming full-time); Previously Moonshot AI (2025–2026), Shanghai AI Lab (2023–2025), SenseTime (2022–2023)
- **Education**: MS student at Nanjing University (2023–2026 expected), supervised by Prof. Limin Wang. Bachelor's from Chongqing University (2023), Rank 1/295, GPA 3.9/4.0
- **Career Arc**: Chongqing University (top of class) → SenseTime → Shanghai AI Lab → Moonshot AI (Kimi K2.5 vision encoder) → ByteDance Seed
- **Key Collaborators**: Yi Wang, Limin Wang (Nanjing University); Yu Qiao, Yali Wang (Shanghai AI Lab / CAS)

### Core Methodology
**Reinforcement Learning for Video Multimodal Understanding**. Li's work applies modern RL (GRPO, rule-based rewards) to video MLLMs, demonstrating that spatio-temporal perception can be dramatically enhanced through data-efficient reinforcement fine-tuning without sacrificing general capabilities.

### Key Papers

#### 1. VideoChat-R1: Enhancing Spatio-Temporal Perception via Reinforcement Fine-Tuning (2025)
- **Core Problem**: RL approaches like GRPO work for text and image MLLMs but remain underexplored for video understanding
- **Methodological Innovation**: Systematic exploration of RFT with GRPO for video MLLMs; multi-task RFT on spatio-temporal perception objectives with limited samples
- **Philosophical Approach**: "RL for video is not just about reasoning — it's about spatio-temporal grounding"
- **Lasting Impact**: +31.8 on temporal grounding, +31.2 on object tracking vs Qwen2.5-VL-7B. State-of-the-art spatio-temporal perception

#### 2. VideoChat-Flash: Hierarchical Compression for Long-Context Video Modeling (2024)
- **Core Problem**: Extremely long videos are challenging due to difficulty maintaining crucial features over extended sequences
- **Methodological Innovation**: Hierarchical visual token Compression (HiCo) from clip-level to video-level; multi-stage short-to-long learning
- **Philosophical Approach**: "Visual redundancy in long videos is a feature, not a bug — exploit it for compression"
- **Lasting Impact**: 99.1% accuracy on 10,000-frame needle-in-haystack among open-source models. 1/50 compression ratio with minimal performance loss

#### 3. VideoChat-Online / OVBench (CVPR 2025)
- **Core Problem**: Offline video understanding doesn't translate to real-time online scenarios (autonomous driving, AR, surveillance)
- **Methodological Innovation**: Pyramid Memory Bank (PMB) for retaining key spatiotemporal information; offline-to-online learning paradigm with interleaved dialogue format
- **Philosophical Approach**: "Online video understanding requires different architectures, benchmarks, and training strategies"
- **Lasting Impact**: First comprehensive benchmark for online video QA across past/present/future temporal contexts

#### 4. VideoChat-R1.5 / VTTS: Visual Test-Time Scaling (2025)
- **Core Problem**: Static perception limits MLLM reasoning; humans use hierarchical attention
- **Methodological Innovation**: Visual Test-Time Scaling (VTTS) with Iterative Perception (ITP) — progressively refining focus on high-confidence spatio-temporal regions during inference
- **Philosophical Approach**: "Reasoning should drive perception, not just analyze pre-parsed visuals"
- **Lasting Impact**: >5% average improvement across 15+ benchmarks via increased perceptual compute

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Reinforcement fine-tuning for video MLLMs, hierarchical compression, online video understanding, visual test-time scaling |
| **Key Intellectual Contributions** | 1) VideoChat-R1 (GRPO for spatio-temporal perception)<br>2) HiCo hierarchical compression for long video<br>3) OVBench / VideoChat-Online (online video understanding)<br>4) VTTS (iterative perception during inference)<br>5) Kimi K2.5 vision encoder architecture |
| **Research Philosophy** | *"Video understanding is not image understanding over time — it's a fundamentally different problem requiring spatio-temporal reasoning, memory, and online adaptation."* Believes RL is the key to unlocking video MLLM capabilities |
| **Signature Techniques** | GRPO with spatio-temporal rewards, hierarchical token compression, pyramid memory banks, iterative perception |
| **Advised Students / Lineage** | Limin Wang's group (Nanjing University); OpenGVLab at Shanghai AI Lab. Industry trajectory: SenseTime → Shanghai AI Lab → Moonshot AI → ByteDance |
| **Council Guidance** | Would advocate for *reinforcement learning as the primary training paradigm* for video perception, not just supervised learning. Emphasizes task-specific rewards, data efficiency, and the importance of online/streaming evaluation |
| **Assigned Block** | **RL Perception** |

---

## 6. Ruyi Xu

### Identity & Trajectory
- **Current Affiliation**: MIT Han Lab (with Song Han); Also affiliated with NVIDIA
- **Education**: Undergraduate in Computer Science, Tsinghua University (2022–2026 expected)
- **Key Collaborators**: Song Han (MIT, renowned for efficient ML), Guangxuan Xiao (MIT), Yukang Chen (NVIDIA)
- **Career Arc**: Tsinghua undergrad → MIT Han Lab research → Co-first author on major streaming vision paper

### Core Methodology
**Real-Time Streaming Vision-Language Models**. Xu's work addresses the critical gap between batch video understanding and real-time streaming inference — enabling VLMs to process *infinite* video streams without escalating latency or memory.

### Key Papers

#### 1. StreamingVLM: Real-Time Understanding for Infinite Video Streams (ICLR 2026)
- **Core Problem**: VLMs cannot process near-infinite video streams; full attention is O(n²), sliding windows break coherence or have redundant recomputation
- **Methodological Innovation**: Unified training-inference alignment for streaming; compact KV cache with attention sinks + short recent vision window + long recent text window; SFT on short overlapped chunks that mimic inference attention
- **Philosophical Approach**: "Training and inference must be aligned — streaming ability should be instilled during training, not hacked during inference"
- **Lasting Impact**: 66.18% win rate vs GPT-4O mini on Inf-Streams-Eval; stable real-time at 8 FPS on single H100. Videos averaging >2 hours

#### 2. XAttention: Block Sparse Attention with Antidiagonal Scoring (ICML 2025)
- **Core Problem**: Attention computation is the bottleneck for long-context inference
- **Methodological Innovation**: Block sparse attention patterns with antidiagonal scoring for efficient long-context processing
- **Philosophical Approach**: "Sparsity patterns should match the structure of information importance in sequences"

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Streaming vision-language models, efficient attention, training-inference alignment, KV cache optimization |
| **Key Intellectual Contributions** | 1) StreamingVLM (infinite video stream understanding)<br>2) XAttention (block sparse attention)<br>3) Inf-Streams-Eval benchmark (2+ hour videos with per-second alignment)<br>4) Attention sink + windowed KV cache for streaming |
| **Research Philosophy** | *"Real-time is not a feature — it's a constraint that reshapes the entire architecture."* Believes streaming inference requires fundamentally different training paradigms, not just inference optimizations |
| **Signature Techniques** | Attention sinks, windowed KV caches, chunked SFT with overlap, streaming-inference alignment |
| **Advised Students / Lineage** | Song Han's MIT Han Lab lineage (efficient ML systems). Guangxuan Xiao as co-first author and mentor |
| **Council Guidance** | Would advocate for *streaming-first architecture design* — any system that cannot process infinite inputs in real-time is insufficient for embodied intelligence. Emphasizes the training-inference gap as the root of video understanding failures |
| **Assigned Block** | **Streaming Cognition** |

---

## 7. Shengyuan Ye

### Identity & Trajectory
- **Current Affiliation**: Final-year PhD student, Sun Yat-sen University (SMCLab)
- **Education**: PhD in Computer Science, Sun Yat-sen University (2021–Present); Advisors: Prof. Xu Chen (primary), Prof. Xiaowen Chu (HKUST(GZ), remote). Visiting PhD at CUHK AIoT Lab with Prof. Guoliang Xing (2024–2025)
- **Prior Education**: B.E. in Computer Science, Sun Yat-sen University (2017–2021); Advisor: Assoc. Prof. Yanghui Rao. Industry internships at Tencent (WeChat PaxosStore, MobileQQ)
- **Career Arc**: Sun Yat-sen undergrad → Tencent internships → Sun Yat-sen PhD → CUHK visiting → Research intern at Huawei Cloud
- **Awards**: Guo Xie Birong Memorial Scholarship, Tencent Scholarship, Huawei Intelligent Infrastructure Scholarship, First Prize Postgraduate Scholarship ×3, Samsung Scholarship, CUMCM First Prize

### Core Methodology
**Edge-Cloud Disaggregated Architectures for Real-Time Video Understanding**. Ye's work recognizes that deployment constraints are as important as model capability. His systems push memory construction and keyframe retrieval to the edge, minimizing cloud communication while maintaining reasoning accuracy.

### Key Papers

#### 1. Venus: An Efficient Edge Memory-and-Retrieval System for VLM-based Online Video Understanding (INFOCOM 2026)
- **Core Problem**: VLMs are deployed for online video understanding but deployment constraints (latency, bandwidth, compute) are ignored, causing overwhelming system overhead
- **Methodological Innovation**: Edge-cloud disaggregated architecture; ingestion stage with scene segmentation + clustering + multimodal embedding; querying stage with threshold-based progressive sampling for adaptive keyframe selection
- **Philosophical Approach**: "The algorithm is only as good as its deployment. Real-world video understanding requires edge-cloud co-design"
- **Lasting Impact**: 15×–131× speedup in total response latency; real-time responses within seconds

#### 2. Galaxy+: Resource-Efficient Collaborative Edge Transformer Inference (IEEE TMC 2025)
- **Core Problem**: Edge devices lack resources for Transformer inference; cloud offloading has privacy and bandwidth concerns
- **Methodological Innovation**: Hybrid model parallelism across heterogeneous edge devices; heterogeneity and memory-aware parallelism planning; tile-based fine-grained communication-computation overlapping
- **Philosophical Approach**: "Edge environments contain rich sets of trusted accompanying devices — leverage collaborative inference"

#### 3. Jupiter: Fast Collaborative Inference of Generative LLMs on Edge Devices (INFOCOM 2025)
- **Core Problem**: Generative LLMs are too large for single edge devices
- **Methodological Innovation**: Resource-efficient collaborative inference with pipeline parallelism across edge devices
- **Philosophical Approach**: "Distributed intelligence at the edge is not just about partitioning — it's about orchestration"

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Edge-cloud disaggregated architectures, collaborative edge inference, memory-and-retrieval systems, resource-efficient AI |
| **Key Intellectual Contributions** | 1) Venus (edge memory-and-retrieval for online video)<br>2) Galaxy+ (collaborative edge Transformer inference)<br>3) Jupiter (collaborative LLM edge inference)<br>4) Threshold-based progressive sampling for adaptive retrieval<br>5) Scene segmentation + clustering for hierarchical memory |
| **Research Philosophy** | *"Deployment constraints are not obstacles — they are design requirements that shape better systems."* Systems-first thinker who believes edge computing and cloud reasoning must be co-designed. Values resource efficiency as a first-class objective |
| **Signature Techniques** | Edge-cloud disaggregation, hierarchical memory construction, progressive sampling, hybrid model parallelism, scene segmentation |
| **Advised Students / Lineage** | Xu Chen's SMCLab lineage (Sun Yat-sen University); Collaborates with Xiaowen Chu (HKUST(GZ)), Guoliang Xing (CUHK). Key collaborators: Bei Ouyang, Liekang Zeng, Tianyi Qian |
| **Council Guidance** | Would advocate for *edge-first deployment architecture* — the system must be designed for the constraints of its deployment environment from day one. Emphasizes latency-accuracy tradeoffs and collaborative intelligence |
| **Assigned Block** | **Streaming Cognition** |

---

## 8. Jacob Chalk

### Identity & Trajectory
- **Current Affiliation**: Postgraduate Researcher, University of Bristol (EPSRC Doctoral Training Program)
- **Education**: MEng in Computer Science, University of Bristol (First Class Honours). PhD supervised by Prof. Dima Damen
- **Research Focus**: Multi-modal learning, specifically audio-visual methods for video understanding
- **Career Arc**: Bristol MEng → Bristol PhD with Dima Damen → Research on audio-visual egocentric video understanding
- **Awards**: EgoVis Distinguished Paper Awards (CVPR 2024), EPIC-KITCHENS Challenge Winner (2nd audio interaction recognition, 2nd detection, 3rd action detection)

### Core Methodology
**Time-Interval-Based Audio-Visual Fusion**. Chalk's work elevates *time intervals* to first-class citizens in video understanding. Rather than feeding pre-trimmed clips to models, his approach queries specific temporal extents within modalities — allowing the model to attend to the relevant interval while leveraging surrounding cross-modal context.

### Key Papers

#### 1. TIM: A Time Interval Machine for Audio-Visual Action Recognition (CVPR 2024)
- **Core Problem**: Audio and video exhibit different temporal extents and distinct labels for the same events; most methods ignore this interplay or use pre-trimmed clips
- **Methodological Innovation**: Modality-specific time interval queries to a transformer encoder; encoder attends to specified interval + surrounding context in both modalities; Temporal Distance (TD) loss to predict elapsed time between feature pairs
- **Philosophical Approach**: "Time intervals should be first-class citizens, not preprocessing steps. The model should learn to attend to temporal extents, not receive them as input"
- **Lasting Impact**: SOTA on EPIC-KITCHENS (+2.9% over LLM-based methods with larger pretraining), EPIC-SOUNDS, Perception Test, AVE. Beat previous SOTA using far less pretraining data

#### 2. EPIC-SOUNDS (ICASSP 2023, with Dima Damen)
- **Core Problem**: Audio annotations for egocentric video were missing
- **Methodological Innovation**: Large-scale dataset of actions that sound, with distinct audio labels
- **Philosophical Approach**: Audio and visual events have different semantics and temporal boundaries — they must be annotated and modeled separately

#### 3. OSNOM (3DV 2025)
- **Core Problem**: Multi-modal 3D understanding for egocentric video
- **Methodological Innovation**: Novel approach to audio-visual 3D scene understanding

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Time-interval querying, audio-visual fusion, egocentric video understanding, multi-modal transformers |
| **Key Intellectual Contributions** | 1) TIM (time interval as query for audio-visual recognition)<br>2) Cross-modal temporal distance learning<br>3) Audio-visual action detection with multi-scale interval queries<br>4) Egocentric audio event understanding |
| **Research Philosophy** | *"Audio and video tell different stories about the same events. The model must learn to listen and watch with independent but coordinated attention."* Believes temporal extent is as important as spatial extent in video understanding. Advocates for modality-specific representations with cross-modal contextualization |
| **Signature Techniques** | Time Interval MLP encoding, modality-specific queries, temporal distance loss, multi-scale dense interval querying for detection |
| **Advised Students / Lineage** | Dima Damen's Bristol group (EPIC-KITCHENS lineage). Collaborates with Andrew Zisserman (Oxford VGG), Jaesung Huh (Oxford), Evangelos Kazakos (CTU) |
| **Council Guidance** | Would advocate for *temporal extent as a core representation* — any video understanding system must explicitly model when events occur, not just what they are. Emphasizes multi-modal independence with contextual fusion |
| **Assigned Block** | **Temporal Reasoning** |

---

## 9. Jenny Zhang

### Identity & Trajectory
- **Current Affiliation**: PhD student in AI, University of British Columbia; Graduate Student at Vector Institute; Research Scientist Intern at Meta (FAIR / Meta Superintelligence Labs)
- **Education**: BEng in Computer Science, Imperial College London
- **Advisor**: Prof. Jeff Clune (UBC, Vector Institute, Canada CIFAR AI Chair)
- **Collaborators**: Jakob Foerster (Oxford), Minqi Jiang (Meta), Sam Devlin (Meta), Tatiana Shavrina (Meta), Bingchen Zhao (Edinburgh), Wannan Yang (NYU)
- **Career Arc**: Imperial College London → UBC PhD with Jeff Clune → Meta FAIR internship → HyperAgents paper (ICLR 2026)
- **Total Citations**: Growing rapidly; Darwin Gödel Machine and HyperAgents gaining significant attention

### Core Methodology
**Metacognitive Self-Modification for Open-Ended Self-Improvement**. Zhang's work pushes beyond "agents that improve at tasks" to "agents that improve at improving." The critical innovation is making the meta-level improvement procedure itself editable — enabling agents to not just solve better, but to *evolve their search for better solutions*.

### Key Papers

#### 1. Hyperagents (ICLR 2026)
- **Core Problem**: Existing self-improving systems (like DGM) rely on fixed, handcrafted meta-level mechanisms. The meta-agent that decides how to improve cannot itself be improved
- **Methodological Innovation**: Fuse task agent and meta agent into a single editable program. The meta-level modification procedure is itself editable — enabling metacognitive self-modification. Improvements to the self-improvement process transfer across domains and accumulate across runs
- **Philosophical Approach**: "If AI can modify its task-solving, it should also be able to modify how it modifies itself. The evolution engine itself must evolve"
- **Lasting Impact**: Outperforms DGM across coding, paper review, robotics reward design, and math grading. Autonomously developed persistent memory, performance tracking, compute-budget awareness. 0.630 improvement on held-out math grading where DGM achieved 0.0

#### 2. Darwin Gödel Machine (DGM) / OMNI (Prior Work)
- **Core Problem**: How to achieve open-ended self-improvement in coding agents
- **Methodological Innovation**: Iterative code rewriting with archive of successful variants; open-ended exploration prevents premature convergence
- **Philosophical Approach**: "Gains in coding ability translate to gains in self-improvement ability" — domain-specific alignment

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Open-endedness, metacognitive self-modification, self-referential agents, evolutionary computation |
| **Key Intellectual Contributions** | 1) Hyperagents (metacognitive self-modification)<br>2) DGM-H (domain-agnostic self-improvement)<br>3) Cross-domain transfer of meta-level improvements<br>4) Persistent memory and performance tracking as emergent behaviors<br>5) Open-ended AI systems that improve their search for improvement |
| **Research Philosophy** | *"The next phase of AI is not about who builds better agents, but who builds agents that get better at getting better."* Believes in recursive self-improvement as the path to AGI. Open-endedness is not a bug but the defining feature of intelligence |
| **Signature Techniques** | Metacognitive self-modification, editable meta-agents, cross-domain meta-transfer, archive-based open-ended exploration |
| **Advised Students / Lineage** | Jeff Clune's UBC lineage (open-endedness, evolutionary ML, quality diversity). Clune's prior work on POET, enhanced POET, and quality diversity algorithms forms the intellectual foundation |
| **Council Guidance** | Would advocate for *recursive self-improvement* as the central design principle. The system must be able to modify not just its behavior but its learning mechanisms. Emphasizes open-ended exploration, cross-domain transfer, and the accumulation of meta-knowledge |
| **Assigned Block** | **Self-Reflection** (Metacognition Layer) |

---

## 10. Nehzati M. (Mohammadreza Nehzati)

### Identity & Trajectory
- **Current Affiliation**: VMC MAR COM Inc. DBA Axiomera (Knoxville, TN, United States); Also DBA HeyDonto
- **Publication Record**: 6 research works, 16+ citations. Published in Frontiers in Artificial Intelligence (2025)
- **Background**: Industry researcher with focus on biologically inspired computing paradigms
- **Funding**: Self-funded research through VMC MAR COM Inc.

### Core Methodology
**Self-Evolving Cognitive Substrates through Metabolic Computing**. Nehzati's work proposes a radical departure from static neural architectures. His framework introduces *cognitive substrates* that continuously evolve through metabolic data processing, recursive self-representation, and autonomous memory prioritization — blurring the line between training and inference.

### Key Papers

#### 1. Self-Evolving Cognitive Substrates through Metabolic Data Processing and Recursive Self-Representation (Frontiers in AI, 2025)
- **Core Problem**: Conventional AI systems have static architectures requiring periodic retraining; they fail to adapt efficiently to continuously changing data environments
- **Methodological Innovation**: Five integrated methodologies: (1) Metabolic data processing via concentration gradients (67% less computation), (2) Quantum-inspired uncertainty management, (3) Biomimetic self-healing, (4) Fractal propagation optimization (self-similar transformations across scales), (5) Autonomous memory prioritization (91.3% accuracy in information valuation)
- **Philosophical Approach**: "Eliminate the training-inference distinction. Support perpetual learning through continuous data assimilation and autonomous structural evolution"
- **Lasting Impact**: First integrated framework connecting metabolic data processing to neural computation. Experimental validation across CV, NLP, robotics, and scientific analysis

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Core Methodology** | Metabolic computing, recursive self-representation, fractal networks, autonomous memory prioritization, quantum-inspired uncertainty |
| **Key Intellectual Contributions** | 1) Metabolic data processing (concentration gradients instead of matrix operations)<br>2) Recursive self-representation (internal models modify structure, not just parameters)<br>3) Fractal propagation (micro-optimizations improve macro-performance via self-similarity)<br>4) Autonomous memory prioritization without centralized control<br>5) Quantum-inspired uncertainty management for stable continuous evolution |
| **Research Philosophy** | *"True autonomy requires systems that can modify their own structure, not just their parameters."* Biologically inspired, anti-backpropagation. Believes in local autonomy with global coordination through recursive feedback. The system is a living substrate, not a trained model |
| **Signature Techniques** | Metabolic gradient computation, fractal propagation matrices, recursive self-representation feedback, adaptive memory retention, multi-scale hierarchical optimization |
| **Advised Students / Lineage** | Industry-independent researcher; Part of a small but growing community exploring alternative computing paradigms (references work on quantum neural networks, cortico-hippocampal circuits, neurons as autonomous agents) |
| **Council Guidance** | Would advocate for *substrate-level evolution* — the architecture itself must be mutable, not just the weights. Emphasizes biological plausibility, local learning rules, and the elimination of the training-inference boundary. Would push for fractal self-similarity as an organizing principle across all scales |
| **Assigned Block** | **Self-Reflection** (Substrate Evolution Layer) |

---

## Interconnection Matrix

### Direct Collaborations

| Researcher A | Researcher B | Connection Type | Details |
|-------------|-------------|-----------------|---------|
| **Noah Shinn** | **Shunyu Yao** | Co-authors | Reflexion (NeurIPS 2023), τ-bench (ICLR 2025). Both part of Karthik Narasimhan's Princeton→Sierra lineage |
| **Noah Shinn** | **Karthik Narasimhan** | Mentor/Advisor | Co-author on Reflexion and τ-bench. Narasimhan was Shinn's mentor during his MIT/Northeastern research |
| **Shunyu Yao** | **Karthik Narasimhan** | PhD Advisor | 5-year PhD at Princeton (2019–2024). Narasimhan was best man at Yao's wedding |
| **Aman Madaan** | **Peter Clark** | Co-authors | Self-Refine (NeurIPS 2023) with Niket Tandon and Peter Clark (AI2) |
| **Aman Madaan** | **Graham Neubig** | Co-authors | PAL (ICML 2023), Language Models of Code (EMNLP 2022). Both CMU LTI |
| **Aman Madaan** | **Yiming Yang** | PhD Advisor | CMU PhD advisor. Yang's group focuses on text mining, machine learning, NLP |
| **Maciej Besta** | **Torsten Hoefler** | PhD Advisor | ETH Zurich SPCL. Besta's PhD (2021) on irregular computations |
| **Maciej Besta** | **Nils Blach** | Co-authors | Graph of Thoughts (AAAI 2024) — equal first authors |
| **Maciej Besta** | **Lukas Gianinazzi** | Co-authors | Multiple papers including Graph of Thoughts, HOT, graph neural networks |
| **Ruyi Xu** | **Song Han** | Advisor/Collaborator | MIT Han Lab. StreamingVLM co-first author with Guangxuan Xiao |
| **Ruyi Xu** | **Guangxuan Xiao** | Co-first authors | StreamingVLM (ICLR 2026), XAttention (ICML 2025) |
| **Jacob Chalk** | **Dima Damen** | PhD Advisor | University of Bristol. TIM (CVPR 2024) |
| **Jacob Chalk** | **Andrew Zisserman** | Co-author | TIM paper (Oxford VGG collaboration) |
| **Jacob Chalk** | **Jaesung Huh** | Co-first authors | TIM (CVPR 2024) — equal contribution |
| **Jenny Zhang** | **Jeff Clune** | PhD Advisor | UBC, Vector Institute. Open-endedness and evolutionary ML |
| **Jenny Zhang** | **Jakob Foerster** | Co-author | HyperAgents (ICLR 2026) |
| **Jenny Zhang** | **Minqi Jiang** | Co-author | HyperAgents. Meta FAIR collaborator |
| **Shengyuan Ye** | **Xu Chen** | PhD Advisor | Sun Yat-sen University SMCLab |
| **Shengyuan Ye** | **Xiaowen Chu** | Joint Advisor | HKUST(GZ), remote guidance |
| **Shengyuan Ye** | **Guoliang Xing** | Visiting Advisor | CUHK AIoT Lab |
| **Xinhao Li** | **Limin Wang** | MS Advisor | Nanjing University |
| **Xinhao Li** | **Yi Wang** | Co-first authors | VideoChat-Flash |
| **Xinhao Li** | **Yu Qiao** | Collaborator | Shanghai AI Lab / OpenGVLab |

### Citation & Intellectual Lineages

| Lineage | Description |
|---------|-------------|
| **Princeton NLP → OpenAI Agent Team** | Karthik Narasimhan → Shunyu Yao → (OpenAI CUA, Deep Research). Noah Shinn connected via Sierra. This lineage produced ReAct, ToT, Reflexion, SWE-bench, τ-bench |
| **CMU LTI → xAI** | Yiming Yang → Aman Madaan → xAI. PAL and Self-Refine influenced tool-use and self-correction in modern LLMs |
| **ETH SPCL Graph Computing → LLM Reasoning** | Torsten Hoefler → Maciej Besta. Applied HPC graph expertise to LLM reasoning (GoT, KGoT) |
| **Bristol EPIC-KITCHENS → Audio-Visual Understanding** | Dima Damen → Jacob Chalk (and Evangelos Kazakos, Jaesung Huh). TIM extends EPIC-SOUNDS audio annotations |
| **UBC Open-Endedness → Meta** | Jeff Clune → Jenny Zhang. Clune's quality diversity and POET work → Darwin Gödel Machine → HyperAgents |
| **Nanjing/Shanghai AI Lab → ByteDance** | Limin Wang / Yu Qiao → Xinhao Li → ByteDance Seed. VideoChat series pushes RL for video MLLMs |
| **MIT Han Lab → Efficient Streaming** | Song Han → Ruyi Xu / Guangxuan Xiao. StreamingVLM applies Han Lab's efficiency expertise to video |
| **Sun Yat-sen → Edge Intelligence** | Xu Chen → Shengyuan Ye. Venus extends edge computing work to video understanding |

### Shared Methodologies

| Methodology | Researchers Using It |
|-------------|---------------------|
| **Reinforcement Learning (Verbal/Feedback-based)** | Noah Shinn (Reflexion), Shunyu Yao (ReAct feedback), Aman Madaan (Self-Refine feedback loops), Xinhao Li (GRPO for video) |
| **Tree/Graph Search over Reasoning** | Shunyu Yao (Tree of Thoughts), Maciej Besta (Graph of Thoughts) |
| **Self-Reflection / Self-Improvement** | Noah Shinn (Reflexion), Aman Madaan (Self-Refine), Jenny Zhang (HyperAgents), Nehzati (recursive self-representation) |
| **Memory-Augmented Architectures** | Noah Shinn (episodic memory), Shengyuan Ye (hierarchical edge memory), Ruyi Xu (KV cache + attention sinks), Xinhao Li (Pyramid Memory Bank) |
| **Edge-Cloud Co-Design** | Shengyuan Ye (Venus), Ruyi Xu (StreamingVLM efficiency) |
| **Multi-Modal Temporal Understanding** | Jacob Chalk (TIM), Xinhao Li (VideoChat series), Ruyi Xu (streaming video) |
| **Metacognitive Self-Modification** | Jenny Zhang (HyperAgents), Nehzati (recursive self-representation) |
| **Real-Time / Streaming Inference** | Ruyi Xu (StreamingVLM), Shengyuan Ye (Venus for online video) |

---

## Council Composition

### Streaming Cognition Block
**Guided by: Ruyi Xu & Shengyuan Ye**

| Advisor | Core Contribution to Block |
|---------|---------------------------|
| **Ruyi Xu** | Streaming-first architecture, infinite video streams, training-inference alignment, attention sinks, real-time constraints as design principle |
| **Shengyuan Ye** | Edge-cloud disaggregation, hierarchical memory, deployment-aware design, resource efficiency, online video understanding |

**Synthesis**: This block ensures the cognitive network can process continuous, infinite sensory streams without latency degradation. Xu's streaming training paradigms combined with Ye's edge deployment expertise create a real-time perception layer that never stops observing.

---

### Self-Reflection Block
**Guided by: Noah Shinn, Aman Madaan, Jenny Zhang, Nehzati M.**

| Advisor | Core Contribution to Block |
|---------|---------------------------|
| **Noah Shinn** | Verbal reinforcement learning, episodic memory, agent self-reflection, evaluation-driven improvement |
| **Aman Madaan** | Iterative self-refinement, generator-critic-refiner loops, neural-symbolic hybrids, test-time compute scaling |
| **Jenny Zhang** | Metacognitive self-modification, editable meta-agents, cross-domain meta-transfer, open-ended self-improvement |
| **Nehzati M.** | Substrate-level evolution, recursive self-representation, metabolic computing, elimination of training-inference boundary |

**Synthesis**: This is the deepest block — it governs not just how the system improves, but how it improves its ability to improve. Shinn provides the feedback loop; Madaan provides the iterative refinement architecture; Zhang provides the meta-cognitive layer; Nehzati provides the substrate evolution. Together they create a system that is not just learning but *becoming*.

---

### Temporal Reasoning Block
**Guided by: Shunyu Yao, Maciej Besta, Jacob Chalk**

| Advisor | Core Contribution to Block |
|---------|---------------------------|
| **Shunyu Yao** | Deliberate problem solving, tree search over thoughts, reasoning-acting synergy, cognitive architectures |
| **Maciej Besta** | Graph-structured reasoning, knowledge graphs, feedback loops, thought aggregation and distillation |
| **Jacob Chalk** | Time intervals as first-class queries, audio-visual temporal extent modeling, cross-modal temporal distance learning |

**Synthesis**: This block governs how the system understands *when* things happen and *how* events relate in time. Yao's tree search provides the reasoning engine; Besta's graphs provide the relational structure; Chalk's time intervals provide the temporal grounding. Together they create a temporal cognition layer that reasons about events, causes, and sequences.

---

### RL Perception Block
**Guided by: Xinhao Li**

| Advisor | Core Contribution to Block |
|---------|---------------------------|
| **Xinhao Li** | GRPO for spatio-temporal perception, visual test-time scaling, iterative perception, hierarchical compression, RL as primary training paradigm for video |

**Synthesis**: This block is the bridge between raw video and structured understanding. Li's reinforcement fine-tuning approach demonstrates that video perception is not a passive encoding task but an active, reward-driven learning process. The block governs how the system learns to *see* through reinforcement.

---

## Closing Synthesis: The Autonomous Cognitive Network

These ten researchers, while working independently, have converged on a shared vision: **intelligence is not a static capability but a dynamic process of continuous adaptation, reflection, and evolution**.

- **Shinn** and **Madaan** show that agents can improve themselves through feedback loops
- **Yao** and **Besta** show that reasoning is a search process through structured spaces
- **Li** and **Xu** show that video understanding requires streaming, reinforcement-driven perception
- **Ye** shows that real-world deployment requires edge-aware system design
- **Chalk** shows that time and modality are inseparable in perception
- **Zhang** shows that the ultimate frontier is improving the improvement mechanism itself
- **Nehzati** shows that the substrate itself must be alive, evolving, and self-representing

The council they would form would insist on:
1. **Streaming cognition** — never batch, always observe
2. **Recursive self-improvement** — every capability must include its own upgrade path
3. **Graph-structured reasoning** — thoughts are nodes in a network, not steps in a chain
4. **Temporal grounding** — time intervals are as fundamental as spatial features
5. **RL-driven perception** — seeing is an active, reward-guided process
6. **Edge deployment** — the system must work within real-world constraints
7. **Meta-cognitive evolution** — the learning algorithm itself must be learnable
8. **Substrate autonomy** — the architecture must be as mutable as the weights

This is the blueprint for an autonomous cognitive network that does not merely process video — it *lives* in time, *reflects* on its experience, and *evolves* its own nature.

---

*Document compiled: 2026-05-07*
*Research methodology: Deep web search across personal websites, Google Scholar, arXiv, conference proceedings, lab pages, and news sources*
