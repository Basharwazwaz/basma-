import uuid
from datetime import date, datetime
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from app.ml.classifier import classify_user, ClassificationResult
from app.ml.risk_predictor import predict_addiction_risk, RiskPrediction


@pytest.mark.asyncio
async def test_classify_user_no_data():
    """Test classification with no user data returns BALANCED with low confidence."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await classify_user(mock_db, uuid.uuid4())

    assert result.user_type == "BALANCED"
    assert result.confidence <= 0.5
    assert "message" in result.factors


@pytest.mark.asyncio
async def test_risk_predictor_no_data():
    """Test risk prediction with no data returns MEDIUM risk."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result

    result = await predict_addiction_risk(mock_db, uuid.uuid4())

    assert result.risk_level == "MEDIUM"
    assert result.risk_score == 50.0
    assert len(result.recommendations) > 0
