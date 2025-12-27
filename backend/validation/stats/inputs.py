from dataclasses import dataclass
from typing import Literal
from dataclasses import dataclass
from typing import Annotated
from pydantic import Field


@dataclass
class TrafficAssumptions:
    daily_users: int
    run_days: int
    allocation: Annotated[float, Field(gt=0, le=1)]


@dataclass
class StatisticalPlan:
    alpha : float   # Type I error rate
    power : float   # Desired 1 - beta
    test_type : Literal['one-tailed', 'two-tailed']


@dataclass
class HypothesisInputs:
    baseline_rate : float   # p0
    expected_lift : float    # absolute lift (Δ)


@dataclass
class TrafficAssumptions:
    daily_users: int
    run_days: int
    allocation: Annotated[float, Field(gt=0, le=1)]


@dataclass
class MeanMetricInputs:
    baseline_mean: float      # μ0
    expected_delta: float     # Δ
    assumed_std: float        # σ (design-time assumption)
