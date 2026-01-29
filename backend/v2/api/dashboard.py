
from fastapi import APIRouter,Depends
from backend.v2.services.dashboard_service import (
    list_experiments_for_dashboard as fetch_dashboard_experiments
)
from backend.v2.auth.dependencies import get_current_user


from backend.v2.models.dashboard import DashboardExperimentListResponse
from backend.v2.auth.utils import get_user_id_from_jwt

#router = APIRouter(prefix="/v2/experiments", tags=["Dashboard"])
router = APIRouter(prefix="/v2/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardExperimentListResponse)
def list_experiments_for_dashboard(current_user = Depends(get_current_user)):
    user_id = get_user_id_from_jwt(current_user)
    experiments = fetch_dashboard_experiments(user_id)

    return {
        "experiments": experiments,
        "total": len(experiments),
    }


