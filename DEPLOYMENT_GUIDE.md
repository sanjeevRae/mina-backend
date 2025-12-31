# Symptom Checker with CSV Data

This implementation allows you to train and use a machine learning model for symptom checking using your own `symptom_data.csv` file.

## Data Format

Your `symptom_data.csv` file should contain:
- One column named `diagnosis` (the target variable)
- Other columns representing symptoms/features (binary: 0/1 or numerical values)

Example format:
```csv
fever,cough,headache,fatigue,diagnosis
1,1,0,1,flu
0,1,1,0,cold
1,0,1,1,migraine
```

## Memory Optimization for Render Deployment

The implementation has been optimized for deployment on Render with limited memory (512MB):
- Reduced model complexity (100 estimators, max depth 10)
- Single-threaded training to reduce memory usage
- Chunked data loading to prevent memory overflow
- Reduced cross-validation folds (3 instead of 5)
- Increased min samples to reduce overfitting and memory usage

## Training the Model

To train the model with your CSV data:

```bash
python train_symptom_checker.py [path_to_your_csv_file]
```

If no path is provided, it defaults to `data/symptom_data.csv`.

## Retraining the Model

To retrain an existing model:

```bash
python retrain_model.py [path_to_your_csv_file]
```

## API Endpoints

Once trained, the following endpoints are available:

### Simple Symptom Check
- **POST** `/api/v1/ml/symptom-checker`
- Input: `{"symptoms": ["fever", "cough", "headache"]}`
- Returns: Predicted conditions with probabilities

### Full Symptom Check
- **POST** `/api/v1/ml/symptom-checker/start`
- Input: More detailed with patient info
- Returns: Detailed predictions with follow-up questions

## Model Storage

Trained models are saved in the `models/` directory with versioning based on timestamp.

## Database Integration

Model information is stored in the `ml_models` table in the database, including:
- Model version
- Training metrics (accuracy, precision, recall, F1-score)
- File path
- Active status

## Key Features

- **Memory Optimized**: Designed to run within 512MB memory limits
- **Flexible Input**: Handles various CSV formats
- **Automatic Feature Detection**: Automatically identifies features from CSV
- **Categorical Encoding**: Handles categorical variables
- **Model Persistence**: Saves and loads trained models
- **Database Integration**: Stores model metadata
- **API Integration**: Works with existing FastAPI endpoints

## Requirements

- pandas
- scikit-learn
- numpy
- joblib

## Troubleshooting

If you encounter issues:
1. Ensure your CSV has a `diagnosis` column
2. Make sure all values are numeric or properly encoded
3. Check that the data directory exists: `data/`
4. Verify that you have write permissions for the `models/` directory
5. For Render deployment, ensure your CSV file is not too large (limit to <50MB)