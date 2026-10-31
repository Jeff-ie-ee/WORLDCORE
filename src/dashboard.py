
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
REPORTS_DIR = PROJECT_ROOT / "reports"

sys.path.insert(0, str(SRC_DIR))

from simulation_engine import WorldCoreSimulation
from risk_classifier import classify_risk, get_recommendation


st.set_page_config(
    page_title="WORLDCORE | Environmental Intelligence",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# 2. LOAD PREDEFINED SIMULATION DATA
# ============================================================

@st.cache_data
def load_data():

    results_path = REPORTS_DIR / "worldcore_full_results.csv"
    summary_path = REPORTS_DIR / "worldcore_final_summary.csv"

    if not results_path.exists():
        st.error(f"Missing file: {results_path}")
        st.stop()

    if not summary_path.exists():
        st.error(f"Missing file: {summary_path}")
        st.stop()

    results = pd.read_csv(results_path)
    summary = pd.read_csv(summary_path)

    return results, summary


# ============================================================
# 3. CUSTOM SIMULATION
# ============================================================

def run_custom_simulation(
    rainfall,
    temperature,
    humidity,
    wind_speed,
    soil_moisture,
    starting_water_level,
    duration
):

    simulator = WorldCoreSimulation()

    raw_result = simulator.simulate(
        rainfall_mm=rainfall,
        temperature_c=temperature,
        humidity_pct=humidity,
        wind_speed_kmh=wind_speed,
        soil_moisture_pct=soil_moisture,
        current_water_level_cm=starting_water_level,
        hours=duration
    )

    # Convert simulation output into a DataFrame.
    if isinstance(raw_result, pd.DataFrame):
        df = raw_result.copy()

    elif isinstance(raw_result, list):
        df = pd.DataFrame(raw_result)

    elif isinstance(raw_result, dict):
        df = pd.DataFrame(raw_result)

    else:
        st.error("Unexpected output from the simulation engine.")
        st.stop()

    # Identify the water-level column.
    if "water_level_cm" not in df.columns:
        possible_columns = [
            column for column in df.columns
            if "water_level" in column.lower()
        ]

        if possible_columns:
            df = df.rename(
                columns={possible_columns[0]: "water_level_cm"}
            )
        else:
            st.error(
                "The simulation output does not contain "
                "a water-level column."
            )
            st.stop()

    # Ensure an hour column exists.
    if "hour" not in df.columns:
        if "simulation_hour" in df.columns:
            df = df.rename(
                columns={"simulation_hour": "hour"}
            )
        else:
            df["hour"] = range(1, len(df) + 1)

    df["hour"] = pd.to_numeric(df["hour"], errors="coerce")
    df["water_level_cm"] = pd.to_numeric(
        df["water_level_cm"], errors="coerce"
    )

    df = df.dropna(
        subset=["hour", "water_level_cm"]
    ).reset_index(drop=True)

    if df.empty:
        st.error("The simulation returned no valid water-level data.")
        st.stop()

    df["scenario"] = "Custom Simulation"

    # Classify risk at every simulation hour.
    df["risk_level"] = df["water_level_cm"].apply(
        classify_risk
    )

    df["recommendation"] = df["risk_level"].apply(
        get_recommendation
    )

    return df


# ============================================================
# 4. RISK COLOUR MAPPING
# ============================================================

RISK_COLORS = {
    "LOW": "green",
    "MODERATE": "orange",
    "HIGH": "darkorange",
    "CRITICAL": "red"
}


# ============================================================
# 5. 3D DIGITAL TWIN
# ============================================================

def create_digital_twin(water_level):

    x = np.linspace(-5, 5, 60)
    y = np.linspace(-5, 5, 60)

    X, Y = np.meshgrid(x, y)

    # Procedurally generated illustrative terrain.
    terrain = (
        0.15
        + 0.018 * (X ** 2 + Y ** 2)
        + 0.10 * np.sin(X) * np.cos(Y)
    )

    # Illustrative water-height mapping.
    water_height = (
        0.30 + (water_level - 40.0) * 0.025
    )

    water_surface = np.where(
        terrain <= water_height,
        water_height,
        np.nan
    )

    fig = go.Figure()

    fig.add_trace(
        go.Surface(
            x=X,
            y=Y,
            z=terrain,
            colorscale="Earth",
            name="Terrain",
            showscale=True,
            colorbar=dict(title="Terrain Height")
        )
    )

    fig.add_trace(
        go.Surface(
            x=X,
            y=Y,
            z=water_surface,
            colorscale=[
                [0, "blue"],
                [1, "cyan"]
            ],
            opacity=0.85,
            name="Simulated Water",
            showscale=False
        )
    )

    fig.update_layout(
        title="WORLDCORE 3D Floodplain",
        scene=dict(
            xaxis_title="Landscape X",
            yaxis_title="Landscape Y",
            zaxis_title="Elevation",
            camera=dict(
                eye=dict(x=1.7, y=1.7, z=1.2)
            )
        ),
        height=650,
        margin=dict(l=0, r=0, t=50, b=0)
    )

    return fig


# ============================================================
# 6. APPLICATION HEADER
# ============================================================

st.sidebar.title("🌍 WORLDCORE Controls")

st.title("🌍 WORLDCORE")

st.subheader(
    "AI-Powered Environmental Intelligence System"
)

st.write(
    "Monitor environmental conditions, simulate rainfall "
    "scenarios, analyze flood risk, and explore an "
    "interactive 3D digital twin."
)

st.markdown("---")


# ============================================================
# 7. SIDEBAR SIMULATION CONTROLS
# ============================================================

simulation_mode = st.sidebar.radio(
    "Choose simulation mode",
    [
        "Predefined Scenarios",
        "Custom Simulation"
    ]
)


# ============================================================
# 8. SELECT PREDEFINED OR CUSTOM SIMULATION
# ============================================================

predefined_results, predefined_summary = load_data()

if simulation_mode == "Predefined Scenarios":

    scenario_options = {
        "Low Rainfall": "Low Rainfall",
        "Moderate Rainfall": "Moderate Rainfall",
        "Heavy Rainfall": "Heavy Rainfall"
    }

    selected_scenario = st.sidebar.selectbox(
        "Select rainfall scenario",
        list(scenario_options.keys()),
        index=2
    )

    scenario_data = predefined_results[
        predefined_results["scenario"] == selected_scenario
    ].copy()

    if scenario_data.empty:
        st.error(
            f"No results found for {selected_scenario}."
        )
        st.stop()

    scenario_data = scenario_data.sort_values("hour")

    current_scenario = selected_scenario

    initial_water_level = 40.0

    st.sidebar.info(
        "Predefined results are generated from the "
        "WORLDCORE integrated simulation pipeline."
    )

    summary_for_comparison = predefined_summary.copy()

else:

    st.sidebar.markdown("### Custom Environmental Conditions")

    rainfall = st.sidebar.slider(
        "Rainfall (mm/hour)",
        min_value=0,
        max_value=100,
        value=35
    )

    temperature = st.sidebar.slider(
        "Temperature (°C)",
        min_value=15,
        max_value=45,
        value=25
    )

    soil_moisture = st.sidebar.slider(
        "Soil Moisture (%)",
        min_value=0,
        max_value=100,
        value=65
    )

    humidity = st.sidebar.slider(
        "Humidity (%)",
        min_value=0,
        max_value=100,
        value=85
    )

    wind_speed = st.sidebar.slider(
        "Wind Speed (km/h)",
        min_value=0,
        max_value=100,
        value=15
    )

    initial_water_level = st.sidebar.slider(
        "Starting Water Level (cm)",
        min_value=0,
        max_value=150,
        value=40
    )

    duration = st.sidebar.slider(
        "Simulation Duration (hours)",
        min_value=1,
        max_value=24,
        value=8
    )

    st.sidebar.success(
        "Custom simulation parameters are ready."
    )

    scenario_data = run_custom_simulation(
        rainfall=rainfall,
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        soil_moisture=soil_moisture,
        starting_water_level=initial_water_level,
        duration=duration
    )

    current_scenario = "Custom Simulation"

    custom_final_level = float(
        scenario_data["water_level_cm"].iloc[-1]
    )

    custom_max_level = float(
        scenario_data["water_level_cm"].max()
    )

    custom_final_risk = classify_risk(
        custom_final_level
    )

    custom_summary = pd.DataFrame([{
        "scenario": "Custom Simulation",
        "final_water_level_cm": custom_final_level,
        "maximum_water_level_cm": custom_max_level,
        "final_risk": custom_final_risk,
        "recommendation": get_recommendation(
            custom_final_risk
        )
    }])

    summary_for_comparison = pd.concat(
        [
            predefined_summary,
            custom_summary
        ],
        ignore_index=True
    )


# ============================================================
# 9. PREPARE SCENARIO METRICS
# ============================================================

scenario_data = scenario_data.sort_values(
    "hour"
).reset_index(drop=True)

final_water_level = float(
    scenario_data["water_level_cm"].iloc[-1]
)

maximum_water_level = float(
    scenario_data["water_level_cm"].max()
)

final_risk = classify_risk(
    final_water_level
)

final_recommendation = get_recommendation(
    final_risk
)

simulation_duration = int(
    scenario_data["hour"].max()
)


# Add starting point to the graph if it is not already present.
if not (scenario_data["hour"] == 0).any():

    starting_row = pd.DataFrame([{
        "hour": 0,
        "water_level_cm": initial_water_level,
        "scenario": current_scenario,
        "risk_level": classify_risk(initial_water_level),
        "recommendation": get_recommendation(
            classify_risk(initial_water_level)
        )
    }])

    chart_data = pd.concat(
        [starting_row, scenario_data],
        ignore_index=True
    )

else:
    chart_data = scenario_data.copy()


# ============================================================
# 10. CURRENT SCENARIO INFORMATION
# ============================================================

st.markdown("---")

st.header(f"Current Mode: {current_scenario}")

if simulation_mode == "Custom Simulation":
    st.caption(
        "Viewing a simulation generated from your custom "
        "environmental parameters."
    )
else:
    st.caption(
        "Viewing a predefined WORLDCORE simulation scenario."
    )


# ============================================================
# 11. ENVIRONMENTAL OVERVIEW
# ============================================================

st.markdown("---")

st.header("📊 Environmental Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Final Water Level",
        f"{final_water_level:.2f} cm"
    )

with col2:
    st.metric(
        "Maximum Water Level",
        f"{maximum_water_level:.2f} cm"
    )

with col3:
    st.metric(
        "Risk Classification",
        final_risk
    )

with col4:
    st.metric(
        "Simulation Duration",
        f"{simulation_duration} hours"
    )


# ============================================================
# 12. WATER-LEVEL SIMULATION CHART
# ============================================================

st.markdown("---")

st.header("📈 Water-Level Simulation")

fig_water = px.line(
    chart_data,
    x="hour",
    y="water_level_cm",
    markers=True,
    title=f"Water-Level Changes — {current_scenario}",
    labels={
        "hour": "Simulation Hour",
        "water_level_cm": "Water Level (cm)"
    }
)

fig_water.update_traces(
    line=dict(width=3)
)

fig_water.update_layout(
    height=450,
    hovermode="x unified"
)

st.plotly_chart(
    fig_water,
    use_container_width=True
)


# ============================================================
# 13. HOURLY FLOOD-RISK ASSESSMENT
# ============================================================

st.markdown("---")

st.header("⚠️ Hourly Flood-Risk Assessment")

risk_table = scenario_data[
    [
        "hour",
        "water_level_cm",
        "risk_level",
        "recommendation"
    ]
].copy()

risk_table = risk_table.rename(
    columns={
        "hour": "Hour",
        "water_level_cm": "Water Level (cm)",
        "risk_level": "Risk Level",
        "recommendation": "System Recommendation"
    }
)

st.dataframe(
    risk_table,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 14. SYSTEM RECOMMENDATION
# ============================================================

st.markdown("---")

st.header("🧠 WORLDCORE Risk Analysis")

st.write(
    f"**Current scenario:** {current_scenario}"
)

st.write(
    f"**Final risk classification:** {final_risk}"
)

st.info(
    f"System recommendation: {final_recommendation}"
)


# ============================================================
# 15. SCENARIO COMPARISON
# ============================================================

st.markdown("---")

st.header("🌧️ Rainfall Scenario Comparison")

if "final_water_level_cm" in summary_for_comparison.columns:

    comparison_fig = px.bar(
        summary_for_comparison,
        x="scenario",
        y="final_water_level_cm",
        color="final_risk",
        text="final_water_level_cm",
        color_discrete_map=RISK_COLORS,
        title="Final Water Level Across Scenarios",
        labels={
            "scenario": "Rainfall Scenario",
            "final_water_level_cm": "Final Water Level (cm)",
            "final_risk": "Final Risk"
        }
    )

    comparison_fig.update_traces(
        texttemplate="%{text:.2f} cm",
        textposition="outside"
    )

    comparison_fig.update_layout(
        height=450
    )

    st.plotly_chart(
        comparison_fig,
        use_container_width=True
    )


# ============================================================
# 16. COMPLETE SCENARIO SUMMARY
# ============================================================

st.markdown("---")

st.header("📋 Complete Scenario Summary")

st.dataframe(
    summary_for_comparison,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 17. 3D DIGITAL TWIN
# ============================================================

st.markdown("---")

st.header("🌊 WORLDCORE 3D Digital Twin")

st.write(
    "Explore the changing simulated water level across "
    "an illustrative three-dimensional landscape."
)

st.subheader("⏱️ Select Simulation Hour")

available_hours = sorted(
    chart_data["hour"].astype(int).unique().tolist()
)

selected_hour = st.slider(
    "Simulation Hour",
    min_value=int(min(available_hours)),
    max_value=int(max(available_hours)),
    value=int(max(available_hours)),
    step=1
)

selected_row = chart_data[
    chart_data["hour"] == selected_hour
]

if selected_row.empty:
    selected_water_level = initial_water_level
else:
    selected_water_level = float(
        selected_row["water_level_cm"].iloc[0]
    )

selected_risk = classify_risk(
    selected_water_level
)

st.subheader("Current Environmental Conditions")

twin_col1, twin_col2, twin_col3 = st.columns(3)

with twin_col1:
    st.metric(
        "Water Level",
        f"{selected_water_level:.2f} cm"
    )

with twin_col2:
    st.metric(
        "Risk Classification",
        selected_risk
    )

with twin_col3:
    st.metric(
        "Simulation Hour",
        selected_hour
    )

st.markdown(
    f"**WORLDCORE 3D Floodplain — {current_scenario}, "
    f"Hour {selected_hour}**"
)

digital_twin_fig = create_digital_twin(
    selected_water_level
)

st.plotly_chart(
    digital_twin_fig,
    use_container_width=True
)

st.subheader("🌍 Digital Twin Interpretation")

st.write(f"Current scenario: **{current_scenario}**")

st.write(f"Simulation hour: **{selected_hour}**")

st.write(
    f"Simulated water level: **{selected_water_level:.2f} cm**"
)

st.write(
    f"Risk classification: **{selected_risk}**"
)

st.warning(
    "The 3D landscape is procedurally generated. Its "
    "water-height mapping is illustrative and does not "
    "represent real terrain, geographic flood extent, "
    "or a physically validated hydrological model."
)


# ============================================================
# 18. EXPORT SIMULATION DATA
# ============================================================

st.markdown("---")

st.header("📥 Export Simulation Data")

csv_current = scenario_data.to_csv(
    index=False
).encode("utf-8")

csv_summary = summary_for_comparison.to_csv(
    index=False
).encode("utf-8")

download_col1, download_col2 = st.columns(2)

with download_col1:
    st.download_button(
        label="Download Current Scenario Results",
        data=csv_current,
        file_name="worldcore_current_simulation.csv",
        mime="text/csv"
    )

with download_col2:
    st.download_button(
        label="Download Scenario Risk Summary",
        data=csv_summary,
        file_name="worldcore_scenario_summary.csv",
        mime="text/csv"
    )


# ============================================================
# 19. FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <h2>🌍 WORLDCORE</h2>
        <p>AI-Powered Environmental Intelligence System</p>
        <p>Academic Project Prototype</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "Disclaimer: This prototype uses synthetic data, simplified "
    "simulation equations, and illustrative risk thresholds. "
    "It is not an operational flood warning or emergency-response system."
)
