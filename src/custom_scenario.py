
import sys
from pathlib import Path

import pandas as pd

# Allow imports from the src directory
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from simulation_engine import WorldCoreSimulation
from risk_classifier import classify_risk, get_recommendation


def run_custom_scenario(
    rainfall_mm,
    temperature_c,
    humidity_pct,
    wind_speed_kmh,
    soil_moisture_pct,
    starting_water_level_cm,
    hours
):
    """
    Run a custom environmental scenario using
    the existing WORLDCORE simulation engine.
    """

    simulator = WorldCoreSimulation()

    results = simulator.simulate(
        rainfall_mm=rainfall_mm,
        temperature_c=temperature_c,
        humidity_pct=humidity_pct,
        wind_speed_kmh=wind_speed_kmh,
        soil_moisture_pct=soil_moisture_pct,
        current_water_level_cm=starting_water_level_cm,
        hours=hours
    )

    # Convert simulation output to a DataFrame
    if isinstance(results, pd.DataFrame):
        results = results.copy()
    else:
        results = pd.DataFrame(results)

    # Add risk classifications
    results["risk_level"] = results[
        "water_level_cm"
    ].apply(classify_risk)

    results["recommendation"] = results[
        "risk_level"
    ].apply(get_recommendation)

    return results


if __name__ == "__main__":

    print("=" * 55)
    print("WORLDCORE - CUSTOM SCENARIO SIMULATOR")
    print("=" * 55)

    custom_results = run_custom_scenario(
        rainfall_mm=35,
        temperature_c=29,
        humidity_pct=85,
        wind_speed_kmh=15,
        soil_moisture_pct=65,
        starting_water_level_cm=40,
        hours=8
    )

    print(custom_results.to_string(index=False))

    output_path = (
        SRC_DIR.parent
        / "reports"
        / "custom_scenario_results.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    custom_results.to_csv(
        output_path,
        index=False
    )

    print("\nCUSTOM SCENARIO COMPLETED!")
    print(f"Results saved to: {output_path}")
