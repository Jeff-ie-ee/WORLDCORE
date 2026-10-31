
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 55)
print("WORLDCORE - EXPLORATORY DATA ANALYSIS")
print("=" * 55)

# Load processed data
df = pd.read_csv("data/processed/worldcore_processed_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Create reports directory
Path("reports").mkdir(exist_ok=True)

# 1. Dataset overview
print("\n1. DATASET OVERVIEW")
print("Shape:", df.shape)
print("\nStatistical summary:")
print(df.describe().round(2))

# 2. Rainfall distribution
plt.figure(figsize=(9, 5))
plt.hist(df["rainfall_mm"], bins=30)
plt.title("Rainfall Distribution")
plt.xlabel("Rainfall (mm)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("reports/rainfall_distribution.png")
plt.close()

# 3. Water level over time
plt.figure(figsize=(12, 5))
plt.plot(df["timestamp"], df["water_level_cm"])
plt.title("Environmental Water Level Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Water Level (cm)")
plt.tight_layout()
plt.savefig("reports/water_level_trend.png")
plt.close()

# 4. Rainfall vs water level
plt.figure(figsize=(8, 5))
plt.scatter(df["rainfall_mm"], df["water_level_cm"], alpha=0.5)
plt.title("Rainfall vs Water Level")
plt.xlabel("Rainfall (mm)")
plt.ylabel("Water Level (cm)")
plt.tight_layout()
plt.savefig("reports/rainfall_water_relationship.png")
plt.close()

# 5. Correlation heatmap
correlation_columns = [
    "rainfall_mm",
    "temperature_c",
    "humidity_pct",
    "wind_speed_kmh",
    "soil_moisture_pct",
    "water_level_cm",
    "target_water_level_next_hour"
]

correlation = df[correlation_columns].corr()

plt.figure(figsize=(10, 7))
plt.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(label="Correlation")
plt.xticks(
    range(len(correlation_columns)),
    correlation_columns,
    rotation=45,
    ha="right"
)
plt.yticks(range(len(correlation_columns)), correlation_columns)
plt.title("Environmental Feature Correlation")
plt.tight_layout()
plt.savefig("reports/environmental_correlation.png")
plt.close()

print("\n2. VISUALIZATIONS GENERATED:")
print("- reports/rainfall_distribution.png")
print("- reports/water_level_trend.png")
print("- reports/rainfall_water_relationship.png")
print("- reports/environmental_correlation.png")

print("\n3. CORRELATION WITH NEXT-HOUR WATER LEVEL:")
print(
    correlation["target_water_level_next_hour"]
    .sort_values(ascending=False)
    .round(3)
)

print("\nWORLDCORE EDA COMPLETED!")
