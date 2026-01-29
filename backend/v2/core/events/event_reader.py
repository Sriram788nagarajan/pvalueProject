from backend.v2.db.connection import get_connection

from backend.v2.core.events.event_types import (
    PHASE3_FEASIBILITY_DETECTABILITY_EVALUATED,
)


def get_latest_phase3_detectability_event(experiment_id):
    """
    Returns the most recent PHASE3_DETECTABILITY_EVALUATED event
    for the given experiment.
    """

    query = """
        SELECT payload
        FROM experiment_events
        WHERE experiment_id = %s
          AND event_type = %s
        ORDER BY occurred_at DESC
        LIMIT 1
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                    query,
                    (str(experiment_id), PHASE3_FEASIBILITY_DETECTABILITY_EVALUATED),
                )

            row = cur.fetchone()

    if not row:
        return None

    payload = row["payload"]

    # psycopg v3 JSON unwrap
    if hasattr(payload, "obj"):
        payload = payload.obj

    return {
        "payload": payload
    }

from backend.v2.core.events.event_types import (
    PHASE3_SAMPLE_TIME_FEASIBILITY_EVALUATED,
)

def get_latest_phase3_sample_time_event(experiment_id):
    """
    Returns the most recent PHASE3_SAMPLE_TIME_FEASIBILITY_EVALUATED event
    for the given experiment.
    """
    query = """
        SELECT payload
        FROM experiment_events
        WHERE experiment_id = %s
          AND event_type = %s
        ORDER BY occurred_at DESC
        LIMIT 1
    """

    from backend.v2.db.connection import get_connection

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    str(experiment_id),
                    PHASE3_SAMPLE_TIME_FEASIBILITY_EVALUATED,
                ),
            )
            row = cur.fetchone()

    if not row:
        return None

    payload = row["payload"]

    # psycopg v3 JSON unwrap
    if hasattr(payload, "obj"):
        payload = payload.obj

    return {
        "payload": payload
    }

