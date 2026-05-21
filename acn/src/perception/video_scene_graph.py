# src/perception/video_scene_graph.py
"""
Temporal Video Scene Graph: Sphota (Manifestation of Form).

Represents video as a temporally evolving scene graph where:
- Nodes are objects with spatial footprints across frames
- Edges are relationships (spatial, temporal, semantic)
- Time dimension enables action understanding and causal reasoning

Inspired by:
- Krishna2017: Visual Genome — scene graphs for images
- ActionGenome2020: Temporal scene graphs for action understanding
- VOST-SGG: Video object segmentation with scene graph guidance
- GraphThinker2026: Event-centric video scene graphs

Principle: Sphota is the burst of form that reveals meaning. A scene graph
is the Sphota of a video frame — the crystallization of visual chaos into
structured understanding.

[CITATION: Krishna2017]
[CITATION: ActionGenome2020]
[CITATION: GraphThinker2026]
"""

import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="VIDEO-SCENE-GRAPH",
    paper="Temporal Video Scene Graph for Spatio-Temporal Understanding",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Scene graphs provide structured representation of visual content across time",
    confidence="CERTAIN",
)
class RelationshipType(Enum):
    """Types of relationships in a video scene graph."""
    SPATIAL = "spatial"           # left_of, right_of, above, below
    TEMPORAL = "temporal"         # before, after, during
    SEMANTIC = "semantic"         # part_of, instance_of, uses
    ACTION = "action"             # subject-verb-object relationships
    CAUSAL = "causal"             # causes, enables, prevents


@cite(
    key="VIDEO-SCENE-GRAPH",
    paper="Temporal Video Scene Graph for Spatio-Temporal Understanding",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Object nodes track identity and state across frames",
    confidence="CERTAIN",
)
@dataclass
class VideoObject:
    """An object tracked across video frames."""
    object_id: str
    class_name: str
    confidence: float
    
    # Temporal footprint: frame_id -> bounding box (x1, y1, x2, y2)
    temporal_footprint: Dict[int, Tuple[float, float, float, float]] = field(default_factory=dict)
    
    # Object state over time
    state_history: Dict[int, str] = field(default_factory=dict)  # frame_id -> state
    
    # Appearance features (e.g., embedding vector)
    appearance_features: Optional[List[float]] = None
    
    first_seen: int = 0
    last_seen: int = 0
    
    def add_detection(self, frame_id: int, bbox: Tuple[float, float, float, float],
                     state: str = "active", confidence: float = None) -> None:
        """Add a detection of this object at a specific frame."""
        self.temporal_footprint[frame_id] = bbox
        self.state_history[frame_id] = state
        if confidence is not None:
            self.confidence = confidence
        if self.first_seen == 0 or frame_id < self.first_seen:
            self.first_seen = frame_id
        self.last_seen = max(self.last_seen, frame_id)
    
    @property
    def duration(self) -> int:
        """Number of frames this object is visible."""
        return self.last_seen - self.first_seen + 1
    
    def center_at_frame(self, frame_id: int) -> Optional[Tuple[float, float]]:
        """Get center point of object at a specific frame."""
        bbox = self.temporal_footprint.get(frame_id)
        if not bbox:
            return None
        return ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)
    
    def iou_at_frame(self, frame_id: int, other_bbox: Tuple[float, float, float, float]) -> float:
        """Compute IoU with another bounding box at a specific frame."""
        bbox = self.temporal_footprint.get(frame_id)
        if not bbox:
            return 0.0
        return compute_iou(bbox, other_bbox)


@cite(
    key="VIDEO-SCENE-GRAPH",
    paper="Temporal Video Scene Graph for Spatio-Temporal Understanding",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Relationships connect objects across space and time",
    confidence="CERTAIN",
)
@dataclass
class VideoRelationship:
    """A relationship between two objects in a video scene graph."""
    rel_id: str
    subject_id: str
    predicate: str
    object_id: str
    rel_type: RelationshipType
    
    # Temporal validity: which frames this relationship holds
    valid_frames: List[int] = field(default_factory=list)
    confidence: float = 0.5
    
    # Temporal dynamics
    start_frame: int = 0
    end_frame: int = 0


@cite(
    key="VIDEO-SCENE-GRAPH",
    paper="Temporal Video Scene Graph for Spatio-Temporal Understanding",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Scene graph evolves over time with objects and relationships",
    confidence="CERTAIN",
)
class TemporalSceneGraph:
    """
    A scene graph that evolves over video frames.
    
    Each frame has a snapshot of objects and relationships. Objects
    persist across frames with temporal footprints. Relationships
    can be transient or persistent.
    """

    def __init__(self, video_id: str = ""):
        self.video_id = video_id
        self.objects: Dict[str, VideoObject] = {}
        self.relationships: Dict[str, VideoRelationship] = {}
        self.frame_graphs: Dict[int, Dict[str, Any]] = {}  # frame_id -> graph snapshot
        self._obj_counter = 0
        self._rel_counter = 0

    def _next_obj_id(self) -> str:
        self._obj_counter += 1
        return f"obj-{self._obj_counter:04d}"

    def _next_rel_id(self) -> str:
        self._rel_counter += 1
        return f"rel-{self._rel_counter:04d}"

    def add_object(self, class_name: str, confidence: float = 0.5,
                   obj_id: Optional[str] = None) -> VideoObject:
        """Add a new object to the scene graph."""
        oid = obj_id or self._next_obj_id()
        obj = VideoObject(object_id=oid, class_name=class_name, confidence=confidence)
        self.objects[oid] = obj
        return obj

    def add_relationship(self, subject_id: str, predicate: str, object_id: str,
                         rel_type: RelationshipType = RelationshipType.SPATIAL,
                         valid_frames: Optional[List[int]] = None,
                         confidence: float = 0.5) -> Optional[VideoRelationship]:
        """Add a relationship between two objects."""
        if subject_id not in self.objects or object_id not in self.objects:
            return None
        
        rel = VideoRelationship(
            rel_id=self._next_rel_id(),
            subject_id=subject_id,
            predicate=predicate,
            object_id=object_id,
            rel_type=rel_type,
            valid_frames=valid_frames or [],
            confidence=confidence,
        )
        if valid_frames:
            rel.start_frame = min(valid_frames)
            rel.end_frame = max(valid_frames)
        
        self.relationships[rel.rel_id] = rel
        return rel

    def get_objects_at_frame(self, frame_id: int) -> List[VideoObject]:
        """Get all objects visible at a specific frame."""
        return [
            obj for obj in self.objects.values()
            if frame_id in obj.temporal_footprint
        ]

    def get_relationships_at_frame(self, frame_id: int) -> List[VideoRelationship]:
        """Get all relationships valid at a specific frame."""
        return [
            rel for rel in self.relationships.values()
            if frame_id in rel.valid_frames
        ]

    def get_object_trajectory(self, object_id: str) -> List[Tuple[int, Tuple[float, float, float, float]]]:
        """Get the full spatio-temporal trajectory of an object."""
        obj = self.objects.get(object_id)
        if not obj:
            return []
        return sorted(obj.temporal_footprint.items())

    def compute_temporal_iou(self, obj_id_a: str, obj_id_b: str) -> float:
        """Compute temporal IoU — overlap in frames where both objects exist."""
        obj_a = self.objects.get(obj_id_a)
        obj_b = self.objects.get(obj_id_b)
        if not obj_a or not obj_b:
            return 0.0
        
        frames_a = set(obj_a.temporal_footprint.keys())
        frames_b = set(obj_b.temporal_footprint.keys())
        
        intersection = len(frames_a & frames_b)
        union = len(frames_a | frames_b)
        
        return intersection / union if union > 0 else 0.0

    def get_cooccurring_objects(self, frame_id: int) -> List[Tuple[str, str]]:
        """Get all pairs of objects that co-occur at a frame."""
        objs = self.get_objects_at_frame(frame_id)
        pairs = []
        for i, a in enumerate(objs):
            for b in objs[i+1:]:
                pairs.append((a.object_id, b.object_id))
        return pairs

    def summarize(self) -> Dict[str, Any]:
        """Generate a summary of the temporal scene graph."""
        all_frames = set()
        for obj in self.objects.values():
            all_frames.update(obj.temporal_footprint.keys())
        
        rel_type_counts = {}
        for rel in self.relationships.values():
            rel_type_counts[rel.rel_type.value] = rel_type_counts.get(rel.rel_type.value, 0) + 1
        
        return {
            "video_id": self.video_id,
            "object_count": len(self.objects),
            "relationship_count": len(self.relationships),
            "frame_count": len(all_frames),
            "object_classes": list(set(obj.class_name for obj in self.objects.values())),
            "relationship_types": rel_type_counts,
        }


def compute_iou(box_a: Tuple[float, float, float, float],
                box_b: Tuple[float, float, float, float]) -> float:
    """Compute Intersection over Union of two bounding boxes."""
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])
    
    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    box_b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    
    union_area = box_a_area + box_b_area - inter_area
    return inter_area / union_area if union_area > 0 else 0.0
