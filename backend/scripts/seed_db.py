import asyncio
import uuid
import sys
import os

# Ensure app path is loaded
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import _get_session_local
from app.models.gamification import Challenges
from app.models.content import LearningContent

CHALLENGES_DATA = [
    {
        "title": "أسبوع التخلص من السموم الرقمية",
        "description": "قلل وقت الشاشة إلى أقل من ساعتين يومياً لمدة ٧ أيام.",
        "category": "الصحة الرقمية",
        "duration_days": 7,
        "points_reward": 500
    },
    {
        "title": "قارئ اليوم",
        "description": "اقرأ ٣ مقالات تعليمية هذا الأسبوع.",
        "category": "التعلم",
        "duration_days": 7,
        "points_reward": 200
    },
    {
        "title": "سيد بومودورو",
        "description": "أكمل ١٠ جلسات تركيز (بومودورو) في ٣ أيام.",
        "category": "الإنتاجية",
        "duration_days": 3,
        "points_reward": 300
    },
    {
        "title": "روتين النوم المثالي",
        "description": "نم ٨ ساعات لمدة ٥ أيام متتالية.",
        "category": "الرفاهية",
        "duration_days": 5,
        "points_reward": 400
    },
    {
        "title": "بداية أسبوع قوية",
        "description": "سجل أهدافك الأسبوعية في يوم الأحد.",
        "category": "التنظيم",
        "duration_days": 1,
        "points_reward": 100
    }
]

CONTENT_DATA = [
    {
        "title": "كيف تتغلب على المماطلة",
        "description": "دليل عملي لتنظيم وقتك والتغلب على التسويف.",
        "content_type": "ARTICLE",
        "url": "https://example.com/procrastination",
        "category": "الإنتاجية",
        "estimated_minutes": 10
    },
    {
        "title": "أساسيات البرمجة بلغة بايثون",
        "description": "مقدمة شاملة للغة بايثون للمبتدئين.",
        "content_type": "COURSE",
        "url": "https://example.com/python-basics",
        "category": "البرمجة",
        "estimated_minutes": 180
    },
    {
        "title": "تأمل لمدة ٥ دقائق",
        "description": "مقطع فيديو قصير للاسترخاء والتأمل.",
        "content_type": "VIDEO",
        "url": "https://example.com/meditation",
        "category": "الرفاهية",
        "estimated_minutes": 5
    },
    {
        "title": "كتاب العادات الذرية",
        "description": "كيف تبني عادات جيدة وتتخلص من السيئة.",
        "content_type": "BOOK",
        "url": "https://example.com/atomic-habits",
        "category": "التطوير الشخصي",
        "estimated_minutes": 1200
    },
    {
        "title": "مقدمة في الذكاء الاصطناعي",
        "description": "ما هو الذكاء الاصطناعي وكيف يغير العالم.",
        "content_type": "ARTICLE",
        "url": "https://example.com/intro-to-ai",
        "category": "التقنية",
        "estimated_minutes": 15
    }
]

async def seed_data(db: AsyncSession):
    # Check if we already have challenges
    from sqlalchemy.future import select
    result = await db.execute(select(Challenges).limit(1))
    if result.scalars().first() is not None:
        print("Database already seeded. Skipping.")
        return

    # Seed Challenges
    print("Seeding Challenges...")
    for c_data in CHALLENGES_DATA:
        challenge = Challenges(**c_data)
        db.add(challenge)
        
    # Seed Content
    print("Seeding Learning Content...")
    for c_data in CONTENT_DATA:
        content = LearningContent(**c_data)
        db.add(content)

    await db.commit()
    print("Database seeded successfully.")

async def main():
    async with _get_session_local()() as session:
        await seed_data(session)

if __name__ == "__main__":
    asyncio.run(main())
