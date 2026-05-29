import pytest

from app.routers import symptom_checker
from app.schemas.symptom_checker import SymptomInput


@pytest.mark.asyncio
async def test_analyze_returns_friendly_prediction_for_greeting(monkeypatch):
    def fake_chat(_message):
        return {
            "intent": "greeting",
            "response": "Hi, I can help you check possible conditions from symptoms.",
            "extracted_symptoms": [],
            "unknown_terms": [],
            "predictions": [],
            "suggestions": ["Describe 2 to 6 symptoms"],
        }

    monkeypatch.setattr(symptom_checker.symptom_checker_service, "chat", fake_chat)

    result = await symptom_checker.analyze_symptoms(
        SymptomInput(symptoms=["hello"]),
        current_user=object(),
    )

    assert result.intent == "greeting"
    assert result.message == "Hi, I can help you check possible conditions from symptoms."
    assert result.predictions
    assert result.predictions[0].condition == "Symptom Checker Assistant"
    assert result.predictions[0].recommendations == [
        "Hi, I can help you check possible conditions from symptoms."
    ]
    assert result.suggestions == ["Describe 2 to 6 symptoms"]

