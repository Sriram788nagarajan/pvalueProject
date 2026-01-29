from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Hypothesis(BaseModel):
    statement: str = Field(..., min_length=1)
    direction: Optional[Literal["increase", "decrease", "no_change"]] = None


class Metric(BaseModel):
    name: str = Field(..., min_length=1)
    type: Literal["binary", "continuous"]
    numerator: Optional[str] = None
    denominator: Optional[str] = None
    direction: Optional[Literal["increase", "decrease", "no_increase"]] = None


class Variant(BaseModel):
    id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class DefinitionSavedRequest(BaseModel):
    hypothesis: Hypothesis
    primary_metric: Metric
    secondary_metrics: Optional[List[Metric]] = []
    guardrails: Optional[List[Metric]] = []
    variants: List[Variant]

    experiment_type: Literal["ab", "multivariate"] = "ab"
    traffic_split_type: Literal["equal", "custom"] = "equal"
