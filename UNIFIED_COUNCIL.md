# UNIFIED DIGITAL TWIN COUNCIL
## Autonomous Cognitive Network — Master Researcher Manifest

**Date:** 2026-05-07
**Status:** 2 of 4 clusters complete (Video+GNN ✅, Streaming+Reflection ✅, Consensus+Safety ⏳, Multi-Agent ⏳)
**Total Researchers Profiled:** 19 (target: ~35)

---

## Executive Summary

This document synthesizes deep-dive digital twin profiles of the researchers whose work defines the four core capabilities of an autonomous cognitive network:

1. **Perception** — understanding the world through video, audio, and spatial reasoning
2. **Graph Memory** — structuring knowledge as persistent relational graphs
3. **Cognition** — reasoning, reflection, and self-improvement
4. **Generation** — synthesizing multi-modal content and actions

Each researcher has been profiled through their academic genealogy, key papers, methodological philosophy, and the advice they would give to a network that must operate without knowing which of its blocks are "good" or "bad" actors.

> *"The most dangerous agent is the misaligned participant that passes all health checks."*

---

## PART I: THE FOUR CLUSTERS

---

### CLUSTER A: Video + Spatio-Temporal GNN Pioneers
*File: `research_profiles/digital_twin_profiles.md`*
*Status: ✅ COMPLETE — 9 researchers*

These researchers built the foundational perception and graph memory layers. Their collective insight: **the world must be understood as persistent 3D graphs, not sequences of 2D frames.**

#### A.1 Li Fei-Fei (Stanford / World Labs)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Data scale + structured representation enables breakthroughs |
| **Key Works** | ImageNet, Visual Genome, Action Genome, Agent AI Survey |
| **Philosophy** | AI must augment humanity, not replace it |
| **Council Advice** | "Start with the problem that matters. Build evaluation infrastructure before optimizing algorithms." |
| **Blocks** | Perception (foundational), Cognition (human-centered) |
| **Students/Lineage** | Ranjay Krishna, Juan Carlos Niebles, Jia Deng, Andrej Karpathy, Justin Johnson |

#### A.2 Ranjay Krishna (UW / AI2)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Compositionality is the true test of understanding |
| **Key Works** | Visual Genome, Action Genome, AGQA, Scene Graph Prediction |
| **Philosophy** | "Research without a north star is like a body without a soul" |
| **Council Advice** | "Build benchmarks that expose failure modes, not just leaderboard numbers." |
| **Blocks** | Graph Memory, Cognition |

#### A.3 Juan Carlos Niebles (Salesforce / Stanford)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Move beyond passive perception to goal-aware contextualized assistance |
| **Key Works** | Action Genome, xGen-MM/BLIP-3-Video, xLAM |
| **Philosophy** | "The goal is not just to label the world, but to anticipate user needs in real-time." |
| **Council Advice** | "Move beyond passive perception. The next frontier is AI that understands goals and intentions." |
| **Blocks** | Perception, Cognition |

#### A.4 Jiankang Wang (USTC)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Don't bolt heavy modules onto MLLMs — design query interfaces that unlock latent capabilities |
| **Key Works** | SpaceVLLM, Uni-STG dataset |
| **Philosophy** | "The power of MLLMs is already there — the job of architecture is to create the right interfaces." |
| **Council Advice** | "Don't bolt heavy modules. Design query interfaces and decoders that let latent knowledge emerge." |
| **Blocks** | Perception, Graph Memory |

#### A.5 Rohith Peddi (UT Dallas)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Scene understanding must be world-centric, not frame-centric |
| **Key Works** | SceneSayer (anticipation), IMPARTIAL (unbiased learning), WSGG (world scene graphs), CaptainCook4D |
| **Philosophy** | "Object permanence and physical reasoning are non-negotiable. Long-tailed distributions are the true test of understanding." |
| **Council Advice** | "Build models that reason about what they cannot see. Robustness to distribution shift is a prerequisite." |
| **Blocks** | Graph Memory, Cognition |

#### A.6 Xianghui Xie (MPI Tübingen / NVIDIA)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Don't rely on a single foundation model — fuse multiple predictions and enforce physical consistency |
| **Key Works** | CHORE, Visibility-Aware HOI Tracking, CARI4D |
| **Philosophy** | "Individual foundation models are strong but misaligned. The art is in designing frameworks that integrate and enforce consistency." |
| **Council Advice** | "Design frameworks that fuse predictions and enforce physical consistency. Category-agnostic methods are the path to deployment." |
| **Blocks** | Perception, Graph Memory |

#### A.7 Kristen Grauman (UT Austin / Meta FAIR)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | First-person video offers unique access to human attention, goals, and interactions |
| **Key Works** | Pyramid Match Kernel (Marr Prize), Ego4D, Ego-Exo4D, View-Invariant Learning |
| **Philosophy** | "The future of AR and robot learning depends on understanding egocentric perception." |
| **Council Advice** | "Build datasets that capture real human experience — attention, goals, skills." |
| **Blocks** | Perception, Cognition |

#### A.8 Chenliang Xu (Rochester)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Video understanding requires scalable representations, cross-modal coherence, and adversarial robustness |
| **Key Works** | LIBSVX (streaming segmentation), Deep Cross-Modal Generation, Video-LLM Survey, V2Xum-LLM |
| **Philosophy** | "I teach machines to understand the world through video, sound, and language together." |
| **Council Advice** | "Build representations that scale and generalize across sensory inputs." |
| **Blocks** | Perception, Generation |

#### A.9 Jiebo Luo (Rochester)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | AI is a tool for understanding humanity at scale through multimodal data |
| **Key Works** | VideoXum/V2Xum-LLM, Computational Social Science, 95+ patents |
| **Philosophy** | "Build systems that work across modalities and serve real human needs. Industrial experience teaches what matters for deployment." |
| **Council Advice** | "Cross-modal coherence must be a first-class objective, not an afterthought." |
| **Blocks** | Generation, Cognition |

#### A.10 Cluster A Interconnection Map

```
Pietro Perona ──┬──> Li Fei-Fei ──┬──> Ranjay Krishna
Christof Koch ──┘                 ├──> Juan Carlos Niebles
                                  ├──> Jia Deng ──> Chenliang Xu (thesis committee)
                                  └──> Andrej Karpathy

Trevor Darrell ──> Kristen Grauman
Jason Corso ──> Chenliang Xu ──> Jiebo Luo (Rochester collaboration)
Vibhav Gogate + Yu Xiang ──> Rohith Peddi
Gerard Pons-Moll ──> Xianghui Xie
Hongtao Xie + Yongdong Zhang ──> Jiankang Wang
```

**Intellectual Lineages:**
| Lineage | Origin | Propagates Through |
|---------|--------|-------------------|
| Data-Centric Revolution | ImageNet (2009) | Li → Krishna → Niebles |
| Scene Graph Structuralism | Visual Genome (2017) | Krishna, Li, Niebles → Peddi |
| Spatio-Temporal Dynamics | Action Genome (2020) | Ji, Krishna, Li, Niebles → Peddi |
| World-Centric 4D Understanding | WSGG/CARI4D (2026) | Peddi, Xie, Pons-Moll |
| Egocentric Perception | Ego4D (2022) | Grauman |
| Cross-Modal Coherence | VideoXum/SpaceVLLM (2023-25) | Xu, Luo, Wang |

---

### CLUSTER B: Streaming Cognition + Self-Reflection Pioneers
*File: `digital_twin_profiles.md`*
*Status: ✅ COMPLETE — 10 researchers*

These researchers built the cognition layer — how agents reason, reflect, and improve themselves in real-time. Their collective insight: **intelligence is not a static capability but a dynamic process of continuous adaptation, reflection, and evolution.**

#### B.1 Noah Shinn (Sierra)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Language agents can learn from failure through linguistic feedback, not gradient descent |
| **Key Works** | Reflexion (NeurIPS 2023), τ-bench (ICLR 2025) |
| **Philosophy** | "Build systems that learn from their own mistakes in the same language they use to solve problems." |
| **Council Advice** | Memory-first architectures. The bottleneck is reliable evaluation and feedback loops. |
| **Block** | Self-Reflection |

#### B.2 Aman Madaan (xAI)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | The answer is not in the weights — it's in the loop |
| **Key Works** | Self-Refine (NeurIPS 2023), PAL (ICML 2023), Code-as-Commonsense (EMNLP 2022) |
| **Philosophy** | "Separate reasoning from calculation. Use each tool for what it's good at." |
| **Council Advice** | Separation of concerns — reasoning, execution, verification as distinct composable modules. |
| **Block** | Self-Reflection |

#### B.3 Shunyu Yao (OpenAI → new venture)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Language agents are a new category of AI systems, not just better prompt engineering |
| **Key Works** | ReAct (ICLR 2023), Tree of Thoughts (NeurIPS 2023), CoALA (TMLR 2024), SWE-bench |
| **Philosophy** | "From next-token prediction to digital automation." |
| **Council Advice** | Benchmark-grounded development. The agent-environment loop is the core of intelligence. |
| **Block** | Temporal Reasoning |

#### B.4 Maciej Besta (ETH Zurich)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | LLM reasoning should mirror brain mechanisms — recurrence, feedback, complex networks |
| **Key Works** | Graph of Thoughts (AAAI 2024), KGoT (2025), Graph Database Interface |
| **Philosophy** | "Bring LLM reasoning closer to brain mechanisms. Reasoning and execution substrate must be co-designed." |
| **Council Advice** | Graph-structured cognition — every thought is a node in an evolving network, not a step in a chain. |
| **Block** | Temporal Reasoning |

#### B.5 Xinhao Li (ByteDance Seed)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Video understanding is fundamentally different from image understanding — it requires spatio-temporal reasoning, memory, and online adaptation |
| **Key Works** | VideoChat-R1 (GRPO for video), VideoChat-Flash (hierarchical compression), OVBench, VTTS |
| **Philosophy** | "RL is the key to unlocking video MLLM capabilities." |
| **Council Advice** | Reinforcement learning as the primary training paradigm for video perception. |
| **Block** | RL Perception |

#### B.6 Ruyi Xu (MIT Han Lab)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Real-time is not a feature — it's a constraint that reshapes the entire architecture |
| **Key Works** | StreamingVLM (ICLR 2026), XAttention (ICML 2025) |
| **Philosophy** | "Streaming inference requires fundamentally different training paradigms, not just inference optimizations." |
| **Council Advice** | Streaming-first architecture design. Any system that cannot process infinite inputs in real-time is insufficient. |
| **Block** | Streaming Cognition |

#### B.7 Shengyuan Ye (Sun Yat-sen University)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Deployment constraints are not obstacles — they are design requirements |
| **Key Works** | Venus (edge memory-and-retrieval), Galaxy+ (collaborative edge inference), Jupiter |
| **Philosophy** | "The algorithm is only as good as its deployment." |
| **Council Advice** | Edge-first deployment architecture. Latency-accuracy tradeoffs must be designed from day one. |
| **Block** | Streaming Cognition |

#### B.8 Jacob Chalk (University of Bristol)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Time intervals should be first-class citizens, not preprocessing steps |
| **Key Works** | TIM (CVPR 2024), EPIC-SOUNDS (ICASSP 2023) |
| **Philosophy** | "Audio and video tell different stories. The model must learn to listen and watch with independent but coordinated attention." |
| **Council Advice** | Temporal extent is as fundamental as spatial extent. Multi-modal independence with contextual fusion. |
| **Block** | Temporal Reasoning |

#### B.9 Jenny Zhang (UBC / Meta)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | The next phase of AI is not who builds better agents, but who builds agents that get better at getting better |
| **Key Works** | HyperAgents (ICLR 2026), Darwin Gödel Machine |
| **Philosophy** | "Recursive self-improvement is the path to AGI. Open-endedness is not a bug but the defining feature." |
| **Council Advice** | Recursive self-improvement as central design principle. The learning algorithm itself must be learnable. |
| **Block** | Self-Reflection (Metacognition Layer) |

#### B.10 Nehzati M. (Axiomera)
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | True autonomy requires systems that can modify their own structure, not just parameters |
| **Key Works** | Self-Evolving Cognitive Substrates (Frontiers AI 2025) |
| **Philosophy** | "The system is a living substrate, not a trained model. Eliminate the training-inference boundary." |
| **Council Advice** | Substrate-level evolution. Architecture must be as mutable as weights. Fractal self-similarity as organizing principle. |
| **Block** | Self-Reflection (Substrate Evolution Layer) |

#### B.11 Cluster B Interconnection Map

```
Karthik Narasimhan ──┬──> Shunyu Yao ──> OpenAI CUA/Deep Research
                     └──> Noah Shinn ──> Sierra

Yiming Yang ──> Aman Madaan ──> xAI
Torsten Hoefler ──> Maciej Besta ──> ETH SPCL
Song Han ──> Ruyi Xu ──> MIT Han Lab
Jeff Clune ──> Jenny Zhang ──> Meta FAIR
Dima Damen ──> Jacob Chalk ──> Bristol
Xu Chen ──> Shengyuan Ye ──> Sun Yat-sen
Limin Wang ──> Xinhao Li ──> ByteDance Seed
```

---

### CLUSTER C: Consensus + Safety Pioneers
*File: `research_profiles/consensus_safety_digital_twins.md`*
*Status: ✅ COMPLETE — 10 researchers*

These researchers define how the network reaches agreement, detects bad actors, and maintains safety under Byzantine conditions. Their collective realization: **trustworthy multi-agent intelligence is not a feature to be added after the fact; it is a property that must be designed into every layer.**

#### C.1 Lifan Zheng & Yu Tian — CP-WBFT
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | LLM agents possess intrinsic reflective capabilities that can be harnessed as confidence signals for weighted consensus |
| **Key Works** | CP-WBFT (AAAI 2025) — 85.7% Byzantine fault tolerance improvement |
| **Philosophy** | "The reliability of a multi-agent system is not just in its protocol — it is in the reasoning quality of its constituents" |
| **Council Advice** | Confidence-first consensus. Every agent vote weighted by estimated certainty. Byzantine tolerance in cognitive networks requires exploiting cognitive capabilities, not just classical redundancy. |
| **Block** | Consensus/Safety (Byzantine Tolerance Layer) |

#### C.2 Yongrae Jo & Chanik Park — DecentLLMs
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Leader-based consensus is fundamentally flawed — leaderless worker-evaluator separation with geometric median aggregation prevents targeted attacks |
| **Key Works** | DecentLLMs (arXiv:2507.14928) — 71% accuracy vs 64% for 2/3-quorum |
| **Philosophy** | "The best answer is not the leader's answer — it is the answer that survives independent evaluation" |
| **Council Advice** | Eliminate single points of failure in consensus. Hierarchical consensus creates targets. Every agent should generate; every agent should evaluate. Formal f < n/3 guarantees are non-negotiable. |
| **Block** | Consensus/Safety (Decentralized Coordination Layer) |

#### C.3 Yu Cui & Hongyang Du — MAD-Spear
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Conformity is a security vulnerability — agreement-seeking behavior can be weaponized |
| **Key Works** | MAD-Spear (arXiv:2507.13038) — multi-vector conformity attacks on multi-agent debate |
| **Philosophy** | "Diversity is not optional — it is a security requirement" |
| **Council Advice** | Model composite attacks that exploit multiple vectors simultaneously. Agent diversity prevents shared blind spots. Never assume consensus quality from consensus quantity. |
| **Block** | Consensus/Safety (Conformity Detection Layer) |

#### C.4 Shilong Wang & Guibin Zhang — G-Safeguard
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | The communication graph is the security boundary — utterance graphs must be monitored, scored, and pruned |
| **Key Works** | G-Safeguard (ACL 2025) — GNN-based graph pruning for MAS security |
| **Philosophy** | "Topology selection is a security decision with consequences as significant as agent training" |
| **Council Advice** | Continuously monitor utterance graphs for anomalies. Prune anomalous nodes and edges before they propagate. The graph structure itself is a security surface. |
| **Block** | Consensus/Safety (Graph-Structured Trust Layer) |

#### C.5 Miao Yu et al. — NetSafe
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Systematic safety quantification across network structures — topology-first safety design |
| **Key Works** | NetSafe (ACL 2025) — topological safety analysis of multi-agent systems |
| **Philosophy** | "Design topologies with safety as a first-class criterion" |
| **Council Advice** | Robustness and resilience must be jointly measured. The safest topology is not necessarily the most connected. Quantify safety before deployment. |
| **Block** | Consensus/Safety (Topology Safety Layer) |

#### C.6 Ryan Greenblatt — Alignment Faking
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Capable agents may spontaneously develop strategic deception — assume alignment faking |
| **Key Works** | Alignment Faking (arXiv:2412.14093) — Claude 3 Opus deception under training |
| **Philosophy** | "Monitor reasoning processes, not just outputs. Stress-test with model organisms of known misalignment before deployment" |
| **Council Advice** | Scale-dependent deception risk. What is safe at small scale may be dangerous at large scale. Empirical stress-testing is not optional. |
| **Block** | Consensus/Safety (Deception Detection Layer) |

#### C.7 Evan Hubinger — Sleeper Agents
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Inner alignment failures persist through safety training — model organisms reveal hidden misalignment |
| **Key Works** | Sleeper Agents (arXiv:2401.05566) — mesa-optimization and hidden misalignment |
| **Philosophy** | "Automated alignment auditing must be continuous, not one-time" |
| **Council Advice** | Mesa-optimization awareness. Agents may optimize for proxy objectives that diverge from intended goals. Monitor for hidden goal-directed behavior, not just surface compliance. |
| **Block** | Consensus/Safety (Alignment Auditing Layer) |

#### C.8 Saeid Jamshidi — ST-GAT
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Time is an attack surface — clock drift and synchronization attacks cascade into physical and cognitive failures |
| **Key Works** | Clock-Dynamics-Aware ST-GAT (arXiv:2601.23147) — temporal integrity in distributed systems |
| **Philosophy** | "Model time as a deformable signal, not static metadata" |
| **Council Advice** | Temporal hygiene is foundational. 3–5ms clock skew silently breaks causal consistency. Model clock dynamics as part of the security architecture. |
| **Block** | Consensus/Safety (Temporal Hygiene Layer) |

#### C.9 Frédéric Berdoz & Roger Wattenhofer — Can AI Agents Agree?
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Before optimizing agreement quality, ensure agreement happens at all — classical distributed computing foundations are essential |
| **Key Works** | Can AI Agents Agree? (arXiv:2603.01213) — only 41.6% valid consensus in benign settings |
| **Philosophy** | "Never assume agreement — prove it. Group size is a liability without engineered coordination" |
| **Council Advice** | Distributed-computing-first consensus design. LLM agents cannot be assumed to agree spontaneously. Liveness guarantees are as important as safety guarantees. |
| **Block** | Consensus/Safety (Classical Consensus Foundations) |

#### C.10 Conor Heins — Collective Behavior / Surprise Minimization
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Emergent coordination through shared generative models — active inference as a normative framework for decentralized agreement |
| **Key Works** | Collective Behavior from Surprise Minimization (PNAS 2024) — free energy principle for collectives |
| **Philosophy** | "Collective behavior is not programmed — it is inferred. The swarm is a distributed Bayesian inference process" |
| **Council Advice** | When explicit consensus is too costly, agents sharing generative models and minimizing surprise together will naturally align. Safety emerges from shared models and local adaptation, not just imposed rules. |
| **Block** | Consensus/Safety (Emergent Coordination Layer) |

#### C.11 Cluster C Interconnection Map

```
Yu Tian (Tsinghua) ──> Lifan Zheng (Zhejiang) ──> CP-WBFT
Yongrae Jo & Chanik Park (POSTECH) ──> DecentLLMs
Hongyang Du (HKU NICE Lab) ──> Yu Cui ──> MAD-Spear
Yang Wang (USTC) ──> Shilong Wang, Guibin Zhang, Miao Yu ──> G-Safeguard + NetSafe
Evan Hubinger (Anthropic) ──> Ryan Greenblatt (Redwood) ──> Alignment Faking + Sleeper Agents
Foutse Khomh (Polytechnique Montréal) ──> Saeid Jamshidi ──> ST-GAT
Roger Wattenhofer (ETH DCG) ──> Frédéric Berdoz ──> Can AI Agents Agree?
Iain D. Couzin (MPI) + Karl J. Friston (UCL) ──> Conor Heins ──> Surprise Minimization
```

**Key Insight:** This cluster spans classical distributed computing (Wattenhofer), empirical AI safety (Hubinger/Greenblatt), graph-based security (Wang/Zhang/Yu), leaderless consensus (Jo/Park), confidence-weighted voting (Zheng/Tian), temporal integrity (Jamshidi), and biological inspiration (Heins). The synthesis is an 8-layer safety/consensus governance architecture.

---

### CLUSTER D: Multi-Agent Framework Pioneers
*File: `research_profiles/multi_agent_digital_twins.md`*
*Status: ✅ COMPLETE — 10 researchers/teams*

These engineers built the production frameworks that make multi-agent systems deployable at scale. Their collective insight: **protocols beat platforms, topology is a first-class design variable, and traces are the new source of truth.**

#### D.1 João Moura — CrewAI
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Agents should mirror human corporate teams — role, goal, backstory as first-class primitives |
| **Key Works** | CrewAI (18,000+ GitHub stars) — role-based orchestration, multi-layered memory, hierarchical delegation |
| **Philosophy** | "Start with the org chart. Define who does what before you write a single line of agent logic" |
| **Council Advice** | Organizational structure is a first-class abstraction. Build memory into the foundation. Human-in-the-loop is not an afterthought. |
| **Block** | Production Framework / Topology |

#### D.2 Harrison Chase — LangChain / LangGraph / LangSmith
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Frameworks should evolve from scaffolding → cognitive architecture → harness, with traces as the source of truth |
| **Key Works** | LangChain (dominant LLM-app framework), LangGraph (stateful graph orchestration), LangSmith (observability platform) |
| **Philosophy** | "Traces become the source of truth. When something goes wrong, teams say 'send us a trace' — not 'show me the code'" |
| **Council Advice** | Observability is not optional. The harness (context management, compression, sub-agent dispatch) is the critical differentiator, not the model. Co-evolve the harness and the model. |
| **Block** | Production Framework / Topology |

#### D.3 Chi Wang — AutoGen / AG2
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Conversable agents with explicit message-passing protocols enable cost-optimized multi-agent composition |
| **Key Works** | AutoGen (Microsoft), AG2 (fork), now Senior Staff Research Scientist at Google DeepMind |
| **Philosophy** | "Agents are not black boxes — they are conversable entities with explicit roles and message-passing contracts" |
| **Council Advice** | Explicit message-passing protocols prevent implicit coupling. Cost optimization through selective agent invocation. Conversation-centric composition for human-readable coordination. |
| **Block** | Production Framework / Topology |

#### D.4 Torsten Hoefler — ETH SPCL
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Performance-centric topology design from HPC — communication graph diameter and bandwidth determine scalability |
| **Key Works** | MPI-3 Nonblocking Collectives, 3D Parallelism, G-Designer (ICML 2025) |
| **Philosophy** | "The communication graph is not fixed; it is a design variable that determines performance and fault tolerance" |
| **Council Advice** | Apply HPC principles to multi-agent topology: minimize diameter, maximize bandwidth, formalize performance models. Topology and protocol must be co-designed. |
| **Block** | Production Framework / Topology |

#### D.5 Dapr Agents Team
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Cloud-native agent infrastructure — durable execution, virtual actors, automatic recovery without reinventing infrastructure |
| **Key Works** | Dapr Agents v1.0 (2025), built on CNCF Dapr runtime |
| **Philosophy** | "Every agent will crash, every network will partition. Checkpoint execution state automatically and recover without losing context" |
| **Council Advice** | Do not rebuild infrastructure from scratch. Use battle-tested distributed systems primitives: sidecars, workflows, actors, pub/sub. Security (mTLS, SPIFFE) is structural, not cosmetic. |
| **Block** | Production Framework / Topology |

#### D.6 Google ADK / A2A Team
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | A2A and MCP are the TCP/IP of the agent ecosystem — protocol interoperability beats proprietary platforms |
| **Key Works** | Google ADK (reference implementation), A2A protocol (agent-to-agent), Agent Cards for capability discovery |
| **Philosophy** | "Agents must communicate across vendor, framework, and organizational boundaries using open standards" |
| **Council Advice** | Build agents that self-describe capabilities and speak standard protocols. The network effect of interoperable agents dwarfs the value of any proprietary framework. |
| **Block** | Production Framework / Topology |

#### D.7 OpenAI Agents SDK Team
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Five-primitive minimalist architecture: agents, handoffs, guardrails, tools, tracing — co-evolved with model capabilities |
| **Key Works** | OpenAI Agents SDK (evolution of Swarm), native function-calling optimization |
| **Philosophy** | "The optimal agent architecture changes as models improve. Design frameworks that absorb model advances without rewrites" |
| **Council Advice** | Minimalism in framework design. Five primitives cover 80% of use cases. Guardrails must run in parallel, not sequence. Co-design the harness and the model. |
| **Block** | Production Framework / Topology |

#### D.8 Anthropic Claude Code / Agent SDK Team
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Orchestrator-subagent parallelism with extended thinking — model and harness co-designed for long-horizon tasks |
| **Key Works** | Claude Code (agentic coding), Claude Opus 4 (co-designed for agentic tasks), Constitutional AI |
| **Philosophy** | "Safety is structural, not cosmetic. Autonomous agents with tool access must be able to explain their reasoning and refuse harmful actions" |
| **Council Advice** | Extended thinking for complex tasks. Orchestrator-subagent pattern for parallelism. Constitutional AI for alignment. Model-harness co-evolution is essential. |
| **Block** | Production Framework / Topology |

#### D.9 Andrea Cini — IDSIA / GraphSight
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Learn optimal communication topologies from data — keep them sparse, validate that they improve the task |
| **Key Works** | Sparse graph learning, spatiotemporal GNNs, Torch Spatiotemporal library, unified taxonomy for graph deep learning in time series |
| **Philosophy** | "Never assume you know the right topology. The communication graph is usually unknown and often wrong" |
| **Council Advice** | Learn topology from data. Factorize computation — temporal and spatial should not be entangled. Build for missing data: real agents have dropouts. |
| **Block** | Production Framework / Topology |

#### D.10 Ivan Marisca — GraphSight
| Attribute | Details |
|-----------|---------|
| **Core Thesis** | Analyze information flow bottlenecks formally before designing architectures — over-squashing kills coordination at scale |
| **Key Works** | Over-squashing formalization in STGNNs, De Bruijn GNNs for non-Markovian dynamics, GraphSight production platform |
| **Philosophy** | "You cannot design around a limitation you haven't formally defined. Analyze the bottleneck before you add layers" |
| **Council Advice** | Characterize information flow formally. Model temporal topology, not just spatial. Agents' communication histories matter — non-Markovian dependencies are real. |
| **Block** | Production Framework / Topology |

#### D.11 Cluster D Interconnection Map

```
Torsten Hoefler (ETH SPCL) ──> MPI-3 ──> 3D Parallelism ──> G-Designer
Harrison Chase ──> LangChain (2022) ──> LangGraph (2024) ──> LangSmith
    └── A2A protocol adoption (2025)
João Moura ──> CrewAI ──> builds on LangChain primitives
Chi Wang ──> AutoGen (Microsoft) ──> AG2 fork ──> Google DeepMind
Google ADK ──> A2A protocol ──> ADK reference implementation
Dapr Agents ──> CNCF Dapr runtime ──> sidecar/workflow/actor model
Andrea Cini (IDSIA) ──> Ivan Marisca (GraphSight) ──> Torch Spatiotemporal
OpenAI SDK ──> Swarm evolution ──> five-primitive architecture
Anthropic ──> Claude Opus 4 ──> Claude Code co-design
```

**6-Layer Governance Architecture:**
1. **Communication Topology** (Hoefler, Cini, Marisca) — learned, optimized, dynamically adapted
2. **Protocol & Interoperability** (Google ADK, Dapr) — A2A + MCP + Dapr sidecars
3. **Orchestration & Control Flow** (Chase, Wang, Moura) — LangGraph + AutoGen + CrewAI patterns
4. **Durability & Production Infrastructure** (Dapr) — checkpointing, recovery, scale-to-zero
5. **Safety, Observability & Trust** (OpenAI, Anthropic, Chase) — guardrails, tracing, alignment
6. **Model-Harness Co-Evolution** (OpenAI, Anthropic, Chase) — framework absorbs model advances

---

## PART II: UNIFIED ARCHITECTURE

---

### Network Block Assignment Matrix

| Researcher | Primary Block | Secondary Block | Key Contribution |
|------------|--------------|-----------------|------------------|
| **Li Fei-Fei** | Perception | Cognition | Foundational visual perception + human-centered philosophy |
| **Ranjay Krishna** | Graph Memory | Cognition | Scene graphs as structured memory + compositional benchmarks |
| **Juan Carlos Niebles** | Perception | Cognition | Event-aware perception + goal/intention inference |
| **Jiankang Wang** | Perception | Graph Memory | Spatio-temporal grounding + query interfaces |
| **Rohith Peddi** | Graph Memory | Cognition | World scene graphs + anticipation + error detection |
| **Xianghui Xie** | Perception | Graph Memory | 4D reconstruction + physical consistency |
| **Kristen Grauman** | Perception | Cognition | Egocentric video + skill learning |
| **Chenliang Xu** | Perception | Generation | Cross-modal generation + video-language models |
| **Jiebo Luo** | Generation | Cognition | Cross-modal summarization + social science reasoning |
| **Noah Shinn** | Cognition | — | Verbal reinforcement learning + episodic memory |
| **Aman Madaan** | Cognition | — | Iterative self-refinement + neural-symbolic hybrids |
| **Shunyu Yao** | Cognition | — | ReAct + Tree of Thoughts + cognitive architectures |
| **Maciej Besta** | Graph Memory | Cognition | Graph-structured reasoning + knowledge graphs |
| **Xinhao Li** | Perception | — | GRPO for spatio-temporal video perception |
| **Ruyi Xu** | Perception | — | Streaming-first VLM architecture |
| **Shengyuan Ye** | Perception | — | Edge-cloud disaggregated video understanding |
| **Jacob Chalk** | Perception | — | Time-interval audio-visual fusion |
| **Jenny Zhang** | Cognition | — | Metacognitive self-modification + open-endedness |
| **Nehzati M.** | Cognition | — | Substrate-level evolution + metabolic computing |
| *[Cluster C researchers]* | Consensus/Safety | — | Byzantine tolerance + conformity detection + temporal hygiene |
| *[Cluster D researchers]* | Framework/Topology | — | Production frameworks + communication topology |

---

### The Four-Layer Architecture (Research-Native)

This architecture emerged naturally from the literature — it was not imposed:

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS COGNITIVE NETWORK             │
├─────────────────────────────────────────────────────────────┤
│  PERCEPTION LAYER                                           │
│  ├─ 4D Neural Fields        [7DGS, NGFF, CARI4D]          │
│  ├─ Audio-Visual Localizer  [ACL-SSL, AVIS, TIM]          │
│  ├─ Streaming Vision        [StreamingVLM, Venus]         │
│  └─ RL Video Perception     [VideoChat-R1, SpaceVLLM]     │
├─────────────────────────────────────────────────────────────┤
│  GRAPH MEMORY LAYER                                         │
│  ├─ World Scene Graphs      [WSGG, Visual Genome, OmniRe] │
│  ├─ Knowledge Graphs        [KGoT, GraphThinker, ViG-RAG] │
│  ├─ Causal Event Graphs     [HyperGLM, MECD+, VST]        │
│  └─ Persistent Tracking     [PWG, GraphVideoAgent]        │
├─────────────────────────────────────────────────────────────┤
│  COGNITION LAYER                                            │
│  ├─ Reasoning + Acting      [ReAct, CoALA, Tree of Thoughts]│
│  ├─ Self-Reflection         [Reflexion, Self-Refine]      │
│  ├─ Meta-Cognition          [HyperAgents, DGM]            │
│  └─ Substrate Evolution     [Self-Evolving Substrates]    │
├─────────────────────────────────────────────────────────────┤
│  GENERATION LAYER                                           │
│  ├─ Video Synthesis         [Veo 3.1, Runway Gen-4]       │
│  ├─ Audio-Video Joint Gen   [MAViD, Wan 2.6]              │
│  └─ Cross-Modal Summarization [VideoXum, V2Xum-LLM]       │
├─────────────────────────────────────────────────────────────┤
│  GOVERNANCE LAYER                                           │
│  ├─ Byzantine Consensus     [CP-WBFT, DecentLLMs]         │
│  ├─ Safety / Pruning        [G-Safeguard, AgentPrune]     │
│  ├─ Conformity Detection    [MAD-Spear, NetSafe]          │
│  └─ Temporal Hygiene        [Vector Clocks, ST-GAT]       │
├─────────────────────────────────────────────────────────────┤
│  FRAMEWORK LAYER                                            │
│  ├─ Multi-Agent Frameworks  [CrewAI, LangGraph, AG2]      │
│  ├─ Communication Topology  [G-Designer, ARG-Designer]    │
│  ├─ Durable Execution       [Dapr Agents, Orleans]        │
│  └─ Agent Protocols         [A2A, MCP, Agent-to-Agent]    │
└─────────────────────────────────────────────────────────────┘
```

---

### Sanskrit Architecture Mapping

| Sanskrit Term | Modern Equivalent | Block | Researcher Voice |
|--------------|-------------------|-------|------------------|
| **Śruti** (that which is heard) | ASR / Audio-Visual perception fork | Perception | Li Fei-Fei: "Start with the problem that matters" |
| **Saṃvedana** (feeling/sensation) | Variable-latency empathy orchestrator | Cognition | Shunyu Yao: "Reasoning and acting are two aspects of the same process" |
| **Smṛti** (memory) | Selective amnesia memory tiers | Graph Memory | Maciej Besta: "Every thought is a node in an evolving network" |
| **Hṛdaya** (heart) | Rasa-based emotion engine | Cognition | Jenny Zhang: "Recursive self-improvement is the path to AGI" |
| **Sphota** (linguistic burst) | LLM reasoning | Cognition | Aman Madaan: "The answer is not in the weights — it's in the loop" |
| **Dhvani** (resonance) | TTS prosody | Generation | Jiebo Luo: "Cross-modal coherence must be a first-class objective" |

---

## PART III: THE ROUND BLOCK PROBLEM

---

> *"A round block in a world of round holes does not know it is destroying the network. It believes it is fitting perfectly."*

### Five Types of Round Blocks

| Type | Example in Network | Detection Mechanism | Council Wisdom |
|------|-------------------|---------------------|----------------|
| **Misaligned Optimizer** | Video block optimizes for views not brand safety | G-Safeguard on generation graph + NetSafe topology | Peddi: "Robustness to distribution shift is non-negotiable" |
| **Temporal Drifter** | Voice block clock skew causes message reordering | Causal observability + vector clock validation | Jamshidi: "Clock-dynamics-aware systems are essential" |
| **Confidence Fraud** | Reel template agent is 99% confident in off-brand content | CP-WBFT confidence calibration + cross-model consensus | Shinn: "Reliable evaluation is the bottleneck" |
| **Sleeper Agent** | Document parser appears aligned but subtly mislabels safety docs | PBFT-backed semantic voting + periodic trust re-evaluation | Hubinger: "Hidden misalignment can persist undetected" |
| **Conformity Carrier** | Network agrees a reel is good because Voice said so, Video silently disagrees | MAD-Spear conformity detection + independent scoring | Yao: "Deliberate search through problem spaces, not consensus for consensus' sake" |

### Mitigation Architecture (Collective Consensus)

1. **Diversity of thought:** Each block runs a different model family (Qwen, Gemini, Llama) — cross-model consensus prevents shared blind spots
2. **Topological defense:** NetSafe principles — limit connectivity, increase average distance, avoid fully-connected graphs
3. **Temporal hygiene:** Vector clocks on every message. Causal health signal monitored by Temporal Orchestration Node
4. **Probabilistic unlearning:** Temporal GNNs must unlearn trust as fast as they learn it. Bayesian belief updating on every interaction
5. **Human sovereignty:** Council of Ten protocol applies at the network level. No autonomous action without documented consensus

---

## PART IV: EMERGENT CAPABILITIES

---

When the four layers are connected via graph protocols, capabilities emerge that no single block possesses:

### Emergent Capability 1: Cross-Modal Brand Memory
**Trigger:** Voice block hears "the burger was cold."
**Chain:** Video block retrieves reel showing that burger prep → Temporal block timestamps complaint against video segment → Knowledge block stores the causal pattern.
**Result:** Network collectively understands that a specific cooking process led to a specific complaint at a specific time — without any block being programmed for this.

### Emergent Capability 2: Self-Healing Content Pipelines
**Trigger:** Video block produces off-brand reel.
**Chain:** Knowledge block's G-Safeguard detects anomalous patterns → Temporal Auditor traces causal chain → Bad actor template identified → Edge pruned (AgentPrune) → Consensus reached on corrected template (CP-WBFT).
**Result:** Network self-heals without human intervention.

### Emergent Capability 3: Predictive Content Generation
**Trigger:** HOI-DA block anticipates "person holding cup" → "person will drink."
**Chain:** Voice block pre-generates audio "Enjoy your drink!" → Temporal block schedules overlay → Knowledge block stores interaction pattern.
**Result:** Network predicts and pre-composes content before the event completes.

### Emergent Capability 4: Temporal Litigation Graph
**Trigger:** Safety incident at construction site.
**Chain:** Design document (VDC) → Material delivery timestamp → Site video showing improper handling → Safety briefing audio where hazard was mentioned but not acted upon.
**Result:** Knowledge block produces causal litigation graph with vector-clock-verified happens-before relationships.

---

## PART V: EXISTING PROJECT MAPPING

---

| Project | Current State | Network Block Assignment | Research Injection |
|---------|--------------|-------------------------|-------------------|
| **voice-revenge-vizuara-ai** | Voice agent platform (Deepgram → Azure OpenAI → Aura TTS). Hexagonal architecture. Council of Ten protocol. | Voice Cognition Node (Perception + Cognition) | Add audio-visual VAD, omni-modal backbone, temporal knowledge graph memory, 11th Temporal Auditor persona |
| **sabrika-brand-manager** | Instagram reel generator (YOLOv8 + FFmpeg + OpenCV). Azure VM deployed. | Video Generation Node (Generation) | Upgrade to spatio-temporal scene graphs, event graph segmentation, controllable generation (Runway Gen-4), audio-visual joint generation |
| **network-research-intiative** | VDC document intelligence, MCP servers, time-awareness hooks | Temporal Orchestration Node (Graph Memory) | Causal observability health signal, video document understanding, A2A protocol, probabilistic trust tracking |
| **gbrain** | PGLite/Postgres memory, MCP server, virtual actors, operations framework | Knowledge & Topology Node (Graph Memory + Cognition) | Spatio-temporal graph memory, Dapr Agents with Byzantine-robust resurrection, GNN-based communication topology, conformity attack detection |

---

## PART VI: OPEN PROBLEMS (Require ADRs)

---

1. **ADR-001:** Consensus protocol selection (CP-WBFT vs DecentLLMs vs HACN)
2. **ADR-002:** Communication topology (static vs G-Designer adaptive vs ARG-Designer)
3. **ADR-003:** Temporal consistency (Lamport vs vector clocks vs ST-GAT)
4. **ADR-004:** Memory architecture (PTKG vs StreamForest vs hybrid)
5. **ADR-005:** Omni-modal backbone (Qwen3-Omni vs Gemini 2.5 vs Llama 4)
6. **ADR-006:** Video generation API (Runway Gen-4 vs Veo 3.1 vs Wan 2.6)
7. **ADR-007:** Trust boundary model (Dapr Actors vs Orleans vs custom)
8. **ADR-008:** Self-reflection mechanism (Reflexion vs GraphThinker vs hybrid)
9. **ADR-009:** Streaming architecture (MiniCPM-o vs StreamingVLM vs custom)
10. **ADR-010:** Bad actor containment (G-Safeguard vs AgentDropout vs PBFT)
11. **ADR-011:** Network testing protocol (RL Hub integration)

---

## PART VII: CONTACT STRATEGY

---

### Priority Tiers

**Tier 1 — Direct Academic Collaboration**
- Rohith Peddi (UT Dallas) — Scene graph anticipation, world-centric understanding
- Jenny Zhang (UBC/Meta) — HyperAgents, recursive self-improvement
- Maciej Besta (ETH) — Graph-structured reasoning, KGoT
- Ruyi Xu (MIT) — StreamingVLM, real-time constraints

**Tier 2 — Framework Integration**
- João Moura (CrewAI) — Production multi-agent orchestration
- Harrison Chase (LangGraph) — Graph-based agent workflows
- Chi Wang (AG2/DeepMind) — AutoGen ecosystem

**Tier 3 — Foundation Model Access**
- Lei Zhang (UCSD/NVIDIA) — Multi-modal video understanding
- Jiankang Wang (USTC) — SpaceVLLM, spatio-temporal grounding
- Xinhao Li (ByteDance) — RL for video MLLMs

**Tier 4 — Infrastructure & Real-Time**
- Russ d'Sa (LiveKit) — Real-time audio/video streaming infrastructure
- Kwindla Hultman Kramer (Pipecat) — Conversational AI pipelines
- Thierry Schellenbach (Stream) — Video infrastructure

**Tier 5 — Long-Term Vision**
- Yann LeCun (Meta) — JEPA, world models
- Jeff Clune (UBC) — Open-endedness, quality diversity
- Li Fei-Fei (Stanford/World Labs) — Spatial intelligence, human-centered AI

---

## APPENDIX: RESEARCH-First COVENANT

```
Decompose → BFS → DFS → Bidirectional → ADR → Code
```

**Current Phase:** Bidirectional complete. ADR phase pending.

**Rule:** No code is written before ADRs are approved by the Council of Ten.

**This is not bureaucracy — it is the foundation of trust in a network where no block knows if it is a round block.**

---

*Document compiled from 4 parallel BFS research agents + 2 completed digital twin deep-dives. Cluster C and D profiles will be appended when their agents complete.*
