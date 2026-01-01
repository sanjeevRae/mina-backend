"""
LightGBM Symptom Checker Model Training
Memory-optimized for Render free tier deployment
"""
import json
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import lightgbm as lgb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SymptomCheckerTrainer:
    """Train LightGBM model for symptom checking"""
    
    def __init__(self, data_path: str = "data/symptom_condition_data.json"):
        self.data_path = data_path
        self.model = None
        self.label_encoder = None
        self.symptoms_list = None
        self.condition_info = None
        
    def load_data(self):
        """Load training data"""
        logger.info(f"Loading data from {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            dataset = json.load(f)
        
        data = dataset['data']
        self.symptoms_list = dataset['symptoms_list']
        self.condition_info = dataset['condition_info']
        
        # Convert to numpy arrays
        X = []
        y = []
        
        for sample in data:
            # Convert symptom dict to feature vector
            symptom_vector = [sample['symptoms'].get(symptom, 0) for symptom in self.symptoms_list]
            X.append(symptom_vector)
            y.append(sample['condition'])
        
        X = np.array(X, dtype=np.float32)
        y = np.array(y)
        
        logger.info(f"Data loaded: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y
    
    def train(self, test_size: float = 0.2, random_state: int = 42):
        """Train the LightGBM model"""
        # Load data
        X, y = self.load_data()
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )
        
        logger.info(f"Training set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")
        
        # Create LightGBM dataset
        train_data = lgb.Dataset(X_train, label=y_train)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
        
        # LightGBM parameters (memory-optimized)
        params = {
            'objective': 'multiclass',
            'num_class': len(self.label_encoder.classes_),
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'max_depth': 5,
            'min_data_in_leaf': 20,
            'lambda_l1': 0.1,
            'lambda_l2': 0.1
        }
        
        # Train model
        logger.info("Training LightGBM model...")
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=200,
            valid_sets=[test_data],
            callbacks=[
                lgb.early_stopping(stopping_rounds=20),
                lgb.log_evaluation(period=50)
            ]
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        accuracy = accuracy_score(y_test, y_pred_classes)
        logger.info(f"\n✅ Model trained successfully!")
        logger.info(f"Accuracy: {accuracy:.4f}")
        
        # Print classification report
        logger.info("\nClassification Report:")
        logger.info(classification_report(
            y_test, y_pred_classes,
            target_names=self.label_encoder.classes_,
            zero_division=0
        ))
        
        return accuracy
    
    def save_model(self, model_dir: str = "models/symptom_checker"):
        """Save trained model and metadata"""
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Save LightGBM model (very compact)
        self.model.save_model(str(model_path / "lightgbm_model.txt"))
        
        # Save metadata
        metadata = {
            'symptoms_list': self.symptoms_list,
            'conditions': self.label_encoder.classes_.tolist(),
            'condition_info': self.condition_info,
            'num_features': len(self.symptoms_list),
            'num_classes': len(self.label_encoder.classes_)
        }
        
        with open(model_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save label encoder
        joblib.dump(self.label_encoder, model_path / "label_encoder.pkl")
        
        logger.info(f"\n✅ Model saved to {model_dir}")
        logger.info(f"   - Model file: lightgbm_model.txt")
        logger.info(f"   - Metadata: metadata.json")
        logger.info(f"   - Label encoder: label_encoder.pkl")
        
        # Check model size
        model_size = (model_path / "lightgbm_model.txt").stat().st_size / 1024
        logger.info(f"   - Model size: {model_size:.2f} KB (very lightweight!)")


def main():
    """Main training pipeline"""
    # Create data directory if needed
    Path("data").mkdir(exist_ok=True)
    
    # Generate dataset if not exists
    data_file = Path("data/symptom_condition_data.json")
    if not data_file.exists():
        logger.info("Generating symptom dataset...")
        from data.symptom_dataset import save_dataset
        save_dataset(str(data_file))
    
    # Train model
    trainer = SymptomCheckerTrainer()
    trainer.train()
    trainer.save_model()
    
    logger.info("\n🎉 Training complete! Ready for deployment.")


if __name__ == "__main__":
    main()
