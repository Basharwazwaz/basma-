from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.dashboard import DashboardSummaryResponse
from app.services import dashboard_service

router = APIRouter()

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Retrieve aggregated data for the dashboard."""
    return dashboard_service.get_dashboard_summary(db, current_user.id)
