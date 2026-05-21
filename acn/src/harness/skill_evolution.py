# src/harness/skill_evolution.py
"""
Skill Evolution Engine: Abhyāsa (Deliberate Practice).

Manages agent skills as evolvable entities that mutate, compete, and
adapt based on performance feedback. Inspired by:
- Schmidhuber1991: Meta-learning — skills that learn to learn
- Mikkulainen2019: Evolving deep neural networks
- Real2017: Large-scale evolution of image classifiers

Principle: Abhyāsa is not repetition of the same action but progressive
refinement through variation and selection. A skill is a behavioral
program; evolution finds better programs.

[CITATION: Schmidhuber1991]
[CITATION: Mikkulainen2019]
[CITATION: Real2017]
"""

import time
import random
import copy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite


@cite(
    key="SKILL-EVOLUTION",
    paper="Skill Evolution Engine for Conscious Agents",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Skills as parameterized behavioral programs enable structural self-improvement",
    confidence="CERTAIN",
)
@dataclass
class Skill:
    """A skill — a parameterized behavioral program for an agent."""
    skill_id: str
    name: str
    skill_type: str              # "reasoning", "communication", "consensus", "research"
    
    # Behavioral parameters
    parameters: Dict[str, float] = field(default_factory=dict)
    
    # Performance tracking
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_reward: float = 0.0
    
    # Evolution metadata
    generation: int = 0
    parent_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.5
    
    @property
    def fitness(self) -> float:
        """Fitness score for selection — balances success rate and reward."""
        usage_bonus = min(self.usage_count / 10.0, 0.1)  # Slight bonus for tested skills
        return self.success_rate * 0.6 + (self.total_reward + 1.0) / 2.0 * 0.3 + usage_bonus
    
    def record_usage(self, reward: float, success: bool) -> None:
        """Record an instance of skill usage."""
        self.usage_count += 1
        self.last_used = time.time()
        self.total_reward += reward
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1


@cite(
    key="SKILL-EVOLUTION",
    paper="Skill Evolution Engine for Conscious Agents",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Mutation + selection + crossover evolve better skills over generations",
    confidence="CERTAIN",
)
class SkillEvolution:
    """
    Abhyāsa — evolves agent skills through variation and selection.
    
    Operations:
    1. Mutate: perturb skill parameters
    2. Crossover: combine parameters from two parent skills
    3. Select: choose skills by fitness for retention
    4. Prune: remove low-fitness skills to limit library size
    """

    def __init__(
        self,
        mutation_rate: float = 0.1,
        mutation_strength: float = 0.15,
        selection_pressure: float = 0.3,
        max_skills_per_agent: int = 10,
    ):
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.selection_pressure = selection_pressure
        self.max_skills_per_agent = max_skills_per_agent
        
        self._skills: Dict[str, List[Skill]] = {}  # agent_id -> skills
        self._skill_counter = 0

    def _generate_id(self) -> str:
        self._skill_counter += 1
        return f"skill-{self._skill_counter:04d}"

    def create_skill(
        self,
        agent_id: str,
        name: str,
        skill_type: str,
        parameters: Optional[Dict[str, float]] = None,
    ) -> Skill:
        """Create a new skill for an agent."""
        skill = Skill(
            skill_id=self._generate_id(),
            name=name,
            skill_type=skill_type,
            parameters=parameters or {},
        )
        
        if agent_id not in self._skills:
            self._skills[agent_id] = []
        self._skills[agent_id].append(skill)
        
        return skill

    def mutate_skill(self, agent_id: str, skill_id: str) -> Optional[Skill]:
        """
        Create a mutated copy of a skill.
        
        Perturbs parameters with Gaussian noise.
        """
        skill = self._get_skill(agent_id, skill_id)
        if not skill:
            return None
        
        new_params = copy.deepcopy(skill.parameters)
        for key in new_params:
            if random.random() < self.mutation_rate:
                noise = random.gauss(0, self.mutation_strength)
                new_params[key] = max(0.0, min(1.0, new_params[key] + noise))
        
        mutated = Skill(
            skill_id=self._generate_id(),
            name=f"{skill.name}-v{skill.generation + 1}",
            skill_type=skill.skill_type,
            parameters=new_params,
            generation=skill.generation + 1,
            parent_id=skill.skill_id,
        )
        
        self._skills[agent_id].append(mutated)
        return mutated

    def crossover_skills(self, agent_id: str, skill_id_a: str, skill_id_b: str) -> Optional[Skill]:
        """
        Create a child skill by combining parameters from two parents.
        """
        skill_a = self._get_skill(agent_id, skill_id_a)
        skill_b = self._get_skill(agent_id, skill_id_b)
        if not skill_a or not skill_b:
            return None
        
        # Take union of parameter keys
        all_keys = set(skill_a.parameters.keys()) | set(skill_b.parameters.keys())
        child_params = {}
        for key in all_keys:
            if key in skill_a.parameters and key in skill_b.parameters:
                # Average with slight noise
                val = (skill_a.parameters[key] + skill_b.parameters[key]) / 2.0
                val += random.gauss(0, self.mutation_strength * 0.5)
                child_params[key] = max(0.0, min(1.0, val))
            elif key in skill_a.parameters:
                child_params[key] = skill_a.parameters[key]
            else:
                child_params[key] = skill_b.parameters[key]
        
        child = Skill(
            skill_id=self._generate_id(),
            name=f"{skill_a.name}x{skill_b.name}",
            skill_type=skill_a.skill_type,
            parameters=child_params,
            generation=max(skill_a.generation, skill_b.generation) + 1,
            parent_id=skill_a.skill_id,
        )
        
        self._skills[agent_id].append(child)
        return child

    def select_skills(self, agent_id: str, skill_type: Optional[str] = None) -> List[Skill]:
        """
        Select top skills by fitness. Retains (1 - selection_pressure) fraction.
        """
        skills = self._skills.get(agent_id, [])
        if skill_type:
            skills = [s for s in skills if s.skill_type == skill_type]
        
        if not skills:
            return []
        
        # Sort by fitness descending
        sorted_skills = sorted(skills, key=lambda s: s.fitness, reverse=True)
        
        # Keep top (1 - selection_pressure) fraction
        keep_count = max(1, int(len(sorted_skills) * (1 - self.selection_pressure)))
        return sorted_skills[:keep_count]

    def prune_skills(self, agent_id: str) -> int:
        """
        Remove low-fitness skills to keep library within size limits.
        Returns number of skills removed.
        """
        skills = self._skills.get(agent_id, [])
        if len(skills) <= self.max_skills_per_agent:
            return 0
        
        # Sort by fitness, keep top max_skills_per_agent
        sorted_skills = sorted(skills, key=lambda s: s.fitness, reverse=True)
        kept = sorted_skills[:self.max_skills_per_agent]
        removed = len(skills) - len(kept)
        self._skills[agent_id] = kept
        return removed

    def evolve_generation(self, agent_id: str) -> Dict[str, Any]:
        """
        Run one generation of evolution: select → mutate/crossover → prune.
        
        Returns summary of evolution results.
        """
        skills = self._skills.get(agent_id, [])
        if len(skills) < 2:
            return {"status": "insufficient_skills", "agent_id": agent_id}
        
        before_count = len(skills)
        
        # Select parents
        parents = self.select_skills(agent_id)
        
        # Generate offspring
        offspring = []
        for parent in parents:
            if random.random() < 0.5:
                mutated = self.mutate_skill(agent_id, parent.skill_id)
                if mutated:
                    offspring.append(mutated)
        
        # Crossover between top 2
        if len(parents) >= 2:
            child = self.crossover_skills(agent_id, parents[0].skill_id, parents[1].skill_id)
            if child:
                offspring.append(child)
        
        # Prune
        removed = self.prune_skills(agent_id)
        
        after_count = len(self._skills.get(agent_id, []))
        
        return {
            "status": "evolved",
            "agent_id": agent_id,
            "before_count": before_count,
            "after_count": after_count,
            "offspring_created": len(offspring),
            "pruned": removed,
            "top_skill_fitness": parents[0].fitness if parents else 0.0,
        }

    def get_best_skill(
        self,
        agent_id: str,
        skill_type: Optional[str] = None,
    ) -> Optional[Skill]:
        """Get the highest-fitness skill for an agent."""
        skills = self._skills.get(agent_id, [])
        if skill_type:
            skills = [s for s in skills if s.skill_type == skill_type]
        
        if not skills:
            return None
        return max(skills, key=lambda s: s.fitness)

    def get_agent_skills(self, agent_id: str, skill_type: Optional[str] = None) -> List[Skill]:
        """Get all skills for an agent."""
        skills = self._skills.get(agent_id, [])
        if skill_type:
            skills = [s for s in skills if s.skill_type == skill_type]
        return skills

    def _get_skill(self, agent_id: str, skill_id: str) -> Optional[Skill]:
        """Get a specific skill by ID."""
        skills = self._skills.get(agent_id, [])
        for skill in skills:
            if skill.skill_id == skill_id:
                return skill
        return None

    def get_evolution_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get evolution statistics for an agent."""
        skills = self._skills.get(agent_id, [])
        if not skills:
            return {"total_skills": 0, "avg_fitness": 0.0, "top_skill": None}
        
        by_type = {}
        for s in skills:
            by_type.setdefault(s.skill_type, []).append(s)
        
        type_summaries = {}
        for stype, sskills in by_type.items():
            best = max(sskills, key=lambda s: s.fitness)
            type_summaries[stype] = {
                "count": len(sskills),
                "avg_fitness": sum(s.fitness for s in sskills) / len(sskills),
                "best_skill": best.name,
                "best_fitness": best.fitness,
            }
        
        return {
            "total_skills": len(skills),
            "avg_fitness": sum(s.fitness for s in skills) / len(skills),
            "type_summaries": type_summaries,
            "top_skill": max(skills, key=lambda s: s.fitness).name if skills else None,
        }
