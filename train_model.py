import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dataset_path = os.path.join(
    BASE_DIR,
    "dataset",
    "accident_data.csv"
)

model_path = os.path.join(
    BASE_DIR,
    "model",
    "accident_model.pkl"
)

encoder_path = os.path.join(
    BASE_DIR,
    "model",
    "label_encoders.pkl"
)

data = pd.read_csv(dataset_path)

print("Dataset loaded successfully")
print(data)

features = [
    "latitude",
    "longitude",
    "weather",
    "traffic_density",
    "road_condition",
    "vehicle_speed",
    "time"
]

target = "accident_severity"

X = data[features].copy()
y = data[target].copy()

label_encoders = {}

categorical_columns = [
    "weather",
    "traffic_density",
    "road_condition",
    "time"
]

for column in categorical_columns:
    encoder = LabelEncoder()
    X[column] = encoder.fit_transform(X[column])
    label_encoders[column] = encoder

target_encoder = LabelEncoder()
y = target_encoder.fit_transform(y)

label_encoders["accident_severity"] = target_encoder

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model trained successfully")
print("Accuracy:", accuracy)

joblib.dump(model, model_path)
joblib.dump(label_encoders, encoder_path)

print("accident_model.pkl created successfully")
print("label_encoders.pkl created successfully")