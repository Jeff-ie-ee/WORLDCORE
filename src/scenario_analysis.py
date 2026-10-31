
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from simulation_engine import WorldCoreSimulation

print("=" * 60)
print("WORLDCORE - MULTI-SCENARIO ANALYSIS")
print("=" * 60)

simulator = WorldCoreSimulation()

initial_conditions = {
    "temperature_c": 29,
    "humidity_pct": 85,
    "wind_speed_kmh": 15,
    "soil_moisture_pct": 65,
    "current_water_level_cm": 40,
    "hours": 6
}

scenarios = {
    "Low Rainfall": 5,
    "Moderate Rainfall": 20,
    "Heavy Rainfall": 50
}

all_results = []

for scenario_name, rainfall in scenarios.items():

    print(f"\nRunning: {scenario_name}")

    result = simulator.simulate(
        rainfall_mm=rainfall,
        **initial_conditions
    )

    result["scenario"] = scenario_name
    all_results.append(result)

    print(
        "Final simulated water level:",
        result["water_level_cm"].iloc[-1],
        "cm"
    )

combined = pd.concat(all_results, ignore_index=True)

Path("reports").mkdir(exist_ok=True)

combined.to_csv(
    "reports/scenario_comparison.csv",
    index=False
)

plt.figure(figsize=(10, 6))

for scenario_name in scenarios:

    scenario_data = combined[
        combined["scenario"] == scenario_name
    ]

    plt.plot(
        scenario_data["hour"],
        scenario_data["water_level_cm"],
        marker="o",
        label=scenario_name
    )

plt.title("WORLDCORE - Rainfall Scenario Comparison")
plt.xlabel("Simulation Hour")
plt.ylabel("Simulated Water Level (cm)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig("reports/scenario_comparison.png")
plt.close()

summary = combined.groupby("scenario").agg(
    initial_level=("water_level_cm", "first"),
    final_level=("water_level_cm", "last")
)

summary["total_change_cm"] = (
    summary["final_level"] - summary["initial_level"]
)

print("\nFINAL SCENARIO COMPARISON")
print(summary.round(2))

print("\nGenerated files:")
print("reports/scenario_comparison.csv")
print("reports/scenario_comparison.png")

print("\nWORLDCORE SCENARIO ANALYSIS COMPLETED!")
