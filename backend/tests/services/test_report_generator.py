from app.services.report_generator import _generate_summary_text


def test_summary_text_screen_time_improvement():
    """Test summary text for improved screen time."""
    metrics = {
        "avg_screen_time_min": 180,
        "screen_time_change_pct": -25,
        "avg_sleep_min": 450,
        "avg_mood_score": 7.0,
        "mood_change": 0.5,
        "total_tasks": 10,
        "completed_tasks": 8,
        "completion_rate": 80,
        "days_tracked": 7,
    }

    text = _generate_summary_text(metrics)

    assert "قلّلت" in text
    assert "25" in text
    assert "8" in text or "10" in text


def test_summary_text_no_data():
    """Test summary text when no data is available."""
    metrics = {
        "avg_screen_time_min": 0,
        "screen_time_change_pct": 0,
        "avg_sleep_min": 0,
        "avg_mood_score": 5.0,
        "mood_change": 0.0,
        "total_tasks": 0,
        "completed_tasks": 0,
        "completion_rate": 0,
        "days_tracked": 0,
    }

    text = _generate_summary_text(metrics)

    assert len(text) > 0  # Should have some text even with no data


def test_summary_text_poor_sleep():
    """Test summary text for poor sleep."""
    metrics = {
        "avg_screen_time_min": 240,
        "screen_time_change_pct": 0,
        "avg_sleep_min": 360,  # 6 hours
        "avg_mood_score": 5.0,
        "mood_change": 0.0,
        "total_tasks": 5,
        "completed_tasks": 3,
        "completion_rate": 60,
        "days_tracked": 7,
    }

    text = _generate_summary_text(metrics)

    assert "6.0" in text or "6" in text
