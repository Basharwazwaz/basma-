import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.analytics import WeeklyReports


async def get_weekly_reports(
    db: AsyncSession, user_id: uuid.UUID
) -> List[WeeklyReports]:
    """Return all weekly reports for a user, newest first."""
    result = await db.execute(
        select(WeeklyReports)
        .where(WeeklyReports.user_id == user_id)
        .order_by(WeeklyReports.start_date.desc())
    )
    return result.scalars().all()
