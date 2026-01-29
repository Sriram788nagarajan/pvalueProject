from backend.v2.db.connection import get_connection
from psycopg.types.json import Json
from datetime import datetime

from uuid import UUID


def _json_safe(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, UUID):
        return str(obj)

    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]

    return obj



def upsert_snapshot(snapshot: dict):

   
    
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
            definition_inputs,
            design_inputs,
            phase3_results,
            phase5_results,
            draft_inputs,
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
            %(definition_inputs)s,
            %(design_inputs)s,
            %(phase3_results)s,
            %(phase5_results)s,
            %(draft_inputs)s,
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
        )

        ON CONFLICT (experiment_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            team = EXCLUDED.team,
            goal = EXCLUDED.goal,
            current_status = EXCLUDED.current_status,
            current_phase = EXCLUDED.current_phase,
            current_step = EXCLUDED.current_step,
            primary_metric = EXCLUDED.primary_metric,
            metric_type = EXCLUDED.metric_type,
            definition_inputs = EXCLUDED.definition_inputs,
            design_inputs = EXCLUDED.design_inputs,
            phase3_results = EXCLUDED.phase3_results,
            phase5_results = EXCLUDED.phase5_results,
            draft_inputs = EXCLUDED.draft_inputs,
            last_updated_at = EXCLUDED.last_updated_at,
            has_warnings = EXCLUDED.has_warnings,
            has_override = EXCLUDED.has_override,
            locked_version = EXCLUDED.locked_version,
            mde = EXCLUDED.mde,
            power = EXCLUDED.power,
            alpha = EXCLUDED.alpha,
            winning_variant = EXCLUDED.winning_variant,
            decision = EXCLUDED.decision,
            phase4_decision = EXCLUDED.phase4_decision,
            phase4_path = EXCLUDED.phase4_path,
            measurement_status = EXCLUDED.measurement_status,
            final_decision = EXCLUDED.final_decision,
            final_notes = EXCLUDED.final_notes

            
    """

    snapshot = snapshot.copy()

    if snapshot.get("design_inputs") is not None:
        snapshot["design_inputs"] = Json(snapshot["design_inputs"])

    if snapshot.get("phase3_results") is not None:
        snapshot["phase3_results"] = Json(
            _json_safe(snapshot["phase3_results"])
        )

    if snapshot.get("phase5_results") is not None:
        snapshot["phase5_results"] = Json(
            _json_safe(snapshot["phase5_results"])
        )

    if snapshot.get("definition_inputs") is not None:
        snapshot["definition_inputs"] = Json(snapshot["definition_inputs"])

    if snapshot.get("draft_inputs") is not None:  
        snapshot["draft_inputs"] = Json(snapshot["draft_inputs"])

    if snapshot.get("phase4_decision") is not None:
        snapshot["phase4_decision"] = Json(snapshot["phase4_decision"])


    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, snapshot)
        conn.commit()
