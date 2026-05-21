"""
Tests for all cognitive twins: import, structure, think(), get_cognitive_signature().

Every twin must:
1. Be importable
2. Have think() returning structured reasoning
3. Have get_cognitive_signature() returning cognitive model
4. Have correct cluster assignment
5. Have citations
"""

from pathlib import Path
from typing import Dict, Any

import pytest

from shared.utils.citations import Citation


# ── Twin Registry ──────────────────────────────────────────────────────
# All 39 researchers across 4 clusters

TWIN_REGISTRY = [
    # Cluster A: Video + Spatio-Temporal GNN
    ("twins.cognitive_models.li_fei_fei", "LiFeiFeiTwin", "video-gnn"),
    ("twins.cognitive_models.ranjay_krishna", "RanjayKrishnaTwin", "video-gnn"),
    ("twins.cognitive_models.juan_carlos_niebles", "JuanCarlosNieblesTwin", "video-gnn"),
    ("twins.cognitive_models.jiankang_wang", "JiankangWangTwin", "video-gnn"),
    ("twins.cognitive_models.rohith_peddi", "RohithPeddiTwin", "video-gnn"),
    ("twins.cognitive_models.xianghui_xie", "XianghuiXieTwin", "video-gnn"),
    ("twins.cognitive_models.kristen_grauman", "KristenGraumanTwin", "video-gnn"),
    ("twins.cognitive_models.chenliang_xu", "ChenliangXuTwin", "video-gnn"),
    ("twins.cognitive_models.jiebo_luo", "JieboLuoTwin", "video-gnn"),
    # Cluster B: Streaming Cognition + Self-Reflection
    ("twins.cognitive_models.noah_shinn", "NoahShinnTwin", "streaming-reflection"),
    ("twins.cognitive_models.aman_madaan", "AmanMadaanTwin", "streaming-reflection"),
    ("twins.cognitive_models.shunyu_yao", "ShunyuYaoTwin", "streaming-reflection"),
    ("twins.cognitive_models.maciej_besta", "MaciejBestaTwin", "streaming-reflection"),
    ("twins.cognitive_models.xinhao_li", "XinhaoLiTwin", "streaming-reflection"),
    ("twins.cognitive_models.ruyi_xu", "RuyiXuTwin", "streaming-reflection"),
    ("twins.cognitive_models.shengyuan_ye", "ShengyuanYeTwin", "streaming-reflection"),
    ("twins.cognitive_models.jacob_chalk", "JacobChalkTwin", "streaming-reflection"),
    ("twins.cognitive_models.jenny_zhang", "JennyZhangTwin", "streaming-reflection"),
    ("twins.cognitive_models.nehzati_m_mohammadreza_nehzati", "NehzatiMMohammadrezaNehzatiTwin", "streaming-reflection"),
    # Cluster C: Consensus + Safety
    ("twins.cognitive_models.conor_heins", "ConorHeinsTwin", "consensus-safety"),
    ("twins.cognitive_models.lifan_zheng_yu_tian", "LifanZhengYuTianTwin", "consensus-safety"),
    ("twins.cognitive_models.yongrae_jo_chanik_park", "YongraeJoChanikParkTwin", "consensus-safety"),
    ("twins.cognitive_models.yu_cui_hongyang_du", "YuCuiHongyangDuTwin", "consensus-safety"),
    ("twins.cognitive_models.shilong_wang_guibin_zhang", "ShilongWangGuibinZhangTwin", "consensus-safety"),
    ("twins.cognitive_models.miao_yu_et_al", "MiaoYuEtAlTwin", "consensus-safety"),
    ("twins.cognitive_models.ryan_greenblatt", "RyanGreenblattTwin", "consensus-safety"),
    ("twins.cognitive_models.evan_hubinger", "EvanHubingerTwin", "consensus-safety"),
    ("twins.cognitive_models.saeid_jamshidi", "SaeidJamshidiTwin", "consensus-safety"),
    ("twins.cognitive_models.frédéric_berdoz_roger_wattenhofer", "FrédéricBerdozRogerWattenhoferTwin", "consensus-safety"),
    # Cluster D: Multi-Agent Framework
    ("twins.cognitive_models.harrison_chase", "HarrisonChaseTwin", "multi-agent"),
    ("twins.cognitive_models.joão_moura", "JoãoMouraTwin", "multi-agent"),
    ("twins.cognitive_models.chi_wang", "ChiWangTwin", "multi-agent"),
    ("twins.cognitive_models.torsten_hoefler", "TorstenHoeflerTwin", "multi-agent"),
    ("twins.cognitive_models.dapr_agents_team", "DaprAgentsTeamTwin", "multi-agent"),
    ("twins.cognitive_models.google_adk_a2a_team", "GoogleAdkA2aTeamTwin", "multi-agent"),
    ("twins.cognitive_models.openai_agents_sdk_team", "OpenaiAgentsSdkTeamTwin", "multi-agent"),
    ("twins.cognitive_models.anthropic_claude_code_agent_sdk_team", "AnthropicClaudeCodeAgentSdkTeamTwin", "multi-agent"),
    ("twins.cognitive_models.andrea_cini", "AndreaCiniTwin", "multi-agent"),
    ("twins.cognitive_models.ivan_marisca", "IvanMariscaTwin", "multi-agent"),
]


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def twin_modules():
    """Import all twin modules once."""
    modules = {}
    for module_path, class_name, cluster in TWIN_REGISTRY:
        try:
            mod = __import__(module_path, fromlist=[class_name])
            modules[class_name] = (mod, class_name, cluster)
        except Exception as e:
            modules[class_name] = (None, class_name, cluster, str(e))
    return modules


# ── Import Tests ───────────────────────────────────────────────────────

@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_importable(module_path, class_name, cluster):
    """Every twin module must be importable."""
    mod = __import__(module_path, fromlist=[class_name])
    assert hasattr(mod, class_name), f"{class_name} not found in {module_path}"


# ── Instantiation Tests ────────────────────────────────────────────────

@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_instantiable(module_path, class_name, cluster):
    """Every twin class must be instantiable without arguments."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    assert twin is not None


# ── Structure Tests ────────────────────────────────────────────────────

@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_has_required_attributes(module_path, class_name, cluster):
    """Every twin must have the CTS-001 schema attributes."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    
    assert hasattr(twin, "TWIN_ID")
    assert hasattr(twin, "NAME")
    assert hasattr(twin, "CLUSTER")
    assert hasattr(twin, "EPISTEMOLOGY")
    assert hasattr(twin, "REASONING_DIRECTION")
    assert hasattr(twin, "PRIMARY_METHOD")
    assert hasattr(twin, "SCALE_PHILOSOPHY")
    assert hasattr(twin, "EVALUATION_STYLE")
    assert hasattr(twin, "FAILURE_RESPONSE")
    assert hasattr(twin, "HEURISTICS")
    assert hasattr(twin, "BIASES")


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_cluster_correct(module_path, class_name, cluster):
    """Every twin must have the correct cluster assignment."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    assert twin.CLUSTER == cluster, f"Expected {cluster}, got {twin.CLUSTER}"


# ── think() Tests ──────────────────────────────────────────────────────

@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_think_returns_dict(module_path, class_name, cluster):
    """think() must return a structured dict."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    result = twin.think("Test task")
    assert isinstance(result, dict)


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_think_has_required_keys(module_path, class_name, cluster):
    """think() result must contain standard keys."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    result = twin.think("Test task")
    
    assert "twin_id" in result
    assert "task" in result
    assert "confidence" in result
    assert "heuristics_invoked" in result
    assert "biases_acknowledged" in result
    # Must have 6 phase keys
    phase_keys = [k for k in result.keys() if k.startswith("phase_")]
    assert len(phase_keys) == 6, f"Expected 6 phases, got {len(phase_keys)}: {phase_keys}"


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_think_phases_are_strings(module_path, class_name, cluster):
    """All phase values must be strings."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    result = twin.think("Test task")
    
    phase_keys = [k for k in result.keys() if k.startswith("phase_")]
    for pk in phase_keys:
        assert isinstance(result[pk], str), f"Phase {pk} is not a string: {type(result[pk])}"


# ── get_cognitive_signature() Tests ────────────────────────────────────

@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_signature_returns_dict(module_path, class_name, cluster):
    """get_cognitive_signature() must return a dict."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    sig = twin.get_cognitive_signature()
    assert isinstance(sig, dict)


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_signature_has_required_keys(module_path, class_name, cluster):
    """Signature must contain the full cognitive model."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    sig = twin.get_cognitive_signature()
    
    assert "twin_id" in sig
    assert "name" in sig
    assert "cluster" in sig
    assert "epistemic_engine" in sig
    assert "reasoning_topology" in sig
    assert "methodological_signature" in sig
    assert "heuristics" in sig
    assert "biases" in sig


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_signature_matches_instance(module_path, class_name, cluster):
    """Signature values must match the instance attributes."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    sig = twin.get_cognitive_signature()
    
    assert sig["twin_id"] == twin.TWIN_ID
    assert sig["name"] == twin.NAME
    assert sig["cluster"] == twin.CLUSTER
    assert sig["heuristics"] == twin.HEURISTICS
    assert sig["biases"] == twin.BIASES


# ── Citation Tests ─────────────────────────────────────────────────────

@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_class_has_citation(module_path, class_name, cluster):
    """Every twin class must have @cite() metadata."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    assert hasattr(cls, "_acn_cited") and cls._acn_cited, f"{class_name} missing @cite() decorator"


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_think_has_citation(module_path, class_name, cluster):
    """Every twin think() must have @cite() metadata."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    assert hasattr(cls.think, "_acn_cited") and cls.think._acn_cited, f"{class_name}.think() missing @cite()"


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_signature_has_citation(module_path, class_name, cluster):
    """Every twin get_cognitive_signature() must have @cite() metadata."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    assert hasattr(cls.get_cognitive_signature, "_acn_cited") and cls.get_cognitive_signature._acn_cited, \
        f"{class_name}.get_cognitive_signature() missing @cite()"


# ── Cluster Heuristics Tests ───────────────────────────────────────────

CLUSTER_HEURISTICS = {
    "video-gnn": ["composition", "abstraction", "separation", "verification"],
    "streaming-reflection": ["composition", "abstraction", "separation", "verification"],
    "consensus-safety": ["composition", "abstraction", "separation", "verification"],
    "multi-agent": ["composition", "abstraction", "separation", "verification"],
}


@pytest.mark.parametrize("module_path,class_name,cluster", TWIN_REGISTRY)
def test_twin_heuristics_structure(module_path, class_name, cluster):
    """Every twin must have the 4 canonical heuristic keys."""
    mod = __import__(module_path, fromlist=[class_name])
    cls = getattr(mod, class_name)
    twin = cls()
    
    expected = CLUSTER_HEURISTICS[cluster]
    for key in expected:
        assert key in twin.HEURISTICS, f"Missing heuristic '{key}' in {class_name}"


# ── Integration: Twin Generator ────────────────────────────────────────

def test_generator_batch_produced_all_twins():
    """The batch generator must have produced all expected files."""
    from twins.generator import TwinGenerator
    
    expected_count = len(TWIN_REGISTRY)
    models_dir = Path(__file__).parent.parent.parent / "acn" / "src" / "twins" / "cognitive_models"
    py_files = [f for f in models_dir.glob("*.py") if f.name != "__init__.py"]
    
    assert len(py_files) == expected_count, f"Expected {expected_count} twins, found {len(py_files)}"
