import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest
from app.ml.recommender import generate_recommendations, _compute_content_score, _extract_tags
from app.models.content import LearningContent


def make_content(id=None, tags=None, category=None):
    content = MagicMock(spec=LearningContent)
    content.id = id or str(uuid.uuid4())
    content.tags = tags
    content.category = category
    return content


def test_compute_content_score_matching_tags():
    content = make_content(tags=["programming", "python", "web"], category="technology")
    interests = ["programming", "python"]
    interactions = {"viewed": set(), "liked": set(), "completed": set(), "bookmarked": set()}
    content_tags = _extract_tags(content)

    score, reason = _compute_content_score(content, content_tags, "programming python", interests, interactions, None)

    assert score > 40
    assert "تطابق" in reason or "محتوى جديد" in reason


def test_compute_content_score_no_match():
    content = make_content(tags=["design", "art"], category="creative")
    interests = ["programming", "python"]
    interactions = {"viewed": set(), "liked": set(), "completed": set(), "bookmarked": set()}
    content_tags = _extract_tags(content)

    score, reason = _compute_content_score(content, content_tags, "programming python", interests, interactions, None)

    assert score < 60


def test_compute_content_score_completed_content():
    content_id = str(uuid.uuid4())
    content = make_content(id=content_id, tags=["python"], category="technology")
    interests = ["python"]
    interactions = {"viewed": {content_id}, "liked": set(), "completed": {content_id}, "bookmarked": set()}
    content_tags = _extract_tags(content)

    score, reason = _compute_content_score(content, content_tags, "python", interests, interactions, None)

    assert score >= 0


@pytest.mark.asyncio
async def test_generate_recommendations_empty_content():
    mock_db = AsyncMock()
    profile_result = MagicMock()
    profile_result.scalars.return_value.first.return_value = MagicMock(interests=["programming"], major=None)

    interactions_result = MagicMock()
    interactions_result.scalars.return_value.all.return_value = []

    content_result = MagicMock()
    content_result.scalars.return_value.all.return_value = []

    mock_db.execute.side_effect = [profile_result, interactions_result, content_result]

    result = await generate_recommendations(mock_db, str(uuid.uuid4()), limit=5)

    assert len(result) == 0
