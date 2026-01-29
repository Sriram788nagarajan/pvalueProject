from backend.api.models import Phase3InferenceRequest

def serialize_inference_inputs(payload: Phase3InferenceRequest) -> dict:
    """
    Canonical JSON serializer for inference inputs.
    This is the ONLY allowed way to persist inference inputs.
    """
    return payload.model_dump(mode="json")