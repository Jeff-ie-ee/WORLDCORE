
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# WORLDCORE - MAIN ENVIRONMENTAL INTELLIGENCE DASHBOARD
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
SPATIAL = REPORTS / "spatial"
TERRAIN = REPORTS / "terrain"

st.set_page_config(
    page_title="WORLDCORE | Environmental Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #159D82;
}
.subtitle {
    color: #8B949E;
    font-size: 15px;
}
div[data-testid="stMetric"] {
    background: rgba(100, 150, 150, 0.08);
    padding: 16px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- DATA LOADING ----------------

@st.cache_data
def load_csv(path):
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


rainfall = load_csv(
    REPORTS / "imd_rainfall_analysis_dataset.csv"
)

indicators = load_csv(
    REPORTS / "worldcore_rainfall_indicators.csv"
)

annual = load_csv(
    REPORTS / "imd_annual_rainfall.csv"
)

monthly = load_csv(
    REPORTS / "imd_monthly_climatology.csv"
)

seasonal = load_csv(
    REPORTS / "imd_seasonal_rainfall.csv"
)

events = load_csv(
    REPORTS / "worldcore_historical_rainfall_events.csv"
)

simulation = load_csv(
    REPORTS / "worldcore_historical_simulation_results.csv"
)

scenario_summary = load_csv(
    REPORTS / "worldcore_simulation_scenario_summary.csv"
)

spatial = load_csv(
    SPATIAL / "worldcore_spatial_grid_summary.csv"
)

terrain_stats = load_csv(
    TERRAIN / "worldcore_terrain_statistics.csv"
)


# ---------------- HELPER FUNCTIONS ----------------

def find_column(data, candidates):
    for candidate in candidates:
        if candidate in data.columns:
            return candidate
    return None


def show_image(path, caption):
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.info(f"Visualization not available yet: {path.name}")


def show_table(data):
    if not data.empty:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("This dataset is not available yet.")


# ---------------- SIDEBAR ----------------

st.sidebar.title("🌍 WORLDCORE")
st.sidebar.caption("Environmental Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Rainfall Intelligence",
        "Historical Events",
        "Terrain Intelligence",
        "Simulation Lab",
        "Reports"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Study Area: Ernakulam, Kerala")
st.sidebar.caption("Historical Dataset: 2015–2025")


# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">WORLDCORE</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Integrated Rainfall, Terrain and Environmental Intelligence'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# PAGE 1: OVERVIEW
# ==================================================

if page == "Overview":

    st.subheader("Environmental Intelligence Overview")

    rainfall_col = find_column(
        indicators,
        ["rainfall_mm"]
    )

    date_col = find_column(
        indicators,
        ["date"]
    )

    if not indicators.empty and rainfall_col:

        values = pd.to_numeric(
            indicators[rainfall_col],
            errors="coerce"
        ).dropna()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Historical Records",
            f"{len(indicators):,}"
        )

        c2.metric(
            "Average Daily Rainfall",
            f"{values.mean():.2f} mm"
        )

        c3.metric(
            "Maximum Daily Rainfall",
            f"{values.max():.2f} mm"
        )

        c4.metric(
            "Spatial Grid Cells",
            str(len(spatial)) if not spatial.empty else "N/A"
        )

    else:
        st.warning("Rainfall indicator dataset is unavailable.")

    st.subheader("WORLDCORE Modules")

    a, b, c = st.columns(3)

    a.info("🌧️ **Rainfall Intelligence**\n\nHistorical rainfall patterns and extremes.")

    b.info("⛰️ **Terrain Intelligence**\n\nElevation and slope analysis.")

    c.info("🌊 **Simulation Lab**\n\nExperimental rainfall scenario simulation.")

    st.subheader("Spatial Intelligence")

    show_image(
        SPATIAL / "worldcore_spatial_intelligence_map.png",
        "Rainfall and Terrain Intelligence"
    )

    st.warning(
        "WORLDCORE is an experimental research prototype. "
        "Its simulation outputs are not calibrated flood forecasts "
        "or official emergency warnings."
    )


# ==================================================
# PAGE 2: RAINFALL INTELLIGENCE
# ==================================================

elif page == "Rainfall Intelligence":

    st.subheader("Historical Rainfall Analysis")

    if not indicators.empty:

        data = indicators.copy()

        if "date" in data.columns:
            data["date"] = pd.to_datetime(
                data["date"],
                errors="coerce"
            )

        if "rainfall_mm" in data.columns:

            data["rainfall_mm"] = pd.to_numeric(
                data["rainfall_mm"],
                errors="coerce"
            )

            data = data.dropna(
                subset=["date", "rainfall_mm"]
            )

            fig = px.line(
                data,
                x="date",
                y="rainfall_mm",
                title="Daily Historical Rainfall",
                labels={
                    "date": "Date",
                    "rainfall_mm": "Rainfall (mm)"
                }
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Annual Rainfall")
        show_table(annual)

        st.subheader("Monthly Rainfall Climatology")
        show_table(monthly)

        st.subheader("Seasonal Rainfall")
        show_table(seasonal)

    else:
        st.warning("Historical rainfall data not found.")


# ==================================================
# PAGE 3: HISTORICAL EVENTS
# ==================================================

elif page == "Historical Events":

    st.subheader("Historical Rainfall Event Intelligence")

    if not indicators.empty:

        columns = [
            col for col in [
                "date",
                "rainfall_mm",
                "rainfall_3_day_total_mm",
                "rainfall_7_day_total_mm",
                "rainfall_intensity"
            ]
            if col in indicators.columns
        ]

        show_table(indicators[columns].tail(30))

    st.subheader("Historical Event Records")
    show_table(events)

    st.subheader("Rainfall Accumulation")

    show_image(
        REPORTS / "worldcore_rainfall_accumulation.png",
        "Historical Rainfall Accumulation"
    )

    show_image(
        REPORTS / "worldcore_top_7_day_rainfall.png",
        "Highest Seven-Day Rainfall Accumulations"
    )

    st.caption(
        "Rolling accumulation windows overlap. Event flags are "
        "experimental indicators, not confirmed flood events."
    )


# ==================================================
# PAGE 4: TERRAIN INTELLIGENCE
# ==================================================

elif page == "Terrain Intelligence":

    st.subheader("Digital Elevation and Terrain Analysis")

    st.markdown("### Terrain Maps")

    col1, col2 = st.columns(2)

    with col1:
        show_image(
            TERRAIN / "worldcore_elevation_map.png",
            "Elevation Map"
        )

    with col2:
        show_image(
            TERRAIN / "worldcore_slope_map.png",
            "Slope Map"
        )

    show_image(
        TERRAIN / "worldcore_hillshade.png",
        "Terrain Hillshade"
    )

    st.subheader("Terrain Statistics")
    show_table(terrain_stats)

    st.subheader("Rainfall Grid and Terrain Integration")
    show_table(spatial)

    show_image(
        SPATIAL / "worldcore_spatial_intelligence_map.png",
        "Spatial Rainfall and Terrain Intelligence"
    )

    st.caption(
        "Terrain elevation is derived from Copernicus DSM data. "
        "DSM heights can include buildings and vegetation."
    )


# ==================================================
# PAGE 5: SIMULATION LAB
# ==================================================

elif page == "Simulation Lab":

    st.subheader("Experimental Rainfall Simulation Lab")

    if not scenario_summary.empty:

        st.markdown("### Scenario Comparison")

        show_table(scenario_summary)

    if not simulation.empty:

        st.markdown("### Simulation Dataset")

        scenario_col = find_column(
            simulation,
            ["scenario", "scenario_name"]
        )

        date_col = find_column(
            simulation,
            ["date"]
        )

        storage_col = find_column(
            simulation,
            ["storage_index", "simulated_storage_index"]
        )

        if scenario_col and date_col and storage_col:

            chart_data = simulation.copy()

            chart_data[date_col] = pd.to_datetime(
                chart_data[date_col],
                errors="coerce"
            )

            chart_data[storage_col] = pd.to_numeric(
                chart_data[storage_col],
                errors="coerce"
            )

            fig = px.line(
                chart_data,
                x=date_col,
                y=storage_col,
                color=scenario_col,
                title="Simulated Storage Index by Scenario"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        show_table(simulation.tail(100))

    else:
        st.warning("Simulation results are not available.")

    show_image(
        REPORTS / "worldcore_historical_simulation.png",
        "Historical Simulation Results"
    )

    show_image(
        REPORTS / "worldcore_storage_scenario_comparison.png",
        "Storage Scenario Comparison"
    )

    st.warning(
        "Simulation parameters are experimental and uncalibrated. "
        "Storage index, soil moisture and runoff are simulated values, "
        "not measured flood conditions."
    )


# ==================================================
# PAGE 6: REPORTS
# ==================================================

elif page == "Reports":

    st.subheader("WORLDCORE Research Reports")

    report_files = sorted(REPORTS.rglob("*.csv"))

    if report_files:

        for file_path in report_files:

            with st.expander(file_path.name):

                try:
                    file_data = pd.read_csv(file_path)

                    st.write(
                        f"Rows: {len(file_data):,} | "
                        f"Columns: {len(file_data.columns)}"
                    )

                    st.dataframe(
                        file_data.head(10),
                        use_container_width=True
                    )

                    st.download_button(
                        label=f"Download {file_path.name}",
                        data=file_path.read_bytes(),
                        file_name=file_path.name,
                        mime="text/csv",
                        key=str(file_path)
                    )

                except Exception as error:
                    st.error(str(error))

    else:
        st.info("No CSV reports found.")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "WORLDCORE | Environmental Intelligence Research Prototype | "
    "Ernakulam, Kerala | 2015–2025"
)
