from typing import List
from backend.v2.db.connection import get_connection
from backend.v2.models.dashboard import DashboardExperimentItem




def list_experiments_for_dashboard(user_id) -> List[DashboardExperimentItem]:
    """
    Returns dashboard experiments from projection table (fast path).
    """

    sql = """
        SELECT
            experiment_id,
            name,
            team,
            overall_status,
            design_status,
            measurement_status,
            final_decision,
            created_at
        FROM dashboard_experiments
        WHERE user_id = %s
        ORDER BY last_updated_at DESC;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

            return [
                DashboardExperimentItem(
                    experiment_id=row["experiment_id"],
                    name=row["name"],
                    team=row["team"] or "Unspecified",
                    overall_status=row["overall_status"],
                    design_status=row["design_status"],
                    measurement_status=row["measurement_status"],
                    final_decision=row["final_decision"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]



