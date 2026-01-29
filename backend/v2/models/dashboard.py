from pydantic import BaseModel
from typing import List
from datetime import datetime
from uuid import UUID


class DashboardExperimentItem(BaseModel):
    experiment_id: UUID
    name: str
    team: str

    design_status: str          # in_progress | accepted | blocked
    overall_status: str         # in_progress | blocked | completed
    measurement_status: str     # not_requested | requested
    final_decision: str | None         # TBD | ship | rollback | ...

    created_at: datetime

class DashboardExperimentListResponse(BaseModel):
    experiments: List[DashboardExperimentItem]
    total: int
