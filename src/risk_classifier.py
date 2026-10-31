
import pandas as pd
from pathlib import Path

INPUT_FILE = "reports/scenario_comparison.csv"
OUTPUT_FILE = "reports/flood_risk_assessment.csv"

# Demonstration thresholds only.
# Replace with locally validated thresholds for real-world use.
def classify_risk(water_level):
    if water_level >= 80:
        return "CRITICAL"
    elif water_level >= 65:
        return "HIGH"
    elif water_level >= 50:
        return "MODERATE"
    else:
        return "LOW"


def get_recommendation(risk):
    recommendations = {
        "LOW": "Continue monitoring environmental conditions.",
        "MODERATE": "Increase monitoring frequency.",
        "HIGH": "Review preparedness and response plans.",
        "CRITICAL": "Urgently review emergency response procedures."
    }

    return recommendations[risk]


print("=" * 60)
print("WORLDCORE - FLOOD RISK CLASSIFICATION")
print("=" * 60)

df = pd.read_csv(INPUT_FILE)

# Classify every simulated hour
df["risk_level"] = df["water_level_cm"].apply(classify_risk)

df["recommendation"] = df["risk_level"].apply(
    get_recommendation
)

# Create a final assessment for each scenario
summary = (
    df.groupby("scenario")
    .agg(
        final_water_level_cm=("water_level_cm", "last"),
        maximum_water_level_cm=("water_level_cm", "max")
    )
    .reset_index()
)

summary["final_risk"] = summary[
    "final_water_level_cm"
].apply(classify_risk)

summary["recommendation"] = summary[
    "final_risk"
].apply(get_recommendation)

Path("reports").mkdir(exist_ok=True)

df.to_csv(OUTPUT_FILE, index=False)

summary.to_csv(
    "reports/flood_risk_summary.csv",
    index=False
)

print("\nHOURLY RISK ASSESSMENT")
print(
    df[
        ["scenario", "hour", "water_level_cm", "risk_level"]
    ].to_string(index=False)
)

print("\nFINAL SCENARIO RISK SUMMARY")
print(summary.to_string(index=False))

print("\nGenerated files:")
print(OUTPUT_FILE)
print("reports/flood_risk_summary.csv")

print("\nWORLDCORE RISK CLASSIFICATION COMPLETED!")
