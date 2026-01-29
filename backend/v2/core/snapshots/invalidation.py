def invalidate_after_phase(snapshot, phase: int):
    if phase <= 1:
        snapshot["phase2_draft"] = None
        snapshot["design_inputs"] = None

    if phase <= 2:
        snapshot["design_inputs"] = None

    return snapshot
