from pydantic import RootModel, Field,BaseModel
from typing import Dict, Optional, Literal, List , Any


class Baseline(BaseModel):
    value: float = Field(..., gt=0, lt=1)
    source: Optional[str] = None


class PlannedTraffic(RootModel[Dict[str, int]]):
    pass


class DesignParametersRequest(BaseModel):
    metric_type: Literal["binary", "continuous"]
    design_type: Literal["independent", "paired"]
    target_mde: float = Field(..., gt=0)

    baseline: Optional[Baseline] = None

    std_dev: Optional[float] = Field(None, gt=0)

    planned_traffic: PlannedTraffic

    alpha: float = Field(..., gt=0, lt=1)
    power: float = Field(..., gt=0, lt=1)

    test_direction: Literal["one_tailed", "two_tailed"] = "two_tailed"

    duration_days: Optional[int] = Field(None, gt=0)

    assumptions_notes: Optional[str] = None



class DesignOverrideRequest(BaseModel):
    override_reason: str = Field(..., min_length=5)
    acknowledged_warnings: List[str] = Field(default_factory=list)
    acknowledged_errors: List[str] = Field(default_factory=list)
    approved_by: str


class DesignValidationResult(BaseModel):
    is_valid: bool

    computed: Dict[str, Any]

    warnings: List[Dict[str, str]] = Field(default_factory=list)
    errors: List[Dict[str, str]] = Field(default_factory=list)

    explanations: List[str]
