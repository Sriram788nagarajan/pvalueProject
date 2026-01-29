def build_entry_context(snapshot: dict) -> dict:
    """
    Builds optional UX context for re-entry.
    """

    if not snapshot.get("last_seen_at"):
        return {}

    return {
        "last_seen": {
            "phase": snapshot.get("last_seen_phase"),
            "step": snapshot.get("last_seen_step"),
            "at": snapshot.get("last_seen_at"),
        }
    }