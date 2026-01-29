from typing import List
from backend.v2.db.connection import get_connection
from backend.v2.models.dashboard import DashboardExperimentItem







def map_design_status(decision: str | None) -> str:
    if decision == "blocked":
        return "blocked"
    if decision == "accepted":
        return "accepted"
    return "in_progress"


def map_overall_status(current_status: str, decision: str | None) -> str:
    if decision == "blocked":
        return "blocked"
    if current_status == "completed":
        return "completed"
    return "in_progress"



def map_measurement_status(
    *,
    decision: str | None,
    phase4_path: str | None,
    current_phase: int,
    current_status: str,
) -> str:
    """
    Measurement status semantics:

    - TBD: user has not explicitly decided
    - not_requested: user explicitly chose no_analyze
    - requested: user chose yes_analyze OR reached phase 5
    """

    # Phase 3 not accepted → cannot decide measurement yet
    if decision != "accepted":
        return "TBD"

    # Phase 3 accepted but Phase 4 not entered
    if current_phase < 4:
        return "TBD"

    # Phase 4 explicit decision
    if phase4_path == "no_analyze":
        return "not_requested"

    if phase4_path == "yes_analyze":
        return "requested"

    # Phase 5 implies measurement happened
    if current_status in {"analysis_pending", "analysis_completed", "completed"}:
        return "requested"

    return "TBD"

def map_final_decision(final_decision: str | None) -> str:
    return final_decision or "TBD"





def list_experiments_for_dashboard(user_id) -> List[DashboardExperimentItem]:
    """
    Returns all experiments as lightweight dashboard summaries.
    """

    sql = """
        SELECT
            experiment_id,
            name,
            team,
            created_at,
            current_status,
            current_phase,
            decision,
            phase4_path,
            final_decision
        FROM experiment_snapshots
        WHERE user_id = %s
        ORDER BY last_updated_at DESC;
    """

    items: List[DashboardExperimentItem] = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

            for row in rows:
                items.append(
                    DashboardExperimentItem(
                        experiment_id=row["experiment_id"],
                        name=row["name"],
                        team=row["team"] or "Unspecified",

                        design_status=map_design_status(row["decision"]),
                        overall_status=map_overall_status(
                            row["current_status"],
                            row["decision"],
                        ),
                                                
                        measurement_status=map_measurement_status(
                            decision=row["decision"],
                            phase4_path=row["phase4_path"],
                            current_phase=row["current_phase"],
                            current_status=row["current_status"],
                        ),
                                                
                        final_decision=map_final_decision(row["final_decision"]),

                        created_at=row["created_at"],
                    )
                )


    return items



