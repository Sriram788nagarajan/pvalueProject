"""
ORCHESTRATION CONTRACTS (LOCKED)

- Orchestration reads snapshot state, never mutates experiment logic
- Orchestration is deterministic and reversible
- All disabled paths must return a reason
- Re-entry must be explainable using snapshot + events
"""