from fastapi import APIRouter, HTTPException
from .schema import MDEInput
from .validation import validate_mde_inputs
from .integrity import check_mde_integrity
from .engine import run_mde_engine
from .explanation import explain_all_results
from .sensitivity import compute_all_sensitivities
from .serializer import serialize_all_results

router = APIRouter()


@router.post("/mde")
def compute_mde(data: MDEInput):
    """
    Computes Minimum Detectable Effects (MDE) for an experiment design.
    """

    # ----------------------------
    # Validation
    # ----------------------------

    validation = validate_mde_inputs(data)

    if not validation.is_valid():
        raise HTTPException(
            status_code=400,
            detail={
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        )

    # ----------------------------
    # Integrity checks
    # ----------------------------

    integrity = check_mde_integrity(data, validation)

    if not integrity.is_valid():
        raise HTTPException(
            status_code=400,
            detail={
                "errors": integrity.errors,
                "warnings": integrity.warnings,
            },
        )

    # ----------------------------
    # Core computation
    # ----------------------------

    engine_results = run_mde_engine(data, integrity)

    # ----------------------------
    # Explanations
    # ----------------------------

    explanations = explain_all_results(
        results=engine_results,
        data=data,
        integrity=integrity,
        validation=validation,
    )

    # ----------------------------
    # Sensitivity analysis
    # ----------------------------

    sensitivities = compute_all_sensitivities(
        results=engine_results,
        data=data,
    )

    # ----------------------------
    # Serialization
    # ----------------------------

    serialized_results = serialize_all_results(
        results=engine_results,
        explanations=explanations,
        sensitivities=sensitivities,
        metric_type=data.metric_type,
        baseline=data.baseline_rate,
        std_dev=data.std_dev,
    )

    # ----------------------------
    # Final response
    # ----------------------------

    return {
        "results": serialized_results,
        "warnings": integrity.warnings + validation.warnings,
    }
