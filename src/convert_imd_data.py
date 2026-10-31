
from pathlib import Path
import xarray as xr
import pandas as pd

# Project folders
ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "raw" / "imd_rainfall.nc"
OUTPUT = ROOT / "data" / "processed"

OUTPUT.mkdir(parents=True, exist_ok=True)

print("WORLDCORE - IMD Rainfall Converter")
print("-" * 45)

if not INPUT.exists():
    raise FileNotFoundError(f"File not found: {INPUT}")

# IMPORTANT: Open the nested 'rain' group
ds = xr.open_dataset(
    INPUT,
    group="rain",
    engine="netcdf4"
)

print("\nDataset information:")
print(ds)

print("\nAvailable variables:")
print(list(ds.data_vars))

# Select rainfall variable
rainfall = ds["rain"]

# Convert to DataFrame
df = rainfall.to_dataframe(
    name="rainfall_mm"
).reset_index()

# Remove missing rainfall values
df = df.dropna(subset=["rainfall_mm"])

# Save grid-level observations
grid_file = OUTPUT / "imd_rainfall_grid.csv"
df.to_csv(grid_file, index=False)

# Calculate daily average over available grid points
daily = (
    df.groupby("time")["rainfall_mm"]
    .mean()
    .reset_index()
)

daily.rename(columns={"time": "date"}, inplace=True)

# Save daily rainfall data
daily_file = OUTPUT / "imd_rainfall_daily.csv"
daily.to_csv(daily_file, index=False)

ds.close()

print("\nCONVERSION SUCCESSFUL!")
print("-" * 45)

print("Grid records:", len(df))
print("Daily records:", len(daily))

print("\nDate range:")
print(daily["date"].min(), "to", daily["date"].max())

print("\nRainfall statistics:")
print(daily["rainfall_mm"].describe())

print("\nSaved files:")
print(grid_file)
print(daily_file)

print("\nFirst 5 daily records:")
print(daily.head())
