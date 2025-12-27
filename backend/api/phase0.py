from fastapi import APIRouter, HTTPException
from backend.validation.engine import validate_experiment_design
from backend.api.models import Phase0Request, Phase0Response

router = APIRouter()

@router.post(
    "/phase0/validate",
    response_model=Phase0Response
)
def validate_phase0(payload: Phase0Request):
    """
    Phase 0.3 endpoint with strict request & response contracts.
    """

    try:
        result = validate_experiment_design(payload.dict())
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_VALIDATION_ERROR",
                "message": str(e)
            }
        )
