from typing import Dict, Any


def persist_phase3_result(
    snapshot: Dict[str, Any],
    pillar: str,
    result: Dict[str, Any],
    event_id,
    occurred_at,
):
    """
    Persist Phase 3 pillar output into the experiment snapshot
    so UI can resume without recomputation.
    """

    if snapshot.get("phase3_results") is None:
        snapshot["phase3_results"] = {}

    snapshot["phase3_results"][pillar] = {
        "result": result,
        "event_id": str(event_id),
        "evaluated_at": occurred_at,
    }

    snapshot["current_view"] = "phase3_feasibility"
    snapshot["last_updated_at"] = occurred_at

    return snapshot


def invalidate_phase3(snapshot: Dict[str, Any]):
    """
    Clear all Phase 3 results when upstream phases change.
    """
    snapshot["phase3_results"] = None
    return snapshot
