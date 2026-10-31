
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "reports"
    / "spatial"
    / "worldcore_spatial_grid_summary.csv"
)

OUTPUT_DIR = ROOT / "reports" / "spatial"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_IMAGE = (
    OUTPUT_DIR / "worldcore_spatial_intelligence_map.png"
)


# ==========================================
# 2. LOAD INTEGRATED DATA
# ==========================================

print("\nWORLDCORE - DAY 26")
print("SPATIAL INTELLIGENCE VISUALIZATION")
print("=" * 55)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Integrated summary not found: {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

required = [
    "lat",
    "lon",
    "average_rainfall_mm",
    "maximum_daily_rainfall_mm",
    "mean_elevation_m",
    "mean_slope_degrees"
]

missing = [column for column in required if column not in df.columns]

if missing:
    raise ValueError(f"Missing columns: {missing}")

df = df.dropna(subset=required)

if df.empty:
    raise ValueError("No valid spatial records found.")

print("Grid cells:", len(df))
print("Coordinates loaded successfully.")


# ==========================================
# 3. CREATE SPATIAL VISUALIZATION
# ==========================================

fig, axes = plt.subplots(
    1, 2,
    figsize=(17, 8)
)

fig.suptitle(
    "WORLDCORE - Spatial Rainfall and Terrain Intelligence",
    fontsize=16,
    fontweight="bold"
)

# Use one shared marker-size scale for average rainfall.
rainfall_min = df["average_rainfall_mm"].min()
rainfall_max = df["average_rainfall_mm"].max()

if rainfall_max == rainfall_min:
    marker_sizes = [180] * len(df)
else:
    marker_sizes = (
        100
        + 250
        * (
            df["average_rainfall_mm"] - rainfall_min
        )
        / (rainfall_max - rainfall_min)
    )


# ==========================================
# 4. ELEVATION MAP
# ==========================================

elevation_plot = axes[0].scatter(
    df["lon"],
    df["lat"],
    c=df["mean_elevation_m"],
    s=marker_sizes,
    cmap="terrain",
    edgecolors="black",
    linewidths=1
)

for row in df.itertuples():
    axes[0].annotate(
        f"{row.mean_elevation_m:.1f} m",
        (row.lon, row.lat),
        xytext=(5, 7),
        textcoords="offset points",
        fontsize=8
    )

axes[0].set_title(
    "Mean Elevation by Rainfall Grid Cell"
)

axes[0].set_xlabel("Longitude (degrees)")
axes[0].set_ylabel("Latitude (degrees)")

axes[0].grid(True, linestyle="--", alpha=0.4)

axes[0].set_xticks(sorted(df["lon"].unique()))
axes[0].set_yticks(sorted(df["lat"].unique()))

colorbar1 = fig.colorbar(
    elevation_plot,
    ax=axes[0]
)

colorbar1.set_label("Mean Elevation (metres)")


# ==========================================
# 5. SLOPE MAP
# ==========================================

slope_plot = axes[1].scatter(
    df["lon"],
    df["lat"],
    c=df["mean_slope_degrees"],
    s=marker_sizes,
    cmap="YlOrRd",
    edgecolors="black",
    linewidths=1
)

for row in df.itertuples():
    axes[1].annotate(
        f"{row.mean_slope_degrees:.2f}°",
        (row.lon, row.lat),
        xytext=(5, 7),
        textcoords="offset points",
        fontsize=8
    )

axes[1].set_title(
    "Mean Terrain Slope by Rainfall Grid Cell"
)

axes[1].set_xlabel("Longitude (degrees)")
axes[1].set_ylabel("Latitude (degrees)")

axes[1].grid(True, linestyle="--", alpha=0.4)

axes[1].set_xticks(sorted(df["lon"].unique()))
axes[1].set_yticks(sorted(df["lat"].unique()))

colorbar2 = fig.colorbar(
    slope_plot,
    ax=axes[1]
)

colorbar2.set_label("Mean Slope (degrees)")


# ==========================================
# 6. ADD MAP NOTES
# ==========================================

fig.text(
    0.5,
    0.015,
    "Marker size represents average daily rainfall. "
    "Points represent IMD grid-cell centres, not 30 m measurements.",
    ha="center",
    fontsize=9
)

plt.tight_layout(rect=[0, 0.05, 1, 0.94])

plt.savefig(
    OUTPUT_IMAGE,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ==========================================
# 7. DISPLAY SPATIAL SUMMARY
# ==========================================

print("\nSPATIAL GRID SUMMARY")
print("-" * 55)

print(
    df[
        [
            "lat",
            "lon",
            "average_rainfall_mm",
            "mean_elevation_m",
            "mean_slope_degrees"
        ]
    ].to_string(index=False)
)

print("\nMap saved successfully:")
print(OUTPUT_IMAGE)

print("\n" + "=" * 55)
print("WORLDCORE SPATIAL VISUALIZATION COMPLETED")
print("=" * 55)

print(
    "\nScientific note: This is a seven-point grid visualization. "
    "It is not a continuous flood-risk map."
)
