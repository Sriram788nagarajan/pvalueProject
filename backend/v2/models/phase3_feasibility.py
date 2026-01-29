from pydantic import BaseModel,Field
from typing import Dict, Any, List, Literal

class Phase3DetectabilityRequest(BaseModel):
    minimum_worthwhile_effect: float = Field(
        ...,
        gt=0,
        description="Smallest effect size that is meaningful to the business",
    )

    effect_scale: Literal["absolute", "relative"] = Field(
        "absolute",
        description="Scale of the effect size (absolute or relative)",
    )

    effect_direction_constraint: Literal[
        "increase_only",
        "decrease_only",
        "two_sided",
    ] = Field(
        "two_sided",
        description="Allowed direction(s) of the effect",
    )


class Phase3DetectabilityResult(BaseModel):
    is_valid: bool

    computed: Dict[str, Any]
    # REQUIRED keys inside computed:
    # - feasibility_verdict: "feasible" | "borderline" | "not_feasible"
    # - statistical_mde: float
    # - power_at_minimum_worthwhile_effect: float
    # - detectability_gap: float

    warnings: List[Dict[str, str]] = Field(default_factory=list)
    errors: List[Dict[str, str]] = Field(default_factory=list)
    explanations: List[str]


class Phase3PowerGridRequest(BaseModel):
    effect_values: List[float] = Field(
        ...,
        min_length=1,
        description="Absolute effect sizes to evaluate power for"
    )

    
class Phase3SampleTimeResult(BaseModel):
    is_valid: bool

    computed: Dict[str, Any]
    # REQUIRED keys:
    # - required_sample_per_variant
    # - planned_sample_per_variant
    # - duration_days
    # - duration_source
    # - time_to_completion_days
    # - time_feasibility_verdict

    warnings: List[Dict[str, str]] = []
    errors: List[Dict[str, str]] = []
    explanations: List[str]




class DecisionRobustnessSignal(BaseModel):
    code: str
    message: str


class Phase3DecisionRobustnessResult(BaseModel):
    is_valid: bool

    verdict: Literal[
        "robust_decision",
        "fragile_decision",
        "weak_decision_signal",
    ]

    computed: Dict[str, Any]

    signals: List[DecisionRobustnessSignal] = Field(default_factory=list)

    explanations: List[str]

    recommended_actions: List[str]