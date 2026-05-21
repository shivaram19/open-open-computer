# src/perception/action_tube.py
"""
Action Tube: Spatio-Temporal Action Localization.

An action tube is a sequence of bounding boxes that localize an action
in both space and time. Unlike static detection, action tubes track the
spatio-temporal extent of activities — from "person walking" to "car turning".

Inspired by:
- ActionTubes2015: Jain et al. — spatio-temporal action localization
- ACT2018: Action detection with tubelets
- VOST-SGG: Video object segmentation tracking
- GraphThinker2026: Event-centric video understanding

Principle: An action is not a label — it is a trajectory through space-time.
To understand "running," you must follow the runner across frames, not just
detect a runner in each frame independently.

[CITATION: ActionTubes2015]
[CITATION: ACT2018]
[CITATION: GraphThinker2026]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="ACTION-TUBE",
    paper="Action Tube: Spatio-Temporal Action Localization",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Actions are spatio-temporal extents, not per-frame labels",
    confidence="CERTAIN",
)
class ActionType(Enum):
    """Categories of actions recognizable in video."""
    LOCOMOTION = "locomotion"         # walk, run, jump
    MANIPULATION = "manipulation"     # pick, place, throw, catch
    INTERACTION = "interaction"       # talk, fight, help
    STATIC = "static"                 # stand, sit, lie
    TRANSITION = "transition"         # enter, exit, approach


@cite(
    key="ACTION-TUBE",
    paper="Action Tube: Spatio-Temporal Action Localization",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Action tube captures full spatio-temporal extent of an activity",
    confidence="CERTAIN",
)
@dataclass
class ActionTube:
    """A spatio-temporal tube localizing an action in video."""
    tube_id: str
    action_class: str
    action_type: ActionType
    confidence: float
    
    # Spatio-temporal extent: frame_id -> bbox
    bbox_sequence: Dict[int, Tuple[float, float, float, float]] = field(default_factory=dict)
    
    # Actor objects participating in this action
    actor_ids: List[str] = field(default_factory=list)
    
    # Target objects (for transitive actions like "throw ball")
    target_ids: List[str] = field(default_factory=list)
    
    start_frame: int = 0
    end_frame: int = 0
    
    # Temporal dynamics
    velocity_profile: Dict[int, Tuple[float, float]] = field(default_factory=dict)
    acceleration_profile: Dict[int, Tuple[float, float]] = field(default_factory=dict)
    
    def add_frame(self, frame_id: int, bbox: Tuple[float, float, float, float]) -> None:
        """Add a bounding box at a specific frame."""
        self.bbox_sequence[frame_id] = bbox
        if self.start_frame == 0 or frame_id < self.start_frame:
            self.start_frame = frame_id
        self.end_frame = max(self.end_frame, frame_id)
    
    @property
    def duration(self) -> int:
        """Duration in frames."""
        return self.end_frame - self.start_frame + 1
    
    @property
    def is_short_action(self) -> bool:
        """Quick actions lasting few frames."""
        return self.duration <= 5
    
    @property
    def is_long_action(self) -> bool:
        """Sustained actions over many frames."""
        return self.duration >= 30
    
    def compute_velocity(self, frame_id: int) -> Optional[Tuple[float, float]]:
        """Compute velocity vector at a frame (pixels/frame)."""
        if frame_id not in self.bbox_sequence or (frame_id - 1) not in self.bbox_sequence:
            return None
        
        curr = self.bbox_sequence[frame_id]
        prev = self.bbox_sequence[frame_id - 1]
        
        curr_center = ((curr[0] + curr[2]) / 2, (curr[1] + curr[3]) / 2)
        prev_center = ((prev[0] + prev[2]) / 2, (prev[1] + prev[3]) / 2)
        
        return (curr_center[0] - prev_center[0], curr_center[1] - prev_center[1])
    
    def compute_average_velocity(self) -> Tuple[float, float]:
        """Compute average velocity across the tube."""
        velocities = []
        for frame_id in sorted(self.bbox_sequence.keys()):
            vel = self.compute_velocity(frame_id)
            if vel:
                velocities.append(vel)
        
        if not velocities:
            return (0.0, 0.0)
        
        avg_x = sum(v[0] for v in velocities) / len(velocities)
        avg_y = sum(v[1] for v in velocities) / len(velocities)
        return (avg_x, avg_y)
    
    def compute_spatial_extent(self) -> Tuple[float, float, float, float]:
        """Compute the overall spatial bounding box of the tube."""
        if not self.bbox_sequence:
            return (0.0, 0.0, 0.0, 0.0)
        
        bboxes = list(self.bbox_sequence.values())
        x1 = min(b[0] for b in bboxes)
        y1 = min(b[1] for b in bboxes)
        x2 = max(b[2] for b in bboxes)
        y2 = max(b[3] for b in bboxes)
        return (x1, y1, x2, y2)
    
    def overlaps_with(self, other: "ActionTube", iou_threshold: float = 0.3) -> bool:
        """Check if this tube overlaps with another in space-time."""
        # Check temporal overlap
        time_overlap = (
            self.start_frame <= other.end_frame and
            other.start_frame <= self.end_frame
        )
        if not time_overlap:
            return False
        
        # Check spatial overlap on common frames
        common_frames = set(self.bbox_sequence.keys()) & set(other.bbox_sequence.keys())
        if not common_frames:
            return False
        
        from perception.video_scene_graph import compute_iou
        for frame_id in common_frames:
            iou = compute_iou(self.bbox_sequence[frame_id], other.bbox_sequence[frame_id])
            if iou >= iou_threshold:
                return True
        return False


@cite(
    key="ACTION-TUBE",
    paper="Action Tube: Spatio-Temporal Action Localization",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Tube library manages multiple action tubes in a video",
    confidence="CERTAIN",
)
class ActionTubeLibrary:
    """Library of action tubes extracted from a video."""

    def __init__(self, video_id: str = ""):
        self.video_id = video_id
        self.tubes: Dict[str, ActionTube] = {}
        self._tube_counter = 0

    def _next_id(self) -> str:
        self._tube_counter += 1
        return f"tube-{self._tube_counter:04d}"

    def create_tube(self, action_class: str, action_type: ActionType,
                    confidence: float = 0.5) -> ActionTube:
        """Create a new action tube."""
        tube = ActionTube(
            tube_id=self._next_id(),
            action_class=action_class,
            action_type=action_type,
            confidence=confidence,
        )
        self.tubes[tube.tube_id] = tube
        return tube

    def get_tubes_by_type(self, action_type: ActionType) -> List[ActionTube]:
        """Get all tubes of a specific action type."""
        return [t for t in self.tubes.values() if t.action_type == action_type]

    def get_tubes_by_class(self, action_class: str) -> List[ActionTube]:
        """Get all tubes of a specific action class."""
        return [t for t in self.tubes.values() if t.action_class == action_class]

    def get_tubes_in_frame_range(self, start: int, end: int) -> List[ActionTube]:
        """Get tubes active in a frame range."""
        return [
            t for t in self.tubes.values()
            if t.start_frame <= end and t.end_frame >= start
        ]

    def find_overlapping_tubes(self, tube_id: str, iou_threshold: float = 0.3) -> List[ActionTube]:
        """Find tubes that overlap with a given tube."""
        target = self.tubes.get(tube_id)
        if not target:
            return []
        return [
            t for t in self.tubes.values()
            if t.tube_id != tube_id and t.overlaps_with(target, iou_threshold)
        ]

    def compute_action_density(self, frame_id: int) -> float:
        """Compute action density at a frame (actions per unit area)."""
        active = [t for t in self.tubes.values() if frame_id in t.bbox_sequence]
        if not active:
            return 0.0
        
        # Average number of active tubes normalized by video area (assumed 1x1)
        return len(active) / 1.0

    def summarize(self) -> Dict[str, Any]:
        """Summarize the action tube library."""
        type_counts = {}
        class_counts = {}
        for tube in self.tubes.values():
            type_counts[tube.action_type.value] = type_counts.get(tube.action_type.value, 0) + 1
            class_counts[tube.action_class] = class_counts.get(tube.action_class, 0) + 1
        
        return {
            "video_id": self.video_id,
            "total_tubes": len(self.tubes),
            "by_type": type_counts,
            "by_class": class_counts,
            "avg_duration": sum(t.duration for t in self.tubes.values()) / max(len(self.tubes), 1),
        }
