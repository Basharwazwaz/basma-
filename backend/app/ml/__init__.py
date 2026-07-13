from app.ml.classifier import classify_user, ClassificationResult
from app.ml.risk_predictor import predict_addiction_risk, RiskPrediction
from app.ml.recommender import generate_recommendations, save_recommendations, RecommendationItem

__all__ = [
    "classify_user", "ClassificationResult",
    "predict_addiction_risk", "RiskPrediction",
    "generate_recommendations", "save_recommendations", "RecommendationItem",
]
