from datetime import datetime, timezone

from backend.v2.core.events.event_types import (
    PHASE4_ENTERED,
    PHASE4_ANALYSIS_PATH_SELECTED,
    PHASE4_IMPLEMENTATION_COMPLETED_NO_ANALYSIS,
    PHASE4_IMPLEMENTATION_COMPLETED_WITH_ANALYSIS,
)

from backend.v2.core.events.event_factory import build_generic_event

from backend.v2.core.gaurds.experiment_state import (
    assert_experiment_not_completed,
    assert_phase4_not_finalized,
)
from backend.v2.core.snapshots.snapshot_phase4 import (
    apply_phase4_entry,
    apply_phase4_decision_selected,
    apply_phase4_finalization,
)

from backend.v2.core.events.event_types import (
    PHASE4_DECISION_RECORDED_NO_ANALYSIS,
)


def enter_phase4(*, snapshot, experiment_id, user_id):
    """
    User lands on Phase 4 page.
    """
    assert_experiment_not_completed(snapshot)

    now = datetime.now(timezone.utc)

    snapshot = apply_phase4_entry(snapshot, now)

    event = build_generic_event(
    experiment_id=experiment_id,
    user_id=user_id,
    event_type=PHASE4_ENTERED,
    phase=4,
    payload={"phase": 4, "action": "entered"},
    )       

    return event, snapshot

def select_phase4_analysis_path(*, snapshot, experiment_id, user_id, choice):
    """
    Reversible selection.
    """
    assert_experiment_not_completed(snapshot)
    assert_phase4_not_finalized(snapshot)

    now = datetime.now(timezone.utc)

    snapshot = apply_phase4_decision_selected(
        snapshot=snapshot,
        decision=choice,
        occurred_at=now,
    )

    event = build_generic_event(
    experiment_id=experiment_id,
    user_id=user_id,
    event_type=PHASE4_ANALYSIS_PATH_SELECTED,
    phase= 4,
    payload={
        
        "analysis_choice": choice,
        "is_final": False,
        },
    )

    return event, snapshot




VALID_NO_ANALYSIS_DECISIONS = {
    "ship",
    "rollback",
    "iterate",
    "hold",
    "abandon",
}


def finalize_phase4(
    *,
    snapshot,
    experiment_id,
    user_id,
    decision,
    notes=None,
):
    """
    Terminal Phase 4 action (no-analysis path).
    """

    assert_experiment_not_completed(snapshot)
    assert_phase4_not_finalized(snapshot)

    if decision not in VALID_NO_ANALYSIS_DECISIONS:
        raise ValueError(f"Invalid Phase 4 decision: {decision}")

    now = datetime.now(timezone.utc)

    snapshot = apply_phase4_finalization(
        snapshot=snapshot,
        final_decision=decision,
        notes=notes,
        occurred_at=now,
    )

    event = build_generic_event(
        experiment_id=experiment_id,
        user_id=user_id,
        event_type=PHASE4_DECISION_RECORDED_NO_ANALYSIS,
        phase=4,
        payload={
            "decision": decision,
            "notes": notes,
            "is_final": True,
        },
    )

    return event, snapshot




def finalize_phase4_with_analysis(
    *,
    snapshot,
    experiment_id,
    user_id,
):
    """
    Terminal Phase 4 action (WITH analysis).
    Point of no return.
    """

    assert_experiment_not_completed(snapshot)
    assert_phase4_not_finalized(snapshot)

    now = datetime.now(timezone.utc)

    # Ensure phase4_path is set
    if snapshot.get("phase4_path") != "yes_analyze":
        snapshot["phase4_path"] = "yes_analyze"

    snapshot["current_phase"] = 5
    snapshot["current_step"] = "phase5_inference"
    snapshot["current_view"] = "phase5_inference"  
    snapshot["current_status"] = "analysis_pending"
    snapshot["last_updated_at"] = now

    event = build_generic_event(
        experiment_id=experiment_id,
        user_id=user_id,
        event_type=PHASE4_IMPLEMENTATION_COMPLETED_WITH_ANALYSIS,
        phase=4,
        payload={
            "analysis_path": "with_analysis",
            "is_final": True,
        },
    )

    return event, snapshot