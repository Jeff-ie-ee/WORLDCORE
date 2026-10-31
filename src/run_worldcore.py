
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from simulation_engine import WorldCoreSimulation
from risk_classifier import classify_risk, get_recommendation

print("=" * 65)
print("WORLDCORE - INTEGRATED ENVIRONMENTAL INTELLIGENCE PIPELINE")
print("=" * 65)

# Create simulator
simulator = WorldCoreSimulation()

# Initial environmental conditions
initial_conditions = {
    "temperature_c": 29,
    "humidity_pct": 85,
    "wind_speed_kmh": 15,
    "soil_moisture_pct": 65,
    "current_water_level_cm": 40,
    "hours": 6
}

# Rainfall scenarios
scenarios = {
    "Low Rainfall": 5,
    "Moderate Rainfall": 20,
    "Heavy Rainfall": 50
}

all_results = []

# Run all scenarios
for scenario_name, rainfall in scenarios.items():

    print(f"\nSimulating: {scenario_name}")

    result = simulator.simulate(
        rainfall_mm=rainfall,
        **initial_conditions
    )

    result["scenario"] = scenario_name

    # Classify hourly risk
    result["risk_level"] = result[
        "water_level_cm"
    ].apply(classify_risk)

    result["recommendation"] = result[
        "risk_level"
    ].apply(get_recommendation)

    print(
        "Final water level:",
        result["water_level_cm"].iloc[-1],
        "cm"
    )

    print(
        "Final risk:",
        result["risk_level"].iloc[-1]
    )

    all_results.append(result)

# Combine results
combined = pd.concat(all_results, ignore_index=True)

# Create output folder
Path("reports").mkdir(exist_ok=True)

# Save hourly results
combined.to_csv(
    "reports/worldcore_full_results.csv",
    index=False
)

# Create scenario summary
summary = (
    combined.groupby("scenario")
    .agg(
        final_water_level_cm=("water_level_cm", "last"),
        maximum_water_level_cm=("water_level_cm", "max"),
        final_risk=("risk_level", "last")
    )
    .reset_index()
)

summary["recommendation"] = summary[
    "final_risk"
].apply(get_recommendation)

summary.to_csv(
    "reports/worldcore_final_summary.csv",
    index=False
)

# Plot water-level comparison
plt.figure(figsize=(11, 6))

for scenario_name in scenarios:

    scenario_data = combined[
        combined["scenario"] == scenario_name
    ]

    # Include initial level at hour zero
    levels = [
        initial_conditions["current_water_level_cm"]
    ] + scenario_data["water_level_cm"].tolist()

    hours = list(range(0, initial_conditions["hours"] + 1))

    plt.plot(
        hours,
        levels,
        marker="o",
        label=scenario_name
    )

plt.title("WORLDCORE - Environmental Scenario Simulation")
plt.xlabel("Simulation Hour")
plt.ylabel("Simulated Water Level (cm)")
plt.xticks(range(0, initial_conditions["hours"] + 1))
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/worldcore_dashboard_chart.png")
plt.close()

# Display summary
print("\n" + "=" * 65)
print("WORLDCORE FINAL RISK ASSESSMENT")
print("=" * 65)

print(summary.to_string(index=False))

print("\nGENERATED OUTPUT FILES")
print("1. reports/worldcore_full_results.csv")
print("2. reports/worldcore_final_summary.csv")
print("3. reports/worldcore_dashboard_chart.png")

print("\nWORLDCORE PIPELINE EXECUTED SUCCESSFULLY!")

