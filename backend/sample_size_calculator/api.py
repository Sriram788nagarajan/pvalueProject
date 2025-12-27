from fastapi import APIRouter, HTTPException
from .schema import SampleSizeRequest
from .validation import validate_request
from .engine import compute_sample_sizes
from .serializer import build_response

router = APIRouter()


@router.post("/sample-size")
def sample_size_endpoint(req: SampleSizeRequest):
    try:
        validate_request(req)
        response = build_response(req)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
