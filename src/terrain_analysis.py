
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt

from scipy.ndimage import distance_transform_edt


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DEM_PATH = (
    ROOT
    / "data"
    / "processed"
    / "terrain"
    / "worldcore_dem_utm43n.tif"
)

OUTPUT_DIR = ROOT / "data" / "processed" / "terrain"
REPORT_DIR = ROOT / "reports" / "terrain"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DEM
# --------------------------------------------------

print("\nWORLDCORE TERRAIN ANALYSIS")
print("=" * 50)

if not DEM_PATH.exists():
    raise FileNotFoundError(
        f"DEM file not found: {DEM_PATH}\n"
        "Run download_process_dem.py first."
    )

with rasterio.open(DEM_PATH) as src:

    dem = src.read(1, masked=True).astype("float32")
    profile = src.profile.copy()

    transform = src.transform
    crs = src.crs

    x_resolution = abs(transform.a)
    y_resolution = abs(transform.e)

    print("DEM loaded successfully.")
    print(f"CRS: {crs}")
    print(f"Raster dimensions: {src.width} x {src.height}")
    print(f"Pixel size: {x_resolution:.2f} m x {y_resolution:.2f} m")
    print(f"Bounds: {src.bounds}")
    print(f"Source NoData value: {src.nodata}")

    if crs is None or not crs.is_projected:
        raise ValueError(
            "DEM must use a projected coordinate system."
        )

    valid_mask = ~np.ma.getmaskarray(dem)
    elevation = dem.filled(np.nan)

    if not np.any(valid_mask):
        raise ValueError("DEM contains no valid elevation pixels.")

    valid_values = elevation[valid_mask]

    print(f"Valid pixels: {len(valid_values):,}")
    print(f"Minimum elevation: {np.min(valid_values):.2f} m")
    print(f"Maximum elevation: {np.max(valid_values):.2f} m")
    print(f"Mean elevation: {np.mean(valid_values):.2f} m")
    print(f"Median elevation: {np.median(valid_values):.2f} m")


# --------------------------------------------------
# 3. PREPARE ELEVATION DATA
# --------------------------------------------------

# Fill only masked NoData pixels for gradient calculation.
# This does not identify water pixels if the source has no
# NoData mask. Inspect the elevation map before interpretation.

if np.any(~valid_mask):

    nearest_indices = distance_transform_edt(
        ~valid_mask,
        return_distances=False,
        return_indices=True
    )

    filled_dem = elevation[tuple(nearest_indices)]

else:
    filled_dem = elevation.copy()

print("\nElevation data prepared.")


# --------------------------------------------------
# 4. CALCULATE SLOPE
# --------------------------------------------------

print("\nCalculating slope...")

gradient_y, gradient_x = np.gradient(
    filled_dem,
    y_resolution,
    x_resolution
)

slope_radians = np.arctan(
    np.sqrt(gradient_x ** 2 + gradient_y ** 2)
)

slope_degrees = np.degrees(slope_radians)

slope_degrees[~valid_mask] = np.nan

print("Slope calculation completed.")


# --------------------------------------------------
# 5. GENERATE HILLSHADE
# --------------------------------------------------

print("Generating hillshade...")

# Calculate terrain orientation.
# The negative y-gradient accounts for raster rows
# increasing southward in a north-up projected raster.

aspect = np.arctan2(
    -gradient_x,
    gradient_y
)

slope_rad = np.arctan(
    np.sqrt(gradient_x ** 2 + gradient_y ** 2)
)

azimuth = np.radians(315)
altitude = np.radians(45)

hillshade = (
    np.sin(altitude) * np.cos(slope_rad)
    +
    np.cos(altitude)
    * np.sin(slope_rad)
    * np.cos(azimuth - aspect)
)

hillshade = np.clip(hillshade, 0, 1)
hillshade[~valid_mask] = np.nan

print("Hillshade generated.")


# --------------------------------------------------
# 6. SAVE SLOPE RASTER
# --------------------------------------------------

slope_profile = profile.copy()

slope_profile.update(
    dtype="float32",
    count=1,
    nodata=-9999.0,
    compress="lzw"
)

slope_output = OUTPUT_DIR / "worldcore_slope_degrees.tif"

slope_to_save = np.where(
    np.isfinite(slope_degrees),
    slope_degrees,
    -9999.0
).astype("float32")

with rasterio.open(slope_output, "w", **slope_profile) as dst:
    dst.write(slope_to_save, 1)

print(f"Slope raster saved: {slope_output}")


# --------------------------------------------------
# 7. SAVE HILLSHADE RASTER
# --------------------------------------------------

hillshade_profile = profile.copy()

hillshade_profile.update(
    dtype="float32",
    count=1,
    nodata=-9999.0,
    compress="lzw"
)

hillshade_output = OUTPUT_DIR / "worldcore_hillshade.tif"

hillshade_to_save = np.where(
    np.isfinite(hillshade),
    hillshade,
    -9999.0
).astype("float32")

with rasterio.open(hillshade_output, "w", **hillshade_profile) as dst:
    dst.write(hillshade_to_save, 1)

print(f"Hillshade raster saved: {hillshade_output}")


# --------------------------------------------------
# 8. ELEVATION MAP
# --------------------------------------------------

print("\nCreating elevation map...")

fig, ax = plt.subplots(figsize=(11, 8))

image = ax.imshow(
    np.ma.masked_invalid(elevation),
    cmap="terrain"
)

plt.colorbar(
    image,
    ax=ax,
    label="Elevation (metres)"
)

ax.set_title("WORLDCORE - Digital Elevation Model")
ax.set_xlabel("Raster column")
ax.set_ylabel("Raster row")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "worldcore_elevation_map.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 9. SLOPE MAP
# --------------------------------------------------

print("Creating slope map...")

fig, ax = plt.subplots(figsize=(11, 8))

image = ax.imshow(
    np.ma.masked_invalid(slope_degrees),
    cmap="YlOrRd",
    vmin=0,
    vmax=30
)

plt.colorbar(
    image,
    ax=ax,
    label="Slope (degrees)"
)

ax.set_title("WORLDCORE - Terrain Slope")
ax.set_xlabel("Raster column")
ax.set_ylabel("Raster row")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "worldcore_slope_map.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 10. HILLSHADE MAP
# --------------------------------------------------

print("Creating hillshade map...")

fig, ax = plt.subplots(figsize=(11, 8))

image = ax.imshow(
    np.ma.masked_invalid(hillshade),
    cmap="gray",
    vmin=0,
    vmax=1
)

plt.colorbar(
    image,
    ax=ax,
    label="Hillshade intensity"
)

ax.set_title("WORLDCORE - Terrain Hillshade")
ax.set_xlabel("Raster column")
ax.set_ylabel("Raster row")

plt.tight_layout()

plt.savefig(
    REPORT_DIR / "worldcore_hillshade.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 11. TERRAIN STATISTICS
# --------------------------------------------------

print("\nCalculating terrain statistics...")

valid_slope = slope_degrees[np.isfinite(slope_degrees)]

slope_classes = {
    "0-2 degrees": (0, 2),
    "2-5 degrees": (2, 5),
    "5-15 degrees": (5, 15),
    "15-30 degrees": (15, 30),
    "Above 30 degrees": (30, np.inf)
}

statistics = [
    {
        "Metric": "Minimum elevation",
        "Value": float(np.min(valid_values)),
        "Unit": "metres"
    },
    {
        "Metric": "Maximum elevation",
        "Value": float(np.max(valid_values)),
        "Unit": "metres"
    },
    {
        "Metric": "Mean elevation",
        "Value": float(np.mean(valid_values)),
        "Unit": "metres"
    },
    {
        "Metric": "Median elevation",
        "Value": float(np.median(valid_values)),
        "Unit": "metres"
    },
    {
        "Metric": "Mean slope",
        "Value": float(np.mean(valid_slope)),
        "Unit": "degrees"
    },
    {
        "Metric": "Maximum slope",
        "Value": float(np.max(valid_slope)),
        "Unit": "degrees"
    }
]

for class_name, (lower, upper) in slope_classes.items():

    count = int(
        np.sum(
            (valid_slope >= lower)
            & (valid_slope < upper)
        )
    )

    percentage = (count / len(valid_slope)) * 100

    statistics.append({
        "Metric": f"Slope class: {class_name}",
        "Value": round(percentage, 2),
        "Unit": "percentage"
    })

statistics_df = pd.DataFrame(statistics)

statistics_path = REPORT_DIR / "worldcore_terrain_statistics.csv"

statistics_df.to_csv(
    statistics_path,
    index=False
)


# --------------------------------------------------
# 12. COMPLETION
# --------------------------------------------------

print("\n" + "=" * 50)
print("WORLDCORE TERRAIN ANALYSIS COMPLETED")
print("=" * 50)

print("\nGenerated files:")

for path in [
    REPORT_DIR / "worldcore_elevation_map.png",
    REPORT_DIR / "worldcore_slope_map.png",
    REPORT_DIR / "worldcore_hillshade.png",
    statistics_path,
    slope_output,
    hillshade_output
]:
    print(path)

print("\nTerrain statistics:")
print(statistics_df.to_string(index=False))

print(
    "\nIMPORTANT: Copernicus GLO-30 is a Digital Surface Model (DSM), "
    "not a bare-earth terrain model. Slope classes are exploratory "
    "descriptions, not flood-risk classifications."
)

print(
    "\nThe DEM has no declared NoData value in the source metadata. "
    "Water pixels and possible artefacts may therefore be included. "
    "Inspect the maps and validate the raster before interpreting "
    "elevations or slopes as land-only measurements."
)
