def resolve_view(snapshot: dict) -> str:
    """
    Deterministic navigation resolver.

    Returns a canonical frontend view name.
    MUST be pure.
    """

    # Experiment fully completed
    if snapshot.get("final_decision"):
        return "phase5_inference_analysis"

    # Phase 5 completed but not finalized
    if snapshot.get("measurement_status") == "analysis_completed":
        return "phase5_inference_analysis"

    # Phase 4 path chosen
    if snapshot.get("phase4_path") == "yes_analyze":
        return "phase5_inference_analysis"

    if snapshot.get("phase4_path"):
        return "phase4_implementation"

    # Phase 3 committed
    if (
    snapshot.get("locked_version") is not None
        and not snapshot.get("phase4_path")
    ):
        return "phase3_decision"

    # Phase 3 in progress (not yet committed)
    if snapshot.get("current_phase") == 3 and snapshot.get("locked_version") is None:
        return "phase3_feasibility"

    # Earlier phases
    if snapshot.get("current_phase") == 2:
        return "design_parameters"

    if snapshot.get("current_phase") == 1:
        return "define_experiment"

    # Default
    return "create_experiment"