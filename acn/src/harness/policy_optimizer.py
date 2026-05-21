# src/harness/policy_optimizer.py
"""
Policy Optimizer: Reward-Weighted Behavioral Adjustment.

Optimizes agent behavioral policies using reward-weighted updates.
Inspired by:
- SuttonBarto2018: Policy gradient methods — REINFORCE
- Ziegler2019: RLHF — learning from human preferences
- Ouyang2022: InstructGPT — reward models guide policy optimization

Principle: Abhyāsa (practice) is not mere repetition but deliberate,
reward-guided refinement. Each experience shapes the policy toward
higher expected reward.

[CITATION: SuttonBarto2018]
[CITATION: Ziegler2019]
[CITATION: Ouyang2022]
"""

import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from shared.utils.citations import cite


@cite(
    key="POLICY-OPTIMIZER",
    paper="Policy Optimizer for Conscious Agents",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="Policy parameters govern agent behavior; reward-weighted updates enable learning",
    confidence="CERTAIN",
)
@dataclass
class Policy:
    """A behavioral policy governing an agent's decision-making parameters."""
    agent_id: str
    
    # Confidence calibration parameters
    base_confidence: float = 0.7
    confidence_learning_rate: float = 0.05
    confidence_momentum: float = 0.9
    
    # Risk threshold parameters
    risk_tolerance: float = 0.5
    risk_learning_rate: float = 0.03
    
    # Peer trust parameters
    peer_trust_weight: float = 0.3
    trust_learning_rate: float = 0.04
    
    # Exploration vs exploitation
    exploration_rate: float = 0.2
    exploration_decay: float = 0.98
    
    # State-dependent multipliers
    state_multipliers: Dict[str, float] = field(default_factory=lambda: {
        "researching": 0.8,
        "analyzing": 1.0,
        "evaluating": 1.1,
        "synthesizing": 0.9,
    })
    
    # Update tracking
    update_count: int = 0
    last_update: float = field(default_factory=time.time)
    reward_history: List[float] = field(default_factory=list)


@cite(
    key="POLICY-OPTIMIZER",
    paper="Policy Optimizer for Conscious Agents",
    venue="ACN Harness Architecture",
    section="Self-Improvement Loop",
    rationale="REINFORCE-style policy gradient with adaptive learning rates",
    confidence="CERTAIN",
)
class PolicyOptimizer:
    """
    Optimizes agent policies using reward-weighted gradient estimates.
    
    Updates policy parameters (confidence, risk tolerance, peer trust,
    exploration) based on experience rewards. Uses momentum for stable
    updates and clips gradients to prevent catastrophic shifts.
    """

    def __init__(self, max_gradient_norm: float = 0.2, min_lr: float = 0.001):
        self.max_gradient_norm = max_gradient_norm
        self.min_lr = min_lr
        self._policies: Dict[str, Policy] = {}
        self._gradients: Dict[str, Dict[str, float]] = {}

    def register_policy(self, policy: Policy) -> None:
        """Register a policy for optimization."""
        self._policies[policy.agent_id] = policy
        self._gradients[policy.agent_id] = {
            "base_confidence": 0.0,
            "risk_tolerance": 0.0,
            "peer_trust_weight": 0.0,
            "exploration_rate": 0.0,
        }

    def get_policy(self, agent_id: str) -> Optional[Policy]:
        """Get a registered policy."""
        return self._policies.get(agent_id)

    def compute_gradient(
        self,
        agent_id: str,
        experiences: List[Any],
    ) -> Dict[str, float]:
        """
        Compute policy gradient from experiences.
        
        Uses reward-weighted parameter adjustment:
        - Positive reward → reinforce the action's parameters
        - Negative reward → push parameters away from action's values
        """
        if not experiences or agent_id not in self._policies:
            return {}
        
        policy = self._policies[agent_id]
        
        # Baseline: average reward
        rewards = [e.reward for e in experiences]
        baseline = sum(rewards) / len(rewards)
        
        # Compute advantage-weighted parameter shifts
        grad_confidence = 0.0
        grad_risk = 0.0
        grad_trust = 0.0
        grad_exploration = 0.0
        
        for exp in experiences:
            advantage = exp.reward - baseline
            
            # Confidence gradient: shift toward confidence that yielded reward
            conf_delta = exp.confidence_after - exp.confidence_before
            grad_confidence += advantage * conf_delta * policy.confidence_learning_rate
            
            # Risk gradient: positive reward with high confidence_after → increase risk tolerance
            if exp.reward > 0 and exp.confidence_after > 0.6:
                grad_risk += advantage * policy.risk_learning_rate
            elif exp.reward < 0:
                grad_risk -= advantage * policy.risk_learning_rate
            
            # Trust gradient: if action involved peer interaction, adjust trust
            if "peer" in exp.action or "communicate" in exp.action:
                grad_trust += advantage * policy.trust_learning_rate
            
            # Exploration: decay over time, increase on negative rewards (encourage exploration)
            if exp.reward < 0:
                grad_exploration += 0.05  # Encourage exploration after failure
            else:
                grad_exploration -= 0.01  # Slowly reduce exploration
        
        # Average over batch
        n = len(experiences)
        gradient = {
            "base_confidence": grad_confidence / n,
            "risk_tolerance": grad_risk / n,
            "peer_trust_weight": grad_trust / n,
            "exploration_rate": grad_exploration / n,
        }
        
        # Clip gradients
        for key in gradient:
            gradient[key] = max(-self.max_gradient_norm, min(self.max_gradient_norm, gradient[key]))
        
        return gradient

    def update_policy(
        self,
        agent_id: str,
        experiences: List[Any],
        reflection_adjustments: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Update a policy using computed gradients and reflection adjustments.
        
        Returns a summary of what changed.
        """
        policy = self._policies.get(agent_id)
        if not policy:
            return {"error": f"No policy registered for {agent_id}"}
        
        gradient = self.compute_gradient(agent_id, experiences)
        if not gradient:
            return {"status": "no_gradient", "agent_id": agent_id}
        
        # Apply momentum
        prev_grad = self._gradients.get(agent_id, {})
        for key in gradient:
            momentum = getattr(policy, "confidence_momentum", 0.9)
            gradient[key] = momentum * prev_grad.get(key, 0.0) + (1 - momentum) * gradient[key]
        
        # Apply updates
        old_values = {
            "base_confidence": policy.base_confidence,
            "risk_tolerance": policy.risk_tolerance,
            "peer_trust_weight": policy.peer_trust_weight,
            "exploration_rate": policy.exploration_rate,
        }
        
        policy.base_confidence = max(0.1, min(1.0, policy.base_confidence + gradient.get("base_confidence", 0.0)))
        policy.risk_tolerance = max(0.1, min(1.0, policy.risk_tolerance + gradient.get("risk_tolerance", 0.0)))
        policy.peer_trust_weight = max(0.0, min(1.0, policy.peer_trust_weight + gradient.get("peer_trust_weight", 0.0)))
        policy.exploration_rate = max(0.05, min(0.5, policy.exploration_rate + gradient.get("exploration_rate", 0.0)))
        
        # Apply reflection adjustments (from Svādhyāya)
        if reflection_adjustments:
            if "confidence_delta" in reflection_adjustments:
                policy.base_confidence = max(0.1, min(1.0,
                    policy.base_confidence + reflection_adjustments["confidence_delta"]))
            if "risk_delta" in reflection_adjustments:
                policy.risk_tolerance = max(0.1, min(1.0,
                    policy.risk_tolerance + reflection_adjustments["risk_delta"]))
            if "trust_delta" in reflection_adjustments:
                policy.peer_trust_weight = max(0.0, min(1.0,
                    policy.peer_trust_weight + reflection_adjustments["trust_delta"]))
        
        # Decay exploration
        policy.exploration_rate *= policy.exploration_decay
        policy.exploration_rate = max(0.05, policy.exploration_rate)
        
        # Update tracking
        policy.update_count += 1
        policy.last_update = time.time()
        policy.reward_history.extend([e.reward for e in experiences])
        self._gradients[agent_id] = gradient
        
        return {
            "status": "updated",
            "agent_id": agent_id,
            "changes": {
                "base_confidence": policy.base_confidence - old_values["base_confidence"],
                "risk_tolerance": policy.risk_tolerance - old_values["risk_tolerance"],
                "peer_trust_weight": policy.peer_trust_weight - old_values["peer_trust_weight"],
                "exploration_rate": policy.exploration_rate - old_values["exploration_rate"],
            },
            "gradient": gradient,
            "new_values": {
                "base_confidence": policy.base_confidence,
                "risk_tolerance": policy.risk_tolerance,
                "peer_trust_weight": policy.peer_trust_weight,
                "exploration_rate": policy.exploration_rate,
            },
        }

    def get_policy_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get a summary of a policy's state."""
        policy = self._policies.get(agent_id)
        if not policy:
            return {"error": f"No policy for {agent_id}"}
        
        recent_rewards = policy.reward_history[-20:] if policy.reward_history else []
        avg_reward = sum(recent_rewards) / len(recent_rewards) if recent_rewards else 0.0
        
        return {
            "agent_id": agent_id,
            "update_count": policy.update_count,
            "avg_recent_reward": avg_reward,
            "base_confidence": policy.base_confidence,
            "risk_tolerance": policy.risk_tolerance,
            "peer_trust_weight": policy.peer_trust_weight,
            "exploration_rate": policy.exploration_rate,
            "state_multipliers": policy.state_multipliers,
        }
