# backend/v2/auth/jwt_verifier.py

import os
import requests
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError


class InvalidAuthToken(Exception):
    pass


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")



if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY missing")


_JWKS_CACHE = None


def get_jwks():
    global _JWKS_CACHE

    if _JWKS_CACHE is not None:
        return _JWKS_CACHE

    jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"


    response = requests.get(
        jwks_url,
        headers={
            "apikey": SUPABASE_ANON_KEY
        },
        timeout=5,
    )

    response.raise_for_status()

    _JWKS_CACHE = response.json()
    return _JWKS_CACHE


def verify_supabase_jwt(token: str):
    try:
        jwks = get_jwks()

        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise InvalidAuthToken("Missing kid in JWT header")

        key = next(
            (k for k in jwks["keys"] if k["kid"] == kid),
            None
        )

        if not key:
            raise InvalidAuthToken("Public key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )

        return payload

    except ExpiredSignatureError:
        raise InvalidAuthToken("Token expired")

    except JWTError as e:
        raise InvalidAuthToken(str(e))
