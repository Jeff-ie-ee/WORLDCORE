
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# WORLDCORE - HISTORICAL FLOOD INTELLIGENCE
# Study Area: Ernakulam, Kerala
# Data Period: 2015-2025
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "reports"
    / "imd_rainfall_analysis_dataset.csv"
)

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 1. LOAD AND VALIDATE DATA
# ------------------------------------------------------------

def load_data():

    print("\nLoading historical rainfall data...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}\n"
            "Run historical_rainfall_analysis.py first."
        )

    df = pd.read_csv(INPUT_FILE)

    required_columns = ["date", "rainfall_mm"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Required column missing: {column}"
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

    if (df["rainfall_mm"] < 0).any():
        raise ValueError(
            "Negative rainfall values detected."
        )

    if df["date"].duplicated().any():
        raise ValueError(
            "Duplicate dates detected. Resolve them before analysis."
        )

    # Create a complete daily calendar.
    # Missing observations remain NaN, not zero.
    df = df.set_index("date")

    full_dates = pd.date_range(
        start=df.index.min(),
        end=df.index.max(),
        freq="D"
    )

    missing_dates = len(full_dates.difference(df.index))

    df = df.reindex(full_dates)
    df.index.name = "date"

    print("Records:", len(df))
    print("Missing calendar dates:", missing_dates)

    return df


# ------------------------------------------------------------
# 2. CALCULATE RAINFALL INTENSITY
# ------------------------------------------------------------

def classify_rainfall(value):

    if pd.isna(value):
        return "Missing"

    if value < 0.1:
        return "No Rain"

    elif value < 15.6:
        return "Light"

    elif value < 64.5:
        return "Moderate"

    elif value < 115.6:
        return "Heavy"

    elif value < 204.5:
        return "Very Heavy"

    return "Extremely Heavy"


# ------------------------------------------------------------
# 3. CALCULATE ANTECEDENT RAINFALL
# ------------------------------------------------------------

def calculate_rainfall_indicators(df):

    print("\nCalculating rainfall indicators...")

    result = df.copy()

    rain = result["rainfall_mm"]

    # Current day + preceding days
    result["rainfall_3_day_total_mm"] = (
        rain.rolling(
            window=3,
            min_periods=3
        ).sum()
    )

    result["rainfall_7_day_total_mm"] = (
        rain.rolling(
            window=7,
            min_periods=7
        ).sum()
    )

    # Previous days only, excluding current day
    result["rainfall_previous_3_days_mm"] = (
        rain.shift(1).rolling(
            window=3,
            min_periods=3
        ).sum()
    )

    result["rainfall_previous_7_days_mm"] = (
        rain.shift(1).rolling(
            window=7,
            min_periods=7
        ).sum()
    )

    result["rainfall_intensity"] = (
        rain.apply(classify_rainfall)
    )

    result["month"] = result.index.month
    result["year"] = result.index.year

    result = result.reset_index()

    return result


# ------------------------------------------------------------
# 4. IDENTIFY IMPORTANT RAINFALL EVENTS
# ------------------------------------------------------------

def identify_events(df):

    print("\nIdentifying important rainfall events...")

    events = df[
        (df["rainfall_mm"] >= 64.5)
        | (df["rainfall_3_day_total_mm"] >= 100)
        | (df["rainfall_7_day_total_mm"] >= 150)
    ].copy()

    events["event_reason"] = events.apply(
        lambda row: ", ".join(
            reason for reason, condition in [
                (
                    "Heavy daily rainfall",
                    row["rainfall_mm"] >= 64.5
                ),
                (
                    "High 3-day accumulation",
                    row["rainfall_3_day_total_mm"] >= 100
                ),
                (
                    "High 7-day accumulation",
                    row["rainfall_7_day_total_mm"] >= 150
                )
            ]
            if condition
        ),
        axis=1
    )

    events = events.sort_values(
        "rainfall_7_day_total_mm",
        ascending=False
    )

    return events


# ------------------------------------------------------------
# 5. ANNUAL ANTECEDENT RAINFALL SUMMARY
# ------------------------------------------------------------

def annual_indicator_summary(df):

    summary = df.groupby("year").agg(
        annual_rainfall_mm=("rainfall_mm", "sum"),
        average_daily_rainfall_mm=("rainfall_mm", "mean"),
        maximum_3_day_rainfall_mm=(
            "rainfall_3_day_total_mm", "max"
        ),
        maximum_7_day_rainfall_mm=(
            "rainfall_7_day_total_mm", "max"
        )
    ).reset_index()

    return summary


# ------------------------------------------------------------
# 6. VISUALIZATION
# ------------------------------------------------------------

def create_visualizations(df):

    print("\nGenerating rainfall intelligence charts...")

    # Daily rainfall and 7-day accumulation
    fig, ax1 = plt.subplots(figsize=(14, 6))

    ax1.plot(
        df["date"],
        df["rainfall_mm"],
        label="Daily rainfall",
        alpha=0.65
    )

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Daily rainfall (mm)")

    ax2 = ax1.twinx()

    ax2.plot(
        df["date"],
        df["rainfall_7_day_total_mm"],
        label="7-day rainfall accumulation",
        alpha=0.8
    )

    ax2.set_ylabel("7-day accumulation (mm)")

    plt.title(
        "WORLDCORE: Daily Rainfall and 7-Day Accumulation"
    )

    fig.tight_layout()

    fig.savefig(
        REPORT_DIR / "worldcore_rainfall_accumulation.png",
        dpi=300
    )

    plt.close(fig)

    # Top 20 accumulated rainfall periods
    top_periods = df.nlargest(
        20,
        "rainfall_7_day_total_mm"
    ).sort_values("rainfall_7_day_total_mm")

    plt.figure(figsize=(12, 8))

    plt.barh(
        top_periods["date"].dt.strftime("%Y-%m-%d"),
        top_periods["rainfall_7_day_total_mm"]
    )

    plt.title("Top 20 Seven-Day Rainfall Accumulations")
    plt.xlabel("Seven-day rainfall (mm)")
    plt.ylabel("Date")

    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "worldcore_top_7_day_rainfall.png",
        dpi=300
    )

    plt.close()


# ------------------------------------------------------------
# 7. MAIN EXECUTION
# ------------------------------------------------------------

def main():

    print("\n========================================")
    print(" WORLDCORE HISTORICAL FLOOD INTELLIGENCE")
    print("========================================")

    df = load_data()

    indicators = calculate_rainfall_indicators(df)

    events = identify_events(indicators)

    annual_summary = annual_indicator_summary(
        indicators
    )

    # Save complete indicator dataset
    indicators.to_csv(
        REPORT_DIR / "worldcore_rainfall_indicators.csv",
        index=False
    )

    # Save important events
    events.to_csv(
        REPORT_DIR / "worldcore_historical_rainfall_events.csv",
        index=False
    )

    # Save annual summary
    annual_summary.to_csv(
        REPORT_DIR / "worldcore_annual_rainfall_indicators.csv",
        index=False
    )

    # Save top 20 accumulation periods
    top20 = indicators.nlargest(
        20,
        "rainfall_7_day_total_mm"
    )

    top20.to_csv(
        REPORT_DIR / "worldcore_top_7_day_events.csv",
        index=False
    )

    create_visualizations(indicators)

    print("\n========================================")
    print(" ANALYSIS COMPLETED SUCCESSFULLY")
    print("========================================")

    print("\nImportant rainfall events:", len(events))

    print("\nTop accumulated rainfall periods:")

    print(
        top20[
            [
                "date",
                "rainfall_mm",
                "rainfall_3_day_total_mm",
                "rainfall_7_day_total_mm"
            ]
        ].to_string(index=False)
    )

    print("\nReports saved in:", REPORT_DIR)


if __name__ == "__main__":
    main()
