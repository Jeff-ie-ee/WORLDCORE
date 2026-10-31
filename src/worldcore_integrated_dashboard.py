
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# WORLDCORE - INTEGRATED INTELLIGENCE DASHBOARD
# Historical Rainfall + Daily Simulation
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = BASE_DIR / "reports"

st.set_page_config(
    page_title="WORLDCORE Integrated Intelligence",
    page_icon="🌍",
    layout="wide"
)


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

@st.cache_data
def load_data():

    files = {
        "rainfall": "imd_rainfall_analysis_dataset.csv",
        "simulation": "worldcore_historical_simulation_results.csv",
        "summary": "worldcore_simulation_scenario_summary.csv",
        "events": "worldcore_simulated_high_storage_periods.csv"
    }

    data = {}

    for key, filename in files.items():

        path = REPORT_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing file: {path}. "
                "Run the historical analysis and simulation scripts first."
            )

        data[key] = pd.read_csv(path)

    for key in ["rainfall", "simulation", "events"]:

        if "date" in data[key].columns:
            data[key]["date"] = pd.to_datetime(
                data[key]["date"],
                errors="coerce"
            )

    return data


try:
    data = load_data()

except Exception as error:
    st.error(str(error))
    st.stop()


rainfall = data["rainfall"]
simulation = data["simulation"]
summary = data["summary"]
events = data["events"]


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.title("🌍 WORLDCORE")
st.subheader("Integrated Environmental Intelligence System")

st.markdown(
    """
    **Study Area:** Ernakulam, Kerala

    **Historical Period:** 2015–2025

    This dashboard combines historical IMD rainfall observations
    with experimental daily rainfall simulation scenarios.
    """
)

st.divider()


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

st.sidebar.title("Dashboard Controls")

years = sorted(
    rainfall["date"].dt.year.dropna().unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Select Historical Year",
    ["All Years"] + years
)

scenario_names = simulation["scenario"].unique().tolist()

selected_scenario = st.sidebar.selectbox(
    "Select Simulation Scenario",
    scenario_names
)


# ------------------------------------------------------------
# FILTER DATA
# ------------------------------------------------------------

if selected_year == "All Years":

    filtered_rainfall = rainfall.copy()
    filtered_simulation = simulation.copy()

else:

    filtered_rainfall = rainfall[
        rainfall["date"].dt.year == selected_year
    ].copy()

    filtered_simulation = simulation[
        simulation["date"].dt.year == selected_year
    ].copy()


selected_simulation = filtered_simulation[
    filtered_simulation["scenario"] == selected_scenario
].copy()


# ------------------------------------------------------------
# KEY METRICS
# ------------------------------------------------------------

st.header("Environmental Overview")

col1, col2, col3, col4 = st.columns(4)

average_rainfall = filtered_rainfall[
    "rainfall_mm"
].mean()

maximum_rainfall = filtered_rainfall[
    "rainfall_mm"
].max()

maximum_storage = selected_simulation[
    "simulated_storage_index"
].max()

average_soil = selected_simulation[
    "soil_moisture_pct"
].mean()

col1.metric(
    "Average Daily Rainfall",
    f"{average_rainfall:.2f} mm"
)

col2.metric(
    "Maximum Daily Rainfall",
    f"{maximum_rainfall:.2f} mm"
)

col3.metric(
    "Maximum Storage Index",
    f"{maximum_storage:.2f}"
)

col4.metric(
    "Average Simulated Soil Moisture",
    f"{average_soil:.2f}%"
)

st.caption(
    "Storage index and soil moisture are outputs of the "
    "experimental simulation, not field measurements."
)

st.divider()


# ------------------------------------------------------------
# HISTORICAL RAINFALL CHART
# ------------------------------------------------------------

st.header("1. Historical Rainfall Behaviour")

rainfall_chart = px.line(
    filtered_rainfall,
    x="date",
    y="rainfall_mm",
    title="Daily Historical Rainfall",
    labels={
        "date": "Date",
        "rainfall_mm": "Rainfall (mm)"
    }
)

rainfall_chart.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    rainfall_chart,
    use_container_width=True
)


# ------------------------------------------------------------
# RAINFALL ACCUMULATION
# ------------------------------------------------------------

st.header("2. Rainfall Accumulation")

if "rainfall_7_day_total_mm" in filtered_rainfall.columns:

    accumulation_chart = px.line(
        filtered_rainfall,
        x="date",
        y="rainfall_7_day_total_mm",
        title="Seven-Day Rainfall Accumulation",
        labels={
            "date": "Date",
            "rainfall_7_day_total_mm": "Seven-Day Rainfall (mm)"
        }
    )

    st.plotly_chart(
        accumulation_chart,
        use_container_width=True
    )


# ------------------------------------------------------------
# SIMULATED STORAGE INDEX
# ------------------------------------------------------------

st.header("3. Simulated Water-Storage Behaviour")

storage_chart = px.line(
    selected_simulation,
    x="date",
    y="simulated_storage_index",
    title=f"Storage Index - {selected_scenario}",
    labels={
        "date": "Date",
        "simulated_storage_index": "Storage Index"
    }
)

storage_chart.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    storage_chart,
    use_container_width=True
)


# ------------------------------------------------------------
# SCENARIO COMPARISON
# ------------------------------------------------------------

st.header("4. Rainfall Scenario Comparison")

comparison_chart = px.bar(
    summary,
    x="scenario",
    y="maximum_storage_index",
    color="scenario",
    title="Maximum Simulated Storage Index",
    labels={
        "scenario": "Scenario",
        "maximum_storage_index": "Maximum Storage Index"
    },
    text_auto=".2f"
)

st.plotly_chart(
    comparison_chart,
    use_container_width=True
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ------------------------------------------------------------
# SOIL MOISTURE BEHAVIOUR
# ------------------------------------------------------------

st.header("5. Simulated Soil Moisture")

soil_chart = px.line(
    selected_simulation,
    x="date",
    y="soil_moisture_pct",
    title=f"Soil Moisture - {selected_scenario}",
    labels={
        "date": "Date",
        "soil_moisture_pct": "Simulated Soil Moisture (%)"
    }
)

st.plotly_chart(
    soil_chart,
    use_container_width=True
)


# ------------------------------------------------------------
# HIGH STORAGE PERIODS
# ------------------------------------------------------------

st.header("6. Experimental High-Storage Periods")

selected_events = events[
    events["scenario"] == selected_scenario
].copy()

if selected_year != "All Years":

    selected_events = selected_events[
        selected_events["date"].dt.year == selected_year
    ]

st.metric(
    "Observations Above Experimental Threshold",
    len(selected_events)
)

if not selected_events.empty:

    st.dataframe(
        selected_events[
            [
                "date",
                "original_rainfall_mm",
                "scenario_rainfall_mm",
                "estimated_runoff_mm",
                "simulated_storage_index"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No observations crossed the experimental "
        "storage-index threshold in this selection."
    )


# ------------------------------------------------------------
# DOWNLOAD
# ------------------------------------------------------------

st.divider()

st.header("7. Export Simulation Results")

download_data = selected_simulation.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Selected Simulation Data",
    data=download_data,
    file_name="worldcore_integrated_simulation.csv",
    mime="text/csv"
)


# ------------------------------------------------------------
# SCIENTIFIC LIMITATIONS
# ------------------------------------------------------------

st.divider()

st.subheader("Model Information and Limitations")

st.warning(
    """
    This is an experimental environmental intelligence prototype.

    Historical rainfall values are regional-average IMD grid estimates.
    Storage index, runoff and soil moisture are simulated values based
    on assumed coefficients.

    The model is not calibrated against observed flood levels, drainage
    networks or local terrain. It must not be used for real-world
    flood warnings or emergency decisions.
    """
)

st.caption(
    "WORLDCORE | Integrated Environmental Intelligence | 2026"
)
