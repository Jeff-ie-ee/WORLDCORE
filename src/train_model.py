
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_FILE = "data/processed/worldcore_features.csv"

features = [
    "rainfall_mm",
    "temperature_c",
    "humidity_pct",
    "wind_speed_kmh",
    "soil_moisture_pct",
    "water_level_cm",
    "hour_sin",
    "hour_cos",
    "month_sin",
    "month_cos",
    "rainfall_lag_1",
    "rainfall_lag_2",
    "water_level_lag_1",
    "rainfall_roll_3",
    "water_level_roll_3"
]

print("=" * 55)
print("WORLDCORE - WATER LEVEL CHANGE MODEL")
print("=" * 55)

df = pd.read_csv(DATA_FILE)

# Predict the change instead of the absolute water level
df["target_delta"] = (
    df["target_water_level_next_hour"] - df["water_level_cm"]
)

X = df[features]
y = df["target_delta"]

split_index = int(len(df) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

current_levels = X_test["water_level_cm"].values
actual_levels = (
    current_levels + y_test.values
)

model = RandomForestRegressor(
    n_estimators=400,
    max_depth=15,
    min_samples_leaf=2,
    max_features=0.8,
    random_state=42,
    n_jobs=-1
)

print("\nTraining change-prediction model...")
model.fit(X_train, y_train)

predicted_changes = model.predict(X_test)

# Convert predicted changes into water levels
predicted_levels = current_levels + predicted_changes

# Persistence baseline predicts no change
baseline_levels = current_levels

print("\nMODEL PERFORMANCE")
print(f"MAE: {mean_absolute_error(actual_levels, predicted_levels):.4f} cm")
print(f"RMSE: {np.sqrt(mean_squared_error(actual_levels, predicted_levels)):.4f} cm")
print(f"R2: {r2_score(actual_levels, predicted_levels):.4f}")

print("\nBASELINE PERFORMANCE")
print(f"MAE: {mean_absolute_error(actual_levels, baseline_levels):.4f} cm")
print(f"RMSE: {np.sqrt(mean_squared_error(actual_levels, baseline_levels)):.4f} cm")

Path("models").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

joblib.dump(
    {
        "model": model,
        "features": features,
        "target": "target_delta",
        "prediction_type": "water_level_change"
    },
    "models/water_level_model.joblib"
)

results = pd.DataFrame({
    "actual": actual_levels,
    "predicted": predicted_levels,
    "baseline_prediction": baseline_levels
})

results.to_csv("reports/model_predictions.csv", index=False)

print("\nModel saved successfully!")
print("WORLDCORE CHANGE MODEL TRAINING COMPLETED!")
