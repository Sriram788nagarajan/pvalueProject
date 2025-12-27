from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ProportionHypothesis(BaseModel):
    baseline_rate: float = Field(..., gt=0, lt=1)
    expected_lift: float = Field(..., gt=0)

class MeanMetric(BaseModel):
    baseline_mean: float
    expected_delta: float
    assumed_std: float = Field(..., gt=0)

class StatisticalPlanModel(BaseModel):
    alpha: float = Field(..., gt=0, lt=1)
    power: float = Field(..., gt=0, lt=1)
    test_type: Literal["one-tailed", "two-tailed"]

class TrafficModel(BaseModel):
    daily_users: int = Field(..., gt=0)
    run_days: int = Field(..., gt=0)
    allocation: float = Field(..., gt=0, le=1)

class Phase0Request(BaseModel):
    metric_type: Literal["proportion", "mean"]

    hypothesis: Optional[ProportionHypothesis] = None
    mean_metric: Optional[MeanMetric] = None

    statistical_plan: StatisticalPlanModel
    traffic: TrafficModel


class ValidationErrorModel(BaseModel):
    code: str
    message: str


class StatisticsModel(BaseModel):
    status: Literal["OK", "BLOCKED"]
    planned_sample_per_variant: Optional[int] = None
    required_sample_per_variant: Optional[int] = None
    achieved_power: Optional[float] = None


class VerdictModel(BaseModel):
    status: Literal["VALID", "RISKY", "BLOCKED"]
    reason: str
    errors: Optional[List[ValidationErrorModel]] = None


class Phase0Response(BaseModel):
    status: Literal["VALID", "RISKY", "BLOCKED"]
    layer: int
    statistics: Optional[StatisticsModel] = None
    verdict: Optional[VerdictModel] = None
    errors: Optional[List[ValidationErrorModel]] = None


# ---------- Phase 3: Statistical Inference Models ----------
class McNemarCounts(BaseModel):
    b: int = Field(..., ge=0)
    c: int = Field(..., ge=0)


class GroupStats(BaseModel):
    n: int = Field(..., gt=0)
    value: float
    sd: Optional[float] = None


class TestGroupStats(GroupStats):
    id: str


class InferenceSettings(BaseModel):
    tail: Literal["one_sided", "two_sided"] = "two_sided"
    confidence_level: float = Field(0.95, gt=0, lt=1)
    minimum_effect: Optional[float] = None

class McNemarInput(BaseModel):
    b: int = Field(..., ge=0)
    c: int = Field(..., ge=0)




class Phase3InferenceRequest(BaseModel):
    metric_type: Literal["binary", "continuous"]
    data_structure: Literal["independent", "paired"] = "independent"

    # Used for independent OR continuous
    control: Optional[GroupStats] = None
    tests: Optional[List[TestGroupStats]] = None

    # Used ONLY for binary + paired
    mcnemar: Optional[McNemarCounts] = None

    settings: Optional[InferenceSettings] = InferenceSettings()
