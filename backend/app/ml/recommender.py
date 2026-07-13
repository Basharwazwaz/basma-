"""
Content Recommendation Engine
Recommends learning content based on user interests, goals, and interaction history.
Uses TF-IDF cosine similarity from scikit-learn for semantic tag matching.
"""
import json
import os
import pickle
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.content import LearningContent, Recommendations, UserContentInteraction
from app.models.user import Profiles

VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "trained", "recommender_vectorizer.pkl")

_vectorizer_cache = None


def _load_vectorizer():
    global _vectorizer_cache
    if _vectorizer_cache is not None:
        return _vectorizer_cache
    try:
        with open(VECTORIZER_PATH, "rb") as f:
            _vectorizer_cache = pickle.load(f)
        return _vectorizer_cache
    except (FileNotFoundError, pickle.UnpicklingError, EOFError):
        return None


@dataclass
class RecommendationItem:
    content_id: str
    score: float
    reason: str


async def get_user_interests(db: AsyncSession, user_id: str) -> dict:
    result = await db.execute(
        select(Profiles).where(Profiles.user_id == user_id)
    )
    profile = result.scalars().first()

    interests = []
    if profile and profile.interests:
        if isinstance(profile.interests, list):
            interests = profile.interests
        elif isinstance(profile.interests, str):
            try:
                interests = json.loads(profile.interests)
            except (json.JSONDecodeError, TypeError):
                interests = [t.strip() for t in profile.interests.split(",")]

    return {
        "interests": interests,
        "major": profile.major if profile else None,
    }


async def get_user_interactions(db: AsyncSession, user_id: str) -> dict:
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

    return {"viewed": viewed, "liked": liked, "completed": completed, "bookmarked": bookmarked}


def _extract_tags(content: LearningContent) -> List[str]:
    if not content.tags:
        return []
    if isinstance(content.tags, list):
        return content.tags
    if isinstance(content.tags, str):
        try:
            parsed = json.loads(content.tags)
            return parsed if isinstance(parsed, list) else [t.strip() for t in content.tags.split(",")]
        except (json.JSONDecodeError, TypeError):
            return [t.strip() for t in content.tags.split(",")]
    return []


def _compute_content_score(
    content: LearningContent,
    content_tags: List[str],
    user_text: str,
    interests: List[str],
    interactions: dict,
    vectorizer_data: Optional[dict],
) -> tuple[float, str]:
    score = 0.0
    reasons = []

    tag_overlap = len(set(interests) & set(content_tags))
    if tag_overlap > 0:
        tag_score = min(40, tag_overlap * 15)
        score += tag_score
        reasons.append(f"يتوافق مع اهتماماتك ({tag_overlap} تطابق)")

    if content.category:
        category_lower = content.category.lower()
        for interest in interests:
            if interest.lower() in category_lower or category_lower in interest.lower():
                score += 20
                reasons.append(f"متعلق بـ {content.category}")
                break

    if vectorizer_data and content_tags:
        try:
            vectorizer = vectorizer_data["vectorizer"]
            content_vec = vectorizer.transform([" ".join(content_tags)])
            user_vec = vectorizer.transform([user_text])
            sim = cosine_similarity(content_vec, user_vec)[0][0]
            semantic_score = int(sim * 25)
            if semantic_score > 5:
                score += semantic_score
                reasons.append(f"تشابه دلالي {semantic_score}%")
        except Exception:
            pass

    if content.id not in interactions.get("viewed", set()):
        score += 15
        reasons.append("محتوى جديد لم تشاهده بعد")

    if content.id in interactions.get("liked", set()):
        score += 10
        reasons.append("أعجبك محتوى مشابه")

    score += 5

    reason = reasons[0] if reasons else "محتوى مقترح لك"
    return min(100, score), reason


async def generate_recommendations(
    db: AsyncSession,
    user_id: str,
    limit: int = 10,
) -> List[RecommendationItem]:
    user_data = await get_user_interests(db, user_id)
    interactions = await get_user_interactions(db, user_id)

    content_result = await db.execute(
        select(LearningContent).order_by(LearningContent.created_at.desc())
    )
    all_content = content_result.scalars().all()

    if not all_content:
        return []

    interests = user_data["interests"]
    major = user_data["major"]
    user_text_parts = list(interests)
    if major:
        user_text_parts.append(major)
    user_text = " ".join(user_text_parts)

    vectorizer_data = _load_vectorizer()

    scored: List[RecommendationItem] = []
    for content in all_content:
        if content.id in interactions.get("completed", set()):
            continue

        content_tags = _extract_tags(content)
        score, reason = _compute_content_score(
            content, content_tags, user_text, interests, interactions, vectorizer_data,
        )
        scored.append(RecommendationItem(
            content_id=content.id,
            score=score,
            reason=reason,
        ))

    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:limit]


async def save_recommendations(
    db: AsyncSession,
    user_id: str,
    recommendations: List[RecommendationItem],
) -> List[Recommendations]:
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
