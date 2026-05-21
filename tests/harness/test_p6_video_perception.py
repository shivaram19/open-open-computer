"""
Tests for P6: Video & Cross-Modal Perception (Sphota + Dhvani).

Covers:
- TemporalSceneGraph: objects, relationships, temporal queries, IoU
- ActionTube: bbox sequences, velocity, overlap detection
- CrossModalFusion: attention weights, fusion, conflict detection
- TemporalIndex: event grounding, temporal queries, gaps, coverage
- Integration: ConsciousAgent perception methods

Citations:
- Krishna2017: Visual Genome scene graphs
- ActionGenome2020: Temporal scene graphs for action understanding
- GraphThinker2026: Event-centric video scene graphs
- MAViD2025: Multi-modal audio-visual understanding
- StreamingVLM2025: Temporal understanding in streaming video
- Jamshidi2026: ST-GAT for spatio-temporal graphs
"""



import pytest

from perception.video_scene_graph import (
    TemporalSceneGraph, VideoObject, VideoRelationship,
    RelationshipType, compute_iou,
)
from perception.action_tube import (
    ActionTube, ActionTubeLibrary, ActionType,
)
from perception.cross_modal_fusion import (
    CrossModalFusion, CrossModalAttention,
    ModalityFeature, FusionContext, ModalityType,
)
from perception.temporal_grounding import (
    TemporalIndex, GroundedEvent, TemporalRelation, compute_temporal_relation,
)
from agents.conscious_agent import ConsciousAgent
from conftest import default_agent_kwargs


# ── Temporal Scene Graph Tests ────────────────────────────────────

class TestTemporalSceneGraph:
    """Tests for TemporalSceneGraph."""

    def test_add_object(self):
        sg = TemporalSceneGraph("vid-1")
        obj = sg.add_object("person", confidence=0.9)
        assert obj.object_id in sg.objects
        assert obj.class_name == "person"

    def test_add_relationship(self):
        sg = TemporalSceneGraph("vid-1")
        obj_a = sg.add_object("person")
        obj_b = sg.add_object("chair")
        rel = sg.add_relationship(obj_a.object_id, "sitting_on", obj_b.object_id,
                                  RelationshipType.ACTION, valid_frames=[1, 2, 3])
        assert rel is not None
        assert rel.rel_id in sg.relationships
        assert rel.start_frame == 1
        assert rel.end_frame == 3

    def test_add_relationship_invalid_object(self):
        sg = TemporalSceneGraph("vid-1")
        rel = sg.add_relationship("nonexistent", "on", "also_nonexistent")
        assert rel is None

    def test_get_objects_at_frame(self):
        sg = TemporalSceneGraph("vid-1")
        obj = sg.add_object("person")
        obj.add_detection(5, (10, 10, 50, 50))
        obj.add_detection(6, (12, 12, 52, 52))
        objs = sg.get_objects_at_frame(5)
        assert len(objs) == 1
        assert objs[0].object_id == obj.object_id

    def test_get_relationships_at_frame(self):
        sg = TemporalSceneGraph("vid-1")
        obj_a = sg.add_object("person")
        obj_b = sg.add_object("chair")
        sg.add_relationship(obj_a.object_id, "sitting_on", obj_b.object_id,
                           valid_frames=[5, 6])
        rels = sg.get_relationships_at_frame(5)
        assert len(rels) == 1
        assert rels[0].predicate == "sitting_on"

    def test_get_object_trajectory(self):
        sg = TemporalSceneGraph("vid-1")
        obj = sg.add_object("person")
        obj.add_detection(1, (10, 10, 20, 20))
        obj.add_detection(3, (15, 15, 25, 25))
        traj = sg.get_object_trajectory(obj.object_id)
        assert len(traj) == 2
        assert traj[0][0] == 1
        assert traj[1][0] == 3

    def test_compute_temporal_iou(self):
        sg = TemporalSceneGraph("vid-1")
        obj_a = sg.add_object("person")
        obj_a.add_detection(1, (0, 0, 10, 10))
        obj_a.add_detection(2, (0, 0, 10, 10))
        obj_a.add_detection(3, (0, 0, 10, 10))
        
        obj_b = sg.add_object("dog")
        obj_b.add_detection(2, (0, 0, 10, 10))
        obj_b.add_detection(3, (0, 0, 10, 10))
        obj_b.add_detection(4, (0, 0, 10, 10))
        
        tiou = sg.compute_temporal_iou(obj_a.object_id, obj_b.object_id)
        # Intersection = {2, 3}, Union = {1, 2, 3, 4} → 2/4 = 0.5
        assert tiou == 0.5

    def test_get_cooccurring_objects(self):
        sg = TemporalSceneGraph("vid-1")
        obj_a = sg.add_object("person")
        obj_a.add_detection(1, (0, 0, 10, 10))
        obj_b = sg.add_object("dog")
        obj_b.add_detection(1, (20, 20, 30, 30))
        pairs = sg.get_cooccurring_objects(1)
        assert len(pairs) == 1
        assert pairs[0] == (obj_a.object_id, obj_b.object_id)

    def test_summarize(self):
        sg = TemporalSceneGraph("vid-1")
        sg.add_object("person")
        sg.add_object("chair")
        summary = sg.summarize()
        assert summary["object_count"] == 2
        assert "person" in summary["object_classes"]


# ── VideoObject Tests ──────────────────────────────────────────────

class TestVideoObject:
    """Tests for VideoObject dataclass."""

    def test_add_detection_updates_duration(self):
        obj = VideoObject("o1", "person", 0.9)
        obj.add_detection(1, (0, 0, 10, 10))
        obj.add_detection(5, (2, 2, 12, 12))
        assert obj.first_seen == 1
        assert obj.last_seen == 5
        assert obj.duration == 5

    def test_center_at_frame(self):
        obj = VideoObject("o1", "person", 0.9)
        obj.add_detection(1, (0, 0, 10, 20))
        center = obj.center_at_frame(1)
        assert center == (5.0, 10.0)

    def test_center_at_missing_frame(self):
        obj = VideoObject("o1", "person", 0.9)
        assert obj.center_at_frame(99) is None

    def test_iou_at_frame(self):
        obj = VideoObject("o1", "person", 0.9)
        obj.add_detection(1, (0, 0, 10, 10))
        iou = obj.iou_at_frame(1, (5, 5, 15, 15))
        # Intersection = 5x5 = 25, Union = 100+100-25 = 175
        assert abs(iou - 25/175) < 0.001


# ── IoU Tests ──────────────────────────────────────────────────────

class TestComputeIoU:
    """Tests for compute_iou utility."""

    def test_perfect_overlap(self):
        assert compute_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0

    def test_no_overlap(self):
        assert compute_iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0

    def test_partial_overlap(self):
        iou = compute_iou((0, 0, 10, 10), (5, 5, 15, 15))
        assert 0.0 < iou < 1.0

    def test_zero_area(self):
        assert compute_iou((0, 0, 0, 10), (0, 0, 10, 10)) == 0.0


# ── Action Tube Tests ──────────────────────────────────────────────

class TestActionTube:
    """Tests for ActionTube."""

    def test_add_frame(self):
        tube = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube.add_frame(1, (10, 10, 50, 100))
        tube.add_frame(2, (12, 10, 52, 100))
        assert len(tube.bbox_sequence) == 2
        assert tube.start_frame == 1
        assert tube.end_frame == 2

    def test_duration(self):
        tube = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube.add_frame(1, (0, 0, 10, 10))
        tube.add_frame(5, (0, 0, 10, 10))
        assert tube.duration == 5

    def test_is_short_action(self):
        tube = ActionTube("t1", "jump", ActionType.LOCOMOTION, 0.8)
        for i in range(3):
            tube.add_frame(i, (0, 0, 10, 10))
        assert tube.is_short_action is True
        assert tube.is_long_action is False

    def test_compute_velocity(self):
        tube = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube.add_frame(1, (0, 0, 10, 10))   # center = (5, 5)
        tube.add_frame(2, (5, 0, 15, 10))   # center = (10, 5)
        vel = tube.compute_velocity(2)
        assert vel == (5.0, 0.0)

    def test_compute_velocity_missing_prev(self):
        tube = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube.add_frame(5, (0, 0, 10, 10))
        assert tube.compute_velocity(5) is None

    def test_compute_average_velocity(self):
        tube = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube.add_frame(1, (0, 0, 10, 10))
        tube.add_frame(2, (10, 0, 20, 10))
        tube.add_frame(3, (20, 0, 30, 10))
        avg_vel = tube.compute_average_velocity()
        assert avg_vel[0] == 10.0
        assert avg_vel[1] == 0.0

    def test_compute_spatial_extent(self):
        tube = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube.add_frame(1, (0, 0, 10, 10))
        tube.add_frame(2, (20, 20, 30, 30))
        extent = tube.compute_spatial_extent()
        assert extent == (0, 0, 30, 30)

    def test_overlaps_with(self):
        tube_a = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube_a.add_frame(1, (0, 0, 10, 10))
        tube_a.add_frame(2, (0, 0, 10, 10))
        
        tube_b = ActionTube("t2", "running", ActionType.LOCOMOTION, 0.8)
        tube_b.add_frame(2, (5, 5, 15, 15))
        tube_b.add_frame(3, (5, 5, 15, 15))
        
        assert tube_a.overlaps_with(tube_b, iou_threshold=0.1) is True

    def test_no_overlap_different_time(self):
        tube_a = ActionTube("t1", "walking", ActionType.LOCOMOTION, 0.8)
        tube_a.add_frame(1, (0, 0, 10, 10))
        
        tube_b = ActionTube("t2", "running", ActionType.LOCOMOTION, 0.8)
        tube_b.add_frame(5, (0, 0, 10, 10))
        
        assert tube_a.overlaps_with(tube_b) is False


# ── ActionTubeLibrary Tests ────────────────────────────────────────

class TestActionTubeLibrary:
    """Tests for ActionTubeLibrary."""

    def test_create_tube(self):
        lib = ActionTubeLibrary("vid-1")
        tube = lib.create_tube("walking", ActionType.LOCOMOTION, 0.8)
        assert tube.tube_id in lib.tubes

    def test_get_tubes_by_type(self):
        lib = ActionTubeLibrary("vid-1")
        lib.create_tube("walking", ActionType.LOCOMOTION)
        lib.create_tube("picking", ActionType.MANIPULATION)
        loco = lib.get_tubes_by_type(ActionType.LOCOMOTION)
        assert len(loco) == 1
        assert loco[0].action_class == "walking"

    def test_get_tubes_by_class(self):
        lib = ActionTubeLibrary("vid-1")
        lib.create_tube("walking", ActionType.LOCOMOTION)
        lib.create_tube("walking", ActionType.LOCOMOTION)
        tubes = lib.get_tubes_by_class("walking")
        assert len(tubes) == 2

    def test_get_tubes_in_frame_range(self):
        lib = ActionTubeLibrary("vid-1")
        tube = lib.create_tube("walking", ActionType.LOCOMOTION)
        tube.add_frame(5, (0, 0, 10, 10))
        tube.add_frame(6, (0, 0, 10, 10))
        active = lib.get_tubes_in_frame_range(4, 7)
        assert len(active) == 1

    def test_find_overlapping_tubes(self):
        lib = ActionTubeLibrary("vid-1")
        t1 = lib.create_tube("walking", ActionType.LOCOMOTION)
        t1.add_frame(1, (0, 0, 10, 10))
        t1.add_frame(2, (0, 0, 10, 10))
        
        t2 = lib.create_tube("running", ActionType.LOCOMOTION)
        t2.add_frame(2, (5, 5, 15, 15))
        t2.add_frame(3, (5, 5, 15, 15))
        
        overlaps = lib.find_overlapping_tubes(t1.tube_id, iou_threshold=0.1)
        assert len(overlaps) == 1

    def test_compute_action_density(self):
        lib = ActionTubeLibrary("vid-1")
        t1 = lib.create_tube("walking", ActionType.LOCOMOTION)
        t1.add_frame(1, (0, 0, 10, 10))
        density = lib.compute_action_density(1)
        assert density == 1.0

    def test_summarize(self):
        lib = ActionTubeLibrary("vid-1")
        lib.create_tube("walking", ActionType.LOCOMOTION)
        lib.create_tube("picking", ActionType.MANIPULATION)
        summary = lib.summarize()
        assert summary["total_tubes"] == 2
        assert "locomotion" in summary["by_type"]


# ── Cross-Modal Attention Tests ────────────────────────────────────

class TestCrossModalAttention:
    """Tests for CrossModalAttention."""

    def test_compute_similarity_identical(self):
        attn = CrossModalAttention()
        sim = attn.compute_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        assert abs(sim - 1.0) < 0.001

    def test_compute_similarity_orthogonal(self):
        attn = CrossModalAttention()
        sim = attn.compute_similarity([1.0, 0.0], [0.0, 1.0])
        assert abs(sim - 0.0) < 0.001

    def test_compute_similarity_opposite(self):
        attn = CrossModalAttention()
        sim = attn.compute_similarity([1.0, 0.0], [-1.0, 0.0])
        assert abs(sim - (-1.0)) < 0.001

    def test_compute_attention_weights_uniform(self):
        attn = CrossModalAttention()
        features = {
            ModalityType.VISUAL: ModalityFeature(ModalityType.VISUAL, [1.0, 0.0], 0.5, 0.0),
            ModalityType.AUDIO: ModalityFeature(ModalityType.AUDIO, [0.0, 1.0], 0.5, 0.0),
        }
        context = FusionContext()
        weights = attn.compute_attention_weights(features, context)
        assert abs(sum(weights.values()) - 1.0) < 0.001
        assert len(weights) == 2

    def test_task_modulation_action_recognition(self):
        attn = CrossModalAttention()
        prefs = attn._task_modulation("action_recognition")
        assert prefs[ModalityType.MOTION] > prefs[ModalityType.TEXT]

    def test_task_modulation_emotion_detection(self):
        attn = CrossModalAttention()
        prefs = attn._task_modulation("emotion_detection")
        assert prefs[ModalityType.AUDIO] > prefs[ModalityType.MOTION]


# ── CrossModalFusion Tests ─────────────────────────────────────────

class TestCrossModalFusion:
    """Tests for CrossModalFusion."""

    def test_fuse_basic(self):
        fusion = CrossModalFusion()
        features = {
            ModalityType.VISUAL: ModalityFeature(ModalityType.VISUAL, [1.0, 0.0, 0.0], 0.8, 0.0),
            ModalityType.AUDIO: ModalityFeature(ModalityType.AUDIO, [0.5, 0.5, 0.0], 0.6, 0.0),
        }
        context = FusionContext(task_hint="scene_understanding")
        result = fusion.fuse(features, context)
        assert "fused_vector" in result
        assert "attention_weights" in result
        assert result["confidence"] > 0.0

    def test_fuse_empty(self):
        fusion = CrossModalFusion()
        result = fusion.fuse({}, FusionContext())
        assert result["fused_vector"] == []
        assert result["confidence"] == 0.0

    def test_fuse_single_modality(self):
        fusion = CrossModalFusion()
        features = {
            ModalityType.VISUAL: ModalityFeature(ModalityType.VISUAL, [1.0, 0.0], 0.9, 0.0),
        }
        result = fusion.fuse(features, FusionContext())
        assert result["dominant_modality"] == "visual"
        assert abs(result["attention_weights"]["visual"] - 1.0) < 0.001

    def test_detect_modality_conflict(self):
        fusion = CrossModalFusion()
        features = {
            ModalityType.VISUAL: ModalityFeature(ModalityType.VISUAL, [1.0, 0.0], 0.8, 0.0),
            ModalityType.AUDIO: ModalityFeature(ModalityType.AUDIO, [-1.0, 0.0], 0.8, 0.0),
        }
        conflicts = fusion.detect_modality_conflict(features, threshold=-0.5)
        assert len(conflicts) == 1
        assert conflicts[0][2] < -0.5

    def test_no_conflict_similar_modalities(self):
        fusion = CrossModalFusion()
        features = {
            ModalityType.VISUAL: ModalityFeature(ModalityType.VISUAL, [1.0, 0.0], 0.8, 0.0),
            ModalityType.AUDIO: ModalityFeature(ModalityType.AUDIO, [0.9, 0.1], 0.8, 0.0),
        }
        conflicts = fusion.detect_modality_conflict(features)
        assert len(conflicts) == 0

    def test_fusion_history(self):
        fusion = CrossModalFusion()
        features = {
            ModalityType.VISUAL: ModalityFeature(ModalityType.VISUAL, [1.0], 0.8, 0.0),
        }
        fusion.fuse(features, FusionContext())
        assert len(fusion.get_fusion_history()) == 1


# ── Temporal Index Tests ───────────────────────────────────────────

class TestTemporalIndex:
    """Tests for TemporalIndex."""

    def test_add_event(self):
        idx = TemporalIndex()
        event = GroundedEvent("", "person_walking", 10, 30, 0.8)
        eid = idx.add_event(event)
        assert eid in idx.events
        assert event.event_id == eid

    def test_query_at_frame(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "walking", 10, 20, 0.8))
        idx.add_event(GroundedEvent("", "running", 15, 25, 0.7))
        events = idx.query_at_frame(15)
        assert len(events) == 2

    def test_query_in_range(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "walking", 5, 10, 0.8))
        idx.add_event(GroundedEvent("", "running", 15, 20, 0.7))
        idx.add_event(GroundedEvent("", "jumping", 8, 18, 0.9))
        events = idx.query_in_range(7, 12)
        assert len(events) == 2  # walking and jumping

    def test_query_before(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "walking", 5, 10, 0.8))
        idx.add_event(GroundedEvent("", "running", 15, 20, 0.7))
        before = idx.query_before(12)
        assert len(before) == 1
        assert before[0].event_label == "walking"

    def test_query_after(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "walking", 5, 10, 0.8))
        idx.add_event(GroundedEvent("", "running", 15, 20, 0.7))
        after = idx.query_after(12)
        assert len(after) == 1
        assert after[0].event_label == "running"

    def test_query_by_label(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "person_walking", 1, 5, 0.8))
        idx.add_event(GroundedEvent("", "dog_running", 3, 8, 0.7))
        matches = idx.query_by_label("walking")
        assert len(matches) == 1
        assert matches[0].event_label == "person_walking"

    def test_find_temporal_relation_before(self):
        idx = TemporalIndex()
        e1 = idx.add_event(GroundedEvent("", "A", 1, 5, 0.8))
        e2 = idx.add_event(GroundedEvent("", "B", 10, 15, 0.8))
        rel = idx.find_temporal_relation(e1, e2)
        assert rel == TemporalRelation.BEFORE

    def test_find_temporal_relation_during(self):
        idx = TemporalIndex()
        e1 = idx.add_event(GroundedEvent("", "A", 5, 15, 0.8))
        e2 = idx.add_event(GroundedEvent("", "B", 8, 12, 0.8))
        rel = idx.find_temporal_relation(e1, e2)
        assert rel == TemporalRelation.DURING

    def test_find_temporal_relation_overlaps(self):
        idx = TemporalIndex()
        e1 = idx.add_event(GroundedEvent("", "A", 1, 10, 0.8))
        e2 = idx.add_event(GroundedEvent("", "B", 5, 15, 0.8))
        rel = idx.find_temporal_relation(e1, e2)
        assert rel == TemporalRelation.OVERLAPS

    def test_get_event_sequence(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "C", 10, 15, 0.8))
        idx.add_event(GroundedEvent("", "A", 1, 5, 0.8))
        idx.add_event(GroundedEvent("", "B", 5, 10, 0.8))
        seq = idx.get_event_sequence()
        assert [e.event_label for e in seq] == ["A", "B", "C"]

    def test_compute_temporal_coverage(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "A", 1, 5, 0.8))
        idx.add_event(GroundedEvent("", "B", 8, 12, 0.8))
        coverage = idx.compute_temporal_coverage(1, 15)
        # Covered: 1-5 (5 frames), 8-12 (5 frames) = 10 out of 15
        assert abs(coverage - 10/15) < 0.01

    def test_get_gaps(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "A", 1, 3, 0.8))
        idx.add_event(GroundedEvent("", "B", 7, 10, 0.8))
        gaps = idx.get_gaps(1, 10)
        assert len(gaps) == 1
        assert gaps[0] == (4, 6)

    def test_summarize(self):
        idx = TemporalIndex()
        idx.add_event(GroundedEvent("", "A", 1, 5, 0.8))
        summary = idx.summarize()
        assert summary["event_count"] == 1
        assert summary["avg_event_duration"] == 5.0


# ── TemporalRelation Tests ─────────────────────────────────────────

class TestComputeTemporalRelation:
    """Tests for compute_temporal_relation utility."""

    def test_equals(self):
        assert compute_temporal_relation((1, 5), (1, 5)) == TemporalRelation.EQUALS

    def test_before(self):
        assert compute_temporal_relation((1, 5), (6, 10)) == TemporalRelation.BEFORE

    def test_after(self):
        assert compute_temporal_relation((6, 10), (1, 5)) == TemporalRelation.AFTER

    def test_meets(self):
        assert compute_temporal_relation((1, 5), (5, 10)) == TemporalRelation.MEETS

    def test_overlaps(self):
        assert compute_temporal_relation((1, 7), (5, 10)) == TemporalRelation.OVERLAPS


# ── ConsciousAgent P6 Integration Tests ────────────────────────────

class TestConsciousAgentP6Integration:
    """Tests for ConsciousAgent P6 perception integration."""

    def test_agent_initializes_perception(self):
        agent = ConsciousAgent("a1", "Test Agent", "video-gnn", **default_agent_kwargs("a1"))
        agent.initialize_perception("vid-1")
        assert agent.perception.scene_graph is not None
        assert agent.perception.action_tube_library is not None
        assert agent.perception.temporal_index is not None

    def test_agent_perceive_frame(self):
        agent = ConsciousAgent("a1", "Test Agent", "video-gnn", **default_agent_kwargs("a1"))
        agent.initialize_perception("vid-1")
        result = agent.perceive_frame(1, [
            {"class_name": "person", "bbox": (10, 10, 50, 100), "confidence": 0.9},
            {"class_name": "chair", "bbox": (60, 60, 100, 120), "confidence": 0.8},
        ])
        assert result["objects_detected"] == 2
        assert len(agent.perception.perception_memory) == 1

    def test_agent_perceive_frame_creates_relationships(self):
        agent = ConsciousAgent("a1", "Test Agent", "video-gnn", **default_agent_kwargs("a1"))
        agent.initialize_perception("vid-1")
        agent.perceive_frame(1, [
            {"class_name": "person", "bbox": (10, 10, 50, 100), "confidence": 0.9},
            {"class_name": "chair", "bbox": (60, 60, 100, 120), "confidence": 0.8},
        ])
        rels = agent.perception.scene_graph.get_relationships_at_frame(1)
        assert len(rels) > 0

    def test_agent_fuse_modalities(self):
        agent = ConsciousAgent("a1", "Test Agent", "video-gnn", **default_agent_kwargs("a1"))
        result = agent.fuse_modalities({
            "visual": {"vector": [1.0, 0.0, 0.0], "confidence": 0.9},
            "audio": {"vector": [0.5, 0.5, 0.0], "confidence": 0.7},
        }, task_hint="emotion_detection")
        assert "fused_vector" in result
        assert "attention_weights" in result

    def test_agent_ground_event(self):
        agent = ConsciousAgent("a1", "Test Agent", "video-gnn", **default_agent_kwargs("a1"))
        agent.initialize_perception("vid-1")
        eid = agent.ground_event("person_walking", 10, 30, 0.8)
        assert eid is not None
        events = agent.perception.temporal_index.query_by_label("walking")
        assert len(events) == 1

    def test_agent_get_perception_report(self):
        agent = ConsciousAgent("a1", "Test Agent", "video-gnn", **default_agent_kwargs("a1"))
        agent.initialize_perception("vid-1")
        agent.perceive_frame(1, [
            {"class_name": "person", "bbox": (10, 10, 50, 100), "confidence": 0.9},
        ])
        report = agent.get_perception_report()
        assert report["perception_initialized"] is True
        assert report["frames_processed"] == 1
        assert "scene_graph" in report
