# Hyderabad Nature-based Solutions (NbS) Planner

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Overview

This project automates the planning of **green and blue infrastructure** for Hyderabad, India, leveraging **Nature-based Solutions (NbS)** aligned with the [G20 Smart Cities Working Paper on NbS](https://unepdhi.org/wp-content/uploads/sites/2/2023/02/Smart_Sustainable_and_Resilient_Cities_The_Power_of_NbS_Working_Paper_for_the_G20.pdf).

Unlike static urban planning models, this tool:
- **Fetches live data** from OpenStreetMap, weather APIs, and air quality monitors
- **Analyzes urban morphology** including Sky View Factor (SVF) and Roughness Length (z₀)
- **Proposes targeted NbS interventions** based on local climate, density, and wind patterns
- **Generates comprehensive reports** with visualizations and statistics

### Key Features

- 🌍 **Real-time Infrastructure Fetching**: Building footprints, road networks, green/blue spaces from OSM
- 🌤️ **Climate Analysis**: Historical wind data to determine prevailing wind directions
- 🏙️ **Urban Morphology Computation**: Calculates density, roughness length, and ventilation potential
- 🌳 **NbS Decision Engine**: Recommends interventions (green roofs, urban forests, ventilation corridors, etc.)
- 📊 **Advanced Visualizations**: Multi-layer maps, statistics dashboards, and export capabilities
- 🌐 **Interactive Web Dashboard**: Streamlit-powered interface with 6 feature-rich tabs
- 🔧 **Modular Architecture**: Easy to extend and customize for other cities

### 🎯 Live Demo

**[🚀 Launch Web Dashboard Locally](http://localhost:8501)** - Run `streamlit run web_app.py`

Want to deploy online? See [Deployment Instructions](docs/DEPLOYMENT_INSTRUCTIONS.md)

---

## Project Structure

```
Hyderabad_Nbs/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration and constants
│   ├── data_loader.py         # OSM, weather, and AQI data fetching
│   ├── morphology.py          # Urban morphology calculations (SVF, z₀, density)
│   ├── nbs_logic.py           # NbS decision engine (G20-based)
│   ├── visualization.py       # Plotting and map generation
│   ├── reporting.py           # Statistics and report generation
│   └── utils.py               # Helper functions (caching, logging)
├── data/
│   ├── cache/                 # Cached OSM data to avoid repeated API calls
│   ├── references/            # Reference data (MS Buildings, WorldPop)
│   └── references.txt         # Links to external datasets
├── outputs/
│   ├── maps/                  # Generated visualization maps
│   ├── reports/               # Analysis reports and statistics
│   └── exports/               # GeoJSON/CSV exports
├── tools/
│   ├── download_ms_data.py    # Helper for Microsoft Building Footprints
│   ├── batch_process.py       # Batch processing for multiple locations
│   └── visualize_results.py   # Enhanced visualization generator
├── docs/
│   ├── METHODOLOGY.md         # Detailed methodology documentation (23 pages)
│   ├── NBS_GUIDELINES.md      # G20 NbS implementation guidelines (25 pages)
│   ├── PROJECT_SUMMARY.md     # Project setup summary
│   ├── COMPLETE_PROJECT_SUMMARY.md  # Full project documentation
│   ├── BUGFIXES.md            # Issues resolved
│   ├── VISUALIZATION_SUMMARY.md     # Visualization guide
│   ├── WEB_DASHBOARD_GUIDE.md       # Web dashboard manual
│   ├── DEPLOYMENT_INSTRUCTIONS.md   # Deployment guide
│   └── STREAMLIT_DEPLOY_GUIDE.md    # Streamlit Cloud guide
├── tests/
│   └── test_modules.py        # Unit tests (optional)
├── main.py                    # Main execution script
├── web_app.py                 # 🌐 Interactive web dashboard (Streamlit)
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── QUICK_DEPLOY.txt           # Quick deployment guide
└── README.md                  # This file
```

---

## Data Sources

### Real-time Data Sources

| Source | Type | Purpose | Access |
|--------|------|---------|--------|
| **OpenStreetMap** | Buildings, Roads, Green/Blue Spaces | Infrastructure geometry | Via `osmnx` library |
| **Open-Meteo** | Historical weather data | Wind direction & climate analysis | [API](https://open-meteo.com/) (Free, CC BY 4.0) |
| **World AQI** | Air quality index | Pollution monitoring | [API](https://waqi.info/) (Free tier available) |

### Reference Data Sources

| Source | Resolution | Purpose | Link |
|--------|------------|---------|------|
| **Microsoft Global Building Footprints** | ~0.5m precision | Building polygons with height estimates | [GitHub](https://github.com/microsoft/GlobalMLBuildingFootprints) |
| **WorldPop** | 100m | Population density rasters | [Hub](https://hub.worldpop.org/) |
| **Telangana Open Data** | Various | Local government data | [Portal](https://data.telangana.gov.in/) |

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for API calls

### Step 1: Clone or Download

```bash
cd /path/to/your/projects
git clone <your-repo-url> Hyderabad_Nbs
cd Hyderabad_Nbs
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `osmnx` - OpenStreetMap data fetching
- `geopandas` - Geospatial data handling
- `matplotlib`, `seaborn` - Visualizations
- `requests` - API calls
- `rasterio` - Raster data processing (for WorldPop)
- `scikit-learn` - Spatial analysis utilities

### Step 3: Configure Analysis Location

Edit `src/config.py` to change the analysis location:

```python
# Default: Charminar, Old City
CITY_LAT = 17.3616
CITY_LON = 78.4747
ANALYSIS_RADIUS_METERS = 1500  # 1.5km radius

# Alternative: Hitech City
# CITY_LAT = 17.4435
# CITY_LON = 78.3772
```

### Step 4: Run the Analysis

```bash
python main.py
```

The script will:
1. Fetch live OSM data for the specified location
2. Retrieve historical wind patterns
3. Calculate urban morphology metrics
4. Apply NbS decision logic
5. Generate maps and reports in the `outputs/` folder

---

## Usage Examples

### Basic Analysis (Default Location)

```bash
python main.py
```

### Custom Location Analysis

```python
from src.data_loader import fetch_live_infrastructure
from src.morphology import create_analysis_grid, calculate_roughness_and_density
from src.nbs_logic import run_nbs_planning

# Custom coordinates (e.g., Gachibowli)
buildings, streets, green = fetch_live_infrastructure(17.4399, 78.3489, dist=2000)
grid = create_analysis_grid(buildings, grid_size=150)
analyzed = calculate_roughness_and_density(grid, buildings)
nbs_plan = run_nbs_planning(analyzed, wind_dir=270)
```

### Batch Processing Multiple Locations

```bash
# Create sample locations file
python tools/batch_process.py --create-sample

# Process multiple locations
python tools/batch_process.py --csv locations.csv
```

### Launch Interactive Web Dashboard

```bash
streamlit run web_app.py
```

Access at: http://localhost:8501

**Features:**
- 🗺️ Interactive map with clickable cells
- 📊 6 tabs: Interventions, Benefits, Morphology, Data Tables, Reports
- 💾 Download capabilities (reports, CSV, charts)
- 📱 Mobile-responsive
- 🔄 Real-time filtering and exploration

See [Web Dashboard Guide](docs/WEB_DASHBOARD_GUIDE.md) for complete documentation.

---

## Key Modules

### 1. `data_loader.py` - Data Acquisition

Handles all API interactions:
- **`fetch_live_infrastructure()`**: Downloads buildings, streets, parks from OSM
- **`fetch_prevailing_wind_direction()`**: Calculates dominant wind from Open-Meteo historical data
- **`fetch_air_quality()`**: Gets current AQI from WAQI

**Note:** OSM queries for large areas can be slow. The module implements caching to avoid repeated calls.

### 2. `morphology.py` - Urban Morphology Analysis

Calculates critical urban metrics:
- **Plan Area Density (λₚ)**: Fraction of ground covered by buildings
- **Roughness Length (z₀)**: Measure of airflow resistance (higher = more stagnant)
- **Sky View Factor (SVF)**: Openness to sky (affects heat island effect)
- **Building Height Distribution**: From OSM tags or MS Buildings data

**Formula Example (Roughness Length):**
```
z₀ ≈ 0.5 × avg_height × density
```
Reference: Macdonald et al. (1998)

### 3. `nbs_logic.py` - Decision Engine

Implements the G20 NbS framework with decision rules:

| Condition | Proposed NbS | Rationale |
|-----------|--------------|-----------|
| High density (>0.6) + High roughness | **Green Roofs** | Retrofit solution for heat reduction |
| Medium density + High roughness | **Ventilation Corridors** | Remove obstructions, align street trees |
| Medium density + Good flow | **Urban Forests** | Street trees without blocking airflow |
| Low density areas | **Permeable Pavement** | Reduce runoff, recharge groundwater |
| Near water bodies | **Wetland Restoration** | Biodiversity + flood mitigation |

### 4. `visualization.py` - Map Generation

Creates publication-quality maps:
- Base map with streets and buildings
- Color-coded NbS intervention overlay
- Existing green/blue space highlights
- Legend and metadata
- Export to PNG/PDF

### 5. `reporting.py` - Statistics & Reports

Generates comprehensive analysis reports:
- Total area by NbS type
- Cost-benefit estimates
- Population benefiting
- Carbon sequestration potential
- Markdown/PDF report generation

---

## Nature-based Solutions (NbS) Categories

Based on the **G20 Working Paper** and IUCN Global Standard:

### 1. Green Roofs 
- **Application**: Dense urban cores with limited ground space
- **Benefits**: Temperature reduction, stormwater retention, air quality
- **Implementation**: Retrofit on flat roofs, 10-20cm substrate depth

### 2. Urban Forests 
- **Application**: Streets, parks, institutional campuses
- **Benefits**: Shade, air purification, carbon sequestration, biodiversity
- **Species**: Native species like Neem, Peepal, Jamun for Hyderabad

### 3. Ventilation Corridors 
- **Application**: Medium-density areas with poor airflow
- **Benefits**: Heat dissipation, pollutant dispersion
- **Design**: Align with prevailing wind direction, remove low-level obstacles

### 4. Permeable Pavement 
- **Application**: Parking lots, sidewalks, low-traffic roads
- **Benefits**: Groundwater recharge, flood reduction
- **Materials**: Porous concrete, permeable pavers

### 5. Wetland Restoration 
- **Application**: Along water bodies, low-lying flood-prone areas
- **Benefits**: Biodiversity habitat, natural water treatment, recreation
- **Examples**: Hussain Sagar buffer zones

### 6. Sponge City Elements 
- **Application**: Integrated urban drainage systems
- **Benefits**: Flood resilience, water conservation
- **Reference**: China's Sponge City program (30 pilot cities)

---

## Methodology

### Step 1: Data Collection
- Fetch real-time OSM data for infrastructure
- Download historical climate data (1-year for wind analysis)
- Optional: Integrate MS Building Footprints for better height data

### Step 2: Grid Creation
- Divide study area into 150m × 150m analysis cells
- Smaller cells = higher resolution but slower processing

### Step 3: Morphology Calculation
For each grid cell:
- Calculate building coverage fraction
- Estimate average building height
- Compute roughness length (z₀)
- Identify existing green/blue spaces

### Step 4: NbS Assignment
Apply decision tree based on:
- Morphology metrics (density, roughness)
- Wind alignment (for ventilation corridors)
- Proximity to water (for wetlands)
- Land use constraints

### Step 5: Visualization & Reporting
- Generate thematic maps
- Calculate total intervention areas
- Estimate costs and benefits
- Export GeoJSON for GIS integration

**See `docs/METHODOLOGY.md` for detailed technical documentation.**

---

## Integration with Microsoft Building Footprints

The Microsoft Global Building Footprints dataset provides high-precision building polygons with inferred heights.

### Download Instructions

1. Visit: https://github.com/microsoft/GlobalMLBuildingFootprints
2. Navigate to **India** dataset
3. Download the GeoJSONL file (~1.5GB for India)
4. Extract Hyderabad subset:

```python
import geopandas as gpd

# Load full India dataset
gdf = gpd.read_file('India.geojsonl')

# Filter for Hyderabad bounding box
hyderabad = gdf.cx[78.3:78.6, 17.3:17.5]

# Save subset
hyderabad.to_file('data/references/hyderabad_buildings_ms.geojson')
```

5. Update `src/data_loader.py` to use this dataset instead of OSM for better accuracy.

---

## 🔧 Advanced Configuration

### Adjusting NbS Parameters

Edit `src/config.py`:

```python
# Roughness thresholds
ROUGHNESS_HIGH = 1.0    # Dense urban core
ROUGHNESS_MED = 0.5     # Suburban
ROUGHNESS_LOW = 0.1     # Open areas

# NbS Cost Estimates (per sq meter)
COST_GREEN_ROOF = 150         # INR
COST_URBAN_FOREST = 50        # INR per tree
COST_PERMEABLE_PAVEMENT = 80  # INR
```

### Caching Configuration

To reduce API load, OSM data is cached locally:

```python
CACHE_ENABLED = True
CACHE_DIR = 'data/cache/'
CACHE_EXPIRY_DAYS = 30  # Re-fetch after 30 days
```

---

## 📚 Documentation

### 📖 Complete Documentation Suite

This project includes comprehensive documentation covering all aspects of the NbS Planner:

#### 🚀 **Getting Started**
- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Overview of features and setup completion
- **[Complete Project Summary](docs/COMPLETE_PROJECT_SUMMARY.md)** - Full documentation with usage examples

#### 🔬 **Technical Documentation**
- **[Methodology](docs/METHODOLOGY.md)** - Technical details, formulas, and algorithms (23 pages)
  - Data acquisition methods
  - Urban morphology calculations
  - NbS decision logic
  - Benefit quantification
  - Validation and limitations
- **[Bug Fixes](docs/BUGFIXES.md)** - Issues resolved and solutions implemented

#### 🌳 **Implementation & Planning**
- **[NbS Implementation Guidelines](docs/NBS_GUIDELINES.md)** - Complete implementation guide (25 pages)
  - G20 NbS 8 principles explained
  - Detailed specifications for each NbS type (green roofs, urban forests, etc.)
  - 10-year phased implementation roadmap
  - Financing mechanisms (CSR, green bonds, PES)
  - Policy integration strategies
  - Case studies from Singapore, China, Milan
  - Native species recommendations for Hyderabad

#### 📊 **Visualization & Results**
- **[Visualization Summary](docs/VISUALIZATION_SUMMARY.md)** - Overview of all generated charts
- **[Visualization Guide](outputs/visualizations/VISUALIZATIONS_GUIDE.md)** - Detailed interpretation guide for each chart

#### 🌐 **Web Dashboard & Deployment**
- **[Web Dashboard Guide](docs/WEB_DASHBOARD_GUIDE.md)** - Complete manual for the interactive Streamlit dashboard
  - Dashboard features and navigation
  - Interactive controls
  - Download capabilities
  - Customization options
- **[Deployment Instructions](docs/DEPLOYMENT_INSTRUCTIONS.md)** - Step-by-step guide to deploy your dashboard online
- **[Streamlit Deploy Guide](docs/STREAMLIT_DEPLOY_GUIDE.md)** - Comprehensive deployment documentation

#### 📁 **Data Sources**
- **[Data References](data/references.txt)** - Complete list with download instructions
  - Microsoft Building Footprints
  - WorldPop population data
  - OpenStreetMap
  - Open-Meteo weather API
  - WAQI air quality

---

## 🌐 Web Dashboard

### Interactive Dashboard

Launch the interactive web interface:

```bash
streamlit run web_app.py
```

Then open: **http://localhost:8501**

**Features:**
- 🗺️ Interactive map with clickable grid cells
- 📊 6 feature-rich tabs (Interventions, Benefits, Morphology, etc.)
- 📈 Real-time data filtering and exploration
- 💾 Download reports and data exports
- 📱 Mobile-responsive design

**Deploy Online:**
Follow the [Deployment Instructions](docs/DEPLOYMENT_INSTRUCTIONS.md) to publish your dashboard to Streamlit Cloud (free!) and get a public URL.

---

## References

### Key Documents

1. **UNEP (2021)**. *Smart, Sustainable and Resilient Cities: The Power of Nature-based Solutions.* G20 Working Paper. [PDF Link](https://unepdhi.org/wp-content/uploads/sites/2/2023/02/Smart_Sustainable_and_Resilient_Cities_The_Power_of_NbS_Working_Paper_for_the_G20.pdf)

2. **IUCN (2020)**. *Global Standard for Nature-based Solutions.* [Link](https://www.iucn.org/theme/nature-based-solutions/resources/iucn-global-standard-nbs)

3. **Microsoft AI for Earth**. *Global ML Building Footprints.* [GitHub](https://github.com/microsoft/GlobalMLBuildingFootprints)

4. **Macdonald et al. (1998)**. *An improved method for the estimation of surface roughness of obstacle arrays.* Atmospheric Environment, 32(11), 1857-1864.

### Data Attribution

- **OpenStreetMap**: © OpenStreetMap contributors, ODbL License
- **Open-Meteo**: CC BY 4.0 License
- **Microsoft Building Footprints**: ODbL License

---

## Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add Sky View Factor (SVF) calculation using ray-tracing
- [ ] Integrate WorldPop raster for population-weighted prioritization
- [x] ~~Add cost-benefit analysis module~~ ✅ Completed
- [ ] Support for other Indian cities
- [x] ~~Web-based interactive dashboard~~ ✅ Completed (Streamlit)
- [ ] Integration with Telangana government APIs
- [ ] Real-time data streaming
- [ ] Machine learning for NbS optimization
- [ ] API endpoint for programmatic access

---

## License

This project is licensed under the **MIT License**. See `LICENSE` file for details.

Data sources have their own licenses:
- OpenStreetMap: ODbL
- Microsoft Building Footprints: ODbL
- Open-Meteo: CC BY 4.0

---

## Author & Contact

Developed for urban climate resilience and sustainable city planning in Hyderabad.

For questions, suggestions, or collaborations:
- **GitHub Issues**: [Report issues or request features]
- **Email**: [Your contact email]
- **Live Dashboard**: [Your Streamlit app URL once deployed]

### Quick Links

- 📖 **[Full Documentation](docs/)** - Complete documentation suite
- 🌐 **[Deploy Guide](docs/DEPLOYMENT_INSTRUCTIONS.md)** - Publish your dashboard online
- 🔬 **[Methodology](docs/METHODOLOGY.md)** - Technical details
- 🌳 **[Implementation Guide](docs/NBS_GUIDELINES.md)** - G20 NbS framework

---

## Acknowledgments

- **UNEP** for the G20 NbS Working Paper framework
- **Microsoft AI for Earth** for building footprint data
- **OpenStreetMap contributors** for open geospatial data
- **Telangana Government** for open data initiatives

---
**Built for Hyderabad's sustainable urban future**
