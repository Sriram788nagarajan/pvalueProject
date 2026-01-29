# backend/v2/projections/dashboard_repository.py

from backend.v2.db.connection import get_connection

def upsert_dashboard_experiment(cur, row: dict):
    sql = """
        INSERT INTO dashboard_experiments (
            experiment_id,
            user_id,
            name,
            team,
            overall_status,
            design_status,
            measurement_status,
            final_decision,
            current_phase,
            current_step,
            current_view,
            created_at,
            last_updated_at
        )
        VALUES (
            %(experiment_id)s,
            %(user_id)s,
            %(name)s,
            %(team)s,
            %(overall_status)s,
            %(design_status)s,
            %(measurement_status)s,
            %(final_decision)s,
            %(current_phase)s,
            %(current_step)s,
            %(current_view)s,
            %(created_at)s,
            %(last_updated_at)s
        )
        ON CONFLICT (experiment_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            team = EXCLUDED.team,
            overall_status = EXCLUDED.overall_status,
            design_status = EXCLUDED.design_status,
            measurement_status = EXCLUDED.measurement_status,
            final_decision = EXCLUDED.final_decision,
            current_phase = EXCLUDED.current_phase,
            current_step = EXCLUDED.current_step,
            current_view = EXCLUDED.current_view,
            last_updated_at = EXCLUDED.last_updated_at;
    """
    cur.execute(sql, row)
