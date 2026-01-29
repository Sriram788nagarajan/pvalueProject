from fastapi import APIRouter, HTTPException
from uuid import UUID
from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from backend.v2.core.snapshots.snapshot_reader import get_snapshot_by_experiment_id
from backend.v2.auth.dependencies import get_current_user
from backend.v2.auth.utils import get_user_id_from_jwt
from backend.v2.auth.guards import require_experiment_owner

router = APIRouter(prefix="/v2/experiments")


@router.get("/{experiment_id}/resume")
def resume_experiment(
    experiment_id: UUID,
    current_user = Depends(get_current_user),
):
    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_by_experiment_id(experiment_id)

    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")

    require_experiment_owner(snapshot, user_id)

    step = snapshot.get("current_step", "create_experiment")

    return {
        "resume_step": step,
        "experiment_id": experiment_id,
        "current_phase": snapshot.get("current_phase"),
        "current_status": snapshot.get("current_status")
    }