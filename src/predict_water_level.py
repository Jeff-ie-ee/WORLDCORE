
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

print("=" * 55)
print("       WORLDCORE - WATER LEVEL PREDICTION")
print("=" * 55)

# Load trained model
model_path = Path("models/water_level_model.joblib")

if not model_path.exists():
    raise FileNotFoundError(
        "Trained model not found. Run src/train_model.py first."
    )

artifact = joblib.load(model_path)

model = artifact["model"]
features = artifact["features"]

print("\nEnter the current environmental measurements.")

def get_value(label, minimum, maximum):
    while True:
        try:
            value = float(input(f"{label}: "))

            if not minimum <= value <= maximum:
                print(f"Please enter a value between {minimum} and {maximum}.")
                continue

            return value

        except ValueError:
            print("Please enter a valid number.")

# Collect environmental measurements
rainfall = get_value("Rainfall (mm)", 0, 500)
temperature = get_value("Temperature (C)", -10, 60)
humidity = get_value("Humidity (%)", 0, 100)
wind_speed = get_value("Wind speed (km/h)", 0, 200)
soil_moisture = get_value("Soil moisture (%)", 0, 100)
current_water_level = get_value("Current water level (cm)", 0, 300)

hour = int(get_value("Current hour (0-23)", 0, 23))
month = int(get_value("Current month (1-12)", 1, 12))

# Prepare model input
input_data = pd.DataFrame([{
    "rainfall_mm": rainfall,
    "temperature_c": temperature,
    "humidity_pct": humidity,
    "wind_speed_kmh": wind_speed,
    "soil_moisture_pct": soil_moisture,
    "water_level_cm": current_water_level,
    "hour_sin": np.sin(2 * np.pi * hour / 24),
    "hour_cos": np.cos(2 * np.pi * hour / 24),
    "month_sin": np.sin(2 * np.pi * month / 12),
    "month_cos": np.cos(2 * np.pi * month / 12)
}])

# Keep the exact training feature order
input_data = input_data[features]

# Generate prediction
prediction = model.predict(input_data)[0]

# Display result
print("\n" + "=" * 55)
print("             WORLDCORE PREDICTION")
print("=" * 55)

print(f"Current water level: {current_water_level:.2f} cm")
print(f"Predicted next-hour water level: {prediction:.2f} cm")

change = prediction - current_water_level

print(f"Estimated change: {change:+.2f} cm")

print("\nPrediction generated successfully!")
print("=" * 55)

print(
    "\nNote: This is an experimental prediction using synthetic "
    "training data. It is not a real-world flood warning."
)
