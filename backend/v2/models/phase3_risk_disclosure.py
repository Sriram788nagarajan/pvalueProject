from pydantic import BaseModel, Field
from typing import List, Literal


class RiskDisclosureItem(BaseModel):
    code: str
    statement: str
    source: Literal[
        "design",
        "detectability",
        "sample_time",
        "decision_robustness",
        "global",
    ]


class ApproximationItem(BaseModel):
    code: str
    statement: str
    impact: str


class Phase3RiskDisclosureResult(BaseModel):
    is_valid: bool = True

    explicit_assumptions: List[RiskDisclosureItem]
    approximations: List[ApproximationItem]
    known_fragilities: List[RiskDisclosureItem]
    invalidation_conditions: List[RiskDisclosureItem]
