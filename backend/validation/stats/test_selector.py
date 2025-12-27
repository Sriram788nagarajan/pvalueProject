

def recommend_test(metric_type: str, variants: int) -> str:
    if metric_type == "proportion" and variants == 2:
        return "two_sample_z_test"
    if metric_type == "mean" and variants == 2:
        return "two_sample_t_test"
    return "unsupported"
