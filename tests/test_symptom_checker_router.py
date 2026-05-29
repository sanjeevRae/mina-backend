import pytest

from app.routers import symptom_checker
from app.schemas.symptom_checker import SymptomInput


@pytest.mark.asyncio
async def test_analyze_routes_greeting_as_clean_chat(monkeypatch):
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
    )

    assert result.intent == "greeting"
    assert result.response_type == "chat"
    assert result.should_show_medical_analysis is False
    assert result.message == "Hi, I can help you check possible conditions from symptoms."
    assert result.predictions == []
    assert result.disclaimer is None
    assert result.suggestions == ["Describe 2 to 6 symptoms"]
