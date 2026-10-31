
import numpy as np
import pandas as pd
from pathlib import Path

# Reproducible sample data
np.random.seed(42)

# Generate 2,000 hourly observations
n = 2000

timestamps = pd.date_range(
    start="2025-01-01",
    periods=n,
    freq="h"
)

# Generate environmental variables
temperature = np.random.normal(29, 4, n)
humidity = np.random.normal(75, 12, n)
humidity = np.clip(humidity, 30, 100)

rainfall = np.random.gamma(1.5, 3, n)
rainfall = np.where(np.random.rand(n) < 0.55, 0, rainfall)
rainfall = np.clip(rainfall, 0, 100)

wind_speed = np.random.normal(12, 5, n)
wind_speed = np.clip(wind_speed, 0, 60)

soil_moisture = np.zeros(n)
water_level = np.zeros(n)

for i in range(n):
    previous_soil = soil_moisture[i - 1] if i > 0 else 35
    previous_water = water_level[i - 1] if i > 0 else 20

    soil_moisture[i] = np.clip(
        previous_soil * 0.94 + rainfall[i] * 0.8
        - 0.15 * max(temperature[i] - 25, 0)
        + np.random.normal(0, 1.5),
        5, 100
    )

    water_level[i] = np.clip(
        previous_water * 0.96 + rainfall[i] * 1.8
        + max(soil_moisture[i] - 60, 0) * 0.08
        - 0.5
        + np.random.normal(0, 2),
        0, 300
    )

df = pd.DataFrame({
    "timestamp": timestamps,
    "rainfall_mm": rainfall.round(2),
    "temperature_c": temperature.round(2),
    "humidity_pct": humidity.round(2),
    "wind_speed_kmh": wind_speed.round(2),
    "soil_moisture_pct": soil_moisture.round(2),
    "water_level_cm": water_level.round(2)
})

# Save dataset
output_path = Path("data/raw/worldcore_environmental_data.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print("=" * 50)
print("WORLDCORE ENVIRONMENTAL DATA GENERATOR")
print("=" * 50)
print("Total observations:", len(df))
print("Features:", list(df.columns))
print("\nFirst five observations:")
print(df.head())
print("\nDataset saved to:", output_path)
print("\nData generation completed!")
