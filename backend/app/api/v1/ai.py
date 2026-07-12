import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import Users
from app.schemas.ai import (
    ClassificationResponse,
    RiskPredictionResponse,
    InsightResponse,
    InsightItem,
    WeeklyReportGenerateResponse,
    PlanGenerateResponse,
    PlanEventResponse,
    RecommendationGenerateResponse,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

@router.get("/classify", response_model=ClassificationResponse)
@limiter.limit("10/hour")
async def classify_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Classify the current user into a profile type (Balanced, Overwhelmed, Digital Addict, High Performer)."""
    from app.ml.classifier import classify_user
    result = await classify_user(db, current_user.id)
    return ClassificationResponse(
        user_type=result.user_type,
        confidence=result.confidence,
        factors=result.factors,
    )


# ---------------------------------------------------------------------------
# Risk Prediction
# ---------------------------------------------------------------------------

@router.post("/predict-risk", response_model=RiskPredictionResponse)
@limiter.limit("10/hour")
async def predict_addiction_risk(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Predict the current user's digital addiction risk level."""
    from app.ml.risk_predictor import predict_addiction_risk
    result = await predict_addiction_risk(db, current_user.id)
    return RiskPredictionResponse(
        risk_level=result.risk_level,
        risk_score=result.risk_score,
        factors=result.factors,
        recommendations=result.recommendations,
    )


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

@router.get("/insights", response_model=InsightResponse)
@limiter.limit("10/hour")
async def get_ai_insights(
    request: Request,
    refresh: bool = Query(False, description="Force regenerate insights"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Get AI-generated insights about the user's data patterns."""
    from app.services.insight_service import generate_insights, save_insights, get_latest_insights

    if refresh:
        insights = await generate_insights(db, current_user.id)
        await save_insights(db, current_user.id, insights)
        return InsightResponse(
            insights=[
                InsightItem(
                    insight_type=i.insight_type,
                    message=i.message,
                    category=i.category,
                    context_data=i.context_data,
                )
                for i in insights
            ]
        )

    # Try to get cached insights
    cached = await get_latest_insights(db, current_user.id, limit=5)
    if cached:
        return InsightResponse(
            insights=[
                InsightItem(
                    insight_type=c.insight_type,
                    message=c.message,
                    category="general",
                    context_data=c.context_data,
                )
                for c in cached
            ]
        )

    # Generate fresh insights if none cached
    insights = await generate_insights(db, current_user.id)
    await save_insights(db, current_user.id, insights)
    return InsightResponse(
        insights=[
            InsightItem(
                insight_type=i.insight_type,
                message=i.message,
                category=i.category,
                context_data=i.context_data,
            )
            for i in insights
        ]
    )


# ---------------------------------------------------------------------------
# Weekly Report
# ---------------------------------------------------------------------------

@router.post("/weekly-report", response_model=WeeklyReportGenerateResponse)
@limiter.limit("5/hour")
async def generate_weekly_report(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Generate a new AI weekly report for the current user."""
    from app.services.report_generator import generate_weekly_report, save_weekly_report

    report_data = await generate_weekly_report(db, current_user.id)
    saved = await save_weekly_report(db, current_user.id, report_data)
    return saved


# ---------------------------------------------------------------------------
# Smart Plan Generation
# ---------------------------------------------------------------------------

@router.post("/generate-plan", response_model=PlanGenerateResponse)
@limiter.limit("5/hour")
async def generate_smart_plan(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Generate a smart weekly study plan based on the user's goals and tasks."""
    from app.services.plan_generator import generate_study_plan, save_plan_to_planner

    events = await generate_study_plan(db, current_user.id)
    saved = await save_plan_to_planner(db, current_user.id, events)

    return PlanGenerateResponse(
        events=[
            PlanEventResponse(
                title=e.title,
                plan_date=e.plan_date,
                start_time=e.start_time.strftime("%H:%M"),
                end_time=e.end_time.strftime("%H:%M"),
                event_type=e.event_type,
            )
            for e in events
        ],
        message=f"تم إنشاء خطة مكونة من {len(events)} أحداث بنجاح.",
    )


# ---------------------------------------------------------------------------
# Content Recommendations
# ---------------------------------------------------------------------------

@router.post("/recommendations/generate", response_model=RecommendationGenerateResponse)
@limiter.limit("10/hour")
async def generate_content_recommendations(
    request: Request,
    limit: int = Query(10, ge=1, le=30, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Generate personalized content recommendations for the user."""
    from app.ml.recommender import generate_recommendations, save_recommendations

    recs = await generate_recommendations(db, current_user.id, limit=limit)
    saved = await save_recommendations(db, current_user.id, recs)

    return RecommendationGenerateResponse(
        message=f"تم إنشاء {len(saved)} توصيات بنجاح.",
        count=len(saved),
    )
