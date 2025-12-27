def validate_schema(payload: dict) -> dict:
    """
    Layer 1: Structural validation only.
    No semantics, no stats.
    """

    required_top_level_keys = [
        "metric_type",
        "statistical_plan",
        "traffic"
    ]

    errors = []

    for key in required_top_level_keys:
        if key not in payload:
            errors.append({
                "code": "MISSING_FIELD",
                "message": f"Missing required field: {key}"
            })

    if errors:
        return {"ok": False, "errors": errors}

    return {"ok": True}
