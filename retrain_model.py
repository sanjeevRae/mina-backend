from app.services.ml_service import SymptomCheckerModel

if __name__ == "__main__":
    model = SymptomCheckerModel()
    metrics = model.train(real_data_path="data/symptom_data.csv")
    model.save_model()
    print("Training complete. Metrics:")
    print(metrics)
