import pandas as pd
from pathlib import Path

INPUT_FILE = "data/processed/worldcore_processed_data.csv"
OUTPUT_FILE = "data/processed/worldcore_features.csv"

df = pd.read_csv(INPUT_FILE)

# Ensure observations are in chronological order
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Historical rainfall features
df["rainfall_lag_1"] = df["rainfall_mm"].shift(1)
df["rainfall_lag_2"] = df["rainfall_mm"].shift(2)

# Historical water-level feature
df["water_level_lag_1"] = df["water_level_cm"].shift(1)

# Trailing averages: current observation and previous two hours
df["rainfall_roll_3"] = (
    df["rainfall_mm"].rolling(window=3).mean()
)

df["water_level_roll_3"] = (
    df["water_level_cm"].rolling(window=3).mean()
)

# Remove rows without sufficient historical information
df = df.dropna().reset_index(drop=True)

Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print("=" * 55)
print("WORLDCORE TIME FEATURES CREATED")
print("=" * 55)
print("Output:", OUTPUT_FILE)
print("Rows:", len(df))
print("\nNew features:")
print([
    "rainfall_lag_1",
    "rainfall_lag_2",
    "water_level_lag_1",
    "rainfall_roll_3",
    "water_level_roll_3"
])
print("\nMissing values:", int(df.isnull().sum().sum()))
print("\nFirst five rows:")
print(df.head())