
from pathlib import Path
import pandas as pd
import numpy as np

# ==========================================================
# WORLDCORE - DAY 29 DATA QUALITY VALIDATION
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
SPATIAL = REPORTS / "spatial"

FILES = {
    "Historical rainfall":
        REPORTS / "imd_rainfall_analysis_dataset.csv",

    "Rainfall indicators":
        REPORTS / "worldcore_rainfall_indicators.csv",

    "Historical events":
        REPORTS / "worldcore_historical_rainfall_events.csv",

    "Simulation results":
        REPORTS / "worldcore_historical_simulation_results.csv",

    "Simulation summary":
        REPORTS / "worldcore_simulation_scenario_summary.csv",

    "Spatial grid summary":
        SPATIAL / "worldcore_spatial_grid_summary.csv",

    "Integrated spatial data":
        ROOT / "data/processed/spatial/worldcore_rainfall_terrain_integrated.csv",
}

checks_passed = 0
checks_failed = 0
warnings = 0


# ==========================================================
# VALIDATION FUNCTIONS
# ==========================================================

def report(name, passed, detail=""):
    global checks_passed, checks_failed

    if passed:
        checks_passed += 1
        print(f"[PASS] {name}: {detail}")
    else:
        checks_failed += 1
        print(f"[FAIL] {name}: {detail}")


def warning(name, detail):
    global warnings
    warnings += 1
    print(f"[WARN] {name}: {detail}")


def load_dataset(name):
    path = FILES[name]

    if not path.exists():
        report(
            f"{name} file exists",
            False,
            str(path)
        )
        return None

    try:
        df = pd.read_csv(path)

        report(
            f"{name} loaded",
            True,
            f"{len(df):,} rows, {len(df.columns)} columns"
        )

        return df

    except Exception as error:
        report(
            f"{name} loaded",
            False,
            str(error)
        )
        return None


def check_numeric_column(df, column):
    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    valid = (
        values.notna().all()
        and np.isfinite(values.to_numpy()).all()
    )

    report(
        f"{column} has valid numeric values",
        valid,
        f"{values.notna().sum():,} valid values"
    )

    return values


# ==========================================================
# START VALIDATION
# ==========================================================

print("=" * 65)
print("WORLDCORE - DAY 29 DATA QUALITY VALIDATION")
print("=" * 65)

datasets = {
    name: load_dataset(name)
    for name in FILES
}


# ==========================================================
# 1. HISTORICAL RAINFALL VALIDATION
# ==========================================================

rain = datasets["Historical rainfall"]

if rain is not None:

    report(
        "Rainfall date column exists",
        "date" in rain.columns
    )

    report(
        "Rainfall measurement column exists",
        "rainfall_mm" in rain.columns
    )

    if "date" in rain.columns:

        dates = pd.to_datetime(
            rain["date"],
            errors="coerce"
        )

        report(
            "Rainfall dates valid",
            dates.notna().all(),
            f"{dates.notna().sum():,} valid dates"
        )

        report(
            "No duplicate rainfall dates",
            not dates.duplicated().any(),
            f"{dates.duplicated().sum()} duplicates"
        )

        if dates.notna().all():

            report(
                "Rainfall date range",
                dates.min() == pd.Timestamp("2015-01-01")
                and dates.max() == pd.Timestamp("2025-12-31"),
                f"{dates.min().date()} to {dates.max().date()}"
            )

    if "rainfall_mm" in rain.columns:

        values = check_numeric_column(
            rain,
            "rainfall_mm"
        )

        report(
            "Rainfall values non-negative",
            (values.dropna() >= 0).all(),
            f"Minimum: {values.min():.3f} mm"
        )


# ==========================================================
# 2. RAINFALL INDICATOR VALIDATION
# ==========================================================

indicators = datasets["Rainfall indicators"]

if indicators is not None:

    required_columns = [
        "date",
        "rainfall_mm",
        "rainfall_3_day_total_mm",
        "rainfall_7_day_total_mm",
        "rainfall_intensity",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in indicators.columns
    ]

    report(
        "Indicator columns present",
        len(missing_columns) == 0,
        f"Missing: {missing_columns}"
    )

    if "date" in indicators.columns:

        dates = pd.to_datetime(
            indicators["date"],
            errors="coerce"
        )

        report(
            "Indicator dates valid and unique",
            dates.notna().all()
            and not dates.duplicated().any()
        )

    # Daily rainfall must have no missing values.
    if "rainfall_mm" in indicators.columns:

        check_numeric_column(
            indicators,
            "rainfall_mm"
        )

    # Rolling totals require previous days.
    # Therefore, initial missing values are expected.

    rolling_columns = {
        "rainfall_3_day_total_mm": 2,
        "rainfall_7_day_total_mm": 6,
    }

    for col, expected_missing in rolling_columns.items():

        if col not in indicators.columns:
            continue

        values = pd.to_numeric(
            indicators[col],
            errors="coerce"
        )

        missing_count = int(values.isna().sum())

        remaining_values = values.iloc[expected_missing:]

        valid_remaining = (
            remaining_values.notna().all()
            and np.isfinite(
                remaining_values.to_numpy()
            ).all()
        )

        report(
            f"{col} expected initial missing values",
            missing_count == expected_missing
            and valid_remaining,
            (
                f"{missing_count} missing; "
                f"expected {expected_missing}; "
                f"{remaining_values.notna().sum():,} valid remaining values"
            )
        )

        if missing_count > 0:
            warning(
                f"{col} initial missing values",
                "Expected at the beginning of the dataset because "
                "previous days are unavailable."
            )


# ==========================================================
# 3. HISTORICAL EVENT VALIDATION
# ==========================================================

events = datasets["Historical events"]

if events is not None:

    report(
        "Historical events dataset non-empty",
        len(events) > 0,
        f"{len(events):,} event observations"
    )

    if "date" in events.columns:

        dates = pd.to_datetime(
            events["date"],
            errors="coerce"
        )

        report(
            "Event dates valid",
            dates.notna().all()
        )

    warning(
        "Event interpretation",
        "Overlapping rolling-window flags are not distinct confirmed floods."
    )


# ==========================================================
# 4. SIMULATION VALIDATION
# ==========================================================

simulation = datasets["Simulation results"]

if simulation is not None:

    report(
        "Simulation dataset non-empty",
        len(simulation) > 0
    )

    date_col = next(
        (
            col for col in [
                "date",
                "time",
                "timestamp"
            ]
            if col in simulation.columns
        ),
        None
    )

    scenario_col = next(
        (
            col for col in [
                "scenario",
                "scenario_name"
            ]
            if col in simulation.columns
        ),
        None
    )

    report(
        "Simulation date column identified",
        date_col is not None,
        str(date_col)
    )

    report(
        "Simulation scenario column identified",
        scenario_col is not None,
        str(scenario_col)
    )

    if date_col:

        dates = pd.to_datetime(
            simulation[date_col],
            errors="coerce"
        )

        report(
            "Simulation dates valid",
            dates.notna().all()
        )

    if scenario_col:

        scenarios = simulation[scenario_col].dropna().unique()

        print("      Scenarios found:")

        for scenario in scenarios:
            print(f"        - {scenario}")

        report(
            "Three simulation scenarios present",
            len(scenarios) == 3,
            f"{len(scenarios)} unique scenarios"
        )

    warning(
        "Simulation interpretation",
        "Storage, runoff and soil moisture are experimental simulated values."
    )


# ==========================================================
# 5. SPATIAL DATA VALIDATION
# ==========================================================

spatial = datasets["Spatial grid summary"]

if spatial is not None:

    report(
        "Seven spatial grid cells present",
        len(spatial) == 7,
        f"{len(spatial)} grid cells"
    )

    required_spatial = [
        "lat",
        "lon",
        "mean_elevation_m",
        "mean_slope_degrees",
    ]

    missing = [
        col for col in required_spatial
        if col not in spatial.columns
    ]

    report(
        "Spatial columns present",
        not missing,
        f"Missing: {missing}"
    )

    for col in required_spatial:

        if col in spatial.columns:

            check_numeric_column(
                spatial,
                col
            )


# ==========================================================
# 6. INTEGRATED SPATIAL DATA VALIDATION
# ==========================================================

integrated = datasets["Integrated spatial data"]

if integrated is not None:

    report(
        "Integrated spatial data has 28,126 rows",
        len(integrated) == 28126,
        f"{len(integrated):,} rows"
    )

    report(
        "Integrated spatial data non-empty",
        not integrated.empty
    )


# ==========================================================
# 7. SIMULATION SUMMARY VALIDATION
# ==========================================================

summary = datasets["Simulation summary"]

if summary is not None:

    report(
        "Simulation summary has three scenarios",
        len(summary) == 3,
        f"{len(summary)} rows"
    )


# ==========================================================
# FINAL VALIDATION SUMMARY
# ==========================================================

print("\n" + "=" * 65)
print("DAY 29 VALIDATION SUMMARY")
print("=" * 65)

print(f"Checks passed : {checks_passed}")
print(f"Checks failed : {checks_failed}")
print(f"Warnings      : {warnings}")

if checks_failed == 0:

    print("\nALL EXECUTED VALIDATION CHECKS PASSED.")

else:

    print("\nSOME VALIDATION CHECKS NEED ATTENTION.")

print("\nSCIENTIFIC LIMITATIONS")
print("-" * 65)

print("1. Rainfall is based on seven coarse IMD grid cells.")
print("2. Terrain is derived from Copernicus DSM data.")
print("3. Simulation is not calibrated against observed flood levels.")
print("4. Rolling rainfall totals have initial missing values.")
print("5. WORLDCORE is not an official flood forecasting service.")

print("=" * 65)
