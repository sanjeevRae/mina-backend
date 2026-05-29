from app.services import ml_service
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
        service.model_load_error,
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
            service.model_load_error,
        ) = original_state


def test_load_model_keeps_metadata_when_lightgbm_raises_unordered_map_at(monkeypatch):
    service = SymptomCheckerService()
    original_state = (
        service.model,
        service.symptoms_list,
        service.condition_info,
        service.metadata,
        service.label_encoder,
        service.model_load_error,
    )

    def broken_booster(*_args, **_kwargs):
        raise RuntimeError("unordered_map::at")

    try:
        service.model = None
        service.symptoms_list = None
        service.condition_info = None
        service.metadata = None
        service.label_encoder = None
        service.model_load_error = None
        monkeypatch.setattr(ml_service.lgb, "Booster", broken_booster)

        valid_symptoms, unknown_symptoms = service.validate_symptoms(["fever", "cough", "fatigue"])
        predictions = service.predict(valid_symptoms, top_k=1)

        assert valid_symptoms == ["fever", "cough", "fatigue"]
        assert unknown_symptoms == []
        assert predictions
        assert str(service.model_load_error) == "unordered_map::at"
    finally:
        (
            service.model,
            service.symptoms_list,
            service.condition_info,
            service.metadata,
            service.label_encoder,
            service.model_load_error,
        ) = original_state
