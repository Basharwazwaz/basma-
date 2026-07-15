import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.analytics import WeeklyReportResponse
from app.services import weekly_report_service

router = APIRouter()


@router.get("/", response_model=List[WeeklyReportResponse])
async def get_weekly_reports(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve all weekly reports for the current user."""
    return await weekly_report_service.get_weekly_reports(db, current_user.id)


@router.post("/generate", response_model=WeeklyReportResponse)
async def generate_weekly_report(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Generate a new weekly report based on real user data for the past 7 days."""
    return await weekly_report_service.generate_weekly_report(db, current_user.id)
