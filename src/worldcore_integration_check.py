
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = {
    "Historical rainfall": [
        "reports/imd_rainfall_analysis_dataset.csv",
        "reports/imd_annual_rainfall.csv",
        "reports/imd_monthly_climatology.csv",
        "reports/imd_seasonal_rainfall.csv",
    ],
    "Rainfall event intelligence": [
        "reports/worldcore_rainfall_indicators.csv",
        "reports/worldcore_historical_rainfall_events.csv",
        "reports/worldcore_top_7_day_events.csv",
    ],
    "Simulation": [
        "reports/worldcore_historical_simulation_results.csv",
        "reports/worldcore_simulation_scenario_summary.csv",
    ],
    "Spatial intelligence": [
        "reports/spatial/worldcore_spatial_grid_summary.csv",
        "data/processed/spatial/worldcore_rainfall_terrain_integrated.csv",
        "data/processed/spatial/worldcore_grid_terrain_features.csv",
    ],
    "Terrain": [
        "reports/terrain/worldcore_terrain_statistics.csv",
        "reports/terrain/worldcore_elevation_map.png",
        "reports/terrain/worldcore_slope_map.png",
        "reports/terrain/worldcore_hillshade.png",
    ],
    "Dashboard": [
        "src/worldcore_pro_dashboard.py",
        "reports/spatial/worldcore_spatial_intelligence_map.png",
    ],
}

print("=" * 65)
print("WORLDCORE - DAY 28 MODULE INTEGRATION CHECK")
print("=" * 65)

total = 0
found = 0
missing = []

for module, files in REQUIRED_FILES.items():
    print(f"\n{module}")
    print("-" * 50)

    for relative_path in files:
        total += 1
        path = ROOT / relative_path

        if path.exists():
            found += 1
            print(f"[OK]      {relative_path}")

            if path.suffix.lower() == ".csv":
                try:
                    df = pd.read_csv(path)
                    print(f"          Rows: {len(df):,} | Columns: {len(df.columns)}")
                except Exception as error:
                    print(f"[WARNING] CSV could not be read: {error}")
        else:
            missing.append(relative_path)
            print(f"[MISSING] {relative_path}")

print("\n" + "=" * 65)
print("INTEGRATION SUMMARY")
print("=" * 65)

print(f"Total files checked : {total}")
print(f"Files available     : {found}")
print(f"Files missing       : {len(missing)}")

if missing:
    print("\nMissing files:")
    for item in missing:
        print(f"- {item}")

if not missing:
    print("\nALL REQUIRED FILES ARE AVAILABLE.")
    print("WORLDCORE MODULE INPUT CHECK PASSED.")
else:
    print("\nINTEGRATION CHECK NEEDS ATTENTION.")

print("\nNote: File availability does not prove scientific validity.")
print("=" * 65)
