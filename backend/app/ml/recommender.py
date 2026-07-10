"""
Content Recommendation Engine
Recommends learning content based on user interests, goals, and interaction history.
Uses tag matching, category preference, and interaction signals.
"""

import uuid
import json
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.content import LearningContent, Recommendations, UserContentInteraction
from app.models.user import Profiles


@dataclass
class RecommendationItem:
    content_id: uuid.UUID
    score: float
    reason: str


async def get_user_interests(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """Extract user interests and preferences from their profile."""
    result = await db.execute(
        select(Profiles).where(Profiles.user_id == user_id)
    )
    profile = result.scalars().first()

    interests = []
    if profile and profile.interests:
        interests = profile.interests if isinstance(profile.interests, list) else []

    return {
        "interests": interests,
        "major": profile.major if profile else None,
    }


async def get_user_interactions(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """Get user's past content interactions."""
    result = await db.execute(
        select(UserContentInteraction).where(UserContentInteraction.user_id == user_id)
    )
    interactions = result.scalars().all()

    viewed = set()
    liked = set()
    completed = set()
    bookmarked = set()

    for i in interactions:
        if i.interaction_type == "view":
            viewed.add(i.content_id)
        elif i.interaction_type == "like":
            liked.add(i.content_id)
        elif i.interaction_type == "complete":
            completed.add(i.content_id)
        elif i.interaction_type == "bookmark":
            bookmarked.add(i.content_id)

    return {
        "viewed": viewed,
        "liked": liked,
        "completed": completed,
        "bookmarked": bookmarked,
    }


def _compute_content_score(
    content: LearningContent,
    interests: List[str],
    interactions: dict,
) -> tuple[float, str]:
    """Compute a relevance score for a content item against user profile."""
    score = 0.0
    reasons = []

    # Tag matching (0-40 points)
    content_tags = []
    if content.tags:
        try:
            content_tags = json.loads(content.tags) if isinstance(content.tags, str) else content.tags
        except (json.JSONDecodeError, TypeError):
            content_tags = [t.strip() for t in content.tags.split(",")] if content.tags else []

    tag_overlap = len(set(interests) & set(content_tags))
    if tag_overlap > 0:
        tag_score = min(40, tag_overlap * 15)
        score += tag_score
        reasons.append(f"يتوافق مع اهتماماتك ({tag_overlap} تطابق)")

    # Category matching with major (0-20 points)
    if content.category:
        category_lower = content.category.lower()
        for interest in interests:
            if interest.lower() in category_lower or category_lower in interest.lower():
                score += 20
                reasons.append(f"متعلق بـ {content.category}")
                break

    # Novelty bonus — content not yet viewed (0-20 points)
    if content.id not in interactions.get("viewed", set()):
        score += 20
        reasons.append("محتوى جديد لم تشاهده بعد")
    
    # Engagement bonus — liked/completed content signals preference (0-10 points)
    if content.id in interactions.get("liked", set()):
        score += 10
        reasons.append("أعجبك محتوى مشابه")

    # Popularity heuristic (0-10 points) — newer content gets slight boost
    score += 10

    reason = reasons[0] if reasons else "محتوى مقترح لك"
    return min(100, score), reason


async def generate_recommendations(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 10,
) -> List[RecommendationItem]:
    """
    Generate personalized content recommendations.
    Returns top-N content items ranked by relevance score.
    """
    user_data = await get_user_interests(db, user_id)
    interactions = await get_user_interactions(db, user_id)

    # Fetch all content
    content_result = await db.execute(
        select(LearningContent).order_by(LearningContent.created_at.desc())
    )
    all_content = content_result.scalars().all()

    if not all_content:
        return []

    # Score each content item
    scored: List[RecommendationItem] = []
    for content in all_content:
        # Skip already completed content
        if content.id in interactions.get("completed", set()):
            continue

        score, reason = _compute_content_score(content, user_data["interests"], interactions)
        scored.append(RecommendationItem(
            content_id=content.id,
            score=score,
            reason=reason,
        ))

    # Sort by score descending
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:limit]


async def save_recommendations(
    db: AsyncSession,
    user_id: uuid.UUID,
    recommendations: List[RecommendationItem],
) -> List[Recommendations]:
    """Persist generated recommendations to the database."""
    saved = []
    for rec in recommendations:
        db_rec = Recommendations(
            user_id=user_id,
            content_id=rec.content_id,
            reason=rec.reason,
            score=rec.score,
        )
        db.add(db_rec)
        saved.append(db_rec)

    await db.commit()
    for rec in saved:
        await db.refresh(rec)
    return saved
