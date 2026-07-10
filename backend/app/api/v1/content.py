import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.content import LearningContentResponse, RecommendationResponse
from app.schemas.ai import ContentInteractionCreate, ContentInteractionResponse
from app.services import content_service

router = APIRouter()


@router.get("/", response_model=List[LearningContentResponse])
async def get_all_content(
    content_type: Optional[str] = Query(None, description="Filter by content type (e.g., COURSE, ARTICLE)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve all learning content with optional filtering and search."""
    return await content_service.get_all_content(db, content_type, category, search)


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_user_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve personalized content recommendations for the user."""
    return await content_service.get_user_recommendations(db, current_user.id)


@router.get("/bookmarks", response_model=List[RecommendationResponse])
async def get_bookmarked_content(
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve user's bookmarked content."""
    return await content_service.get_bookmarked_content(db, current_user.id)


@router.get("/{content_id}", response_model=LearningContentResponse)
async def get_content(
    content_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Retrieve a specific learning content item."""
    content = await content_service.get_content_by_id(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.post("/{content_id}/interact", response_model=ContentInteractionResponse)
async def interact_with_content(
    content_id: uuid.UUID,
    interaction_in: ContentInteractionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Record a user interaction with content (view, like, complete, bookmark)."""
    return await content_service.record_interaction(db, current_user.id, content_id, interaction_in.interaction_type)


@router.get("/{content_id}/interactions", response_model=List[ContentInteractionResponse])
async def get_content_interactions(
    content_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get the user's interactions with a specific content item."""
    return await content_service.get_content_interactions(db, current_user.id, content_id)


@router.delete("/recommendations/{recommendation_id}/dismiss", response_model=RecommendationResponse)
async def dismiss_recommendation(
    recommendation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Dismiss a recommendation so it doesn't show up again."""
    return await content_service.dismiss_recommendation(db, current_user.id, recommendation_id)
