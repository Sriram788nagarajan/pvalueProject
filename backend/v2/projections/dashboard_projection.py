# backend/v2/projections/dashboard_projection.py

from typing import Dict


def _map_design_status(decision: str | None) -> str:
    if decision == "blocked":
        return "blocked"
    if decision == "accepted":
        return "accepted"
    return "in_progress"


def _map_overall_status(current_status: str, decision: str | None) -> str:
    if decision == "blocked":
        return "blocked"
    if current_status == "completed":
        return "completed"
    return "in_progress"


def _map_measurement_status(
    *,
    decision: str | None,
    phase4_path: str | None,
    current_phase: int,
    current_status: str,
) -> str:
    # Phase 3 not accepted → cannot decide measurement yet
    if decision != "accepted":
        return "TBD"

    # Phase 3 accepted but Phase 4 not entered
    if current_phase < 4:
        return "TBD"

    # Explicit Phase 4 choice
    if phase4_path == "no_analyze":
        return "not_requested"

    if phase4_path == "yes_analyze":
        return "requested"

    # Phase 5 implies measurement happened
    if current_status in {
        "analysis_pending",
        "analysis_completed",
        "completed",
    }:
        return "requested"

    return "TBD"


def project_snapshot_to_dashboard(snapshot: Dict) -> Dict:
    """
    PURE projection:
    snapshot dict -> dashboard_experiments row
    """

    return {
        "experiment_id": snapshot["experiment_id"],
        "user_id": snapshot["user_id"],

        "name": snapshot.get("name") or "Untitled Experiment",
        "team": snapshot.get("team"),

        "design_status": _map_design_status(snapshot.get("decision")),
        "overall_status": _map_overall_status(
            snapshot.get("current_status"),
            snapshot.get("decision"),
        ),
        "measurement_status": _map_measurement_status(
            decision=snapshot.get("decision"),
            phase4_path=snapshot.get("phase4_path"),
            current_phase=snapshot.get("current_phase"),
            current_status=snapshot.get("current_status"),
        ),
        "final_decision": snapshot.get("final_decision") or "TBD",

        # Navigation safety (future-proof, no behavior change yet)
        "current_phase": snapshot.get("current_phase"),
        "current_step": snapshot.get("current_step"),
        "current_view": snapshot.get("current_view"),

        "created_at": snapshot.get("created_at"),
        "last_updated_at": snapshot.get("last_updated_at"),
    }
