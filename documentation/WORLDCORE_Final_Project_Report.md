# WORLDCORE
## Integrated Environmental Intelligence Platform for Historical Rainfall and Terrain Analysis

**Project Domain:** Artificial Intelligence, Environmental Intelligence, Geospatial Analysis and Data Science  
**Study Area:** Ernakulam, Kerala, India  
**Historical Study Period:** 2015–2025  
**Project Duration:** 30 Days  
**Student Name:** [Your Name]  
**Institution:** [College Name]  
**Department:** [Department Name]  
**Academic Year:** [Academic Year]

---

## 1. Abstract

WORLDCORE is an integrated environmental intelligence research prototype designed to analyse historical rainfall patterns, identify rainfall accumulation events, integrate rainfall observations with terrain characteristics and explore experimental rainfall scenarios.

The project uses historical Indian Meteorological Department (IMD) gridded rainfall data covering 2015–2025 for the Ernakulam study area. It performs annual, monthly and seasonal rainfall analysis, identifies high-intensity rainfall observations and calculates three-day and seven-day rainfall accumulations.

Copernicus Digital Surface Model (DSM) elevation data is processed to derive elevation, slope and hillshade information. These terrain characteristics are integrated with seven available rainfall grid cells to create spatial visualizations.

An experimental simulation module compares historical baseline, increased rainfall and extreme stress-test scenarios. A Streamlit dashboard brings together rainfall analytics, historical event indicators, terrain visualizations, simulation results and downloadable reports.

WORLDCORE is a research and analytical prototype. Its simulation is not calibrated against observed flood levels and must not be interpreted as an operational flood forecasting or warning system.

## 2. Problem Statement

Historical rainfall and terrain information are often analysed separately. This makes it difficult to explore their combined characteristics through a unified analytical platform.

WORLDCORE addresses this by integrating historical rainfall analysis, terrain processing, spatial comparison and experimental simulation into a single dashboard.

## 3. Objectives

- Analyse historical rainfall patterns from 2015 to 2025.
- Identify high-intensity rainfall observations.
- Calculate three-day and seven-day rainfall accumulations.
- Analyse elevation, slope and terrain characteristics.
- Integrate rainfall and terrain information spatially.
- Compare experimental rainfall scenarios.
- Develop an interactive environmental intelligence dashboard.

## 4. Technologies Used

- Python
- Pandas and NumPy
- Matplotlib and Plotly
- Streamlit
- Rasterio
- SciPy
- IMD gridded rainfall data
- Copernicus DEM/DSM data
- VS Code

## 5. System Modules

### Module 1: Historical Rainfall Analysis
Analyses daily rainfall records and produces annual, monthly and seasonal summaries.

### Module 2: Historical Rainfall Event Intelligence
Calculates rainfall intensity and rolling accumulation indicators to identify observations that meet exploratory thresholds.

### Module 3: Terrain Intelligence
Processes elevation data to derive slope and hillshade visualizations and terrain statistics.

### Module 4: Spatial Rainfall-Terrain Integration
Combines rainfall grid observations with corresponding terrain characteristics for spatial comparison.

### Module 5: Experimental Simulation
Compares three scenarios: Historical Baseline, Increased Rainfall and Extreme Stress Test.

### Module 6: Interactive Dashboard
Provides a unified interface for exploring rainfall, historical events, terrain, simulation and downloadable reports.

## 6. Dataset and Project Results

- Historical rainfall records: 4,018 daily records.
- Historical period: 1 January 2015 to 31 December 2025.
- Spatial rainfall grid cells: 7.
- Integrated rainfall-terrain records: 28,126.
- Simulation records: 12,054.
- Historical event observations: 500.
- Terrain raster resolution: approximately 30 metres.

The highest recorded regional daily rainfall value in the analysed dataset was approximately 175.01 mm on 16 August 2018.

The wettest year in the analysis was 2018, with approximately 4,215.88 mm cumulative rainfall. The driest year was 2016, with approximately 2,192.14 mm.

## 7. Testing and Validation

The Day 28 integration check confirmed that all 18 required project files were available.

The Day 29 data-quality validation completed with:

- 35 checks passed.
- 0 checks failed.
- 4 warnings.

The initial missing values in rolling accumulation columns were retained because earlier observations were unavailable at the beginning of the dataset.

## 8. Limitations

- Rainfall analysis uses seven coarse grid cells rather than continuous high-resolution rainfall observations.
- The approximate grid-cell boundaries require further verification.
- Copernicus DSM elevation can include buildings and vegetation.
- The simulation parameters are experimental and uncalibrated.
- No observed flood-depth or drainage measurements were used for model calibration.
- The system does not produce official flood forecasts or emergency warnings.

## 9. Future Enhancements

- Integrate authoritative administrative boundaries.
- Incorporate higher-resolution rainfall datasets.
- Include drainage networks, soil properties and land-use information.
- Calibrate hydrological models using observed streamflow and flood-level data.
- Develop more advanced geospatial visualization.
- Explore machine-learning models after obtaining suitable validated training data.
- Deploy the platform for controlled research demonstrations.

## 10. Conclusion

WORLDCORE demonstrates an integrated workflow for historical rainfall analysis, terrain processing, spatial comparison and experimental rainfall scenario simulation.

The project combines multiple environmental datasets and analytical methods through a unified interactive dashboard. It provides a foundation for future research into geospatial environmental intelligence and data-driven flood-related studies.

**WORLDCORE is an experimental research prototype and not an operational flood prediction system.**