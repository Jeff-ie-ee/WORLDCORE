
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent

GRID_FILE = ROOT / "data" / "processed" / "imd_rainfall_grid.csv"
DAILY_FILE = ROOT / "data" / "processed" / "imd_rainfall_daily.csv"

REPORTS = ROOT / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

print("\nWORLDCORE - IMD DATA VALIDATION")
print("-" * 45)

# 1. Check that both files exist
if not GRID_FILE.exists():
    raise FileNotFoundError(f"Missing file: {GRID_FILE}")

if not DAILY_FILE.exists():
    raise FileNotFoundError(f"Missing file: {DAILY_FILE}")

# 2. Load datasets
grid = pd.read_csv(GRID_FILE)
daily = pd.read_csv(DAILY_FILE)

grid["time"] = pd.to_datetime(grid["time"])
daily["date"] = pd.to_datetime(daily["date"])

required_grid = {"time", "lat", "lon", "rainfall_mm"}
required_daily = {"date", "rainfall_mm"}

if not required_grid.issubset(grid.columns):
    raise ValueError(f"Unexpected grid columns: {list(grid.columns)}")

if not required_daily.issubset(daily.columns):
    raise ValueError(f"Unexpected daily columns: {list(daily.columns)}")

# 3. Check rainfall values
if (grid["rainfall_mm"].dropna() < 0).any():
    raise ValueError("Negative rainfall values detected.")

# 4. Check daily record coverage
daily_counts = grid.groupby("time").size()

cell_counts = (
    grid.groupby(["lat", "lon"])
    .size()
    .reset_index(name="valid_records")
)

# 5. Recalculate daily average from grid data
recalculated = (
    grid.groupby("time")["rainfall_mm"]
    .mean()
    .reset_index()
)

recalculated.rename(
    columns={"time": "date", "rainfall_mm": "recalculated_mm"},
    inplace=True
)

comparison = daily.merge(recalculated, on="date", how="inner")

comparison["difference_mm"] = (
    comparison["rainfall_mm"] - comparison["recalculated_mm"]
).abs()

max_difference = comparison["difference_mm"].max()

# 6. Check missing dates
expected_dates = pd.date_range(
    start="2015-01-01",
    end="2025-12-31",
    freq="D"
)

missing_dates = expected_dates.difference(
    pd.DatetimeIndex(daily["date"])
)

# 7. Save validation reports
cell_counts.to_csv(
    REPORTS / "imd_grid_cell_coverage.csv",
    index=False
)

comparison.to_csv(
    REPORTS / "imd_daily_validation.csv",
    index=False
)

# 8. Display results
print("\nDATASET SUMMARY")
print(f"Grid records: {len(grid)}")
print(f"Daily records: {len(daily)}")
print(f"Unique grid cells: {grid[['lat', 'lon']].drop_duplicates().shape[0]}")
print(f"Date range: {daily['date'].min()} to {daily['date'].max()}")

print("\nGRID COVERAGE")
print(cell_counts.to_string(index=False))

print("\nDAILY COVERAGE")
print(f"Minimum valid grid cells per day: {daily_counts.min()}")
print(f"Maximum valid grid cells per day: {daily_counts.max()}")
print(f"Average valid grid cells per day: {daily_counts.mean():.2f}")
print(f"Missing dates: {len(missing_dates)}")

print("\nDAILY AVERAGE VALIDATION")
print(f"Matched dates: {len(comparison)}")
print(f"Maximum difference: {max_difference:.10f} mm")

if len(missing_dates) == 0 and max_difference < 0.000001:
    print("\nVALIDATION SUCCESSFUL!")
else:
    print("\nVALIDATION NEEDS ATTENTION.")

print("\nReports saved in:", REPORTS)
