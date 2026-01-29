from backend.v2.db.connection import get_connection


def get_snapshot_by_experiment_id(experiment_id):
    sql = """
        SELECT *
        FROM experiment_snapshots
        WHERE experiment_id = %(experiment_id)s
        LIMIT 1;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"experiment_id": experiment_id})
            row = cur.fetchone()
            return dict(row) if row else None       

def get_snapshot_for_orchestration(experiment_id):
    """
    Read-only snapshot accessor for orchestration layer.

    IMPORTANT:
    - No mutation
    - No inference
    - No workflow logic
    """
    snapshot = get_snapshot_by_experiment_id(experiment_id)

    if not snapshot:
        return None

    return {
        "experiment_id": snapshot["experiment_id"],
        "user_id": snapshot["user_id"],
        "current_phase": snapshot.get("current_phase"),
        "current_step": snapshot.get("current_step"),
        "current_status": snapshot.get("current_status"),
        "locked_version": snapshot.get("locked_version"),

        # Phase-specific flags
        "phase4_path": snapshot.get("phase4_path"),
        "phase5_results": snapshot.get("phase5_results"),
        "final_decision": snapshot.get("final_decision"),
        "measurement_status": snapshot.get("measurement_status"),

        # Navigation metadata
        "last_seen_at": snapshot.get("last_seen_at"),
        "last_seen_phase": snapshot.get("last_seen_phase"),
        "last_seen_step": snapshot.get("last_seen_step"),
    }
