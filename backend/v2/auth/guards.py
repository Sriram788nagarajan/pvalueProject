from fastapi import HTTPException, status

def require_experiment_owner(snapshot: dict, user_id):
    if snapshot["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this experiment",
        )
    

def forbid_if_completed(snapshot: dict):
    if snapshot.get("current_status") == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment is completed and read-only",
        )