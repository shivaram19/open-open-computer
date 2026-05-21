# src/harness/experience_buffer.py
"""
Experience Buffer: Svādhyāya's Memory of Practice.

Stores agent experiences (state, action, reward, next_state) for later
reflection and policy optimization. Inspired by:
- Lin1992: Experience replay for reinforcement learning
- Schaul2015: Prioritized experience replay
- SuttonBarto2018: RL fundamentals — reward signals shape behavior

Principle: An agent that cannot remember its mistakes cannot learn from them.
Abhyāsa (practice) requires Smṛti (memory) of past actions.

[CITATION: Lin1992]
[CITATION: Schaul2015]
[CITATION: SuttonBarto2018]
"""

import time
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from collections import deque

from shared.utils.citations import cite


@cite(
    key="EXPERIENCE-BUFFER",
    paper="Experience Buffer for Meta-Cognitive Learning",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Storing experiences enables offline reflection and policy optimization",
    confidence="CERTAIN",
)
@dataclass
class Experience:
    """A single experience episode from an agent's deliberation."""
    agent_id: str
    task_id: str
    state: Dict[str, Any]           # Agent state before action
    action: str                     # Action taken (e.g., "propose", "critique", "agree")
    reward: float                   # Shaped reward from outcome
    next_state: Dict[str, Any]      # Agent state after action
    confidence_before: float
    confidence_after: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@cite(
    key="EXPERIENCE-BUFFER",
    paper="Experience Buffer for Meta-Cognitive Learning",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Circular buffer with priority sampling for efficient learning",
    confidence="CERTAIN",
)
class ExperienceBuffer:
    """
    Circular experience buffer with priority sampling.
    
    Stores experiences from agent deliberations. Supports:
    - Uniform or priority-weighted sampling
    - Per-agent experience isolation
    - Reward statistics for calibration
    """

    def __init__(self, capacity: int = 1000, alpha: float = 0.6):
        """
        Initialize experience buffer.
        
        Args:
            capacity: Maximum number of experiences to store
            alpha: Priority exponent (0 = uniform, 1 = full priority)
        """
        self.capacity = capacity
        self.alpha = alpha
        self.buffer: deque = deque(maxlen=capacity)
        self.priorities: deque = deque(maxlen=capacity)
        self._agent_indices: Dict[str, List[int]] = {}
        self._total_reward = 0.0
        self._reward_count = 0

    def add(self, experience: Experience) -> None:
        """Add an experience to the buffer."""
        idx = len(self.buffer)
        self.buffer.append(experience)
        
        # Priority based on absolute reward (higher magnitude = more to learn)
        priority = (abs(experience.reward) + 1e-6) ** self.alpha
        self.priorities.append(priority)
        
        # Track per-agent indices
        agent_id = experience.agent_id
        if agent_id not in self._agent_indices:
            self._agent_indices[agent_id] = []
        self._agent_indices[agent_id].append(idx)
        
        # Update reward statistics
        self._total_reward += experience.reward
        self._reward_count += 1

    def sample(self, batch_size: int = 32, agent_id: Optional[str] = None) -> List[Experience]:
        """
        Sample a batch of experiences.
        
        Args:
            batch_size: Number of experiences to sample
            agent_id: If provided, sample only from this agent's experiences
        
        Returns:
            List of sampled experiences
        """
        if not self.buffer:
            return []
        
        if agent_id and agent_id in self._agent_indices:
            indices = self._agent_indices[agent_id]
            if not indices:
                return []
            # Sample from agent's experiences
            probs = [self.priorities[i] for i in indices]
            total = sum(probs)
            if total == 0:
                sampled_indices = random.choices(indices, k=min(batch_size, len(indices)))
            else:
                sampled_indices = random.choices(
                    indices,
                    weights=[p / total for p in probs],
                    k=min(batch_size, len(indices)),
                )
            return [self.buffer[i] for i in sampled_indices]
        
        # Sample from all experiences with priority
        total_priority = sum(self.priorities)
        if total_priority == 0:
            if len(self.buffer) <= batch_size:
                return list(self.buffer)
            return random.sample(list(self.buffer), batch_size)
        
        probs = [p / total_priority for p in self.priorities]
        k = min(batch_size, len(self.buffer))
        sampled = random.choices(list(self.buffer), weights=probs, k=k)
        return sampled

    def get_agent_experiences(self, agent_id: str) -> List[Experience]:
        """Get all experiences for a specific agent."""
        indices = self._agent_indices.get(agent_id, [])
        return [self.buffer[i] for i in indices if i < len(self.buffer)]

    def get_reward_statistics(self) -> Dict[str, float]:
        """Get reward statistics for calibration."""
        if self._reward_count == 0:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        
        rewards = [e.reward for e in self.buffer]
        return {
            "mean": self._total_reward / self._reward_count,
            "min": min(rewards) if rewards else 0.0,
            "max": max(rewards) if rewards else 0.0,
            "count": self._reward_count,
        }

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self.priorities.clear()
        self._agent_indices.clear()
        self._total_reward = 0.0
        self._reward_count = 0

    def __len__(self) -> int:
        return len(self.buffer)
