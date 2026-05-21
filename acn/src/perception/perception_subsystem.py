"""
PerceptionSubsystem — encapsulates P6 perception substrates.

Extracted from ConsciousAgent to enforce SRP and enable DI.
Agents that don't process video can be constructed without this subsystem.
"""

import time
from typing import Dict, List, Optional, Any

from perception.video_scene_graph import TemporalSceneGraph, RelationshipType
from perception.action_tube import ActionTubeLibrary
from perception.cross_modal_fusion import CrossModalFusion, ModalityFeature, FusionContext, ModalityType
from perception.temporal_grounding import TemporalIndex, GroundedEvent


class PerceptionSubsystem:
    """Encapsulates multi-modal perception for a conscious agent."""

    def __init__(
        self,
        video_id: str = "",
    ):
        self.video_id = video_id
        self.scene_graph: Optional[TemporalSceneGraph] = None
        self.action_tube_library: Optional[ActionTubeLibrary] = None
        self.cross_modal_fusion = CrossModalFusion()
        self.temporal_index: Optional[TemporalIndex] = None
        self.perception_memory: List[Dict[str, Any]] = []

    def initialize(self, video_id: str = "") -> None:
        """Initialize perception substrates for video understanding."""
        self.scene_graph = TemporalSceneGraph(video_id=video_id)
        self.action_tube_library = ActionTubeLibrary(video_id=video_id)
        self.temporal_index = TemporalIndex()

    def perceive_frame(
        self,
        frame_id: int,
        detections: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Process a video frame: build scene graph, index events."""
        if self.scene_graph is None:
            self.initialize()

        added_objects = []
        for det in detections:
            obj = self.scene_graph.add_object(
                class_name=det["class_name"],
                confidence=det.get("confidence", 0.5),
            )
            obj.add_detection(
                frame_id=frame_id,
                bbox=det["bbox"],
                confidence=det.get("confidence", 0.5),
            )
            added_objects.append(obj.object_id)

        # Infer spatial relationships between co-occurring objects
        objs = self.scene_graph.get_objects_at_frame(frame_id)
        for i, a in enumerate(objs):
            for b in objs[i + 1:]:
                rel_type = self._infer_spatial_relationship(a, b, frame_id)
                if rel_type:
                    self.scene_graph.add_relationship(
                        subject_id=a.object_id,
                        predicate=rel_type,
                        object_id=b.object_id,
                        rel_type=RelationshipType.SPATIAL,
                        valid_frames=[frame_id],
                        confidence=0.6,
                    )

        self.perception_memory.append({
            "frame_id": frame_id,
            "objects": added_objects,
            "timestamp": time.time(),
        })

        return {
            "frame_id": frame_id,
            "objects_detected": len(added_objects),
            "object_ids": added_objects,
        }

    def _infer_spatial_relationship(self, obj_a, obj_b, frame_id: int) -> Optional[str]:
        """Infer spatial relationship between two objects at a frame."""
        center_a = obj_a.center_at_frame(frame_id)
        center_b = obj_b.center_at_frame(frame_id)
        if not center_a or not center_b:
            return None
        dx = center_a[0] - center_b[0]
        dy = center_a[1] - center_b[1]
        if abs(dx) > abs(dy):
            return "left_of" if dx < 0 else "right_of"
        else:
            return "above" if dy < 0 else "below"

    def fuse_modalities(
        self,
        features: Dict[str, Any],
        task_hint: str = "scene_understanding",
    ) -> Dict[str, Any]:
        """Fuse multi-modal features into unified representation."""
        modality_features = {}
        for mod_name, feat in features.items():
            mod_type = getattr(ModalityType, mod_name.upper(), ModalityType.VISUAL)
            modality_features[mod_type] = ModalityFeature(
                modality=mod_type,
                feature_vector=feat.get("vector", []),
                confidence=feat.get("confidence", 0.5),
                timestamp=time.time(),
            )
        context = FusionContext(
            task_hint=task_hint,
            available_modalities=list(modality_features.keys()),
        )
        return self.cross_modal_fusion.fuse(modality_features, context)

    def ground_event(
        self,
        event_label: str,
        start_frame: int,
        end_frame: int,
        confidence: float = 0.5,
    ) -> str:
        """Ground a semantic event to a temporal interval in the video."""
        if self.temporal_index is None:
            self.initialize()
        event = GroundedEvent(
            event_id="",
            event_label=event_label,
            start_frame=start_frame,
            end_frame=end_frame,
            confidence=confidence,
        )
        event_id = self.temporal_index.add_event(event)
        return event_id

    def get_perception_report(self, agent_id: str = "") -> Dict[str, Any]:
        """Generate a report of the perceptual state."""
        report = {
            "agent_id": agent_id,
            "perception_initialized": self.scene_graph is not None,
            "frames_processed": len(self.perception_memory),
        }
        if self.scene_graph:
            report["scene_graph"] = self.scene_graph.summarize()
        if self.action_tube_library:
            report["action_tubes"] = self.action_tube_library.summarize()
        if self.temporal_index:
            report["temporal_events"] = self.temporal_index.summarize()
        return report
