
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
    import time
    start = time.time()
    
    user_id = get_user_id_from_jwt(current_user)
    print(f">>> DASHBOARD: User ID extracted in {(time.time() - start)*1000:.2f}ms")
    
    checkpoint = time.time()
    experiments = fetch_dashboard_experiments(user_id)
    print(f">>> DASHBOARD: Query took {(time.time() - checkpoint)*1000:.2f}ms")
    print(f">>> DASHBOARD: Returned {len(experiments)} experiments")
    
    checkpoint = time.time()
    result = {
        "experiments": experiments,
        "total": len(experiments),
    }
    print(f">>> DASHBOARD: Serialization took {(time.time() - checkpoint)*1000:.2f}ms")
    print(f">>> DASHBOARD: TOTAL TIME: {(time.time() - start)*1000:.2f}ms")
    
    return result

