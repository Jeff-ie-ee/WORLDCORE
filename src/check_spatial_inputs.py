
from pathlib import Path
import pandas as pd
import rasterio

ROOT = Path(__file__).resolve().parent.parent

FILES = {
    "Rainfall grid": ROOT / "data/processed/imd_rainfall_grid.csv",
    "Rainfall analysis": ROOT / "reports/imd_rainfall_analysis_dataset.csv",
    "Historical indicators": ROOT / "reports/worldcore_rainfall_indicators.csv",
}

print("\nWORLDCORE - DAY 26")
print("SPATIAL INPUT VALIDATION")
print("=" * 60)

for name, path in FILES.items():

    print(f"\n{name}")
    print("-" * 60)

    if not path.exists():
        print(f"FILE NOT FOUND: {path}")
        continue

    df = pd.read_csv(path)

    print("File:", path.name)
    print("Rows:", len(df))
    print("Columns:", list(df.columns))
    print("\nFirst 5 records:")
    print(df.head().to_string(index=False))


# Inspect the processed DEM
dem_path = (
    ROOT
    / "data/processed/terrain/worldcore_dem_utm43n.tif"
)

print("\nDEM INFORMATION")
print("-" * 60)

if dem_path.exists():

    with rasterio.open(dem_path) as src:

        print("File:", dem_path.name)
        print("CRS:", src.crs)
        print("Width:", src.width)
        print("Height:", src.height)
        print("Bounds:", src.bounds)
        print("Resolution:", src.res)
        print("NoData:", src.nodata)

else:
    print("DEM FILE NOT FOUND:", dem_path)

print("\n" + "=" * 60)
print("SPATIAL INPUT VALIDATION COMPLETED")
