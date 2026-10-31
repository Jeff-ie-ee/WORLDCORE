# WORLDCORE
### Integrated Environmental Intelligence Platform for Historical Rainfall and Terrain Analysis

WORLDCORE is an environmental intelligence prototype developed to analyse historical rainfall patterns, explore terrain characteristics, identify rainfall accumulation events, and demonstrate experimental rainfall-based simulation scenarios for the Ernakulam region of Kerala, India.

The project combines historical meteorological data, geospatial terrain analysis, rainfall indicators, and an interactive Streamlit dashboard into one integrated platform.

> **Research prototype:** WORLDCORE is designed for historical analysis and educational experimentation. Its simulation is not calibrated for operational flood prediction, and it must not be used for emergency warnings or real-world flood-risk decisions.

## Key Features

- Historical rainfall analysis covering 2015–2025.
- Annual, monthly, and seasonal rainfall analysis.
- Identification of high-intensity rainfall days.
- Three-day and seven-day rainfall accumulation indicators.
- Historical rainfall event analysis.
- Digital Elevation Model (DEM) processing.
- Terrain elevation and slope analysis.
- Integration of rainfall observations with terrain features.
- Experimental rainfall simulation under multiple scenarios.
- Interactive Streamlit dashboard.
- Automated data validation and integration checks.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data analysis | Pandas, NumPy |
| Visualization | Matplotlib, Plotly |
| Dashboard | Streamlit |
| Geospatial processing | Rasterio, SciPy |
| Machine learning ecosystem | Scikit-learn, PyTorch |
| Data formats | CSV, NetCDF, GeoTIFF |
| Development | Visual Studio Code |

## Project Modules

### 1. Historical Rainfall Intelligence
Analyses historical rainfall data to identify annual trends, monthly patterns, seasonal variations, and extreme rainfall days.

### 2. Historical Rainfall Event Analysis
Calculates rainfall intensity categories and rolling three-day and seven-day accumulation indicators to identify periods of significant rainfall.

### 3. Terrain Intelligence
Uses Copernicus DEM data to generate elevation, slope, and hillshade outputs for terrain exploration.

### 4. Spatial Rainfall–Terrain Integration
Combines rainfall grid observations with terrain characteristics to compare rainfall and elevation/slope across seven spatial grid cells.

### 5. Experimental Simulation Lab
Compares three illustrative rainfall scenarios:
- Historical Baseline
- Increased Rainfall (+25%)
- Extreme Stress Test (+50%)

The simulation uses experimental soil-moisture and storage-index parameters. These values are not measured flood levels or calibrated hydrological outputs.

### 6. Interactive Dashboard
Provides a Streamlit interface for exploring rainfall intelligence, historical events, terrain information, simulation scenarios, and generated reports.

## Dataset and Project Scale

| Dataset / Output | Project scale |
|---|---:|
| Historical rainfall period | 2015–2025 |
| Daily rainfall records | 4,018 |
| Valid rainfall grid cells | 7 |
| Spatial rainfall records | 28,126 |
| Simulation records | 12,054 |
| Flagged rainfall observations | 500 |
| DEM nominal resolution | Approximately 30 m |

The rainfall dataset is based on IMD gridded rainfall data. Terrain analysis uses Copernicus DEM data.

## Selected Historical Findings

- **Wettest year:** 2018, with approximately 4,215.88 mm cumulative regional rainfall.
- **Driest year:** 2016, with approximately 2,192.14 mm cumulative regional rainfall.
- **Highest daily regional rainfall:** Approximately 175.01 mm on 16 August 2018.
- **Spatial analysis:** Seven rainfall grid cells were integrated with corresponding terrain summaries.

The 500 flagged observations are not 500 separate confirmed flood events. Rolling accumulation windows overlap, and the project thresholds are exploratory rather than official warning thresholds.

## Project Structure

```text
WORLDCORE/
│
├── data/
│   ├── raw/
│   │   ├── imd_rainfall.nc
│   │   └── dem/
│   │
│   └── processed/
│       ├── terrain/
│       ├── spatial/
│       ├── imd_rainfall_daily.csv
│       └── imd_rainfall_grid.csv
│
├── src/
│   ├── historical_rainfall_analysis.py
│   ├── historical_flood_intelligence.py
│   ├── historical_simulation_integration.py
│   ├── terrain_analysis.py
│   ├── spatial_rainfall_terrain_integration.py
│   ├── spatial_intelligence_visualization.py
│   ├── worldcore_pro_dashboard.py
│   ├── worldcore_integration_check.py
│   └── worldcore_data_validation.py
│
├── reports/
│   ├── terrain/
│   ├── spatial/
│   └── generated analysis reports
│
├── documentation/
│   ├── screenshots/
│   └── WORLDCORE_Final_Project_Report.md
│
├── README.md
└── requirements.txt
```

*The structure above summarizes the main project folders and scripts. Your actual repository may contain additional files.*

## Installation and Execution

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd WORLDCORE
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the dashboard

```bash
python -m streamlit run .\src\worldcore_pro_dashboard.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

The dashboard requires the project's processed datasets and report files to be available in their expected locations.

## Validation and Testing

The project includes an integration check and a data validation script.

Run the integration check:

```powershell
python .\src\worldcore_integration_check.py
```

Run data validation:

```powershell
python .\src\worldcore_data_validation.py
```

The final validation run completed with **35 checks passed and 0 checks failed**, alongside four warnings documenting expected data and scientific limitations.

## Limitations

- Rainfall analysis uses seven valid coarse