from backend.v2.orchestration.view_resolver import resolve_view


def test_new_experiment():
    snapshot = {}
    assert resolve_view(snapshot) == "create_experiment"


def test_define_experiment():
    snapshot = {"current_phase": 1}
    assert resolve_view(snapshot) == "define_experiment"


def test_design_feasibility():
    snapshot = {"current_phase": 2}
    assert resolve_view(snapshot) == "design_feasibility"


def test_phase3_committed():
    snapshot = {"locked_version": 1}
    assert resolve_view(snapshot) == "phase3_decision"


def test_phase4_no_analyze():
    snapshot = {"phase4_path": "no_analyze"}
    assert resolve_view(snapshot) == "phase4_implementation"


def test_phase4_yes_analyze():
    snapshot = {"phase4_path": "yes_analyze"}
    assert resolve_view(snapshot) == "phase5_inference_analysis"


def test_completed_experiment():
    snapshot = {"final_decision": "ship"}
    assert resolve_view(snapshot) == "dashboard"