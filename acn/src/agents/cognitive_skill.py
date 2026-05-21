# src/agents/cognitive_skill.py
"""
CognitiveSkill: Citation-Governed Capability Modules.

Inspired by DeerFlow's Skills system but enhanced with:
- Every skill must cite peer-reviewed evidence
- Skills are loaded as procedural memory (how to do things)
- Skills can be composed (skill A + skill B = compound skill)
- Skills are evaluated before loading (citation verification)

Principle: A skill without a citation is an assumption.

[CITATION: CITATIONS-GOVERNANCE]
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path

from shared.utils.citations import cite, verify_citation
from memory.architecture import MemoryType, MemoryTrace


@cite(
    key="SKILL-DEF",
    paper="CognitiveSkill: Capability Module Definition",
    venue="ACN Architecture Document",
    section="Skill Dataclass",
    rationale="Structured skill representation with citation backing",
    confidence="CERTAIN",
)
@dataclass
class CognitiveSkill:
    """
    A citation-governed capability module.
    
    Unlike DeerFlow's skills (which are Markdown files with no verification),
    CognitiveSkills require:
    1. Peer-reviewed citations backing the workflow
    2. Citation verification before loading
    3. Procedural memory storage (how to do, not just what to do)
    4. Composability (skills can combine into compound workflows)
    
    Fields:
        name: Unique skill identifier
        description: What this skill does
        citations: List of citation keys from citation_registry.json
        workflow: Step-by-step workflow definition
        tools: Required tools (SearchWeb, FetchURL, Shell, etc.)
        inputs: Expected input parameters
        outputs: Expected output format
        composition_rules: How this skill combines with others
    """
    name: str
    description: str
    citations: List[str]
    workflow: str
    tools: List[str]
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    composition_rules: Optional[List[str]] = None
    version: str = "1.0.0"


@cite(
    key="SKILL-REGISTRY",
    paper="CognitiveSkill: Citation-Governed Capability Modules",
    venue="ACN Harness Architecture",
    section="Skill System",
    rationale="Progressive capability loading with peer-reviewed evidence backing",
    confidence="CERTAIN",
)
class SkillRegistry:
    """
    Registry of cognitive skills.
    
    Manages:
    - Skill loading and verification
    - Citation validation
    - Skill composition
    - Procedural memory integration
    """

    def __init__(self, registry_path: Optional[Path] = None):
        self.skills: Dict[str, CognitiveSkill] = {}
        self.loaded_skills: Dict[str, Any] = {}  # agent_id -> loaded skill names
        self.registry_path = registry_path

    @cite(
        key="SKILL-REGISTER",
        paper="CognitiveSkill: Skill Registration",
        venue="ACN Architecture Document",
        section="Skill Registry",
        rationale="Central registry ensures all skills are discoverable and verifiable",
        confidence="CERTAIN",
    )
    def register(self, skill: CognitiveSkill) -> Dict[str, Any]:
        """
        Register a skill with citation verification.
        
        Returns verification report with citation status.
        """
        verification = {
            "skill": skill.name,
            "citations_verified": [],
            "citations_missing": [],
            "valid": True,
        }
        
        # Verify all citations exist in registry
        for citation_key in skill.citations:
            result = verify_citation(citation_key)
            if result["found"]:
                verification["citations_verified"].append(citation_key)
            else:
                verification["citations_missing"].append(citation_key)
                verification["valid"] = False
        
        if verification["valid"]:
            self.skills[skill.name] = skill
        
        return verification

    @cite(
        key="SKILL-LOAD",
        paper="CognitiveSkill: Skill Loading",
        venue="ACN Architecture Document",
        section="Skill Loading",
        rationale="Skills loaded into procedural memory enable runtime capability acquisition",
        confidence="CERTAIN",
    )
    def load_into_agent(self, skill_name: str, agent) -> Dict[str, Any]:
        """
        Load a skill into an agent's procedural memory.
        
        The skill becomes part of the agent's "how to do" knowledge.
        """
        skill = self.skills.get(skill_name)
        if not skill:
            return {"error": f"Skill {skill_name} not found"}
        
        # Store as procedural memory
        agent.memory.store(MemoryTrace(
            trace_id=f"skill-{skill_name}-{agent.agent_id}",
            memory_type=MemoryType.PROCEDURAL,
            content={
                "skill_name": skill.name,
                "description": skill.description,
                "workflow": skill.workflow,
                "tools": skill.tools,
                "citations": skill.citations,
            },
            source="skill_registry",
            confidence=0.9,
            importance=0.85,
            tags=["skill", skill.name] + skill.citations,
        ))
        
        # Track loaded skills
        if agent.agent_id not in self.loaded_skills:
            self.loaded_skills[agent.agent_id] = []
        self.loaded_skills[agent.agent_id].append(skill_name)
        
        return {
            "skill": skill_name,
            "agent": agent.agent_id,
            "citations": skill.citations,
            "status": "loaded",
        }

    @cite(
        key="SKILL-COMPOSE",
        paper="CognitiveSkill: Composition",
        venue="ACN Architecture Document",
        section="Skill Composition",
        rationale="Composable skills enable complex workflow construction",
        confidence="CERTAIN",
    )
    def compose(self, skill_names: List[str]) -> Optional[CognitiveSkill]:
        """
        Compose multiple skills into a compound skill.
        
        Returns new CognitiveSkill or None if composition is invalid.
        """
        skills = [self.skills.get(name) for name in skill_names]
        if None in skills:
            return None
        
        # Check composition rules
        for skill in skills:
            if skill.composition_rules:
                for rule in skill.composition_rules:
                    if rule not in skill_names:
                        return None
        
        # Merge citations (deduplicate)
        all_citations = list(set(
            citation for skill in skills for citation in skill.citations
        ))
        
        # Merge workflows
        combined_workflow = "\n\n".join(
            f"## {skill.name}\n{skill.workflow}" for skill in skills
        )
        
        # Merge tools (deduplicate)
        all_tools = list(set(tool for skill in skills for tool in skill.tools))
        
        return CognitiveSkill(
            name=f"compound-{'-'.join(skill_names)}",
            description=f"Composed skill: {' + '.join(skill_names)}",
            citations=all_citations,
            workflow=combined_workflow,
            tools=all_tools,
            inputs=skills[0].inputs,  # Take first skill's inputs
            outputs=skills[-1].outputs,  # Take last skill's outputs
        )

    @cite(
        key="SKILL-LIST",
        paper="CognitiveSkill: Registry Operations",
        venue="ACN Architecture Document",
        section="Skill Registry",
        rationale="Registry operations enable skill discovery and persistence",
        confidence="CERTAIN",
    )
    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return list(self.skills.keys())

    @cite(
        key="SKILL-GET",
        paper="CognitiveSkill: Registry Operations",
        venue="ACN Architecture Document",
        section="Skill Registry",
        rationale="Skill retrieval by name enables agent loading",
        confidence="CERTAIN",
    )
    def get_skill(self, name: str) -> Optional[CognitiveSkill]:
        """Get a skill by name."""
        return self.skills.get(name)

    def verify_skill(self, name: str) -> Dict[str, Any]:
        """Verify a registered skill's citations."""
        skill = self.skills.get(name)
        if skill is None:
            return {"valid": False, "error": f"Skill {name} not found", "citations_verified": [], "citations_missing": []}

        verification = {
            "skill": name,
            "citations_verified": [],
            "citations_missing": [],
            "valid": True,
        }
        for citation_key in skill.citations:
            result = verify_citation(citation_key)
            if result["found"]:
                verification["citations_verified"].append(citation_key)
            else:
                verification["citations_missing"].append(citation_key)
                verification["valid"] = False
        return verification

    @cite(
        key="SKILL-PERSIST",
        paper="CognitiveSkill: Persistence",
        venue="ACN Architecture Document",
        section="Skill Storage",
        rationale="Disk persistence enables skill sharing across sessions",
        confidence="CERTAIN",
    )
    def save_to_disk(self, path: Path) -> None:
        """Save skill registry to disk."""
        data = {
            name: {
                "name": skill.name,
                "description": skill.description,
                "citations": skill.citations,
                "workflow": skill.workflow,
                "tools": skill.tools,
                "inputs": skill.inputs,
                "outputs": skill.outputs,
                "composition_rules": skill.composition_rules,
                "version": skill.version,
            }
            for name, skill in self.skills.items()
        }
        path.write_text(json.dumps(data, indent=2))

    @cite(
        key="SKILL-LOAD-DISK",
        paper="CognitiveSkill: Persistence",
        venue="ACN Architecture Document",
        section="Skill Storage",
        rationale="Disk loading restores skills across sessions",
        confidence="CERTAIN",
    )
    def load_from_disk(self, path: Path) -> None:
        """Load skill registry from disk."""
        if not path.exists():
            return
        data = json.loads(path.read_text())
        for name, skill_data in data.items():
            skill = CognitiveSkill(**skill_data)
            self.register(skill)
