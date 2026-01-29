# backend/v2/cache/dashboard_cache.py

from typing import Dict, List
from threading import Lock

# In-memory cache
_DASHBOARD_CACHE: Dict[str, List[dict]] = {}
_LOCK = Lock()


def get_dashboard_cache(user_id: str):
    with _LOCK:
        return _DASHBOARD_CACHE.get(user_id)


def set_dashboard_cache(user_id: str, data: List[dict]):
    with _LOCK:
        _DASHBOARD_CACHE[user_id] = data


def invalidate_dashboard_cache(user_id: str):
    with _LOCK:
        _DASHBOARD_CACHE.pop(user_id, None)