from uuid import UUID
from fastapi import HTTPException, status

def get_user_id_from_jwt(current_user: dict) -> UUID:
    try:
        return UUID(current_user["sub"])
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity",
        )