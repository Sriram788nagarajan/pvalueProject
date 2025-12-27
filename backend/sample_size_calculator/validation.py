def validate_request(req):
    # ---- Variants ----
    controls = [v for v in req.variants if v.is_control]
    treatments = [v for v in req.variants if not v.is_control]

    if len(controls) != 1:
        raise ValueError("Exactly one control variant is required.")

    if len(treatments) < 1:
        raise ValueError("At least one treatment variant is required.")

    total_alloc = sum(v.allocation_percent for v in req.variants)
    if abs(total_alloc - 100) > 1e-6:
        raise ValueError("Allocation percentages must sum to 100.")

    # ---- Decimal-only enforcement ----
    if req.outcome_type == "binary":
        if not (0 < req.baseline_value < 1):
            raise ValueError("Baseline must be decimal between 0 and 1.")
        if not (0 < req.mde < 1):
            raise ValueError("MDE must be decimal between 0 and 1.")

    if req.outcome_type == "continuous":
        if req.baseline_value <= 0:
            raise ValueError("Baseline must be positive.")
        if req.mde <= 0:
            raise ValueError("MDE must be positive.")
        if req.variance is None or req.variance <= 0:
            raise ValueError("Variance / SD must be provided and positive.")
