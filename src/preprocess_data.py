
import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 55)
print("WORLDCORE DATA PREPROCESSING")
print("=" * 55)

# Load raw environmental dataset
input_path = Path("data/raw/worldcore_environmental_data.csv")
output_path = Path("data/processed/worldcore_processed_data.csv")

df = pd.read_csv(input_path)

print("\n1. Original dataset shape:", df.shape)

# Convert timestamp into datetime
df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

# Remove rows with invalid timestamps
df = df.dropna(subset=["timestamp"])

# Remove duplicate timestamps and sort chronologically
df = df.drop_duplicates(subset=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Identify numeric columns
numeric_columns = [
    "rainfall_mm",
    "temperature_c",
    "humidity_pct",
    "wind_speed_kmh",
    "soil_moisture_pct",
    "water_level_cm"
]

# Convert numeric columns safely
for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# Replace infinite values
df[numeric_columns] = df[numeric_columns].replace(
    [np.inf, -np.inf],
    np.nan
)

# Fill missing numeric values using interpolation
df[numeric_columns] = df[numeric_columns].interpolate(
    method="linear",
    limit_direction="both"
)

# Remove rows that still contain missing values
df = df.dropna().reset_index(drop=True)

print("2. Cleaned dataset shape:", df.shape)

# Feature engineering: extract time information
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.day_of_week
df["month"] = df["timestamp"].dt.month

# Cyclical encoding for hour and month
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

# Target: water level one hour into the future
df["target_water_level_next_hour"] = (
    df["water_level_cm"].shift(-1)
)

# The last row has no next-hour target
df = df.dropna().reset_index(drop=True)

# Save processed dataset
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print("\n3. Feature engineering completed.")
print("4. Target column: target_water_level_next_hour")
print("5. Final dataset shape:", df.shape)

print("\nProcessed columns:")
print(df.columns.tolist())

print("\nFirst five processed rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nProcessed dataset saved to:")
print(output_path)

print("\nWORLDCORE PREPROCESSING COMPLETED!")
