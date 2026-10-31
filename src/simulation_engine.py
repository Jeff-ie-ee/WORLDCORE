
import numpy as np
import pandas as pd


class WorldCoreSimulation:

    def __init__(self):
        self.name = "WORLDCORE Environmental Simulator"

    def simulate(
        self,
        rainfall_mm,
        temperature_c,
        humidity_pct,
        wind_speed_kmh,
        soil_moisture_pct,
        current_water_level_cm,
        hours=6
    ):

        water_level = float(current_water_level_cm)
        soil_moisture = float(soil_moisture_pct)

        results = []

        for hour in range(1, hours + 1):

            # Simplified experimental environmental model
            rainfall_effect = rainfall_mm * 0.12
            soil_effect = soil_moisture * 0.015

            evaporation_effect = max(
                0,
                (temperature_c - 20) * 0.015
            )

            change = (
                rainfall_effect
                + soil_effect
                - evaporation_effect
                - 0.05
            )

            water_level += change

            water_level = max(0, water_level)

            # Simplified soil moisture response
            soil_moisture = min(
                100,
                soil_moisture + rainfall_mm * 0.03
            )

            results.append({
                "hour": hour,
                "rainfall_mm": rainfall_mm,
                "soil_moisture_pct": round(soil_moisture, 2),
                "water_level_cm": round(water_level, 2),
                "water_level_change_cm": round(change, 2)
            })

        return pd.DataFrame(results)


if __name__ == "__main__":

    simulator = WorldCoreSimulation()

    result = simulator.simulate(
        rainfall_mm=20,
        temperature_c=29,
        humidity_pct=85,
        wind_speed_kmh=15,
        soil_moisture_pct=65,
        current_water_level_cm=40,
        hours=6
    )

    print("\nWORLDCORE SIMULATION RESULTS")
    print("=" * 55)
    print(result.to_string(index=False))

    result.to_csv(
        "reports/simulation_results.csv",
        index=False
    )

    print("\nSimulation saved to reports/simulation_results.csv")
