def validate_definition(payload: dict):
    variants = payload.get("variants", [])
    if len(variants) < 2:
        raise ValueError("At least two variants are required")

    metric_names = set()
    for metric in [payload["primary_metric"]] + payload.get("secondary_metrics", []):
        if metric["name"] in metric_names:
            raise ValueError(f"Duplicate metric name: {metric['name']}")
        metric_names.add(metric["name"])
