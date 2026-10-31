
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# WORLDCORE - DAY 24
# Geographic and Spatial Rainfall Intelligence
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "imd_rainfall_grid.csv"

st.set_page_config(
    page_title="WORLDCORE | Spatial Intelligence",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 WORLDCORE")
st.subheader("Day 24 — Geographic & Spatial Rainfall Intelligence")

st.caption(
    "Study area: Ernakulam, Kerala | "
    "Source: Processed IMD gridded rainfall data"
)

st.info(
    "This dashboard explores rainfall variation across available IMD grid cells. "
    "It does not predict street-level flooding or represent actual flood depth."
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    # Normalize column names
    df.columns = [
        str(col).strip().lower().replace(" ", "_")
        for col in df.columns
    ]

    # Detect required columns
    aliases = {
        "date": ["date", "time", "datetime"],
        "latitude": ["latitude", "lat"],
        "longitude": ["longitude", "lon", "long"],
        "rainfall": [
            "rainfall_mm",
            "rainfall",
            "rain_mm",
            "rf"
        ]
    }

    detected = {}

    for target, possible_names in aliases.items():

        for name in possible_names:

            if name in df.columns:
                detected[target] = name
                break

        if target not in detected:
            raise ValueError(
                f"Could not identify the {target} column. "
                f"Available columns: {list(df.columns)}"
            )

    df = df.rename(columns={
        detected["date"]: "date",
        detected["latitude"]: "latitude",
        detected["longitude"]: "longitude",
        detected["rainfall"]: "rainfall_mm"
    })

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    for col in ["latitude", "longitude", "rainfall_mm"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        subset=[
            "date",
            "latitude",
            "longitude",
            "rainfall_mm"
        ]
    )

    return df


try:
    data = load_data()

except Exception as error:
    st.error(f"Dataset loading failed: {error}")
    st.stop()


# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

if data.empty:
    st.error("No valid geographic rainfall records found.")
    st.stop()

grid_summary = (
    data.groupby(
        ["latitude", "longitude"],
        as_index=False
    )
    .agg(
        average_rainfall=("rainfall_mm", "mean"),
        maximum_rainfall=("rainfall_mm", "max"),
        cumulative_rainfall=("rainfall_mm", "sum"),
        observation_count=("rainfall_mm", "count")
    )
)

dates = sorted(data["date"].dt.date.unique())

st.success(
    f"Loaded {len(data):,} rainfall observations "
    f"across {len(grid_summary)} valid grid cells."
)


# --------------------------------------------------
# TOP-LEVEL METRICS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Valid Grid Cells",
    len(grid_summary)
)

col2.metric(
    "Average Rainfall",
    f"{data['rainfall_mm'].mean():.2f} mm"
)

col3.metric(
    "Maximum Rainfall",
    f"{data['rainfall_mm'].max():.2f} mm"
)

col4.metric(
    "Observation Days",
    data["date"].dt.date.nunique()
)


# --------------------------------------------------
# MAP MODE
# --------------------------------------------------

st.divider()
st.header("1. Geographic Rainfall Distribution")

map_mode = st.radio(
    "Choose geographic analysis",
    [
        "Average Rainfall",
        "Maximum Rainfall",
        "Cumulative Rainfall",
        "Selected Day"
    ],
    horizontal=True
)

if map_mode == "Average Rainfall":

    map_data = grid_summary.copy()
    color_column = "average_rainfall"
    map_title = "Average Rainfall Across Grid Cells"

elif map_mode == "Maximum Rainfall":

    map_data = grid_summary.copy()
    color_column = "maximum_rainfall"
    map_title = "Maximum Daily Rainfall Across Grid Cells"

elif map_mode == "Cumulative Rainfall":

    map_data = grid_summary.copy()
    color_column = "cumulative_rainfall"
    map_title = "Cumulative Rainfall Across Grid Cells"

else:

    selected_date = st.select_slider(
        "Select a date",
        options=dates,
        value=dates[-1]
    )

    map_data = data[
        data["date"].dt.date == selected_date
    ].copy()

    color_column = "rainfall_mm"
    map_title = f"Rainfall Distribution — {selected_date}"


# --------------------------------------------------
# INTERACTIVE GEOGRAPHIC MAP
# --------------------------------------------------

if not map_data.empty:

    figure = px.scatter_geo(
        map_data,
        lat="latitude",
        lon="longitude",
        color=color_column,
        size=color_column,
        hover_data={
            "latitude": ":.4f",
            "longitude": ":.4f",
            color_column: ":.2f"
        },
        color_continuous_scale="Turbo",
        projection="natural earth",
        title=map_title,
        labels={
            "latitude": "Latitude",
            "longitude": "Longitude",
            color_column: "Rainfall (mm)"
        }
    )

    figure.update_geos(
        showcountries=True,
        showland=True,
        showocean=True,
        fitbounds="locations"
    )

    figure.update_layout(
        height=550,
        margin=dict(l=10, r=10, t=60, b=10)
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )


# --------------------------------------------------
# GRID CELL COMPARISON
# --------------------------------------------------

st.divider()
st.header("2. Grid Cell Rainfall Comparison")

comparison = grid_summary.sort_values(
    "average_rainfall",
    ascending=False
)

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True
)

bar = px.bar(
    comparison,
    x="longitude",
    y="average_rainfall",
    color="average_rainfall",
    hover_data=["latitude", "maximum_rainfall"],
    color_continuous_scale="Turbo",
    title="Average Rainfall by Geographic Grid Cell",
    labels={
        "longitude": "Longitude",
        "average_rainfall": "Average Rainfall (mm)"
    }
)

st.plotly_chart(
    bar,
    use_container_width=True
)


# --------------------------------------------------
# HIGHEST RAINFALL GRID CELL
# --------------------------------------------------

st.divider()
st.header("3. Highest Rainfall Grid Cell")

highest = grid_summary.loc[
    grid_summary["maximum_rainfall"].idxmax()
]

left, right = st.columns(2)

with left:

    st.metric(
        "Highest Recorded Daily Rainfall",
        f"{highest['maximum_rainfall']:.2f} mm"
    )

with right:

    st.write(
        f"**Latitude:** {highest['latitude']:.4f}"
    )

    st.write(
        f"**Longitude:** {highest['longitude']:.4f}"
    )


# --------------------------------------------------
# EXPORT
# --------------------------------------------------

st.divider()
st.header("4. Download Spatial Analysis")

csv = grid_summary.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Grid Cell Analysis CSV",
    data=csv,
    file_name="worldcore_spatial_rainfall_analysis.csv",
    mime="text/csv"
)

st.caption(
    "WORLDCORE spatial analysis prototype. "
    "Grid-cell statistics describe the available rainfall dataset, "
    "not measured local flood conditions."
)
