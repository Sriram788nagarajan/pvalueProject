from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# -------------------------------
# Variant-level schema
# -------------------------------

class VariantInput(BaseModel):
    name: str
    n: int = Field(..., gt=0, description="Raw sample size (count of users)")
    is_control: bool


# -------------------------------
# Top-level MDE input schema
# -------------------------------

class MDEInput(BaseModel):
    # Metric & design
    metric_type: Literal["binary", "continuous"]
    design_type: Literal["independent", "paired"]

    # Binary-only
    baseline_rate: Optional[float] = Field(
        None, description="Baseline conversion rate (0–1)"
    )

    # Paired-binary only (planning parameter)
    discordance_rate: Optional[float] = Field(
        None,
        gt=0,
        lt=1,
        description="Estimated probability of discordant outcomes (p01 + p10) for paired binary MDE (planning-only)"
    )


    # Continuous-only
    std_dev: Optional[float] = Field(
        None, gt=0, description="Standard deviation of the metric"
    )

    # Risk parameters
    alpha: float = Field(..., gt=0, lt=1)
    power: float = Field(..., gt=0, lt=1)
    test_direction: Literal["one_tailed", "two_tailed"]

    # Traffic
    variants: List[VariantInput]
