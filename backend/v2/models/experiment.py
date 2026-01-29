from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class CreateExperimentRequest(BaseModel):
    experiment_id: UUID
    name: str
    team: Optional[str] = None
    goal: Optional[str] = None