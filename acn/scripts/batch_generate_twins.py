#!/usr/bin/env python3
"""
Batch generate all remaining cognitive twins from researcher profiles.

Usage:
    python3 acn/scripts/batch_generate_twins.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from twins.generator import batch_generate


# ── Researcher Configurations ──────────────────────────────────────────
# Each entry: name must match the markdown section header
# key_papers must exist in citation_registry.json

RESEARCHER_CONFIGS = [
    # ── Cluster A: Video + Spatio-Temporal GNN ──
    # Source: research_profiles/digital_twin_profiles.md
    {
        "name": "Jiankang Wang",
        "cluster": "video-gnn",
        "source_file": "digital_twin_profiles.md",
        "key_papers": [],
    },
    {
        "name": "Rohith Peddi",
        "cluster": "video-gnn",
        "source_file": "digital_twin_profiles.md",
        "key_papers": ["WSGG2026"],
    },
    {
        "name": "Xianghui Xie",
        "cluster": "video-gnn",
        "source_file": "digital_twin_profiles.md",
        "key_papers": ["CARI4D2026"],
    },
    {
        "name": "Kristen Grauman",
        "cluster": "video-gnn",
        "source_file": "digital_twin_profiles.md",
        "key_papers": [],
    },
    {
        "name": "Chenliang Xu",
        "cluster": "video-gnn",
        "source_file": "digital_twin_profiles.md",
        "key_papers": [],
    },
    {
        "name": "Jiebo Luo",
        "cluster": "video-gnn",
        "source_file": "digital_twin_profiles.md",
        "key_papers": [],
    },
    # ── Cluster B: Streaming Cognition + Self-Reflection ──
    # Source: digital_twin_profiles.md (root)
    {
        "name": "Aman Madaan",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Madaan2023"],
    },
    {
        "name": "Shunyu Yao",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Yao2023"],
    },
    {
        "name": "Maciej Besta",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Besta2024"],
    },
    {
        "name": "Xinhao Li",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Li2025"],
    },
    {
        "name": "Ruyi Xu",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["StreamingVLM2026"],
    },
    {
        "name": "Shengyuan Ye",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Ye2026"],
    },
    {
        "name": "Jacob Chalk",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Chalk2024"],
    },
    {
        "name": "Jenny Zhang",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Zhang2026"],
    },
    {
        "name": "Nehzati M. (Mohammadreza Nehzati)",
        "cluster": "streaming-reflection",
        "source_file": "../digital_twin_profiles.md",
        "key_papers": ["Nehzati2025"],
    },
    # ── Cluster C: Consensus + Safety ──
    # Source: research_profiles/consensus_safety_digital_twins.md
    {
        "name": "Lifan Zheng & Yu Tian",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["CP-WBFT2025"],
    },
    {
        "name": "Yongrae Jo & Chanik Park",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["DecentLLMs2025"],
    },
    {
        "name": "Yu Cui & Hongyang Du",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["MAD-Spear2025"],
    },
    {
        "name": "Shilong Wang & Guibin Zhang",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["G-Safeguard2025"],
    },
    {
        "name": "Miao Yu et al.",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["NetSafe2025"],
    },
    {
        "name": "Ryan Greenblatt",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["Greenblatt2024"],
    },
    {
        "name": "Evan Hubinger",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["Hubinger2024"],
    },
    {
        "name": "Saeid Jamshidi",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["Jamshidi2026"],
    },
    {
        "name": "Frédéric Berdoz & Roger Wattenhofer",
        "cluster": "consensus-safety",
        "source_file": "consensus_safety_digital_twins.md",
        "key_papers": ["Berdoz2026"],
    },
    # ── Cluster D: Multi-Agent Framework ──
    # Source: research_profiles/multi_agent_digital_twins.md
    {
        "name": "João Moura",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": ["Moura2023"],
    },
    {
        "name": "Chi Wang",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": [],
    },
    {
        "name": "Torsten Hoefler",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": ["Besta2024"],
    },
    {
        "name": "Dapr Agents Team",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": ["DaprAgents2025"],
    },
    {
        "name": "Google ADK / A2A Team",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": ["GoogleADK2025"],
    },
    {
        "name": "OpenAI Agents SDK Team",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": [],
    },
    {
        "name": "Anthropic Claude Code / Agent SDK Team",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": [],
    },
    {
        "name": "Andrea Cini",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": ["CiniMarisca2022"],
    },
    {
        "name": "Ivan Marisca",
        "cluster": "multi-agent",
        "source_file": "multi_agent_digital_twins.md",
        "key_papers": ["CiniMarisca2022"],
    },
]


def main():
    repo_root = Path(__file__).parent.parent.parent
    profile_dir = repo_root / "research_profiles"
    output_dir = repo_root / "acn" / "src" / "twins" / "cognitive_models"

    # Also check root for digital_twin_profiles.md
    root_profile = repo_root / "digital_twin_profiles.md"

    print(f"Profile dir: {profile_dir}")
    print(f"Output dir:  {output_dir}")
    print(f"Researchers: {len(RESEARCHER_CONFIGS)}")
    print()

    # Pre-verify source files exist
    for cfg in RESEARCHER_CONFIGS:
        sf = cfg["source_file"]
        if sf.startswith("../"):
            path = repo_root / sf[3:]
        else:
            path = profile_dir / sf
        if not path.exists():
            print(f"⚠️  Missing source: {path}")
            return 1

    results = batch_generate(
        profile_dir=profile_dir,
        output_dir=output_dir,
        researcher_configs=RESEARCHER_CONFIGS,
    )

    print(f"✅ Success: {results['success']}")
    print(f"❌ Failed:  {results['failed']}")
    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"]:
            print(f"  - {err}")

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
