"""
Setup script: creates admin user + seeds learning content.
Run: python scripts/setup_admin_content.py
"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import app.models.user
import app.models.health
import app.models.productivity
import app.models.gamification
import app.models.content
import app.models.coach
import app.models.notifications
import app.models.analytics

from app.db.session import _get_session_local
from app.models.user import Users
from app.models.content import LearningContent
from app.core.security import get_password_hash
from sqlalchemy import select, func


async def main():
    session = _get_session_local()
    async with session() as db:
        # ── Admin ───────────────────────────────────────────
        admin = await db.execute(select(Users).where(Users.role == 'ADMIN'))
        admin_user = admin.scalars().first()
        if not admin_user:
            existing = await db.execute(select(Users).where(Users.email == 'admin@basma.com'))
            existing_user = existing.scalars().first()
            if existing_user:
                existing_user.role = 'ADMIN'
                print(f'Promoted {existing_user.email} to ADMIN')
            else:
                new_admin = Users(
                    email='admin@basma.com',
                    hashed_password=get_password_hash('Admin123!'),
                    role='ADMIN'
                )
                db.add(new_admin)
                print(f'Created admin: admin@basma.com / Admin123!')
        else:
            print(f'Admin exists: {admin_user.email}')

        # ── Learning Content ────────────────────────────────
        count = (await db.execute(select(func.count(LearningContent.id)))).scalar()
        print(f'Existing content: {count}')
        if count == 0:
            samples = [
                ('أساسيات Python', 'دورة شاملة في لغة بايثون للمبتدئين', 'COURSE', 'programming', 'BEGINNER'),
                ('مقدمة في الذكاء الاصطناعي', 'تعلم أساسيات AI و Machine Learning', 'VIDEO', 'ai', 'INTERMEDIATE'),
                ('كيف تبدأ مشروعك الخاص', 'دليل خطوة بخطوة لريادة الأعمال', 'ARTICLE', 'business', 'BEGINNER'),
                ('إدارة الوقت بفعالية', 'استراتيجيات عملية لتنظيم وقتك وزيادة إنتاجيتك', 'ARTICLE', 'productivity', 'BEGINNER'),
                ('تصميم واجهات المستخدم', 'تعلم مبادئ UX/UI مع Figma', 'COURSE', 'design', 'INTERMEDIATE'),
                ('العناية بالصحة النفسية', 'نصائح وإرشادات يومية', 'ARTICLE', 'health', 'BEGINNER'),
                ('تطوير تطبيقات الويب', 'دورة HTML, CSS, JavaScript', 'COURSE', 'programming', 'BEGINNER'),
                ('مهارات التواصل الفعال', 'ابنِ علاقات ناجحة وتواصل بثقة', 'BOOK', 'soft-skills', 'BEGINNER'),
                ('تحليل البيانات بـ Python', 'Pandas, NumPy و Matplotlib', 'VIDEO', 'data-science', 'ADVANCED'),
                ('مقدمة في الأمن السيبراني', 'أساسيات حماية المعلومات', 'BOOK', 'security', 'INTERMEDIATE'),
                ('التحدث أمام الجمهور', 'كيف تقدّم عروضاً مؤثرة', 'VIDEO', 'soft-skills', 'BEGINNER'),
                ('مقدمة في تطبيقات الموبايل', 'بناء تطبيقات Android و iOS', 'COURSE', 'programming', 'ADVANCED'),
                ('التسويق الرقمي', 'استراتيجيات التسويق عبر وسائل التواصل', 'ARTICLE', 'business', 'INTERMEDIATE'),
                ('علم النفس الإيجابي', 'كيف تنمي عقليّة النجاح', 'BOOK', 'health', 'BEGINNER'),
                ('إدارة المشاريع', 'منهجيات Agile و Scrum', 'VIDEO', 'business', 'INTERMEDIATE'),
            ]
            for title, desc, ctype, cat, diff in samples:
                db.add(LearningContent(
                    title=title,
                    description=desc,
                    content_type=ctype,
                    category=cat,
                    difficulty_level=diff,
                    tags='[]',
                ))
            await db.commit()
            print(f'Seeded {len(samples)} content items')
        else:
            print('Content exists, skipping')

    await db.commit()

asyncio.run(main())
print('Setup complete!')
