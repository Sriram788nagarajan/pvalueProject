from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.v2.auth.dependencies import get_current_user
from backend.v2.auth.utils import get_user_id_from_jwt
from backend.v2.db.connection import get_connection
from backend.v2.core.snapshots.snapshot_reader import (
    get_snapshot_for_orchestration,
)
from backend.v2.orchestration.entrypoint import orchestrate_entry


router = APIRouter(
    prefix="/v2/orchestration",
    tags=["Orchestration"],
)


@router.get("/enter/{experiment_id}")
def enter_experiment(
    experiment_id: UUID,
    current_user=Depends(get_current_user),
):
    user_id = get_user_id_from_jwt(current_user)

    snapshot = get_snapshot_for_orchestration(experiment_id)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found",
        )

    if snapshot["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized experiment access",
        )

    with get_connection() as conn:
        return orchestrate_entry(
            snapshot=snapshot,
            conn=conn,
        )