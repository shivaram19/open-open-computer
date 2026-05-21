# Digital Twin Profiles: Architects of Video Understanding, Spatio-Temporal Scene Graphs, and Spatial GNNs

## A Comprehensive Archaeological Survey of Intellectual Lineages, Methodologies, and Philosophies

---

## Table of Contents
1. [Li Fei-Fei (Stanford / World Labs)](#1-li-fei-fei)
2. [Ranjay Krishna (University of Washington / AI2)](#2-ranjay-krishna)
3. [Juan Carlos Niebles (Salesforce / Stanford)](#3-juan-carlos-niebles)
4. [Jiankang Wang (USTC)](#4-jiankang-wang)
5. [Rohith Peddi (UT Dallas)](#5-rohith-peddi)
6. [Xianghui Xie (MPI Tübingen / NVIDIA)](#6-xianghui-xie)
7. [Kristen Grauman (UT Austin / Meta FAIR)](#7-kristen-grauman)
8. [Chenliang Xu (University of Rochester)](#8-chenliang-xu)
9. [Jiebo Luo (University of Rochester)](#9-jiebo-luo)
10. [The Interconnection Map](#10-the-interconnection-map)

---

## 1. Li Fei-Fei

### Academic Genealogy
- **PhD**: California Institute of Technology (Caltech), 2005, Electrical Engineering
- **Advisors**: **Pietro Perona** (primary) and **Christof Koch** (secondary)
- **Thesis**: *"Visual Recognition: Computational Models and Human Psychophysics"*
- **Undergraduate**: Princeton University, 1999, B.A. in Physics (High Honors)
- **Career Trajectory**:
  - 2005–2006: Assistant Professor, University of Illinois Urbana-Champaign (UIUC)
  - 2007–2009: Assistant Professor, Princeton University
  - 2009–present: Stanford University (Assistant → Associate with tenure 2012 → Full Professor 2018 → Sequoia Capital Professor)
  - 2013–2018: Director, Stanford AI Lab (SAIL)
  - 2017–2018: VP & Chief Scientist of AI/ML, Google Cloud (sabbatical)
  - 2019–present: Co-Director, Stanford Institute for Human-Centered AI (HAI)
  - 2024–present: Co-founder/CEO, World Labs (spatial intelligence startup)

### Key Papers

#### 1. ImageNet (CVPR 2009, IJCV 2015)
- **Core Problem**: How to overcome the data bottleneck that was stalling progress in object recognition
- **Methodological Innovation**: Crowdsourced hierarchical image database with 14M+ images across 20K+ categories; launched the ImageNet Large Scale Visual Recognition Challenge (ILSVRC)
- **Philosophical Approach**: Radically **empirical** — she bet the field that data scale, not just algorithms, was the missing ingredient. This was contrarian at a time when most believed better features were the answer.
- **Lasting Impact**: Directly catalyzed the deep learning revolution; AlexNet's 2012 ILSVRC victory trained on ImageNet ignited modern AI.

#### 2. Visual Genome (IJCV 2017, with Ranjay Krishna et al.)
- **Core Problem**: Images are not bags of objects — they contain rich relationships, attributes, and semantic structure
- **Methodological Innovation**: Dense scene graph annotations connecting objects, attributes, and relationships using crowdsourced natural language
- **Philosophical Approach**: **First-principles cognitive** — humans understand scenes through structured relationships, not isolated labels
- **Lasting Impact**: Established scene graph generation as a core computer vision task; foundational dataset for visual-language models

#### 3. Action Genome (CVPR 2020, with Ji, Krishna, Niebles)
- **Core Problem**: Actions in video are compositional and depend on spatio-temporal object interactions
- **Methodological Innovation**: Extended scene graphs into the temporal domain, annotating objects and their relationships across video frames tied to human actions
- **Philosophical Approach**: **Compositionality-first** — actions decompose into objects, relationships, and temporal dynamics
- **Lasting Impact**: Foundational benchmark for spatio-temporal scene graph generation and video understanding

#### 4. Agent AI (Survey, 2024, with Katsuhi Ikeuchi et al.)
- **Core Problem**: How multimodal AI agents can perceive, reason, and act in embodied environments
- **Methodological Innovation**: Framework unifying multimodal perception, action, and reasoning
- **Philosophical Approach**: **Human-centered augmentation** — AI should extend human capabilities, not replace them

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | Stanford University; World Labs |
| **Core Methodology** | Start with the "North Star" question (cognitively inspired); build data infrastructure at scale; empirically validate whether scale unlocks capability |
| **Key Intellectual Contributions** | 1. **Data-centric AI thesis**: ImageNet proved data scale enables algorithmic breakthroughs<br>2. **Structured visual understanding**: Scene graphs (Visual Genome, Action Genome) as cognitively plausible representations<br>3. **Human-Centered AI**: Founded HAI to embed ethics, policy, and human augmentation into AI research<br>4. **Spatial Intelligence**: World Labs aims to build generative world models with 3D spatial reasoning |
| **Research Philosophy** | AI must be understood as a human technology, not a replacement. The "worlds I see" are fundamentally about human perception, curiosity, and discovery. Believes in augmentative AI and diversity (co-founded AI4ALL). |
| **Signature Techniques** | Large-scale dataset construction, crowdsourced annotation pipelines, hierarchical semantic taxonomies, human psychophysics experiments |
| **Advised Students / Lineage** | **Jia Deng** (Princeton → Michigan), **Andrej Karpathy** (OpenAI, Tesla), **Justin Johnson** (Michigan), **Ranjay Krishna** (UW/AI2), **Juan Carlos Niebles** (Salesforce/Stanford), **Serena Yeung**, **Yuke Zhu**, **Agrim Gupta**, **Linxi Fan**, **Timnit Gebru** (co-advised), **Danfei Xu** |
| **Council Advice** | "Start with the problem that matters to humanity, not the method that is fashionable. Build the data and evaluation infrastructure before optimizing algorithms." |
| **Network Block** | **Perception** (foundational) and **Cognition** (human-centered reasoning) |

---

## 2. Ranjay Krishna

### Academic Genealogy
- **PhD**: Stanford University, 2021, Computer Science (GPA 4.00, Distinction in Teaching)
- **Co-Advisors**: **Li Fei-Fei** and **Michael Bernstein** (HCI)
- **Thesis**: *"Visual Intelligence from Human Learning"* — Christofer Stephenson Memorial Award (Best Stanford CS Thesis)
- **MSc**: Stanford University, 2016, Computer Science (GPA 3.98, Distinction in Research)
- **BSc**: Cornell University, 2013, Electrical & Computer Engineering and Computer Science (Magna Cum Laude)
- **Career Trajectory**:
  - 2021–2022: Research Scientist, Facebook AI Research (FAIR)
  - 2022–present: Assistant Professor, University of Washington, Paul G. Allen School
  - 2024–present: Research Director, Allen Institute for AI (AI2) — leading PRIOR (Computer Vision team)

### Key Papers

#### 1. Visual Genome (IJCV 2017, with Fei-Fei Li et al.)
- **Core Problem**: How to represent the dense, structured knowledge humans extract from a single glance at an image
- **Methodological Innovation**: Crowdsourced dense image annotations linking objects, attributes, and relationships into a scene graph; designed to connect language and vision
- **Philosophical Approach**: **Cognitively-inspired empiricism** — humans learn visual concepts through rich, structured, linguistic descriptions
- **Lasting Impact**: The canonical dataset for scene graph generation; cited thousands of times across vision-language research

#### 2. Action Genome (CVPR 2020, with Ji, Li, Niebles)
- **Core Problem**: Actions are compositional spatio-temporal events, not just labels
- **Methodological Innovation**: Annotated object relationships over time in video, linked to action labels, enabling spatio-temporal scene graph generation
- **Philosophical Approach**: **Compositionality and grounding** — actions must be grounded in object interactions across time
- **Lasting Impact**: Established the spatio-temporal scene graph generation benchmark; precursor to 4D scene understanding

#### 3. AGQA: Compositional Spatio-Temporal Reasoning (CVPR 2021, with Grunde-McLaughlin, Agrawala)
- **Core Problem**: Existing video question answering benchmarks do not require true compositional reasoning
- **Methodological Innovation**: Synthetic benchmark with explicit compositional templates testing temporal and spatial reasoning
- **Philosophical Approach**: **Benchmark-driven science** — identify what models fail at by construction
- **Lasting Impact**: Standard benchmark for evaluating compositional reasoning in video-language models

#### 4. Scene Graph Prediction with Limited Labels (ICCV 2019, with Chen, Varma, Bernstein, Re, Li)
- **Core Problem**: Scene graph annotation is expensive; how to learn with fewer labels
- **Methodological Innovation**: Semi-supervised learning with linguistic priors and graph consistency
- **Philosophical Approach**: **Human-AI collaboration** — leverage human knowledge (language priors) to reduce annotation burden

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | University of Washington; Allen Institute for AI |
| **Core Methodology** | Intersection of computer vision, human-computer interaction, and crowdsourcing. Builds datasets and benchmarks that force the community to confront what models actually understand. Uses human cognitive insights to design AI evaluation. |
| **Key Intellectual Contributions** | 1. **Visual Genome**: Dense structured visual knowledge representation<br>2. **Action Genome**: Temporal extension of scene graphs for action understanding<br>3. **Compositional Benchmarking**: AGQA and related works expose reasoning failures<br>4. **Human-in-the-loop AI**: Crowdsourcing and human-AI collaboration frameworks |
| **Research Philosophy** | "Research without a north star is like a body without a soul." Believes AI must be evaluated against human-like structured understanding, not just accuracy metrics. Advocates for agile, collaborative research communities. |
| **Signature Techniques** | Crowdsourced annotation design, scene graph representations, compositional benchmarking, human-AI interaction protocols |
| **Advised Students / Lineage** | **Xiang Fan**, **Scott Geng** (co-advised with Pang Wei Koh), **Zixian Ma** (co-advised with Dan Weld), **Sebastian Santy**, **Jieyu Zhang** (co-advised with Alex Ratner), **Jiafei Duan** (co-advised with Dieter Fox), **Ainaz Eftekhar** (co-advised with Ali Farhadi), **Cheng-Yu Hsieh** (co-advised with Alex Ratner) |
| **Council Advice** | "Build benchmarks that expose failure modes, not just leaderboard numbers. The gap between human and machine understanding is in compositionality, not scale." |
| **Network Block** | **Graph Memory** (scene graphs as structured memory) and **Cognition** (compositional reasoning) |

---

## 3. Juan Carlos Niebles

### Academic Genealogy
- **PhD**: Princeton University, 2011, Electrical Engineering
- **MSc**: University of Illinois at Urbana-Champaign (UIUC), 2007, Electrical and Computer Engineering
- **Undergraduate**: Universidad del Norte (Colombia), 2002, Electronics Engineering
- **Career Trajectory**:
  - 2005–2010: PhD student; during this time Li Fei-Fei was at UIUC and Princeton, and Niebles was her graduate student at UIUC (per her 2005-2006 CV)
  - 2011–2019: Associate Professor, Universidad del Norte (Colombia)
  - 2015–2021: Senior Research Scientist, Stanford AI Lab; Associate Director, Stanford-Toyota Center for AI Research
  - 2021–present: Research Director, Salesforce AI Research; Adjunct Professor, Stanford; Co-Director, Stanford Vision and Learning Lab (SVL)

### Key Papers

#### 1. Action Genome (CVPR 2020, with Ji, Krishna, Li)
- **Core Problem**: Bridging action recognition and structured scene understanding in video
- **Methodological Innovation**: Composable spatio-temporal scene graphs where actions decompose into object-relationship trajectories
- **Philosophical Approach**: **Event-aware perception** — understanding requires structured representation of how objects interact over time
- **Lasting Impact**: Foundation for all subsequent spatio-temporal scene graph research

#### 2. Motion Reasoning for Goal-Based Imitation Learning (ICRA 2020, with Huang, Chao, Paxton, Deng, Li, Garg, Fox)
- **Core Problem**: Robots need to understand human motion goals, not just mimic trajectories
- **Methodological Innovation**: Structured motion reasoning with goal inference
- **Philosophical Approach**: **Functional understanding** — perception must serve action and goal prediction

#### 3. xGen-MM / BLIP-3-Video (Salesforce, 2024-2025)
- **Core Problem**: Scalable multimodal understanding for video
- **Methodological Innovation**: Efficient multimodal pretraining architectures for video-language tasks
- **Philosophical Approach**: **Practical scalability** — bridge research and production multimodal AI

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | Salesforce AI Research; Stanford University (Adjunct) |
| **Core Methodology** | Build multimodal AI systems that move from passive observation to active contextualized assistance. Event-aware perception → goal/intention inference → embodied action. |
| **Key Intellectual Contributions** | 1. **Spatio-temporal action understanding**: Action Genome bridges recognition and structured reasoning<br>2. **Multimodal AI agents**: Leading xLAM (Large Action Models) and multimodal foundation models at Salesforce<br>3. **Event-aware perception**: Transform raw video into structured understanding of human actions<br>4. **Academic-industrial bridge**: Maintains dual academic and industry leadership |
| **Research Philosophy** | "The goal is not just to label the world, but to anticipate a user's needs in real-time." Believes in embodied agents that navigate dynamic environments and perform supportive tasks. |
| **Signature Techniques** | Spatio-temporal scene graphs, action decomposition, goal-based imitation learning, multimodal foundation models |
| **Advised Students / Lineage** | Advised by **Li Fei-Fei** (UIUC). As faculty at Stanford/Salesforce, has mentored researchers in the Stanford Vision and Learning Lab. Collaborates closely with **Silvio Savarese**, **Jiajun Wu**, **Chelsea Finn** (all part of the Stanford robotics/vision ecosystem). |
| **Council Advice** | "Move beyond passive perception. The next frontier is AI that understands goals and intentions, enabling real-time contextualized assistance." |
| **Network Block** | **Perception** (event-aware video understanding) and **Cognition** (goal/intention inference) |

---

## 4. Jiankang Wang

### Academic Genealogy
- **Institution**: University of Science and Technology of China (USTC)
- **Collaborators**: **Hongtao Xie** (corresponding author, USTC), **Yongdong Zhang** (USTC)
- **Career Trajectory**: Active PhD researcher at USTC in the video understanding and multimodal AI group

### Key Papers

#### 1. SpaceVLLM (arXiv 2025 / AAAI 2026, with Zhang, Liu, Li, Ge, Xie, Zhang)
- **Core Problem**: MLLMs can do temporal or spatial localization separately, but fail at joint spatio-temporal video grounding
- **Methodological Innovation**: 
  - Spatio-Temporal Aware Queries interleaved with video frames
  - Query-Guided Space Decoder mapping queries to precise spatial coordinates without textual coordinate generation
  - Unified Spatio-Temporal Grounding (Uni-STG) dataset with 480K instances
- **Philosophical Approach**: **Elegant unlocking of latent potential** — rather than attaching complex external modules, design a paradigm that lets MLLMs use their inherent strengths for joint spatio-temporal reasoning
- **Lasting Impact**: State-of-the-art on 11 benchmarks across temporal, spatial, spatio-temporal, and general video understanding

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | University of Science and Technology of China (USTC) |
| **Core Methodology** | Design lightweight, elegant architectural modifications that unlock latent capabilities in large pre-trained models. Focus on query-based representations that bridge language and continuous spatial-temporal coordinates. |
| **Key Intellectual Contributions** | 1. **Spatio-Temporal Aware Queries**: Interleaved query representations for joint temporal and spatial reasoning<br>2. **Query-Guided Space Decoder**: Bypasses textual coordinate generation for precise spatial localization<br>3. **Dataset construction**: Uni-STG benchmark enabling MLLM spatio-temporal grounding research |
| **Research Philosophy** | The power of MLLMs is already there — the job of architecture is to create the right interfaces (queries, decoders) that let the model express what it knows. Favor elegant, minimal interventions over heavy task-specific modules. |
| **Signature Techniques** | Query-based video representations, interleaved spatio-temporal modeling, lightweight space decoders, automated data synthesis |
| **Advised Students / Lineage** | Early-career researcher; works within the USTC video understanding group led by **Hongtao Xie** and **Yongdong Zhang** |
| **Council Advice** | "Don't bolt heavy modules onto MLLMs. Design query interfaces and decoders that let the model's latent spatio-temporal knowledge emerge." |
| **Network Block** | **Perception** (spatio-temporal grounding) |

---

## 5. Rohith Peddi

### Academic Genealogy
- **PhD**: University of Texas at Dallas (UT Dallas), ongoing
- **Advisors**: **Vibhav Gogate** (UT Dallas, probabilistic reasoning, graphical models) and **Yu Xiang** (UT Dallas, robotics, computer vision)
- **Collaborators**: **Parag Singla** (IIT Delhi), **Nicholas Ruozzi** (UT Dallas)
- **Career Trajectory**: PhD candidate at UT Dallas; emerging leader in spatio-temporal scene graph generation and 4D scene understanding

### Key Papers

#### 1. Towards Scene Graph Anticipation (ECCV 2024 Oral, with Singh, Saurabh, Singla, Gogate)
- **Core Problem**: Predicting future object relationships before they happen
- **Methodological Innovation**: SceneSayer — uses Neural ODE and Neural SDE to model continuous-time evolution of object relationships from observed frames
- **Philosophical Approach**: **Dynamical systems perspective** — relationships evolve continuously, not discretely; model the latent dynamics
- **Lasting Impact**: Introduced scene graph anticipation as a formal task

#### 2. Towards Unbiased and Robust Spatio-Temporal Scene Graph Generation (CVPR 2025 Highlight, with Saurabh, Shrivastava, Singla, Gogate)
- **Core Problem**: Real-world relationships have long-tailed distributions; models become biased toward head classes
- **Methodological Innovation**: IMPARTIAL framework using loss masking and curriculum learning to focus on tail relationships without adding architectural complexity
- **Philosophical Approach**: **Training dynamics matter more than architecture** — bias can be addressed through how the model learns, not just what it learns
- **Lasting Impact**: Established robust scene graph generation benchmarks

#### 3. Towards Spatio-Temporal World Scene Graph Generation from Monocular Videos (arXiv 2026, with Saurabh, Shanmugam, Pallapothula, Xiang, Singla, Gogate)
- **Core Problem**: Existing methods are frame-centric — they discard occluded objects and operate in 2D
- **Methodological Innovation**: 
  - ActionGenome4D dataset with 3D reconstruction and world-frame bounding boxes
  - World Scene Graph Generation (WSGG) task including unobserved objects
  - Three complementary methods: PWG (object permanence), MWAE (masked completion), 4DST (4D temporal attention)
- **Philosophical Approach**: **World-centric, not frame-centric** — true understanding requires object permanence and 3D spatial reasoning
- **Lasting Impact**: Advances video understanding toward persistent, interpretable world reasoning

#### 4. CaptainCook4D (NeurIPS 2024 Datasets, with Arya, Challa, Pallapothula, Vyas, Gouripeddi, Zhang, Wang, Komaragiri, Ragan, Ruozzi, Xiang, Gogate)
- **Core Problem**: Understanding errors in procedural activities from egocentric video
- **Methodological Innovation**: 4D egocentric dataset with both correct and error-induced procedural executions
- **Philosophical Approach**: **Error-aware understanding** — intelligent systems must detect and reason about failures, not just successes

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | University of Texas at Dallas |
| **Core Methodology** | Merge probabilistic graphical models with deep learning for structured spatio-temporal understanding. Treat scene graphs as dynamical systems. Address real-world distribution challenges (long-tail, occlusion, noise) through principled training and world-centric representations. |
| **Key Intellectual Contributions** | 1. **Scene Graph Anticipation**: Predicting future relationships via continuous dynamical models<br>2. **Unbiased Scene Graph Learning**: IMPARTIAL framework for long-tailed distributions<br>3. **World Scene Graph Generation**: 4D persistent scene graphs with object permanence<br>4. **Error-aware procedural understanding**: CaptainCook4D for failure detection |
| **Research Philosophy** | Scene understanding must be world-centric, not frame-centric. Object permanence and physical reasoning are non-negotiable. Long-tailed distributions are not nuisances to be ignored — they are the true test of understanding. |
| **Signature Techniques** | Neural ODE/SDE for relationship dynamics, loss masking with curriculum learning, 4D scene reconstruction, object permanence via feature buffers and masked autoencoding |
| **Advised Students / Lineage** | PhD student; mentors include **Vibhav Gogate** (probabilistic AI) and **Yu Xiang** (robotics vision). Collaborates with **Parag Singla** (IIT Delhi) and **Nicholas Ruozzi** (graphical models). Part of the IRVL lab at UT Dallas. |
| **Council Advice** | "Build models that reason about what they cannot see. Object permanence and robustness to distribution shift are prerequisites for trustworthy autonomous systems." |
| **Network Block** | **Graph Memory** (world scene graphs) and **Cognition** (anticipation, error detection) |

---

## 6. Xianghui Xie

### Academic Genealogy
- **PhD**: Max Planck Institute for Informatics / University of Tübingen, ongoing
- **Advisor**: **Gerard Pons-Moll** (MPI-INF, world-leading researcher in 4D human reconstruction and virtual humans)
- **Collaborators**: **Jan Eric Lenssen** (MPI), **Bharat Lal Bhatnagar** (MPI), **Stan Birchfield** (NVIDIA)
- **Career Trajectory**: 
  - MSc: Saarland University, 2022 (thesis on tracking human-object interaction from single RGB camera)
  - PhD student at MPI Tübingen (Real Virtual Humans group)
  - NVIDIA intern (CARI4D developed during internship)

### Key Papers

#### 1. CHORE (ECCV 2022, with Bhatnagar, Pons-Moll)
- **Core Problem**: Reconstructing both human and object from a single RGB image, including their contact
- **Methodological Innovation**: First method to jointly reconstruct human and object with contact reasoning from a single image
- **Philosophical Approach**: **Contact is the key signal** — understanding interaction requires explicit physical contact modeling
- **Lasting Impact**: Foundation for single-image human-object interaction reconstruction

#### 2. Visibility Aware Human-Object Interaction Tracking (CVPR 2023, with Bhatnagar, Pons-Moll)
- **Core Problem**: Tracking interaction through occlusions from a single RGB camera
- **Methodological Innovation**: Visibility-aware network that reasons about what is occluded and what is visible
- **Philosophical Approach**: **Occlusion-aware reasoning** — tracking requires inferring what happens when objects disappear from view

#### 3. CARI4D (CVPR 2026, with Wen, Chang, Rabeti, Li, Yuan, Pons-Moll, Birchfield)
- **Core Problem**: Category-agnostic 4D reconstruction of human-object interaction from monocular RGB video at metric scale
- **Methodological Innovation**: 
  - Pose hypothesis selection algorithm robust to occlusion
  - CoCoNet: category-agnostic contact reasoning network with render-and-compare
  - Contact-aware joint optimization with physical constraints
- **Philosophical Approach**: **Foundation model integration with physical reasoning** — individual predictions from foundation models (shape, pose, depth) are noisy; the key is designing optimization frameworks that fuse them and enforce physical consistency
- **Lasting Impact**: First category-agnostic metric-scale 4D HOI reconstruction; generalizes zero-shot to in-the-wild video

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | Max Planck Institute for Informatics / University of Tübingen; NVIDIA (internship) |
| **Core Methodology** | Combine foundation model predictions through optimization frameworks that enforce physical consistency (contacts, metric scale, temporal coherence). Render-and-compare paradigms with learned contact reasoning. Category-agnostic design for generalization. |
| **Key Intellectual Contributions** | 1. **CHORE**: Joint human-object reconstruction with contact from single image<br>2. **Visibility-aware tracking**: Handling occlusion in monocular HOI tracking<br>3. **CARI4D**: Category-agnostic metric-scale 4D HOI reconstruction<br>4. **Contact reasoning**: CoCoNet for learning physically plausible contacts |
| **Research Philosophy** | Individual foundation models are strong but misaligned. The art is in designing frameworks that integrate their predictions and enforce physical and geometric consistency. Generalization requires category-agnostic design — no object templates, no category constraints. |
| **Signature Techniques** | Render-and-compare optimization, contact reasoning networks, pose hypothesis selection, metric-scale reconstruction, foundation model integration |
| **Advised Students / Lineage** | PhD student advised by **Gerard Pons-Moll**. Collaborates closely with **Jan Eric Lenssen**. Part of the Real Virtual Humans and Geometric RL groups at MPI. |
| **Council Advice** | "Don't rely on a single foundation model prediction. Design frameworks that fuse multiple predictions and enforce physical consistency through optimization. Category-agnostic methods are the path to real-world deployment." |
| **Network Block** | **Perception** (4D reconstruction) and **Graph Memory** (human-object interaction graphs) |

---

## 7. Kristen Grauman

### Academic Genealogy
- **PhD**: Massachusetts Institute of Technology (MIT), 2006, Computer Science and AI Laboratory (CSAIL)
- **Advisor**: **Trevor Darrell** (now UC Berkeley)
- **Undergraduate**: Boston College, 2001, Computer Science (top honors)
- **Career Trajectory**:
  - 2006–2007: Postdoctoral Fellow, MIT
  - 2007–present: University of Texas at Austin (Assistant → Associate → Full Professor)
  - 2017: Inducted into UT Academy of Distinguished Teachers
  - ~2018–present: Research Director, Meta Fundamental AI Research (FAIR)
  - Leadership: Program Chair CVPR 2015, NeurIPS 2018, ICCV 2023; Associate Editor-in-Chief, IEEE TPAMI (6 years)

### Key Papers

#### 1. Pyramid Match Kernel (CVPR 2005 / IJCV 2007, with Darrell)
- **Core Problem**: How to compare variable-size sets of local features efficiently for recognition
- **Methodological Innovation**: Multi-resolution histogram intersection kernel approximating optimal partial matching in linear time
- **Philosophical Approach**: **Efficient approximation of combinatorial problems** — exact matching is expensive; multi-resolution histograms approximate it with theoretical guarantees
- **Lasting Impact**: 2011 Marr Prize, 2017 Helmholtz Prize (test of time); foundational for efficient visual recognition and set matching

#### 2. Ego4D (CVPR 2022, with Grauman as technical lead, multi-institution)
- **Core Problem**: First-person (egocentric) video understanding at scale
- **Methodological Innovation**: Massive egocentric video dataset of daily life with benchmarks for episodic memory, forecasting, hand-object interaction, audio-visual conversation
- **Philosophical Approach**: **Egocentric perception is the future** — wearable cameras give unique access to attention, goals, and interactions
- **Lasting Impact**: Catalyzed egocentric vision research worldwide; annual benchmark competitions

#### 3. Ego-Exo4D (CVPR 2024 Oral, with Grauman as technical lead)
- **Core Problem**: Understanding skilled human activity from both first-person and third-person views
- **Methodological Innovation**: Multi-view, time-synchronized video dataset with expert commentary, proficiency benchmarks, and 3D spatial context
- **Philosophical Approach**: **Learning from skill** — the path to robot learning and AR is through understanding human expertise from multiple perspectives
- **Lasting Impact**: Unprecedented resource for skill learning, 3D vision, and ego-exo representation learning

#### 4. Learning Fine-grained View-Invariant Representations from Unpaired Ego-Exo Videos (NeurIPS 2023, with Xue)
- **Core Problem**: How to learn representations that align first-person and third-person views without paired data
- **Methodological Innovation**: Temporal alignment and contrastive learning for view-invariant representations
- **Philosophical Approach**: **View invariance through temporal structure** — the same action seen from different perspectives shares temporal dynamics

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | University of Texas at Austin; Meta FAIR |
| **Core Methodology** | Pioneered efficient visual matching and kernel methods; now focuses on first-person video understanding, multimodal perception, and learning from human skill. Strong emphasis on dataset infrastructure and benchmark-driven research. |
| **Key Intellectual Contributions** | 1. **Pyramid Match Kernel**: Efficient set matching for visual recognition (Marr Prize)<br>2. **Ego4D**: Large-scale egocentric video understanding benchmark<br>3. **Ego-Exo4D**: Multi-perspective skill learning dataset<br>4. **View-invariant learning**: Aligning ego and exo perspectives for robot learning |
| **Research Philosophy** | "First-person video offers a special window into human attention, goals, and interactions." Believes the future of AR and robot learning depends on understanding egocentric perception. Advocates for multimodal integration (vision, audio, language) and learning from human skill. |
| **Signature Techniques** | Pyramid match kernels, egocentric video datasets, audio-visual learning, view-invariant representation learning, temporal alignment |
| **Advised Students / Lineage** | Advised by **Trevor Darrell** (MIT/UC Berkeley). Her students include **Zihui Xue** (FAIR), **Bo Xiong**, **Kumar Ashutosh**, **Suyog Jain**, **Dinesh Jayaraman**, and many others who have gone to top industry labs and faculty positions. |
| **Council Advice** | "Build datasets that capture real human experience — attention, goals, skills. The future of embodied AI depends on understanding people from their own perspective." |
| **Network Block** | **Perception** (egocentric video, multimodal) and **Cognition** (skill learning, view-invariant reasoning) |

---

## 8. Chenliang Xu

### Academic Genealogy
- **PhD**: University of Michigan, Ann Arbor, 2016, Computer Science and Engineering
- **Advisor**: **Jason J. Corso**
- **Thesis Committee**: Jia Deng, Irfan Essa (Georgia Tech), Matthew Johnson-Roberson, Benjamin Kuipers
- **MSc**: SUNY Buffalo, 2012, Computer Science
- **BSc**: Nanjing University of Aeronautics and Astronautics, 2010, Information and Computing Science
- **Career Trajectory**:
  - 2016–2022: Assistant Professor, University of Rochester
  - 2022–present: Associate Professor (tenured), University of Rochester
  - James P. Wilmot Distinguished Professorship (2021)
  - 2025 Edmund A. Hajim Outstanding Faculty Award

### Key Papers

#### 1. LIBSVX / Streaming Hierarchical Video Segmentation (ECCV 2012, PhD work with Corso)
- **Core Problem**: How to segment arbitrarily long videos with constant memory
- **Methodological Innovation**: First approximation framework for streaming hierarchical segmentation generating multiscale decompositions
- **Philosophical Approach**: **Scalable video representation** — videos are too long for batch processing; streaming is essential
- **Lasting Impact**: LIBSVX became the de facto standard evaluation for supervoxel methods; Best Open Source Code Prize at CVPR 2012

#### 2. Deep Cross-Modal Audio-Visual Generation (ACM MM 2017, with Chen, Srivastava, Duan)
- **Core Problem**: Generating visual content from audio and vice versa
- **Methodological Innovation**: Cross-modal generation using shared latent representations
- **Philosophical Approach**: **Multi-sensory integration** — vision and hearing are coupled in human perception; AI should model this

#### 3. Video Understanding with Large Language Models (Survey, 2023, with Tang, Bi, Xu, Song, Liang, Wang, Zhang, Luo, et al.)
- **Core Problem**: Taxonomy and analysis of how LLMs are being integrated into video understanding
- **Methodological Innovation**: Comprehensive categorization of Video-LLM architectures
- **Philosophical Approach**: **Survey-driven clarity** — the field moves fast; synthesis enables progress

#### 4. V2Xum-LLM / VideoXum (IEEE TMM 2023 / CVPR 2024, with Luo's group)
- **Core Problem**: Cross-modal video summarization — generating aligned video clips and text summaries
- **Methodological Innovation**: VTSUM-BLIP framework with hierarchical video encoding and task-specific decoders for V2V, V2T, and V2VT summarization
- **Philosophical Approach** | **Cross-modal coherence** — summarization must preserve semantic alignment across modalities |

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | University of Rochester (Associate Professor, tenured) |
| **Core Methodology** | Start with scalable video representations (supervoxels, streaming), then expand to cross-modal understanding (audio-visual, vision-language). Strong emphasis on trustworthy AI and adversarial robustness in recent work. |
| **Key Intellectual Contributions** | 1. **Streaming hierarchical video segmentation**: LIBSVX and scalable video representations<br>2. **Cross-modal generation**: Audio-visual synthesis and shared representations<br>3. **Video-language understanding**: Survey and methods for video-LLM integration<br>4. **Cross-modal summarization**: VideoXum/V2Xum-LLM for aligned video-text summaries |
| **Research Philosophy** | "I teach machines to understand the world through video, sound, and language together." Believes in interdisciplinary approaches and trustworthy AI. Values both foundational representations and cross-modal integration. |
| **Signature Techniques** | Supervoxel hierarchies, streaming segmentation, cross-modal generation, video-language models, adversarial robustness |
| **Advised Students / Lineage** | Advised by **Jason Corso** (Michigan). His PhD graduates include **Lele Chen** (OPPO US Research), **Yapeng Tian** (UT Dallas faculty), **Jing Shi** (Adobe Research), **Zhiheng Li** (Amazon AWS Bedrock). Collaborates closely with **Jiebo Luo** at Rochester. **Jia Deng** served on his thesis committee. |
| **Council Advice** | "Video understanding requires handling arbitrary length, multiple modalities, and adversarial robustness. Build representations that scale and generalize across sensory inputs." |
| **Network Block** | **Perception** (video segmentation, cross-modal) and **Generation** (audio-visual synthesis, summarization) |

---

## 9. Jiebo Luo

### Academic Genealogy
- **PhD**: University of Rochester, 1995, Electrical Engineering
- **Thesis**: *"Low Bit-rate Wavelet-based Image and Video Compression with Adaptive Quantization, Coding and Postprocessing"*
- **Advisor**: Part of the imaging/vision group at UR (specific advisor not prominently listed, but thesis was in image/video compression)
- **BSc/MSc**: University of Science and Technology of China (USTC), 1989 and 1992, Electrical Engineering
- **Career Trajectory**:
  - 1995: Summer at Xerox Wilson Center for Technology
  - 1995–2011: Senior Research Scientist → Senior Principal Scientist, Kodak Research Laboratories (15 years)
  - 2011–2014: Associate Professor, University of Rochester
  - 2014–present: Full Professor, University of Rochester
  - 2020–2022: Editor-in-Chief, IEEE Transactions on Multimedia
  - 2022: Elected to Academia Europaea
  - 2023: Fellow, National Academy of Inventors (95+ US patents)
  - Fellow of ACM, AAAI, IEEE, SPIE, IAPR

### Key Papers

#### 1. VideoXum: Cross-modal Visual and Textual Summarization of Videos (IEEE TMM 2023, with Lin, Hua, Chen, Li, Hsiao, Ho, Luo)
- **Core Problem**: Existing summarization treats video and text as independent; real applications need aligned cross-modal summaries
- **Methodological Innovation**: 
  - VideoXum dataset: 14K videos, 140K aligned video-text summary pairs
  - VTSUM-BLIP: Hierarchical video encoder with frozen BLIP backbone and task-specific decoders
  - CLIPScore adaptation for measuring cross-modal consistency
- **Philosophical Approach**: **Multi-modal coherence as first-class objective** — summaries must align across modalities, not just be good in isolation
- **Lasting Impact**: Established cross-modal video summarization as a formal task with large-scale benchmark

#### 2. V2Xum-LLM: Cross-Modal Video Summarization with Temporal Prompt Instruction Tuning (2024, with Hua, Tang, Xu, Luo)
- **Core Problem**: Scaling cross-modal summarization with instruction tuning
- **Methodological Innovation**: Temporal prompt instruction tuning unifying video-to-video, video-to-text, and video-to-video&text tasks in one LLM decoder
- **Philosophical Approach**: **Unified generative modeling** — one model should handle all summarization variants through instruction prompts

#### 3. Social Multimedia Sentiment Analysis / Computational Social Science (2010s–present)
- **Core Problem**: Understanding sentiment, emotion, and social dynamics in multimedia content
- **Methodological Innovation**: Pioneered contextual inference and visual sentiment analysis; applied computer vision to social science questions
- **Philosophical Approach**: **AI as a social science tool** — computer vision can answer questions about human behavior at scale
- **Lasting Impact**: Hundreds of publications spanning vision, NLP, data mining, and social science; ACM SIGMM Technical Achievement Award (2021)

### Digital Twin Profile

| Attribute | Details |
|-----------|---------|
| **Current Affiliation** | University of Rochester (Albert Arendt Hopeman Professor of Engineering) |
| **Core Methodology** | Bridge computer vision with natural language processing and social science. Emphasize large-scale dataset construction, cross-modal coherence, and real-world application. Deep experience in image/video processing from industrial research (Kodak). |
| **Key Intellectual Contributions** | 1. **Cross-modal video summarization**: VideoXum and V2Xum-LLM establish benchmarks and methods<br>2. **Computational social science**: Pioneered visual sentiment analysis and social multimedia mining<br>3. **Multimodal integration**: Bridging vision, language, and audio for holistic understanding<br>4. **Industrial research translation**: 95+ patents and technology transfer from Kodak to academia |
| **Research Philosophy** | "AI is a tool for understanding humanity at scale." Believes in the power of multimodal data (images, video, text) to reveal social patterns. Values real-world impact, as evidenced by industrial career and patent portfolio. |
| **Signature Techniques** | Cross-modal summarization, visual sentiment analysis, instruction tuning for video, computational social science methods |
| **Advised Students / Lineage** | Mentored numerous PhD students at Rochester including **Songyang Zhang** (AWS), **Haitian Zheng** (Adobe Research), **Jie An** (PhD student), **Wei Zhu** (AWS). Collaborates extensively with **Chenliang Xu** on video understanding and cross-modal research. |
| **Council Advice** | "Build systems that work across modalities and serve real human needs. Industrial experience teaches you what matters for deployment — take that seriously." |
| **Network Block** | **Generation** (cross-modal summarization) and **Cognition** (social science reasoning) |

---

## 10. The Interconnection Map

### Direct Advisor-Student Lineages

```
Pietro Perona (Caltech) ──┬──> Li Fei-Fei (Caltech PhD 2005) ──┬──> Ranjay Krishna (Stanford PhD 2021)
Christof Koch (Caltech) ──┘                                    ├──> Juan Carlos Niebles (UIUC/Princeton)
                                                               ├──> Andrej Karpathy (Stanford PhD 2016)
                                                               ├──> Justin Johnson (Stanford PhD 2018)
                                                               ├──> Jia Deng (Princeton PhD 2012)
                                                               └──> Yuke Zhu (Stanford PhD 2019)

Trevor Darrell (MIT) ──> Kristen Grauman (MIT PhD 2006) ──> Zihui Xue, Bo Xiong, Kumar Ashutosh, et al.

Jason Corso (Michigan) ──> Chenliang Xu (Michigan PhD 2016) ──> Lele Chen, Yapeng Tian, Jing Shi, Zhiheng Li
                                      │
                                      └── Thesis committee: Jia Deng (Fei-Fei's student)

Vibhav Gogate + Yu Xiang (UT Dallas) ──> Rohith Peddi (UT Dallas PhD) 
    │                                        │
    └── Parag Singla (IIT Delhi) <───────────┘
    └── Nicholas Ruozzi (UT Dallas) <────────┘

Gerard Pons-Moll (MPI) ──> Xianghui Xie (MPI PhD student)

Hongtao Xie + Yongdong Zhang (USTC) ──> Jiankang Wang (USTC)
```

### Collaboration and Citation Networks

#### The Stanford Vision Nexus (Li Fei-Fei, Ranjay Krishna, Juan Carlos Niebles)
- **Visual Genome** (2017): Li + Krishna + Bernstein + dozens of collaborators
- **Action Genome** (2020): Ji + Krishna + Li + Niebles — the canonical spatio-temporal scene graph dataset
- **Scene Graph Prediction with Limited Labels** (2019): Chen + Varma + Krishna + Bernstein + Re + Li
- **Grafting** (2025): Chandrasegaran + Poli + Fu + Kim + ... + Niebles + Ermon + Li — recent collaboration showing continued ties
- **Revisiting the "Video" in Video-Language Understanding** (2022): Buch + Eyzaguirre + Gaidon + Wu + Li + Niebles

#### The UT Dallas Scene Graph Ecosystem (Rohith Peddi, Vibhav Gogate, Yu Xiang)
- Peddi's work **directly builds on** Visual Genome and Action Genome (cites Krishna et al. and Ji et al.)
- **SceneSayer** (ECCV 2024): Peddi + Singh + Saurabh + Singla + Gogate — introduces anticipation
- **IMPARTIAL** (CVPR 2025): Peddi + Saurabh + Shrivastava + Singla + Gogate — addresses bias in scene graphs
- **WSGG** (2026): Peddi + Saurabh + Shanmugam + Pallapothula + Xiang + Singla + Gogate — world scene graphs
- **CaptainCook4D** (NeurIPS 2024): Large team including Peddi, Xiang, Gogate — error-aware procedural understanding

#### The Rochester Cross-Modal Alliance (Chenliang Xu, Jiebo Luo)
- **VideoXum / V2Xum-LLM** (2023-2024): Joint work between Xu's and Luo's groups
- **Video Understanding with LLMs Survey** (2023): Co-authored by Tang, Bi, Xu, Song, Liang, Wang, Zhang, Luo, et al.
- Both are at University of Rochester and frequently co-advise students and co-author papers

#### The Ego-Exo Multimodal Web (Kristen Grauman)
- **Ego4D** (2022) and **Ego-Exo4D** (2024): Massive multi-institutional efforts led by Grauman at Meta FAIR/UT Austin
- Collaborators include **Jitendra Malik** (Berkeley), **Lorenzo Torresani** (Meta), **Kris Kitani** (CMU/Meta)
- Connects to the broader vision community but focuses on egocentric/perceptual AI rather than explicit scene graphs

#### The European 4D Reconstruction Thread (Xianghui Xie)
- **CHORE** (ECCV 2022) → **VisTracker** (CVPR 2023) → **ProcGen-HDM** (CVPR 2024) → **CARI4D** (CVPR 2026)
- Advisor **Gerard Pons-Moll** is a leader in virtual humans and 4D reconstruction
- **CARI4D** connects to NVIDIA (co-author Stan Birchfield) — bridging academic and industrial 3D vision

### Intellectual Lineages and Philosophical Threads

| Lineage | Origin | Key Proponents | Core Philosophy |
|---------|--------|---------------|-----------------|
| **The Data-Centric Revolution** | ImageNet (2009) | Li Fei-Fei → Krishna → Niebles | Scale + structure in data enables algorithmic breakthroughs |
| **Scene Graph Structuralism** | Visual Genome (2017) | Krishna, Li, Niebles → Peddi, Singla, Gogate | Visual understanding requires explicit relational structures, not just labels |
| **Spatio-Temporal Dynamics** | Action Genome (2020) | Ji, Krishna, Li, Niebles → Peddi et al. | Actions are compositional spatio-temporal events; model object interactions over time |
| **World-Centric 4D Understanding** | WSGG / CARI4D (2025-2026) | Peddi, Xie, Pons-Moll | True understanding requires 3D world persistence, object permanence, and physical reasoning |
| **Egocentric Perception** | Ego4D / Ego-Exo4D (2022-2024) | Grauman, Torresani, Malik | First-person video is the path to embodied AI and skill learning |
| **Cross-Modal Coherence** | VideoXum / SpaceVLLM (2023-2025) | Xu, Luo, Wang, Xie | Video understanding must align language, space, and time through unified representations |

### Network Block Assignments for an Autonomous Cognitive Network

| Researcher | Primary Block | Secondary Block | Rationale |
|------------|--------------|----------------|-----------|
| **Li Fei-Fei** | Perception | Cognition | Foundational visual perception + human-centered reasoning philosophy |
| **Ranjay Krishna** | Graph Memory | Cognition | Scene graphs as structured memory; compositional reasoning benchmarks |
| **Juan Carlos Niebles** | Perception | Cognition | Event-aware perception; goal/intention inference for agents |
| **Jiankang Wang** | Perception | Graph Memory | Spatio-temporal grounding; query-based spatial representations |
| **Rohith Peddi** | Graph Memory | Cognition | World scene graphs; anticipation; error detection; robustness |
| **Xianghui Xie** | Perception | Graph Memory | 4D reconstruction; human-object interaction graphs; physical consistency |
| **Kristen Grauman** | Perception | Cognition | Egocentric video; multimodal perception; skill learning |
| **Chenliang Xu** | Perception | Generation | Video segmentation; cross-modal generation; video-language models |
| **Jiebo Luo** | Generation | Cognition | Cross-modal summarization; computational social science; multimodal coherence |

### The Council Consensus: What They Would Collectively Advise

If these nine researchers sat on a council guiding an autonomous cognitive network, their consensus would likely be:

1. **Perception must be world-centric, not frame-centric** (Peddi, Xie, Niebles) — The network must maintain persistent 3D world models with object permanence, not just process frames.

2. **Structured representations (scene graphs) are essential** (Krishna, Peddi, Li) — Relational knowledge graphs connecting objects, attributes, and relationships over time provide the substrate for reasoning.

3. **Spatio-temporal grounding is the critical interface** (Wang, Niebles, Xu) — The network must precisely localize language in space and time through query-based representations.

4. **Compositionality is the true test of understanding** (Krishna, Peddi, Li) — The network must handle novel combinations of concepts, not just memorize patterns.

5. **Multi-modal coherence must be enforced** (Grauman, Xu, Luo) — Vision, language, audio, and action must be aligned through shared representations.

6. **Human-centered augmentation over replacement** (Li, Grauman) — The network should enhance human capability, embed ethical constraints, and serve diverse users.

7. **Robustness to distribution shift and occlusion is non-negotiable** (Peddi, Xie) — The real world is long-tailed, occluded, and noisy; models must be robust.

8. **Benchmarks should expose failure modes, not just celebrate successes** (Krishna, Peddi) — Evaluation must test what the network cannot do, driving targeted improvement.

---

*Document compiled from public academic sources including personal websites, Google Scholar profiles, university pages, published papers, and the Mathematics Genealogy Project.*
