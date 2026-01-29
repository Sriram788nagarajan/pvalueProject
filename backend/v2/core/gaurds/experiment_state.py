
class ExperimentStateError(Exception):
    pass


TERMINAL_STATUSES = {
    "completed",
}


def assert_experiment_not_completed(snapshot):
    """
    Prevent any mutation once an experiment is completed.
    """
    if snapshot.get("current_status") in TERMINAL_STATUSES:
        raise ExperimentStateError(
            "Experiment is completed and cannot be modified."
        )


def assert_phase4_not_finalized(snapshot):
    """
    Phase 4 allows reversibility UNTIL implementation is completed.
    """
    decision = snapshot.get("decision")
    if decision in {
        "implementation_completed_no_analysis",
        "implementation_completed_with_analysis",
    }:
        raise ExperimentStateError(
            "Phase 4 is finalized and cannot be changed."
        )