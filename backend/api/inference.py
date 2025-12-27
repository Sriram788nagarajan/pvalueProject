from fastapi import APIRouter
from .models import Phase3InferenceRequest
from backend.validation.stats.inference_engine import run_inference



router = APIRouter(
    prefix="/api/inference",
    tags=["Statistical Inference"]
)

@router.post("/run")
def run_inference_api(payload: Phase3InferenceRequest):
    results, warnings = run_inference(payload)

    # -------------------------------
    # Decision logic (safe for McNemar)
    # -------------------------------
    if payload.metric_type == "binary" and payload.data_structure == "paired":
        decision = "mcnemar"
        comparisons = 1
        control_value = None
    else:
        decision = (
            "all_significant" if all(r["significant"] for r in results)
            else "none_significant" if all(not r["significant"] for r in results)
            else "mixed"
        )
        comparisons = len(payload.tests)
        if payload.metric_type == "binary":
            control_value = payload.control.value / payload.control.n
        else:
            control_value = payload.control.value


    return {
        "summary": {
            "metric_type": payload.metric_type,
            "data_structure": payload.data_structure,
            "control_value": control_value,
            "decision": decision
        },
        "results": results,
        "warnings": list(set(warnings)),
        "metadata": {
            "alpha": 1 - payload.settings.confidence_level,
            "comparisons": comparisons,
            "engine_version": "v1.0"
        }
    }
