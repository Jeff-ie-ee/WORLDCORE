
from pathlib import Path
import calendar

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# WORLDCORE - HISTORICAL RAINFALL ANALYSIS
# Study Area: Ernakulam, Kerala
# Period: 2015-2025
# Data Source: IMD Gridded Rainfall Dataset
# ============================================================


# 1. PROJECT PATHS
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "imd_rainfall_daily.csv"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# 2. LOAD DATA
def load_rainfall_data():

    print("\nLoading IMD rainfall dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("Available columns:", list(df.columns))

    # Detect date column
    date_candidates = ["date", "timestamp", "time", "datetime"]

    date_column = next(
        (col for col in date_candidates if col in df.columns),
        None
    )

    # Detect rainfall column
    rainfall_candidates = [
        "rainfall_mm",
        "rain_mm",
        "rainfall",
        "rain",
        "daily_average_rainfall_mm"
    ]

    rainfall_column = next(
        (col for col in rainfall_candidates if col in df.columns),
        None
    )

    if date_column is None:
        raise ValueError("Could not identify the date column.")

    if rainfall_column is None:
        raise ValueError("Could not identify the rainfall column.")

    df = df.rename(columns={
        date_column: "date",
        rainfall_column: "rainfall_mm"
    })

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["rainfall_mm"] = pd.to_numeric(
        df["rainfall_mm"],
        errors="coerce"
    )

    df = df.dropna(subset=["date", "rainfall_mm"])

    df = df.sort_values("date").reset_index(drop=True)

    # Keep the requested analysis period
    df = df[
        (df["date"] >= "2015-01-01") &
        (df["date"] <= "2025-12-31")
    ].copy()

    # Negative rainfall values are invalid
    df = df[df["rainfall_mm"] >= 0].copy()

    if df.empty:
        raise ValueError("No valid rainfall records found.")

    print("\nDataset loaded successfully.")
    print("Total records:", len(df))
    print("Start date:", df["date"].min().date())
    print("End date:", df["date"].max().date())

    return df


# 3. ADD TIME FEATURES
def add_time_features(df):

    df = df.copy()

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["month"].map(
        lambda month: calendar.month_name[int(month)]
    )

    df["day"] = df["date"].dt.day

    # Kerala seasonal classification
    def get_season(month):

        if month in [1, 2]:
            return "Winter"

        elif month in [3, 4, 5]:
            return "Pre-Monsoon"

        elif month in [6, 7, 8, 9]:
            return "Southwest Monsoon"

        else:
            return "Post-Monsoon"

    df["season"] = df["month"].apply(get_season)

    return df


# 4. ANNUAL RAINFALL ANALYSIS
def annual_analysis(df):

    annual = df.groupby("year").agg(
        total_rainfall_mm=("rainfall_mm", "sum"),
        average_daily_rainfall_mm=("rainfall_mm", "mean"),
        maximum_daily_rainfall_mm=("rainfall_mm", "max")
    ).reset_index()

    annual["rainy_days"] = (
        df.assign(rainy=df["rainfall_mm"] >= 2.5)
        .groupby("year")["rainy"]
        .sum()
        .values
    )

    annual.to_csv(
        REPORT_DIR / "imd_annual_rainfall.csv",
        index=False
    )

    print("\nANNUAL RAINFALL ANALYSIS")
    print(annual.to_string(index=False))

    return annual


# 5. MONTHLY CLIMATOLOGY
def monthly_analysis(df):

    monthly = df.groupby("month").agg(
        average_rainfall_mm=("rainfall_mm", "mean"),
        total_rainfall_mm=("rainfall_mm", "sum"),
        maximum_rainfall_mm=("rainfall_mm", "max")
    ).reset_index()

    monthly["month_name"] = monthly["month"].map(
        lambda month: calendar.month_name[int(month)]
    )

    monthly.to_csv(
        REPORT_DIR / "imd_monthly_climatology.csv",
        index=False
    )

    print("\nMONTHLY RAINFALL CLIMATOLOGY")
    print(monthly.to_string(index=False))

    return monthly


# 6. SEASONAL RAINFALL ANALYSIS
def seasonal_analysis(df):

    yearly_seasonal = df.groupby(
        ["year", "season"]
    )["rainfall_mm"].sum().reset_index()

    seasonal = yearly_seasonal.groupby("season").agg(
        average_rainfall_mm=("rainfall_mm", "mean"),
        minimum_rainfall_mm=("rainfall_mm", "min"),
        maximum_rainfall_mm=("rainfall_mm", "max")
    ).reset_index()

    season_order = [
        "Winter",
        "Pre-Monsoon",
        "Southwest Monsoon",
        "Post-Monsoon"
    ]

    seasonal["season"] = pd.Categorical(
        seasonal["season"],
        categories=season_order,
        ordered=True
    )

    seasonal = seasonal.sort_values("season")

    seasonal.to_csv(
        REPORT_DIR / "imd_seasonal_rainfall.csv",
        index=False
    )

    print("\nSEASONAL RAINFALL ANALYSIS")
    print(seasonal.to_string(index=False))

    return seasonal


# 7. EXTREME RAINFALL ANALYSIS
def extreme_rainfall_analysis(df):

    extreme = df[df["rainfall_mm"] >= 64.5].copy()

    extreme = extreme.sort_values(
        "rainfall_mm",
        ascending=False
    )

    extreme.to_csv(
        REPORT_DIR / "imd_extreme_rainfall_days.csv",
        index=False
    )

    print("\nEXTREME RAINFALL DAYS")
    print("Days with rainfall >= 64.5 mm:", len(extreme))

    print(extreme.head(10).to_string(index=False))

    return extreme


# 8. RAINFALL CATEGORY ANALYSIS
def rainfall_category_analysis(df):

    bins = [
        -0.001,
        0.1,
        15.6,
        64.5,
        115.6,
        204.5,
        float("inf")
    ]

    labels = [
        "No Rain",
        "Light",
        "Moderate",
        "Heavy",
        "Very Heavy",
        "Extremely Heavy"
    ]

    df = df.copy()

    df["rainfall_category"] = pd.cut(
        df["rainfall_mm"],
        bins=bins,
        labels=labels,
        right=False
    )

    category_counts = (
        df["rainfall_category"]
        .value_counts(sort=False)
        .reset_index()
    )

    category_counts.columns = [
        "rainfall_category",
        "number_of_days"
    ]

    category_counts.to_csv(
        REPORT_DIR / "imd_rainfall_category_counts.csv",
        index=False
    )

    print("\nRAINFALL CATEGORY DISTRIBUTION")
    print(category_counts.to_string(index=False))

    return category_counts


# 9. TOP 10 RAINFALL DAYS
def top_rainfall_days(df):

    top10 = df.nlargest(
        10,
        "rainfall_mm"
    ).copy()

    top10.to_csv(
        REPORT_DIR / "imd_top_10_rainfall_days.csv",
        index=False
    )

    print("\nTOP 10 RAINFALL DAYS")
    print(top10.to_string(index=False))

    return top10


# 10. VISUALIZATION - ANNUAL RAINFALL
def plot_annual_rainfall(annual):

    plt.figure(figsize=(12, 6))

    plt.bar(
        annual["year"].astype(str),
        annual["total_rainfall_mm"]
    )

    plt.title("Annual Rainfall in Ernakulam (2015-2025)")
    plt.xlabel("Year")
    plt.ylabel("Total Rainfall (mm)")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "imd_annual_rainfall.png",
        dpi=300
    )

    plt.close()


# 11. VISUALIZATION - MONTHLY CLIMATOLOGY
def plot_monthly_rainfall(monthly):

    plt.figure(figsize=(12, 6))

    plt.bar(
        monthly["month_name"],
        monthly["average_rainfall_mm"]
    )

    plt.title("Average Daily Rainfall by Month")
    plt.xlabel("Month")
    plt.ylabel("Average Daily Rainfall (mm)")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "imd_monthly_climatology.png",
        dpi=300
    )

    plt.close()


# 12. VISUALIZATION - SEASONAL RAINFALL
def plot_seasonal_rainfall(seasonal):

    plt.figure(figsize=(10, 6))

    plt.bar(
        seasonal["season"].astype(str),
        seasonal["average_rainfall_mm"]
    )

    plt.title("Average Seasonal Rainfall in Ernakulam")
    plt.xlabel("Season")
    plt.ylabel("Average Seasonal Rainfall (mm)")
    plt.xticks(rotation=20)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        REPORT_DIR / "imd_seasonal_rainfall.png",
        dpi=300
    )

    plt.close()


# 13. MAIN EXECUTION
def main():

    print("\n======================================")
    print(" WORLDCORE HISTORICAL RAINFALL SYSTEM")
    print("======================================")

    df = load_rainfall_data()

    df = add_time_features(df)

    # Save cleaned analysis dataset
    df.to_csv(
        REPORT_DIR / "imd_rainfall_analysis_dataset.csv",
        index=False
    )

    print("\nOVERALL RAINFALL STATISTICS")

    print(
        "Average daily rainfall:",
        round(df["rainfall_mm"].mean(), 2),
        "mm"
    )

    print(
        "Maximum daily rainfall:",
        round(df["rainfall_mm"].max(), 2),
        "mm"
    )

    print(
        "Total of daily regional-average rainfall:",
        round(df["rainfall_mm"].sum(), 2),
        "mm"
    )

    annual = annual_analysis(df)

    monthly = monthly_analysis(df)

    seasonal = seasonal_analysis(df)

    extreme = extreme_rainfall_analysis(df)

    categories = rainfall_category_analysis(df)

    top10 = top_rainfall_days(df)

    # Generate visualizations
    plot_annual_rainfall(annual)

    plot_monthly_rainfall(monthly)

    plot_seasonal_rainfall(seasonal)

    print("\n======================================")
    print(" HISTORICAL ANALYSIS COMPLETED")
    print("======================================")

    print("\nGenerated reports are saved in:")
    print(REPORT_DIR)

    print("\nGenerated charts:")
    print("- imd_annual_rainfall.png")
    print("- imd_monthly_climatology.png")
    print("- imd_seasonal_rainfall.png")


if __name__ == "__main__":
    main()
