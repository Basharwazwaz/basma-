import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.models.coach import CoachMessages
from app.schemas.coach import MessageCreate
from app.core.config import settings

# Attempt to import google-genai
try:
    from google import genai
    from google.genai import types
    has_gemini = True
except ImportError:
    has_gemini = False


async def get_chat_history(db: AsyncSession, user_id: uuid.UUID) -> List[CoachMessages]:
    """Retrieve all chat messages for a user, ordered by creation time."""
    result = await db.execute(
        select(CoachMessages)
        .filter(CoachMessages.user_id == user_id)
        .order_by(CoachMessages.created_at.asc())
    )
    return result.scalars().all()


async def clear_chat_history(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Delete all chat messages for a user."""
    await db.execute(
        delete(CoachMessages).where(CoachMessages.user_id == user_id)
    )
    await db.commit()


async def chat_with_coach(db: AsyncSession, user_id: uuid.UUID, message_in: MessageCreate) -> CoachMessages:
    """
    Process a user message, save it, call the AI model to get a response, save and return the AI's response.
    """
    # 1. Save user message
    user_msg = CoachMessages(
        user_id=user_id,
        role="user",
        content=message_in.content
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # 2. Get history for context
    history = await get_chat_history(db, user_id)
    
    # 3. Call AI
    ai_response_text = ""
    
    if not has_gemini or not settings.GEMINI_API_KEY:
        # Fallback if no API key or package
        ai_response_text = (
            "مرحباً! أنا المدرب الذكي لبصمة+. عذراً، لا يمكنني التفكير حالياً بسبب عدم "
            "إعداد مفتاح `GEMINI_API_KEY` في الإعدادات أو عدم توفر المكتبة. "
            "يرجى التواصل مع المطور لإعدادي!"
        )
    else:
        try:
            # Initialize client
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            # Prepare contents
            contents = []
            
            # Add system prompt as the first message context
            system_instruction = (
                "أنت مدرب ذكي (AI Coach) في تطبيق بصمة+، وهو تطبيق يساعد الشباب على تطوير مهاراتهم "
                "الإنتاجية والصحية والرقمية والتعلم. تحدث باللغة العربية بأسلوب مشجع وإيجابي، "
                "وقدم نصائح عملية ومختصرة."
            )
            
            # Map roles to Gemini roles ('user' or 'model')
            # History includes the user's message we just saved
            for msg in history:
                role = "user" if msg.role == "user" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.content)]
                    )
                )

            # Generate response
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            
            ai_response_text = response.text if response.text else "لم أستطع فهم ذلك. هل يمكنك إعادة الصياغة؟"
            
        except Exception as e:
            # Fallback on error
            print(f"Gemini API Error: {e}")
            ai_response_text = "عذراً، حدث خطأ أثناء معالجة طلبك عبر الذكاء الاصطناعي. المرجو المحاولة لاحقاً."

    # 4. Save AI message
    ai_msg = CoachMessages(
        user_id=user_id,
        role="ai",
        content=ai_response_text
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    return ai_msg
