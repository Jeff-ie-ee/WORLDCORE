
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt

from rasterio.mask import mask
from rasterio.warp import transform_geom


# ==================================================
# 1. PROJECT PATHS
# ==================================================

ROOT = Path(__file__).resolve().parent.parent

RAINFALL_PATH = (
    ROOT / "data" / "processed" / "imd_rainfall_grid.csv"
)

DEM_PATH = (
    ROOT / "data" / "processed" / "terrain"
    / "worldcore_dem_utm43n.tif"
)

SLOPE_PATH = (
    ROOT / "data" / "processed" / "terrain"
    / "worldcore_slope_degrees.tif"
)

OUTPUT_DIR = ROOT / "data" / "processed" / "spatial"
REPORT_DIR = ROOT / "reports" / "spatial"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. LOAD RAINFALL GRID
# ==================================================

print("\nWORLDCORE - DAY 26")
print("RAINFALL AND TERRAIN INTEGRATION")
print("=" * 60)

for path in [RAINFALL_PATH, DEM_PATH, SLOPE_PATH]:
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {path}")

rainfall = pd.read_csv(RAINFALL_PATH)

required_columns = {"time", "lat", "lon", "rainfall_mm"}

if not required_columns.issubset(rainfall.columns):
    raise ValueError(
        f"Rainfall CSV must contain: {required_columns}"
    )

rainfall["time"] = pd.to_datetime(rainfall["time"])
rainfall["lat"] = pd.to_numeric(rainfall["lat"])
rainfall["lon"] = pd.to_numeric(rainfall["lon"])
rainfall["rainfall_mm"] = pd.to_numeric(
    rainfall["rainfall_mm"], errors="coerce"
)

rainfall = rainfall.dropna(
    subset=["time", "lat", "lon", "rainfall_mm"]
)

print(f"Rainfall records: {len(rainfall):,}")

grid_cells = rainfall[["lat", "lon"]].drop_duplicates()

print(f"Unique rainfall grid cells: {len(grid_cells)}")


# ==================================================
# 3. CHECK GRID SPACING
# ==================================================

lat_values = np.sort(grid_cells["lat"].unique())
lon_values = np.sort(grid_cells["lon"].unique())

lat_steps = np.diff(lat_values)
lon_steps = np.diff(lon_values)

print("\nGrid coordinates:")
print("Latitudes:", lat_values)
print("Longitudes:", lon_values)

# The supplied IMD grid uses nominal 0.25-degree spacing.
# Verify that the available coordinate differences agree.

if len(lat_steps) and not np.allclose(lat_steps, 0.25):
    raise ValueError(
        "Unexpected latitude spacing. Review grid-cell dimensions."
    )

if len(lon_steps) and not np.allclose(lon_steps, 0.25):
    raise ValueError(
        "Unexpected longitude spacing. Review grid-cell dimensions."
    )

CELL_SIZE = 0.25
HALF_CELL = CELL_SIZE / 2


# ==================================================
# 4. CALCULATE TERRAIN STATISTICS PER GRID CELL
# ==================================================

terrain_records = []

print("\nCalculating terrain statistics for each rainfall cell...")

with rasterio.open(DEM_PATH) as dem_src, \
     rasterio.open(SLOPE_PATH) as slope_src:

    if dem_src.crs != slope_src.crs:
        raise ValueError("DEM and slope rasters have different CRS.")

    print("DEM CRS:", dem_src.crs)
    print("Slope CRS:", slope_src.crs)

    for index, cell in grid_cells.reset_index(drop=True).iterrows():

        lat = float(cell["lat"])
        lon = float(cell["lon"])

        # Create an approximate 0.25-degree grid-cell polygon
        # around the IMD grid coordinate.
        west = lon - HALF_CELL
        east = lon + HALF_CELL
        south = lat - HALF_CELL
        north = lat + HALF_CELL

        polygon_geo = {
            "type": "Polygon",
            "coordinates": [[
                [west, south],
                [east, south],
                [east, north],
                [west, north],
                [west, south]
            ]]
        }

        # Transform geographic polygon into DEM CRS.
        polygon_projected = transform_geom(
            "EPSG:4326",
            dem_src.crs,
            polygon_geo
        )

        try:
            dem_data, _ = mask(
                dem_src,
                [polygon_projected],
                crop=True,
                filled=False
            )

            slope_data, _ = mask(
                slope_src,
                [polygon_projected],
                crop=True,
                filled=False
            )

            elevation_values = dem_data[0].compressed()
            slope_values = slope_data[0].compressed()

            elevation_values = elevation_values[
                np.isfinite(elevation_values)
            ]

            slope_values = slope_values[
                np.isfinite(slope_values)
            ]

            if len(elevation_values) == 0 or len(slope_values) == 0:
                print(f"WARNING: No valid terrain data for {lat}, {lon}")
                continue

            record = {
                "lat": lat,
                "lon": lon,
                "mean_elevation_m": float(
                    np.mean(elevation_values)
                ),
                "median_elevation_m": float(
                    np.median(elevation_values)
                ),
                "min_elevation_m": float(
                    np.min(elevation_values)
                ),
                "max_elevation_m": float(
                    np.max(elevation_values)
                ),
                "mean_slope_degrees": float(
                    np.mean(slope_values)
                ),
                "median_slope_degrees": float(
                    np.median(slope_values)
                ),
                "terrain_pixels": int(len(elevation_values))
            }

            terrain_records.append(record)

            print(
                f"Cell {index + 1}: "
                f"Lat={lat}, Lon={lon}, "
                f"Mean elevation={record['mean_elevation_m']:.2f} m, "
                f"Mean slope={record['mean_slope_degrees']:.2f} degrees"
            )

        except ValueError as error:
            print(
                f"WARNING: Could not process cell "
                f"{lat}, {lon}: {error}"
            )


# ==================================================
# 5. SAVE TERRAIN GRID DATASET
# ==================================================

terrain_df = pd.DataFrame(terrain_records)

if terrain_df.empty:
    raise ValueError(
        "No terrain grid cells were successfully processed."
    )

terrain_output = OUTPUT_DIR / "worldcore_grid_terrain_features.csv"

terrain_df.to_csv(terrain_output, index=False)

print("\nTerrain grid features saved.")
print("Successfully processed cells:", len(terrain_df))


# ==================================================
# 6. INTEGRATE DAILY RAINFALL AND TERRAIN
# ==================================================

integrated = rainfall.merge(
    terrain_df,
    on=["lat", "lon"],
    how="left",
    validate="many_to_one"
)

integrated["terrain_data_available"] = (
    integrated["mean_elevation_m"].notna()
)

integrated_output = (
    OUTPUT_DIR / "worldcore_rainfall_terrain_integrated.csv"
)

integrated.to_csv(integrated_output, index=False)

print("\nIntegrated dataset created.")
print("Integrated records:", len(integrated))
print(
    "Records with terrain data:",
    int(integrated["terrain_data_available"].sum())
)


# ==================================================
# 7. CREATE GRID-CELL SUMMARY
# ==================================================

cell_summary = (
    integrated.groupby(["lat", "lon"], as_index=False)
    .agg(
        average_rainfall_mm=("rainfall_mm", "mean"),
        maximum_daily_rainfall_mm=("rainfall_mm", "max"),
        cumulative_rainfall_mm=("rainfall_mm", "sum"),
        mean_elevation_m=("mean_elevation_m", "first"),
        mean_slope_degrees=("mean_slope_degrees", "first")
    )
)

summary_output = (
    REPORT_DIR / "worldcore_spatial_grid_summary.csv"
)

cell_summary.to_csv(summary_output, index=False)


# ==================================================
# 8. CREATE TERRAIN COMPARISON CHART
# ==================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].bar(
    range(len(cell_summary)),
    cell_summary["mean_elevation_m"]
)

axes[0].set_title("Mean Elevation by Rainfall Grid Cell")
axes[0].set_xlabel("Rainfall grid cell")
axes[0].set_ylabel("Mean elevation (m)")
axes[0].set_xticks(range(len(cell_summary)))
axes[0].set_xticklabels(
    [
        f"{row.lat:.2f}, {row.lon:.2f}"
        for row in cell_summary.itertuples()
    ],
    rotation=45,
    ha="right"
)

axes[1].bar(
    range(len(cell_summary)),
    cell_summary["mean_slope_degrees"]
)

axes[1].set_title("Mean Slope by Rainfall Grid Cell")
axes[1].set_xlabel("Rainfall grid cell")
axes[1].set_ylabel("Mean slope (degrees)")
axes[1].set_xticks(range(len(cell_summary)))
axes[1].set_xticklabels(
    [
        f"{row.lat:.2f}, {row.lon:.2f}"
        for row in cell_summary.itertuples()
    ],
    rotation=45,
    ha="right"
)

plt.tight_layout()

chart_path = (
    REPORT_DIR / "worldcore_grid_terrain_comparison.png"
)

plt.savefig(chart_path, dpi=300)
plt.close()


# ==================================================
# 9. VALIDATION
# ==================================================

print("\nINTEGRATION VALIDATION")
print("-" * 60)

print("Original rainfall rows:", len(rainfall))
print("Integrated rows:", len(integrated))
print("Terrain grid cells:", len(terrain_df))

print(
    "Missing terrain records:",
    int(integrated["mean_elevation_m"].isna().sum())
)

print("\nGrid-cell summary:")
print(cell_summary.to_string(index=False))


# ==================================================
# 10. COMPLETION
# ==================================================

print("\n" + "=" * 60)
print("WORLDCORE SPATIAL INTEGRATION COMPLETED")
print("=" * 60)

print("\nGenerated files:")

for path in [
    terrain_output,
    integrated_output,
    summary_output,
    chart_path
]:
    print(path)

print(
    "\nSCIENTIFIC NOTE: Each IMD grid coordinate is treated as "
    "the centre of an approximate 0.25-degree cell. Terrain "
    "statistics are calculated from DEM pixels within that cell. "
    "The rainfall values remain coarse-grid observations; they "
    "are not 30-metre rainfall measurements."
)

print(
    "\nThis integration is an exploratory spatial analysis, "
    "not a calibrated flood-risk prediction."
)
