"""Seed learning content

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None

CONTENT = [
    {
        "id": uuid.uuid4(),
        "title": "إدارة الوقت بفعالية بأسلوب بومودورو",
        "description": "تعلّم كيف تقسم وقتك لفترات عمل وراحة باستخدام تقنية البومودورو لزيادة الإنتاجية.",
        "content_type": "ARTICLE",
        "url": "https://example.com/pomodoro",
        "category": "إنتاجية",
        "estimated_minutes": 5,
        "created_at": datetime.utcnow()
    },
    {
        "id": uuid.uuid4(),
        "title": "كيف تتغلب على التسويف",
        "description": "دورة مصغرة حول الأسباب النفسية للتسويف وخطوات عملية للتخلص منه.",
        "content_type": "COURSE",
        "url": "https://example.com/procrastination",
        "category": "تطوير الذات",
        "estimated_minutes": 45,
        "created_at": datetime.utcnow()
    },
    {
        "id": uuid.uuid4(),
        "title": "تأثير الهاتف الذكي على النوم",
        "description": "فيديو يشرح لماذا يؤثر الضوء الأزرق المنبعث من الشاشات على جودة نومك.",
        "content_type": "VIDEO",
        "url": "https://example.com/sleep-screen",
        "category": "الصحة الرقمية",
        "estimated_minutes": 12,
        "created_at": datetime.utcnow()
    },
    {
        "id": uuid.uuid4(),
        "title": "كتاب العادات الذرية (ملخص)",
        "description": "ملخص شامل لكتاب العادات الذرية لجيمس كلير، وكيف تبني عادات جيدة وتتخلص من العادات السيئة.",
        "content_type": "BOOK",
        "url": "https://example.com/atomic-habits",
        "category": "عادات",
        "estimated_minutes": 20,
        "created_at": datetime.utcnow()
    },
    {
        "id": uuid.uuid4(),
        "title": "التأمل لتقليل التوتر",
        "description": "مقال تطبيقي حول تمارين التنفس والتأمل التي يمكن القيام بها في أي مكان.",
        "content_type": "ARTICLE",
        "url": "https://example.com/meditation",
        "category": "صحة نفسية",
        "estimated_minutes": 7,
        "created_at": datetime.utcnow()
    }
]

def upgrade() -> None:
    # Cast content_type strings to proper enum format
    content_data = []
    for item in CONTENT:
        item_copy = item.copy()
        # Use the enum value directly - PostgreSQL will handle the conversion
        content_data.append(item_copy)
    
    learning_content_table = sa.table(
        'learning_content',
        sa.column('id', sa.dialects.postgresql.UUID(as_uuid=True)),
        sa.column('title', sa.String),
        sa.column('description', sa.String),
        sa.column('content_type', sa.Enum('ARTICLE', 'VIDEO', 'COURSE', 'BOOK', name='content_type_enum')),
        sa.column('url', sa.String),
        sa.column('category', sa.String),
        sa.column('estimated_minutes', sa.Integer),
        sa.column('created_at', sa.DateTime(timezone=True))
    )
    
    op.bulk_insert(learning_content_table, content_data)


def downgrade() -> None:
    # Remove the seeded data
    op.execute("DELETE FROM learning_content WHERE title IN ('إدارة الوقت بفعالية بأسلوب بومودورو', 'كيف تتغلب على التسويف', 'تأثير الهاتف الذكي على النوم', 'كتاب العادات الذرية (ملخص)', 'التأمل لتقليل التوتر')")
