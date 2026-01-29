from backend.v2.db.connection import get_connection
from backend.v2.projections.dashboard_projection import project_snapshot_to_dashboard
from backend.v2.projections.dashboard_repository import upsert_dashboard_experiment


def insert_snapshot(snapshot: dict):
    sql = """
        INSERT INTO experiment_snapshots (
            experiment_id,
            user_id,
            name,
            team,
            goal,
            current_status,
            current_phase,
            current_step,
            has_warnings,
            has_override,
            locked_version,
            primary_metric,
            metric_type,
            mde,
            power,
            alpha,
            winning_variant,
            decision,
            phase4_decision,
            phase4_path,
            measurement_status,
            final_decision,
            final_notes,
            created_at,
            last_updated_at
        )
        VALUES (
            %(experiment_id)s,
            %(user_id)s,
            %(name)s,
            %(team)s,
            %(goal)s,
            %(current_status)s,
            %(current_phase)s,
            %(current_step)s,
            %(has_warnings)s,
            %(has_override)s,
            %(locked_version)s,
            %(primary_metric)s,
            %(metric_type)s,
            %(mde)s,
            %(power)s,
            %(alpha)s,
            %(winning_variant)s,
            %(decision)s,
            %(phase4_decision)s,
            %(phase4_path)s,
            %(measurement_status)s,
            %(final_decision)s,
            %(final_notes)s,
            %(created_at)s,
            %(last_updated_at)s
        );
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, snapshot)

            # NEW: dashboard projection
            dashboard_row = project_snapshot_to_dashboard(snapshot)
            upsert_dashboard_experiment(cur, dashboard_row)
        conn.commit()