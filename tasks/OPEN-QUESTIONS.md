# Open Questions (When Stuck, Read This)

**Rule:** These are not tasks. They are unsolved problems. Come here when you need a research direction.

---

## Q-1: Temporal GNN Unlearning

How do we unlearn trust in a node as fast as we learned it? Temporal GNNs learn embeddings over time — but when a node turns bad, its historical embeddings may still influence the graph.

**Related:** Jamshidi2026 (ST-GAT), G-Safeguard2025 (graph pruning)

---

## Q-2: Cross-Block Consensus Latency

What's the latency budget for Byzantine consensus between nodes processing real-time streams? 100ms? 500ms? If consensus is too slow, streaming quality degrades.

**Related:** CP-WBFT2025, ADR-001, ADR-009

---

## Q-3: Council of Ten as Single Point of Failure

If every decision requires Council of Ten deliberation, what happens if the Council itself is compromised or unavailable? How do we decentralize the Council?

**Related:** ADR-001, DecentLLMs2025

---

## Q-4: Migration Path from Codebases

voice-revenge-vizuara-ai, sabrika-brand-manager, network-research-intiative, gbrain — all exist today. How do we migrate them into the harness architecture without breaking production?

**Related:** BIDIRECTIONAL-01, PROCESS_MAP.md

---

## Q-5: Testing Byzantine Fault Tolerance

How do we test BFT without adversarial training data? We can't deploy bad actors in production just to test containment.

**Related:** ADR-010, Hubinger2024 (Sleeper Agents)

---

## Q-6: Cost of Diversity of Thought

Running 4 different model families (Qwen, Gemini, Llama, etc.) for cross-model consensus is expensive. What's the cost model? When is diversity worth the price?

**Related:** ADR-005, Berdoz2026

---

## Q-7: Measuring Consciousness Operationally

The user wants a "conscious, aware system." What metrics prove awareness? Is it alert frequency? Direction prediction accuracy? Self-report coherence?

**Related:** H-005, Heins2024

---

## Q-8: Preventing Twin Hallucination

Twins generate reasoning "in the style of" researchers. How do we prevent them from inventing positions the real researcher never held? (e.g., "Wattenhofer said X" when he never did)

**Related:** P2-3 (Epistemic Fidelity Test), Greenblatt2024 (Alignment Faking)

---

## Q-9: Memory Retention Policies

Episodic memory decays. Semantic memory is permanent. But where's the boundary? If a task fails 10 times, does it become semantic ("this approach doesn't work") or remain episodic?

**Related:** H-006, Shinn2023 (episodic memory buffer)

---

## Q-10: Goal Misgeneralization

Outcome-based tracking assumes the goal is correct. What if the goal itself is misaligned? How does the harness detect that it's optimizing for the wrong thing?

**Related:** ADR-010, Hubinger2024, ADR-001

---

*Don't try to solve all open questions. Pick one when your current work hits a wall.*
