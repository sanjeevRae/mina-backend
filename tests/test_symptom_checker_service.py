from app.services.ml_service import SymptomCheckerService


class BrokenModel:
    def predict(self, _features):
        raise RuntimeError("unordered_map::at")


def test_predict_falls_back_when_lightgbm_raises_unordered_map_at():
    service = SymptomCheckerService()
    original_state = (
        service.model,
        service.symptoms_list,
        service.condition_info,
        service.metadata,
        service.label_encoder,
    )

    try:
        service.model = BrokenModel()
        service.symptoms_list = ["fever", "cough", "fatigue"]
        service.condition_info = {
            "Common Cold": {
                "symptoms": ["fever", "cough"],
                "severity": "mild",
                "recommendations": ["Rest and drink fluids"],
            }
        }
        service.metadata = {"symptoms_list": service.symptoms_list}

        predictions = service.predict([" fever ", "cough"], top_k=1)

        assert predictions == [
            {
                "condition": "Common Cold",
                "confidence": 100.0,
                "severity": "mild",
                "recommendations": ["Rest and drink fluids"],
                "matched_symptoms": [" fever ", "cough"],
            }
        ]
    finally:
        (
            service.model,
            service.symptoms_list,
            service.condition_info,
            service.metadata,
            service.label_encoder,
        ) = original_state

