"""
Admin endpoints for content and user management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.session import get_db
from app.api.deps import get_admin_user
from app.models.user import Users
from app.models.content import LearningContent
from app.models.gamification import Challenges
from app.schemas.content import ContentCreate, ContentResponse
from app.schemas.gamification import ChallengeResponse, ChallengeCreate, ChallengeUpdate

router = APIRouter()


@router.get("/admin/users", response_model=List[dict])
async def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(
        select(Users).offset(skip).limit(limit).order_by(Users.created_at.desc())
    )
    users = result.scalars().all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.get("/admin/users/count")
async def admin_user_count(
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(select(func.count(Users.id)))
    count = result.scalar()
    return {"total_users": count}


@router.put("/admin/users/{user_id}/deactivate")
async def admin_deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(select(Users).where(Users.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    return {"status": "deactivated", "user_id": user_id}


# ── Content Management ─────────────────────────────────────────────


@router.get("/admin/content", response_model=List[ContentResponse])
async def admin_list_content(
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(
        select(LearningContent).order_by(LearningContent.created_at.desc())
    )
    return result.scalars().all()


def _map_content_data(data: dict) -> dict:
    """Map schema field names to model column names."""
    mapped = {}
    field_map = {"difficulty": "difficulty_level"}
    for k, v in data.items():
        if v is None:
            continue
        col = field_map.get(k, k)
        if col == "tags" and not isinstance(v, str):
            import json
            v = json.dumps(v, ensure_ascii=False)
        mapped[col] = v
    return mapped


@router.post("/admin/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_content(
    content_in: ContentCreate,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    data = _map_content_data(content_in.model_dump(exclude_unset=True))
    content = LearningContent(**data)
    db.add(content)
    await db.commit()
    await db.refresh(content)
    return content


@router.put("/admin/content/{content_id}", response_model=ContentResponse)
async def admin_update_content(
    content_id: str,
    content_in: ContentCreate,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(select(LearningContent).where(LearningContent.id == content_id))
    content = result.scalars().first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    data = _map_content_data(content_in.model_dump(exclude_unset=True))
    for field, value in data.items():
        setattr(content, field, value)

    await db.commit()
    await db.refresh(content)
    return content


@router.delete("/admin/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(select(LearningContent).where(LearningContent.id == content_id))
    content = result.scalars().first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    await db.delete(content)
    await db.commit()


@router.post("/admin/content/seed")
async def admin_seed_content(
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    """Seed sample learning content for development/testing."""
    existing = await db.execute(select(func.count(LearningContent.id)))
    if existing.scalar() > 0:
        return {"message": "Content already exists"}

    samples = [
        LearningContent(
            title="أساسيات Python",
            description="دورة شاملة في لغة بايثون للمبتدئين",
            content_type="COURSE",
            category="programming",
            tags='["programming", "python", "beginner"]',
            difficulty_level="BEGINNER",
            url="https://example.com/python-basics",
        ),
        LearningContent(
            title="مقدمة في الذكاء الاصطناعي",
            description="تعلم أساسيات AI و Machine Learning",
            content_type="VIDEO",
            category="ai",
            tags='["ai", "machine-learning", "data-science"]',
            difficulty_level="INTERMEDIATE",
            url="https://example.com/ai-intro",
        ),
        LearningContent(
            title="كيف تبدأ مشروعك الخاص",
            description="دليل خطوة بخطوة لريادة الأعمال",
            content_type="ARTICLE",
            category="business",
            tags='["business", "entrepreneurship", "startup"]',
            difficulty_level="BEGINNER",
            url="https://example.com/start-business",
        ),
        LearningContent(
            title="إدارة الوقت بفعالية",
            description="تقنيات وأدوات لتحسين إدارة وقتك",
            content_type="BOOK",
            category="productivity",
            tags='["productivity", "time-management", "focus"]',
            difficulty_level="BEGINNER",
            url="https://example.com/time-management",
        ),
        LearningContent(
            title="تعلّم JavaScript من الصفر",
            description="دورة تفاعلية في JavaScript للمبتدئين",
            content_type="COURSE",
            category="programming",
            tags='["programming", "javascript", "web"]',
            difficulty_level="BEGINNER",
            url="https://example.com/js-basics",
        ),
    ]

    for c in samples:
        db.add(c)
    await db.commit()
    return {"message": f"Seeded {len(samples)} content items"}


# ── Challenge Management ────────────────────────────────────────────


@router.get("/admin/challenges", response_model=List[ChallengeResponse])
async def admin_list_challenges(
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(
        select(Challenges).order_by(Challenges.created_at.desc())
    )
    return result.scalars().all()


@router.post("/admin/challenges", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_challenge(
    challenge_in: ChallengeCreate,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    challenge = Challenges(**challenge_in.model_dump())
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)
    return challenge


@router.put("/admin/challenges/{challenge_id}", response_model=ChallengeResponse)
async def admin_update_challenge(
    challenge_id: str,
    challenge_in: ChallengeUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(select(Challenges).where(Challenges.id == challenge_id))
    challenge = result.scalars().first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    for field, value in challenge_in.model_dump(exclude_unset=True).items():
        setattr(challenge, field, value)

    await db.commit()
    await db.refresh(challenge)
    return challenge


@router.delete("/admin/challenges/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_challenge(
    challenge_id: str,
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    result = await db.execute(select(Challenges).where(Challenges.id == challenge_id))
    challenge = result.scalars().first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    await db.delete(challenge)
    await db.commit()


@router.post("/admin/challenges/seed")
async def admin_seed_challenges(
    db: AsyncSession = Depends(get_db),
    admin: Users = Depends(get_admin_user),
):
    existing = await db.execute(select(func.count(Challenges.id)))
    if existing.scalar() > 0:
        return {"message": "Challenges already exist"}

    samples = [
        Challenges(title="تحدي القراءة ٣٠ يومًا", description="اقرأ ٢٠ دقيقة يوميًا لمدة شهر", category="تعلّم", duration_days=30, points_reward=100),
        Challenges(title="تحدي المشي اليومي", description="امشِ ٣٠ دقيقة كل يوم لمدة أسبوع", category="صحة", duration_days=7, points_reward=50),
        Challenges(title="تحدي تصفير السوشال ميديا", description="قلّل استخدام وسائل التواصل لـ ٣٠ دقيقة يوميًا", category="رفاه", duration_days=14, points_reward=75),
        Challenges(title="تحدي النوم المنتظم", description="نم ٨ ساعات يوميًا لمدة ٢١ يومًا", category="صحة", duration_days=21, points_reward=150),
        Challenges(title="تحدي الإنجاز اليومي", description="أنجز ٣ مهام يوميًا لمدة أسبوع", category="إنجاز", duration_days=7, points_reward=60),
    ]
    for c in samples:
        db.add(c)
    await db.commit()
    return {"message": f"Seeded {len(samples)} challenges"}
