
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# WORLDCORE - HISTORICAL RAINFALL SIMULATION INTEGRATION
# Study Area: Ernakulam, Kerala
# Historical Period: 2015-2025
# ============================================================


# 1. PROJECT PATHS

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "reports"
    / "imd_rainfall_analysis_dataset.csv"
)

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# 2. SIMULATION PARAMETERS
# These are experimental assumptions, not calibrated values.

INITIAL_STORAGE_INDEX = 40.0
INITIAL_SOIL_MOISTURE = 65.0

RUNOFF_BASE = 0.15
RUNOFF_SOIL_FACTOR = 0.35

SOIL_RAINFALL_FACTOR = 0.08
DAILY_SOIL_DRYING = 1.0

STORAGE_CONVERSION_FACTOR = 0.10
DAILY_STORAGE_RETENTION = 0.95


# 3. RAINFALL SCENARIOS

SCENARIOS = {
    "Historical Baseline": 1.00,
    "Increased Rainfall": 1.25,
    "Extreme Stress Test": 1.50
}


# ------------------------------------------------------------
# 4. LOAD HISTORICAL DATA
# ------------------------------------------------------------

def load_data():

    print("\nLoading historical rainfall data...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing input dataset: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = ["date", "rainfall_mm"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing required column: {column}"
            )

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["rainfall_mm"] = pd.to_numeric(
        df["rainfall_mm"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["date", "rainfall_mm"]
    )

    df = df.sort_values("date")

    if df["date"].duplicated().any():
        raise ValueError(
            "Duplicate dates found in rainfall dataset."
        )

    if (df["rainfall_mm"] < 0).any():
        raise ValueError(
            "Negative rainfall values found."
        )

    # Ensure that the daily timeline is complete.
    df = df.set_index("date")

    full_dates = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="D"
    )

    df = df.reindex(full_dates)
    df.index.name = "date"

    if df["rainfall_mm"].isna().any():
        missing_count = int(
            df["rainfall_mm"].isna().sum()
        )

        raise ValueError(
            f"{missing_count} rainfall dates are missing. "
            "Do not automatically replace missing observations "
            "with zero rainfall."
        )

    df = df.reset_index()

    print("Records loaded:", len(df))
    print("Start:", df["date"].min().date())
    print("End:", df["date"].max().date())

    return df


# ------------------------------------------------------------
# 5. DAILY SIMULATION ENGINE
# ------------------------------------------------------------

def simulate_daily_rainfall(df, scenario_name, multiplier):

    print(f"\nRunning scenario: {scenario_name}")

    storage_index = INITIAL_STORAGE_INDEX
    soil_moisture = INITIAL_SOIL_MOISTURE

    results = []

    for _, row in df.iterrows():

        date = row["date"]

        original_rainfall = float(
            row["rainfall_mm"]
        )

        # Apply scenario multiplier.
        rainfall = (
            original_rainfall * multiplier
        )

        # Estimate runoff fraction.
        runoff_fraction = (
            RUNOFF_BASE
            + RUNOFF_SOIL_FACTOR
            * (soil_moisture / 100)
        )

        runoff_fraction = min(
            1.0,
            max(0.0, runoff_fraction)
        )

        # Estimated runoff contribution.
        runoff_mm = (
            rainfall * runoff_fraction
        )

        # Update soil moisture.
        soil_moisture = (
            soil_moisture
            + rainfall * SOIL_RAINFALL_FACTOR
            - DAILY_SOIL_DRYING
        )

        soil_moisture = min(
            100.0,
            max(0.0, soil_moisture)
        )

        # Daily storage balance.
        storage_index = (
            storage_index * DAILY_STORAGE_RETENTION
            + runoff_mm * STORAGE_CONVERSION_FACTOR
        )

        storage_index = max(
            0.0,
            storage_index
        )

        results.append({
            "date": date,
            "scenario": scenario_name,
            "original_rainfall_mm": original_rainfall,
            "scenario_rainfall_mm": rainfall,
            "estimated_runoff_mm": runoff_mm,
            "soil_moisture_pct": soil_moisture,
            "simulated_storage_index": storage_index
        })

    return pd.DataFrame(results)


# ------------------------------------------------------------
# 6. RUN ALL SCENARIOS
# ------------------------------------------------------------

def run_all_scenarios(df):

    print("\nRunning all rainfall scenarios...")

    scenario_results = []

    for scenario_name, multiplier in SCENARIOS.items():

        result = simulate_daily_rainfall(
            df,
            scenario_name,
            multiplier
        )

        scenario_results.append(result)

    combined = pd.concat(
        scenario_results,
        ignore_index=True
    )

    return combined


# ------------------------------------------------------------
# 7. GENERATE SCENARIO SUMMARY
# ------------------------------------------------------------

def generate_summary(results):

    summary = results.groupby("scenario").agg(
        average_storage_index=(
            "simulated_storage_index", "mean"
        ),
        maximum_storage_index=(
            "simulated_storage_index", "max"
        ),
        final_storage_index=(
            "simulated_storage_index", "last"
        ),
        average_soil_moisture=(
            "soil_moisture_pct", "mean"
        ),
        maximum_daily_runoff=(
            "estimated_runoff_mm", "max"
        )
    ).reset_index()

    return summary


# ------------------------------------------------------------
# 8. IDENTIFY HIGH STORAGE PERIODS
# ------------------------------------------------------------

def identify_high_storage_periods(results):

    # Exploratory threshold for this simulation only.
    threshold = 50.0

    events = results[
        results["simulated_storage_index"] >= threshold
    ].copy()

    events.to_csv(
        REPORT_DIR
        / "worldcore_simulated_high_storage_periods.csv",
        index=False
    )

    return events


# ------------------------------------------------------------
# 9. VISUALIZE HISTORICAL SIMULATION
# ------------------------------------------------------------

def create_visualizations(results):

    print("\nGenerating simulation charts...")

    # Storage index over time.
    plt.figure(figsize=(15, 7))

    for scenario in SCENARIOS:

        subset = results[
            results["scenario"] == scenario
        ]

        plt.plot(
            subset["date"],
            subset["simulated_storage_index"],
            label=scenario,
            linewidth=1.2
        )

    plt.title(
        "WORLDCORE - Historical Rainfall Simulation"
    )

    plt.xlabel("Date")
    plt.ylabel("Simulated Storage Index")

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR
        / "worldcore_historical_simulation.png",
        dpi=300
    )

    plt.close()

    # Scenario comparison.
    summary = generate_summary(results)

    plt.figure(figsize=(10, 6))

    plt.bar(
        summary["scenario"],
        summary["maximum_storage_index"]
    )

    plt.title(
        "Maximum Simulated Storage Index by Scenario"
    )

    plt.xlabel("Rainfall Scenario")
    plt.ylabel("Maximum Storage Index")

    plt.xticks(rotation=15)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR
        / "worldcore_storage_scenario_comparison.png",
        dpi=300
    )

    plt.close()


# ------------------------------------------------------------
# 10. MAIN EXECUTION
# ------------------------------------------------------------

def main():

    print("\n========================================")
    print(" WORLDCORE HISTORICAL SIMULATION SYSTEM")
    print("========================================")

    historical_data = load_data()

    results = run_all_scenarios(
        historical_data
    )

    summary = generate_summary(
        results
    )

    high_storage_periods = (
        identify_high_storage_periods(results)
    )

    # Save complete simulation results.
    results.to_csv(
        REPORT_DIR
        / "worldcore_historical_simulation_results.csv",
        index=False
    )

    # Save scenario summary.
    summary.to_csv(
        REPORT_DIR
        / "worldcore_simulation_scenario_summary.csv",
        index=False
    )

    # Create charts.
    create_visualizations(results)

    print("\n========================================")
    print(" SIMULATION COMPLETED SUCCESSFULLY")
    print("========================================")

    print("\nSCENARIO SUMMARY")

    print(
        summary.round(3).to_string(index=False)
    )

    print(
        "\nHigh-storage observations:",
        len(high_storage_periods)
    )

    print(
        "\nReports saved in:",
        REPORT_DIR
    )


if __name__ == "__main__":
    main()

