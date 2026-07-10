import uuid
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.content import LearningContent, Recommendations, UserContentInteraction


async def get_all_content(
    db: AsyncSession,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[LearningContent]:
    stmt = select(LearningContent)

    if content_type:
        stmt = stmt.where(LearningContent.content_type == content_type)
    if category:
        stmt = stmt.where(LearningContent.category == category)
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            LearningContent.title.ilike(search_pattern)
            | LearningContent.description.ilike(search_pattern)
        )

    stmt = stmt.order_by(LearningContent.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_content_by_id(
    db: AsyncSession, content_id: uuid.UUID
) -> Optional[LearningContent]:
    result = await db.execute(
        select(LearningContent).where(LearningContent.id == content_id)
    )
    return result.scalars().first()


async def get_user_recommendations(
    db: AsyncSession, user_id: uuid.UUID
) -> List[Recommendations]:
    stmt = (
        select(Recommendations)
        .options(selectinload(Recommendations.content))
        .where(
            Recommendations.user_id == user_id,
            Recommendations.is_dismissed == False,  # noqa: E712
        )
        .order_by(Recommendations.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_bookmarked_content(
    db: AsyncSession, user_id: uuid.UUID
) -> List[Recommendations]:
    """Get user's bookmarked content via UserContentInteraction."""
    stmt = (
        select(UserContentInteraction)
        .options(selectinload(UserContentInteraction.content))
        .where(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.interaction_type == "bookmark",
        )
        .order_by(UserContentInteraction.created_at.desc())
    )
    result = await db.execute(stmt)
    interactions = result.scalars().all()

    # Convert interactions to Recommendation-like responses for the frontend
    bookmarks = []
    for inter in interactions:
        if inter.content:
            rec = Recommendations(
                user_id=user_id,
                content_id=inter.content_id,
                reason="محفوظ في قائمة المفضلة",
                is_dismissed=False,
            )
            rec.content = inter.content
            bookmarks.append(rec)
    return bookmarks


async def dismiss_recommendation(
    db: AsyncSession, user_id: uuid.UUID, recommendation_id: uuid.UUID
) -> Recommendations:
    result = await db.execute(
        select(Recommendations).where(
            Recommendations.id == recommendation_id,
            Recommendations.user_id == user_id,
        )
    )
    db_rec = result.scalars().first()

    if not db_rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    db_rec.is_dismissed = True
    await db.commit()
    await db.refresh(db_rec)
    return db_rec


async def record_interaction(
    db: AsyncSession,
    user_id: uuid.UUID,
    content_id: uuid.UUID,
    interaction_type: str,
) -> UserContentInteraction:
    """Record a user interaction with content."""
    if interaction_type not in ("view", "like", "complete", "bookmark"):
        raise HTTPException(status_code=400, detail="Invalid interaction type")

    # Check content exists
    content = await get_content_by_id(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check for existing interaction of same type
    existing = await db.execute(
        select(UserContentInteraction).where(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.content_id == content_id,
            UserContentInteraction.interaction_type == interaction_type,
        )
    )
    existing_interaction = existing.scalars().first()

    if existing_interaction:
        # Toggle off (unlike, unbookmark)
        if interaction_type in ("like", "bookmark"):
            await db.delete(existing_interaction)
            await db.commit()
            raise HTTPException(status_code=200, detail=f"Removed {interaction_type}")
        # For view and complete, return existing
        return existing_interaction

    # Create new interaction
    interaction = UserContentInteraction(
        user_id=user_id,
        content_id=content_id,
        interaction_type=interaction_type,
    )
    db.add(interaction)
    await db.commit()
    await db.refresh(interaction)
    return interaction


async def get_content_interactions(
    db: AsyncSession,
    user_id: uuid.UUID,
    content_id: uuid.UUID,
) -> List[UserContentInteraction]:
    """Get all of a user's interactions with a specific content item."""
    result = await db.execute(
        select(UserContentInteraction).where(
            UserContentInteraction.user_id == user_id,
            UserContentInteraction.content_id == content_id,
        )
    )
    return result.scalars().all()
