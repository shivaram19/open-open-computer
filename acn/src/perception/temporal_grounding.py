# src/perception/temporal_grounding.py
"""
Temporal Grounding: Kāla-Drṣṭi (The Vision of Time).

Grounds natural language events and queries into specific temporal
intervals in a video. Answers: "When does X happen?" and "What happens
between T1 and T2?"

Inspired by:
- StreamingVLM2025: Temporal understanding in streaming video
- GraphThinker2026: Event-centric temporal graphs
- Jamshidi2026: ST-GAT for spatio-temporal graph attention
- ActionGenome2020: Temporal action localization

Principle: Time is not a line but a graph of events. Temporal grounding
finds the node in this graph that corresponds to a query, connecting
language to the Kāla (time) structure of video.

[CITATION: StreamingVLM2025]
[CITATION: GraphThinker2026]
[CITATION: Jamshidi2026]
"""

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from shared.utils.citations import cite


@cite(
    key="TEMPORAL-GROUNDING",
    paper="Temporal Grounding for Video Event Localization",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Events must be grounded in specific temporal intervals for actionable understanding",
    confidence="CERTAIN",
)
class TemporalRelation(Enum):
    """Relations between events in time."""
    BEFORE = "before"
    AFTER = "after"
    DURING = "during"
    OVERLAPS = "overlaps"
    MEETS = "meets"
    EQUALS = "equals"


@cite(
    key="TEMPORAL-GROUNDING",
    paper="Temporal Grounding for Video Event Localization",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Grounded events have precise temporal extents and semantic labels",
    confidence="CERTAIN",
)
@dataclass
class GroundedEvent:
    """An event grounded to a specific temporal interval in video."""
    event_id: str
    event_label: str
    start_frame: int
    end_frame: int
    confidence: float
    
    # Source of grounding
    source_modality: str = "visual"  # visual, audio, text, fused
    
    # Associated objects and actions
    object_ids: List[str] = field(default_factory=list)
    action_tube_ids: List[str] = field(default_factory=list)
    
    # Semantic description
    description: str = ""
    
    # Temporal relations to other events
    temporal_relations: Dict[str, TemporalRelation] = field(default_factory=dict)


@cite(
    key="TEMPORAL-GROUNDING",
    paper="Temporal Grounding for Video Event Localization",
    venue="ACN Architecture Document",
    section="Video Perception",
    rationale="Temporal index enables efficient event retrieval by time interval",
    confidence="CERTAIN",
)
class TemporalIndex:
    """
    Index for efficient temporal event retrieval.
    
    Supports:
    - Point queries: what happens at frame F?
    - Range queries: what happens between F1 and F2?
    - Relation queries: what happens before/after event E?
    """

    def __init__(self):
        self.events: Dict[str, GroundedEvent] = {}
        self.frame_index: Dict[int, List[str]] = {}  # frame -> event_ids
        self._event_counter = 0

    def _next_id(self) -> str:
        self._event_counter += 1
        return f"event-{self._event_counter:04d}"

    def add_event(self, event: GroundedEvent) -> str:
        """Add an event to the temporal index."""
        if not event.event_id:
            event.event_id = self._next_id()
        
        self.events[event.event_id] = event
        
        # Index by frame
        for frame in range(event.start_frame, event.end_frame + 1):
            if frame not in self.frame_index:
                self.frame_index[frame] = []
            self.frame_index[frame].append(event.event_id)
        
        return event.event_id

    def query_at_frame(self, frame_id: int) -> List[GroundedEvent]:
        """Get all events active at a specific frame."""
        event_ids = self.frame_index.get(frame_id, [])
        return [self.events[eid] for eid in event_ids]

    def query_in_range(self, start_frame: int, end_frame: int) -> List[GroundedEvent]:
        """Get all events overlapping with a frame range."""
        result_ids = set()
        for frame in range(start_frame, end_frame + 1):
            result_ids.update(self.frame_index.get(frame, []))
        return [self.events[eid] for eid in result_ids]

    def query_before(self, frame_id: int) -> List[GroundedEvent]:
        """Get events that end before a frame."""
        return [
            e for e in self.events.values()
            if e.end_frame < frame_id
        ]

    def query_after(self, frame_id: int) -> List[GroundedEvent]:
        """Get events that start after a frame."""
        return [
            e for e in self.events.values()
            if e.start_frame > frame_id
        ]

    def query_by_label(self, label: str) -> List[GroundedEvent]:
        """Get events matching a label."""
        return [
            e for e in self.events.values()
            if label.lower() in e.event_label.lower()
        ]

    def find_temporal_relation(self, event_id_a: str, event_id_b: str) -> Optional[TemporalRelation]:
        """Find the temporal relation between two events."""
        event_a = self.events.get(event_id_a)
        event_b = self.events.get(event_id_b)
        if not event_a or not event_b:
            return None
        
        return compute_temporal_relation(
            (event_a.start_frame, event_a.end_frame),
            (event_b.start_frame, event_b.end_frame),
        )

    def get_event_sequence(self) -> List[GroundedEvent]:
        """Get all events sorted by start time."""
        return sorted(self.events.values(), key=lambda e: e.start_frame)

    def compute_temporal_coverage(self, start_frame: int, end_frame: int) -> float:
        """Compute what fraction of a range is covered by events."""
        covered_frames = set()
        for event in self.events.values():
            for frame in range(max(event.start_frame, start_frame),
                              min(event.end_frame, end_frame) + 1):
                covered_frames.add(frame)
        
        total_frames = end_frame - start_frame + 1
        return len(covered_frames) / total_frames if total_frames > 0 else 0.0

    def get_gaps(self, start_frame: int, end_frame: int) -> List[Tuple[int, int]]:
        """Find temporal gaps (unexplained intervals) in a range."""
        # Mark covered frames
        covered = set()
        for event in self.events.values():
            for frame in range(max(event.start_frame, start_frame),
                              min(event.end_frame, end_frame) + 1):
                covered.add(frame)
        
        # Find gaps
        gaps = []
        in_gap = False
        gap_start = 0
        for frame in range(start_frame, end_frame + 1):
            if frame not in covered:
                if not in_gap:
                    in_gap = True
                    gap_start = frame
            else:
                if in_gap:
                    gaps.append((gap_start, frame - 1))
                    in_gap = False
        
        if in_gap:
            gaps.append((gap_start, end_frame))
        
        return gaps

    def summarize(self) -> Dict[str, Any]:
        """Summarize the temporal index."""
        if not self.events:
            return {"event_count": 0, "frame_coverage": 0.0, "avg_event_duration": 0.0}
        
        all_frames = set(self.frame_index.keys())
        min_frame = min(all_frames) if all_frames else 0
        max_frame = max(all_frames) if all_frames else 0
        
        durations = [e.end_frame - e.start_frame + 1 for e in self.events.values()]
        coverage = self.compute_temporal_coverage(min_frame, max_frame)
        
        return {
            "event_count": len(self.events),
            "frame_range": (min_frame, max_frame),
            "frame_coverage": coverage,
            "avg_event_duration": sum(durations) / len(durations),
            "gaps": len(self.get_gaps(min_frame, max_frame)),
        }


def compute_temporal_relation(
    interval_a: Tuple[int, int],
    interval_b: Tuple[int, int],
) -> TemporalRelation:
    """
    Compute Allen's interval algebra relation between two intervals.
    
    Returns the relation of A to B (e.g., A BEFORE B means A ends before B starts).
    """
    a_start, a_end = interval_a
    b_start, b_end = interval_b
    
    if a_start == b_start and a_end == b_end:
        return TemporalRelation.EQUALS
    elif a_end < b_start:
        return TemporalRelation.BEFORE
    elif a_start > b_end:
        return TemporalRelation.AFTER
    elif a_start <= b_start and a_end >= b_end:
        return TemporalRelation.DURING
    elif b_start <= a_start and b_end >= a_end:
        return TemporalRelation.DURING  # A is during B
    elif a_end == b_start:
        return TemporalRelation.MEETS
    elif b_end == a_start:
        return TemporalRelation.MEETS
    else:
        return TemporalRelation.OVERLAPS
