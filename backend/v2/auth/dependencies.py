from fastapi import Header, HTTPException, status
from typing import Dict, Any, Optional

from backend.v2.auth.jwt_verifier import verify_supabase_jwt, InvalidAuthToken


def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    FastAPI dependency that enforces authentication via Supabase JWT.

    Returns:
        Decoded JWT payload (user context)

    Raises:
        HTTPException(401) if missing or invalid token
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = verify_supabase_jwt(token)
        return payload

    except InvalidAuthToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
