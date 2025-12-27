from pydantic import BaseModel, Field
from typing import List, Literal


class VariantInput(BaseModel):
    name: str
    allocation_percent: float = Field(gt=0, lt=100)
    is_control: bool


class SampleSizeRequest(BaseModel):
    outcome_type: Literal["binary", "continuous"]
    design_type: Literal["independent", "paired"]
    baseline_value: float
    mde: float
    variance: float | None
    alpha: float = Field(gt=0, lt=1)
    power: float = Field(gt=0, lt=1)
    test_direction: Literal["one_tailed", "two_tailed"]
    variants: List[VariantInput]
