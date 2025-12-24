
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
import joblib
import numpy as np

# Settings
DATA_PATH = 'data/symptom_data.csv'
MODEL_PATH = 'models/symptom_checker_model.joblib'
CHUNKSIZE = 10000  # Adjust based on your RAM
TARGET_COL = 'diagnosis'

# Initialize model for incremental learning
clf = SGDClassifier(loss='log_loss', max_iter=5, tol=None)
classes = None
first = True
X_test, y_test = None, None

for chunk in pd.read_csv(DATA_PATH, chunksize=CHUNKSIZE):
	X = chunk.drop(TARGET_COL, axis=1)
	y = chunk[TARGET_COL]
	if first:
		classes = np.unique(y)
		# Save a test set from the first chunk
		X_test, y_test = X.iloc[:1000], y.iloc[:1000]
		X_train, y_train = X.iloc[1000:], y.iloc[1000:]
		clf.partial_fit(X_train, y_train, classes=classes)
		first = False
	else:
		clf.partial_fit(X, y)

# Evaluate
if X_test is not None and y_test is not None:
	y_pred = clf.predict(X_test)
	print('Accuracy:', accuracy_score(y_test, y_pred))

# Save the trained model
joblib.dump(clf, MODEL_PATH)
print(f'Model saved to {MODEL_PATH}')
