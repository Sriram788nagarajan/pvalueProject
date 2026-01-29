from datetime import datetime,timezone

def record_last_seen(conn, *, experiment_id, phase, step):
    """
    Best-effort navigation metadata write.

    - MUST NOT raise
    - MUST NOT block navigation
    """

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE experiment_snapshots
                SET
                    last_seen_at = %(ts)s,
                    last_seen_phase = %(phase)s,
                    last_seen_step = %(step)s
                WHERE experiment_id = %(experiment_id)s
                """,
                {
                    "ts": datetime.now(timezone.utc),
                    "phase": phase,
                    "step": step,
                    "experiment_id": experiment_id,
                },
            )
    except Exception:
        # Explicitly swallowed — orchestration must not fail
        pass