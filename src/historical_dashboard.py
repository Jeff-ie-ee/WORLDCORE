
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# WORLDCORE - HISTORICAL RAINFALL INTELLIGENCE DASHBOARD
# Study area: Ernakulam, Kerala
# Data source: IMD gridded rainfall dataset
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"

# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="WORLDCORE | Historical Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 WORLDCORE")
st.subheader("Historical Rainfall Intelligence")
st.caption(
    "Ernakulam, Kerala | IMD Daily Rainfall Data | 2015–2025"
)

st.divider()

# ------------------------------------------------------------
# LOAD REPORTS
# ------------------------------------------------------------

@st.cache_data
def load_data():

    files = {
        "annual": "imd_annual_rainfall.csv",
        "monthly": "imd_monthly_climatology.csv",
        "seasonal": "imd_seasonal_rainfall.csv",
        "extreme": "imd_extreme_rainfall_days.csv",
        "categories": "imd_rainfall_category_counts.csv",
        "top10": "imd_top_10_rainfall_days.csv",
        "daily": "imd_rainfall_daily.csv"
    }

    data = {}

    for key, filename in files.items():

        path = (
            ROOT / "data" / "processed" / filename
            if key == "daily"
            else REPORTS / filename
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Required report not found: {path}"
            )

        data[key] = pd.read_csv(path)

    data["daily"]["date"] = pd.to_datetime(
        data["daily"]["date"]
    )

    data["extreme"]["date"] = pd.to_datetime(
        data["extreme"]["date"]
    )

    data["top10"]["date"] = pd.to_datetime(
        data["top10"]["date"]
    )

    return data


try:
    data = load_data()

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.info(
        "Run python src/historical_rainfall_analysis.py "
        "before starting this dashboard."
    )
    st.stop()


annual = data["annual"].copy()
monthly = data["monthly"].copy()
seasonal = data["seasonal"].copy()
extreme = data["extreme"].copy()
categories = data["categories"].copy()
top10 = data["top10"].copy()
daily = data["daily"].copy()

# ------------------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------------------

st.sidebar.header("Dashboard Controls")

years = sorted(annual["year"].astype(int).tolist())

selected_year = st.sidebar.selectbox(
    "Select year",
    options=["All Years"] + years
)

st.sidebar.markdown("---")

st.sidebar.info(
    """
    **Data information**

    Source: IMD gridded rainfall

    Period: 2015–2025

    Resolution: 0.25° grid

    Available grid cells: 7

    Measurement: mm/day
    """
)

# ------------------------------------------------------------
# FILTER DATA
# ------------------------------------------------------------

if selected_year == "All Years":

    filtered_daily = daily.copy()
    filtered_annual = annual.copy()
    filtered_extreme = extreme.copy()

    dashboard_title = "Historical Overview: 2015–2025"

else:

    selected_year = int(selected_year)

    filtered_daily = daily[
        daily["date"].dt.year == selected_year
    ].copy()

    filtered_annual = annual[
        annual["year"] == selected_year
    ].copy()

    filtered_extreme = extreme[
        extreme["date"].dt.year == selected_year
    ].copy()

    dashboard_title = (
        f"Rainfall Analysis: {selected_year}"
    )

# ------------------------------------------------------------
# KEY METRICS
# ------------------------------------------------------------

total_days = len(filtered_daily)

average_rainfall = (
    filtered_daily["rainfall_mm"].mean()
    if total_days else 0
)

maximum_rainfall = (
    filtered_daily["rainfall_mm"].max()
    if total_days else 0
)

total_rainfall = (
    filtered_daily["rainfall_mm"].sum()
)

heavy_days = len(filtered_extreme)

st.header(dashboard_title)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average Daily Rainfall",
    f"{average_rainfall:.2f} mm"
)

col2.metric(
    "Maximum Daily Rainfall",
    f"{maximum_rainfall:.2f} mm"
)

col3.metric(
    "Rainfall Sum",
    f"{total_rainfall:,.2f} mm"
)

col4.metric(
    "Heavy Rainfall Days",
    str(heavy_days)
)

st.caption(
    "Heavy rainfall days here use the project's analysis "
    "threshold of 64.5 mm/day or higher. These are not "
    "flood warnings."
)

st.divider()

# ------------------------------------------------------------
# ANNUAL RAINFALL CHART
# ------------------------------------------------------------

st.subheader("1. Annual Rainfall Trends")

if selected_year == "All Years":

    fig_annual = px.bar(
        annual,
        x="year",
        y="annual_rainfall_mm",
        title="Annual Rainfall (2015–2025)",
        labels={
            "year": "Year",
            "annual_rainfall_mm": "Rainfall (mm)"
        },
        hover_data=[
            "rainy_days",
            "maximum_daily_rainfall_mm"
        ]
    )

    fig_annual.update_layout(
        xaxis=dict(dtick=1),
        height=420
    )

    st.plotly_chart(
        fig_annual,
        use_container_width=True
    )

else:

    year_row = filtered_annual.iloc[0]

    st.metric(
        f"{selected_year} Annual Rainfall",
        f"{year_row['annual_rainfall_mm']:,.2f} mm"
    )

    st.metric(
        "Rainy Days",
        int(year_row["rainy_days"])
    )

# ------------------------------------------------------------
# DAILY RAINFALL CHART
# ------------------------------------------------------------

st.subheader("2. Daily Rainfall Pattern")

fig_daily = px.line(
    filtered_daily,
    x="date",
    y="rainfall_mm",
    title="Daily Regional-Average Rainfall",
    labels={
        "date": "Date",
        "rainfall_mm": "Rainfall (mm/day)"
    }
)

fig_daily.update_layout(height=420)

st.plotly_chart(
    fig_daily,
    use_container_width=True
)

# ------------------------------------------------------------
# MONTHLY CLIMATOLOGY
# ------------------------------------------------------------

st.subheader("3. Monthly Rainfall Distribution")

month_order = [
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September",
    "October", "November", "December"
]

monthly_plot = monthly.copy()

monthly_plot["month_name"] = pd.Categorical(
    monthly_plot["month_name"],
    categories=month_order,
    ordered=True
)

monthly_plot = monthly_plot.sort_values("month")

fig_monthly = px.bar(
    monthly_plot,
    x="month_name",
    y="average_monthly_rainfall_mm",
    title="Average Monthly Rainfall Across 2015–2025",
    labels={
        "month_name": "Month",
        "average_monthly_rainfall_mm": "Rainfall (mm)"
    },
    hover_data=[
        "minimum_monthly_rainfall_mm",
        "maximum_monthly_rainfall_mm"
    ]
)

fig_monthly.update_layout(height=420)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# ------------------------------------------------------------
# SEASONAL ANALYSIS
# ------------------------------------------------------------

st.subheader("4. Seasonal Rainfall Analysis")

fig_seasonal = px.bar(
    seasonal,
    x="season",
    y="average_rainfall_mm",
    title="Average Seasonal Rainfall (2015–2025)",
    labels={
        "season": "Season",
        "average_rainfall_mm": "Average rainfall (mm)"
    },
    hover_data=[
        "minimum_rainfall_mm",
        "maximum_rainfall_mm"
    ]
)

fig_seasonal.update_layout(height=400)

st.plotly_chart(
    fig_seasonal,
    use_container_width=True
)

# ------------------------------------------------------------
# RAINFALL CATEGORY DISTRIBUTION
# ------------------------------------------------------------

st.subheader("5. Rainfall Category Distribution")

category_order = [
    "No Rain",
    "Light",
    "Moderate",
    "Heavy",
    "Very Heavy",
    "Extremely Heavy"
]

categories["category"] = pd.Categorical(
    categories["category"],
    categories=category_order,
    ordered=True
)

categories = categories.sort_values("category")

fig_category = px.pie(
    categories,
    names="category",
    values="number_of_days",
    title="Distribution of Daily Rainfall Categories",
    hole=0.4
)

fig_category.update_layout(height=450)

st.plotly_chart(
    fig_category,
    use_container_width=True
)

# ------------------------------------------------------------
# EXTREME RAINFALL EVENTS
# ------------------------------------------------------------

st.subheader("6. Historical Extreme Rainfall Events")

if filtered_extreme.empty:

    st.info(
        "No days met the project's 64.5 mm/day "
        "extreme-rainfall threshold for this selection."
    )

else:

    st.dataframe(
        filtered_extreme.sort_values(
            "rainfall_mm",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------------------------------
# TOP 10 EVENTS
# ------------------------------------------------------------

if selected_year == "All Years":

    st.subheader("7. Top 10 Historical Rainfall Events")

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True
    )

# ------------------------------------------------------------
# ANNUAL DATA TABLE
# ------------------------------------------------------------

st.subheader("8. Annual Rainfall Statistics")

st.dataframe(
    filtered_annual,
    use_container_width=True,
    hide_index=True
)

# ------------------------------------------------------------
# DOWNLOAD DATA
# ------------------------------------------------------------

st.divider()

st.subheader("Download Historical Data")

csv_data = filtered_daily.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Selected Rainfall Data (CSV)",
    data=csv_data,
    file_name="worldcore_historical_rainfall.csv",
    mime="text/csv"
)

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.divider()

st.caption(
    """
    WORLDCORE | Environmental Intelligence Prototype

    Historical source: IMD gridded rainfall dataset.

    Spatial coverage: Seven available 0.25° grid cells
    within the selected Ernakulam study region.

    The dashboard presents historical rainfall analysis,
    not a validated flood forecast or emergency warning.
    """
)
