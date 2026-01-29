from psycopg.types.json import Json

from backend.v2.db.connection import get_connection


def insert_event(event: dict):
    sql = """
        INSERT INTO experiment_events (
            event_id,
            experiment_id,
            user_id,
            event_type,
            phase,
            severity,
            occurred_at,
            schema_version,
            payload
        )
        VALUES (
            %(event_id)s,
            %(experiment_id)s,
            %(user_id)s,
            %(event_type)s,
            %(phase)s,
            %(severity)s,
            %(occurred_at)s,
            %(schema_version)s,
            %(payload)s
        );
    """

    # IMPORTANT:
    # psycopg v3 requires explicit JSON adaptation
    event = event.copy()
    event["payload"] = Json(event["payload"])

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, event)
