from backend.v2.orchestration.view_resolver import resolve_view
from backend.v2.orchestration.entry_context import build_entry_context
from backend.v2.orchestration.last_seen_writer import record_last_seen



def orchestrate_entry(*, snapshot: dict, conn) -> dict:
    """
    Single orchestration entrypoint.

    Input:
      - snapshot: read-only snapshot dict
      - conn: existing DB connection

    Output:
      - resolved_view
      - entry_context
    """

  

    resolved_view = resolve_view(snapshot)

   

    entry_context = build_entry_context(snapshot)

    record_last_seen(
        conn,
        experiment_id=snapshot["experiment_id"],
        phase=snapshot.get("current_phase"),
        step=snapshot.get("current_step"),
    )

    return {
        "resolved_view": resolved_view,
        "entry_context": entry_context,
        "resolution_reason": {
            "current_phase": snapshot.get("current_phase"),
            "current_status": snapshot.get("current_status"),
        },
    }