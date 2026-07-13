"""
Train and save scikit-learn models for Basma+ AI components.
Generates synthetic training data based on domain heuristics,
then trains real ML models and saves them as .pkl files.
"""
import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODELS_DIR = os.path.join(os.path.dirname(__file__), "trained")
os.makedirs(MODELS_DIR, exist_ok=True)


def _screen_risk_features(screen_min: float, social_min: float, sleep_min: float) -> list:
    return [screen_min, social_min, social_min / max(screen_min, 1), sleep_min]


def _mood_features(stress: float, mood: float) -> list:
    return [stress, mood]


def _productivity_features(completed_ratio: float, active_goals: int) -> list:
    return [completed_ratio, active_goals]


def generate_classifier_data(n_samples: int = 2000) -> tuple:
    np.random.seed(42)
    X = []
    y = []
    for _ in range(n_samples):
        screen = np.random.uniform(60, 720)
        social = np.random.uniform(0, screen * 0.8)
        sleep = np.random.uniform(240, 540)
        stress = np.random.uniform(1, 10)
        mood = np.random.uniform(1, 10)
        completed = np.random.uniform(0, 1)
        goals = np.random.randint(0, 8)

        feat = _screen_risk_features(screen, social, sleep)
        feat += _mood_features(stress, mood)
        feat += _productivity_features(completed, goals)

        screen_h = screen / 60
        composite_score = (100 - max(0, (screen_h - 4) * 15)) * 0.15
        composite_score += max(0, 100 - abs(sleep / 60 - 8) * 10) * 0.10
        composite_score += mood * 0.25
        composite_score += completed * 100 * 0.25

        if screen_h >= 8 and stress >= 7:
            label = "DIGITAL_ADDICT"
        elif screen_h <= 4 and completed >= 0.7 and mood >= 6:
            label = "HIGH_PERFORMER"
        elif stress >= 6 and completed < 0.5:
            label = "OVERWHELMED"
        else:
            label = "BALANCED"

        noise = np.random.random()
        if noise < 0.05:
            choices = [l for l in ["BALANCED", "OVERWHELMED", "DIGITAL_ADDICT", "HIGH_PERFORMER"] if l != label]
            label = np.random.choice(choices)

        X.append(feat)
        y.append(label)

    return np.array(X), np.array(y)


def generate_risk_data(n_samples: int = 2000) -> tuple:
    np.random.seed(42)
    X = []
    y = []
    for _ in range(n_samples):
        screen = np.random.uniform(60, 720)
        social = np.random.uniform(0, screen * 0.8)
        sleep = np.random.uniform(240, 540)
        stress = np.random.uniform(1, 10)
        failed = np.random.randint(0, 5)

        avg_screen_risk = min(100, max(0, (screen - 120) / 4.0))
        social_ratio = social / max(screen, 1)
        social_risk = min(100, max(0, social_ratio * 120))
        sleep_risk = min(100, max(0, (480 - sleep) / 2.4))
        stress_risk = min(100, max(0, (stress - 3) * 14.3))
        challenge_risk = min(100, failed * 25.0)

        risk_score = (
            avg_screen_risk * 0.30
            + social_risk * 0.25
            + sleep_risk * 0.20
            + stress_risk * 0.15
            + challenge_risk * 0.10
        )

        feat = [screen, social, social_ratio, sleep, stress, failed]
        feat += [avg_screen_risk, social_risk, sleep_risk, stress_risk, challenge_risk]

        if risk_score >= 65:
            label = "HIGH"
        elif risk_score >= 35:
            label = "MEDIUM"
        else:
            label = "LOW"

        noise = np.random.random()
        if noise < 0.05:
            choices = [l for l in ["LOW", "MEDIUM", "HIGH"] if l != label]
            label = np.random.choice(choices)

        X.append(feat)
        y.append(label)

    return np.array(X), np.array(y)


def train_and_save_classifier():
    print("Training classifier model...")
    X, y = generate_classifier_data()
    label_map = {l: i for i, l in enumerate(sorted(set(y)))}
    y_num = np.array([label_map[l] for l in y])
    reverse_map = {i: l for l, i in label_map.items()}

    X_train, X_test, y_train, y_test = train_test_split(X, y_num, test_size=0.2, random_state=42)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=4,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  Accuracy: {acc:.3f}")
    print(f"  Report:\n{classification_report(y_test, y_pred, target_names=list(label_map.keys()))}")

    path = os.path.join(MODELS_DIR, "classifier.pkl")
    with open(path, "wb") as f:
        pickle.dump({"model": model, "label_map": label_map, "reverse_map": reverse_map, "accuracy": acc}, f)
    print(f"  Saved to {path}")


def train_and_save_risk_predictor():
    print("Training risk predictor model...")
    X, y = generate_risk_data()
    label_map = {l: i for i, l in enumerate(sorted(set(y)))}
    y_num = np.array([label_map[l] for l in y])
    reverse_map = {i: l for l, i in label_map.items()}

    X_train, X_test, y_train, y_test = train_test_split(X, y_num, test_size=0.2, random_state=42)

    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"  Accuracy: {acc:.3f}")
    print(f"  Report:\n{classification_report(y_test, y_pred, target_names=list(label_map.keys()))}")

    path = os.path.join(MODELS_DIR, "risk_predictor.pkl")
    with open(path, "wb") as f:
        pickle.dump({"model": model, "label_map": label_map, "reverse_map": reverse_map, "accuracy": acc}, f)
    print(f"  Saved to {path}")

def train_and_save_recommender_model():
    print("Training recommender encoder...")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    sample_tags = [
        "technology programming python web",
        "design ui ux graphic",
        "business entrepreneurship marketing",
        "sports fitness health",
        "music production audio",
        "gaming development unity",
        "science data machine-learning",
        "self-improvement productivity focus",
        "language english learning",
        "art creative photography",
        "mathematics logic problem-solving",
        "writing content blogging",
        "finance investment crypto",
        "psychology mindfulness meditation",
        "cooking nutrition wellness",
    ]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        max_features=500,
        sublinear_tf=True,
    )
    vectorizer.fit(sample_tags)

    path = os.path.join(MODELS_DIR, "recommender_vectorizer.pkl")
    with open(path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "sample_tags": sample_tags}, f)
    print(f"  Saved to {path}")


if __name__ == "__main__":
    train_and_save_classifier()
    train_and_save_risk_predictor()
    train_and_save_recommender_model()
    print("\nAll models trained and saved successfully!")
