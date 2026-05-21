# src/perception/cross_modal_fusion.py
"""
Cross-Modal Fusion: Dhvani (Resonance Across Senses).

Fuses information from multiple modalities (visual, audio, text) into a
unified representation. Uses attention gating to dynamically weight modalities
based on their reliability for the current context.

Inspired by:
- MAViD2025: Multi-modal audio-visual understanding
- MiniCPM-o2026: Omni-modal perception
- Gemini2.5Pro2025: Native multi-modal reasoning
- Ouyang2022: RLHF for aligning multi-modal outputs

Principle: Dhvani is the resonance that carries meaning beyond the literal.
Cross-modal fusion is the Dhvani of perception — the meaning that emerges
when sight and sound converge into understanding.

[CITATION: MAViD2025]
[CITATION: MiniCPM-o2026]
[CITATION: Gemini2.5Pro2025]
"""

import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="CROSS-MODAL",
    paper="Cross-Modal Fusion with Attention Gating",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Multi-modal perception requires dynamic fusion weighted by modality reliability",
    confidence="CERTAIN",
)
class ModalityType(Enum):
    """Types of sensory modalities."""
    VISUAL = "visual"
    AUDIO = "audio"
    TEXT = "text"
    MOTION = "motion"
    DEPTH = "depth"


@cite(
    key="CROSS-MODAL",
    paper="Cross-Modal Fusion with Attention Gating",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Modality features carry confidence and temporal anchors",
    confidence="CERTAIN",
)
@dataclass
class ModalityFeature:
    """A feature vector from a specific modality at a point in time."""
    modality: ModalityType
    feature_vector: List[float]
    confidence: float
    timestamp: float
    frame_id: Optional[int] = None
    source_id: str = ""  # e.g., which video, audio stream


@cite(
    key="CROSS-MODAL",
    paper="Cross-Modal Fusion with Attention Gating",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Attention weights determine how much each modality contributes",
    confidence="CERTAIN",
)
@dataclass
class FusionContext:
    """Context for fusion: what task, what modalities available, their reliabilities."""
    task_hint: str = ""  # e.g., "action_recognition", "emotion_detection"
    available_modalities: List[ModalityType] = field(default_factory=list)
    modality_reliability: Dict[ModalityType, float] = field(default_factory=dict)
    temporal_window: int = 5  # frames to fuse


@cite(
    key="CROSS-MODAL",
    paper="Cross-Modal Fusion with Attention Gating",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Cross-modal attention computes alignment between modalities",
    confidence="CERTAIN",
)
class CrossModalAttention:
    """
    Attention mechanism for cross-modal fusion.
    
    Computes attention weights between modalities based on:
    1. Feature similarity (cosine similarity between modalities)
    2. Confidence gating (reliable modalities get higher weight)
    3. Task relevance (certain tasks favor certain modalities)
    """

    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature

    def compute_similarity(self, feat_a: List[float], feat_b: List[float]) -> float:
        """Compute cosine similarity between two feature vectors."""
        if len(feat_a) != len(feat_b) or len(feat_a) == 0:
            return 0.0
        
        dot = sum(a * b for a, b in zip(feat_a, feat_b))
        norm_a = math.sqrt(sum(a * a for a in feat_a))
        norm_b = math.sqrt(sum(b * b for b in feat_b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)

    def compute_attention_weights(
        self,
        features: Dict[ModalityType, ModalityFeature],
        context: FusionContext,
    ) -> Dict[ModalityType, float]:
        """
        Compute attention weights for each modality.
        
        Returns a dictionary mapping modality to weight (sums to 1.0).
        """
        if not features:
            return {}
        
        # Base weights from confidence and reliability
        raw_weights = {}
        for modality, feature in features.items():
            reliability = context.modality_reliability.get(modality, 0.5)
            raw_weights[modality] = feature.confidence * reliability
        
        # Cross-modal similarity boost: modalities that agree get boosted
        modalities = list(features.keys())
        for i, mod_a in enumerate(modalities):
            for mod_b in modalities[i+1:]:
                sim = self.compute_similarity(
                    features[mod_a].feature_vector,
                    features[mod_b].feature_vector,
                )
                # Boost both if they agree (positive similarity)
                if sim > 0:
                    boost = sim * 0.2
                    raw_weights[mod_a] += boost
                    raw_weights[mod_b] += boost
        
        # Task-based modulation
        task_weights = self._task_modulation(context.task_hint)
        for modality in raw_weights:
            raw_weights[modality] *= task_weights.get(modality, 1.0)
        
        # Softmax normalization
        total = sum(raw_weights.values())
        if total == 0:
            n = len(raw_weights)
            return {m: 1.0 / n for m in raw_weights}
        
        return {m: w / total for m, w in raw_weights.items()}

    def _task_modulation(self, task_hint: str) -> Dict[ModalityType, float]:
        """Modality preference based on task type."""
        task_prefs = {
            "action_recognition": {
                ModalityType.VISUAL: 1.2,
                ModalityType.MOTION: 1.5,
                ModalityType.AUDIO: 0.8,
                ModalityType.TEXT: 0.5,
            },
            "emotion_detection": {
                ModalityType.VISUAL: 1.0,
                ModalityType.AUDIO: 1.3,
                ModalityType.TEXT: 1.1,
                ModalityType.MOTION: 0.7,
            },
            "object_tracking": {
                ModalityType.VISUAL: 1.5,
                ModalityType.MOTION: 1.2,
                ModalityType.DEPTH: 1.1,
                ModalityType.AUDIO: 0.3,
            },
            "scene_understanding": {
                ModalityType.VISUAL: 1.3,
                ModalityType.TEXT: 1.0,
                ModalityType.DEPTH: 1.1,
                ModalityType.AUDIO: 0.6,
            },
        }
        return task_prefs.get(task_hint, {m: 1.0 for m in ModalityType})


@cite(
    key="CROSS-MODAL",
    paper="Cross-Modal Fusion with Attention Gating",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Fused representation combines modalities with learned weights",
    confidence="CERTAIN",
)
class CrossModalFusion:
    """
    Fuses multi-modal features into a unified representation.
    
    Uses CrossModalAttention for dynamic weighting, then computes
    a weighted sum of normalized features.
    """

    def __init__(self):
        self.attention = CrossModalAttention()
        self.fusion_history: List[Dict[str, Any]] = []

    def fuse(
        self,
        features: Dict[ModalityType, ModalityFeature],
        context: FusionContext,
    ) -> Dict[str, Any]:
        """
        Fuse features from multiple modalities.
        
        Returns:
            {
                "fused_vector": List[float],
                "attention_weights": Dict[ModalityType, float],
                "dominant_modality": ModalityType,
                "confidence": float,
            }
        """
        if not features:
            return {
                "fused_vector": [],
                "attention_weights": {},
                "dominant_modality": None,
                "confidence": 0.0,
            }
        
        # Compute attention weights
        weights = self.attention.compute_attention_weights(features, context)
        
        # Normalize and weight features
        weighted_vectors = []
        for modality, feature in features.items():
            weight = weights.get(modality, 0.0)
            # Normalize feature vector
            norm = math.sqrt(sum(v * v for v in feature.feature_vector))
            if norm > 0:
                normalized = [v / norm for v in feature.feature_vector]
            else:
                normalized = feature.feature_vector
            weighted = [v * weight for v in normalized]
            weighted_vectors.append(weighted)
        
        # Element-wise sum (assuming same dimensionality)
        if weighted_vectors:
            fused = [sum(v[i] for v in weighted_vectors if i < len(v))
                     for i in range(max(len(v) for v in weighted_vectors))]
        else:
            fused = []
        
        # Dominant modality
        dominant = max(weights, key=weights.get) if weights else None
        
        # Overall confidence
        avg_confidence = sum(f.confidence * weights.get(m, 0.0)
                            for m, f in features.items())
        
        result = {
            "fused_vector": fused,
            "attention_weights": {m.value: w for m, w in weights.items()},
            "dominant_modality": dominant.value if dominant else None,
            "confidence": avg_confidence,
        }
        
        self.fusion_history.append({
            "timestamp": time.time(),
            "context": context,
            "weights": weights,
            "result_confidence": avg_confidence,
        })
        
        return result

    def detect_modality_conflict(
        self,
        features: Dict[ModalityType, ModalityFeature],
        threshold: float = -0.3,
    ) -> List[Tuple[ModalityType, ModalityType, float]]:
        """
        Detect conflicts between modalities (strong negative similarity).
        
        Returns list of (modality_a, modality_b, similarity) tuples.
        """
        conflicts = []
        modalities = list(features.keys())
        for i, mod_a in enumerate(modalities):
            for mod_b in modalities[i+1:]:
                sim = self.attention.compute_similarity(
                    features[mod_a].feature_vector,
                    features[mod_b].feature_vector,
                )
                if sim < threshold:
                    conflicts.append((mod_a, mod_b, sim))
        return conflicts

    def get_fusion_history(self) -> List[Dict[str, Any]]:
        """Get history of fusion operations."""
        return self.fusion_history
