from typing import Dict, Any, List

# V1 imports (canonical engine)
from backend.mde_calculator.engine import run_mde_engine
from backend.mde_calculator.schema import MDEInput, VariantInput
from backend.mde_calculator.validation import validate_mde_inputs
from backend.mde_calculator.integrity import check_mde_integrity


def compute_mde_v1(
    *,
    metric_type: str,
    design_type: str,
    baseline_rate: float | None,
    std_dev: float | None,
    discordance_rate: float | None,
    planned_traffic: Dict[str, int],
    alpha: float,
    power: float,
    test_direction: str,
) -> Dict[str, Any]:

    # ----------------------------
    # 1. Build V1 variants (explicit control)
    # ----------------------------
    variants: List[VariantInput] = []

    for name, n in planned_traffic.items():
        variants.append(
            VariantInput(
                name=name,
                n=n,
                is_control=(name == "control")
            )
        )

    # ----------------------------
    # 2. Build MDEInput
    # ----------------------------
    try:
        data = MDEInput(
            metric_type=metric_type,
            design_type=design_type,
            baseline_rate=baseline_rate,
            std_dev=std_dev,
            discordance_rate=discordance_rate,
            alpha=alpha,
            power=power,
            test_direction=test_direction,
            variants=variants,
        )
    except Exception as e:
        return {
            "valid": False,
            "engine_errors": [str(e)],
            "engine_warnings": [],
            "pairwise_results": [],
        }

    # ----------------------------
    # 3. Run V1 validation (MANDATORY)
    # ----------------------------
    validation = validate_mde_inputs(data)

    if not validation.is_valid():
        return {
            "valid": False,
            "engine_errors": validation.errors,
            "engine_warnings": validation.warnings,
            "pairwise_results": [],
        }

    # ----------------------------
    # 4. Run V1 integrity (MANDATORY)
    # ----------------------------
    integrity = check_mde_integrity(data, validation)

    if not integrity.is_valid():
        return {
            "valid": False,
            "engine_errors": integrity.errors,
            "engine_warnings": integrity.warnings,
            "pairwise_results": [],
        }

    # ----------------------------
    # 5. Run canonical MDE engine
    # ----------------------------
    results = run_mde_engine(data=data, integrity=integrity)

    # ----------------------------
    # 6. Normalize output + propagate warnings
    # ----------------------------
    pairwise_results = [
        {
            "control": r.control_name,
            "test": r.test_name,
            "n_control": r.n_control,
            "n_test": r.n_test,
            "mde": r.mde,
        }
        for r in results
    ]

    return {
        "valid": True,
        "engine_errors": [],
        "engine_warnings": validation.warnings + integrity.warnings,
        "pairwise_results": pairwise_results,
        "engine": "v1_mde",
    }
