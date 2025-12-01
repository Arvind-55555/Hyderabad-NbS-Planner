# Methodology Documentation

## Hyderabad Nature-based Solutions (NbS) Planner

### Technical Implementation Details

---

## 1. Overview

This document describes the technical methodology used in the Hyderabad NbS Planner, including data sources, algorithms, calculations, and decision logic.

---

## 2. Data Acquisition

### 2.1 OpenStreetMap (OSM) Data

**API**: osmnx library wrapping Overpass API

**Query Structure**:
```python
# Buildings
tags = {'building': True}
buildings = ox.features_from_point((lat, lon), tags=tags, dist=radius)

# Street Network
G = ox.graph_from_point((lat, lon), dist=radius, network_type='drive')

# Green/Blue Spaces
env_tags = {
    'leisure': ['park', 'garden', 'playground'],
    'landuse': ['grass', 'forest', 'meadow'],
    'natural': ['water', 'wetland', 'wood']
}
green_blue = ox.features_from_point((lat, lon), tags=env_tags, dist=radius)
```

**Caching**:
- OSM data is cached locally for 30 days
- Cache key: `osm_{lat}_{lon}_{radius}`
- Format: GeoJSON files in `data/cache/`

### 2.2 Climate Data (Open-Meteo)

**Endpoint**: `https://archive-api.open-meteo.com/v1/archive`

**Parameters**:
- Time Range: 2023-01-01 to 2023-12-31 (or current year)
- Variables: wind_direction_10m, wind_speed_10m, temperature_2m
- Temporal Resolution: Hourly

**Wind Direction Calculation**:
```python
# Filter significant winds (> 2 m/s)
significant_winds = df[df['speed'] > 2.0]

# Mode (most frequent direction)
dominant_dir = significant_winds['dir'].mode()[0]
```

### 2.3 Air Quality (WAQI)

**Endpoint**: `https://api.waqi.info/feed/geo:{lat};{lon}/`

Retrieved metrics:
- AQI (Air Quality Index)
- PM2.5 concentration
- PM10 concentration

---

## 3. Coordinate Systems

### 3.1 Input Coordinates
- **System**: WGS84 (EPSG:4326)
- **Format**: Decimal degrees
- **Range**: Latitude [-90, 90], Longitude [-180, 180]

### 3.2 Processing Coordinates
- **System**: UTM Zone 44N (EPSG:32644) for Hyderabad
- **Units**: Meters
- **Reason**: Accurate distance and area calculations

### 3.3 Output Coordinates
- **GeoJSON**: WGS84 (EPSG:4326) for compatibility
- **Internal Processing**: UTM for calculations

---

## 4. Urban Morphology Analysis

### 4.1 Grid Creation

**Method**: Regular rectangular grid overlay

**Parameters**:
- Default Cell Size: 150m × 150m (22,500 m²)
- Adjustable via `--grid-size` parameter

**Algorithm**:
```python
minx, miny, maxx, maxy = buildings.total_bounds
cols = np.arange(minx, maxx, grid_size)
rows = np.arange(miny, maxy, grid_size)

for x in cols:
    for y in rows:
        cell = box(x, y, x + grid_size, y + grid_size)
```

### 4.2 Plan Area Density (λp)

**Definition**: Fraction of ground area covered by buildings

**Formula**:
```
λp = A_buildings / A_cell
```

Where:
- A_buildings = Total building footprint area within cell
- A_cell = Grid cell area (150m × 150m = 22,500 m²)

**Method**:
1. Spatial join: Match buildings to grid cells
2. Overlay operation: Calculate intersection areas
3. Normalize: Divide by cell area

**Range**: [0, 1]
- 0 = No buildings (open space)
- 1 = Completely built (100% coverage)

**Classification**:
- Very High: λp ≥ 0.7
- High: 0.6 ≤ λp < 0.7
- Medium: 0.3 ≤ λp < 0.6
- Low: 0.15 ≤ λp < 0.3
- Very Low: λp < 0.15

### 4.3 Building Height Estimation

**Priority Order**:
1. OSM `height` tag (direct measurement in meters)
2. OSM `building:levels` tag × 3.0 meters per floor
3. Building type heuristics (e.g., apartments = 18m, houses = 6m)
4. Default: 6.0 meters (2 floors)

**Formula for Levels**:
```
height = building:levels × 3.0 meters/floor
```

### 4.4 Roughness Length (z₀)

**Definition**: Measure of surface roughness affecting wind flow

**Simplified Formula** (Macdonald et al., 1998):
```
z₀ ≈ 0.5 × mean_height × density
```

Where:
- mean_height = Average building height in the cell (meters)
- density = Plan area density (λp)

**Full Formula** (for reference):
```
z₀ = (1 - d/H) × exp(-[0.5 × β × C_d / κ² × (1 - d/H) × λ_f]^(-0.5))
```

Where:
- d = Zero-plane displacement height
- H = Mean building height
- β = Drag coefficient parameter
- C_d = Drag coefficient
- κ = von Kármán constant (0.4)
- λ_f = Frontal area index

**Classification**:
- Very High: z₀ ≥ 1.5m (Dense high-rise)
- High: 1.0m ≤ z₀ < 1.5m (Dense mid-rise)
- Medium: 0.5m ≤ z₀ < 1.0m (Suburban)
- Low: 0.1m ≤ z₀ < 0.5m (Open, scattered)
- Very Low: z₀ < 0.1m (Grassland, water)

### 4.5 Sky View Factor (SVF)

**Definition**: Fraction of sky hemisphere visible from ground level

**Simplified Formula**:
```
SVF ≈ 1 - (coverage × height_factor)
```

Where:
- coverage = Building coverage fraction
- height_factor = min(mean_height / 20.0, 1.0)

**Note**: Full SVF calculation requires ray-tracing or fisheye analysis. Our simplified version provides a first-order approximation.

**Range**: [0, 1]
- 1 = Completely open sky
- 0 = Completely obstructed

**Classification**:
- Open: SVF ≥ 0.8
- Moderate: 0.5 ≤ SVF < 0.8
- Enclosed: 0.3 ≤ SVF < 0.5
- Urban Canyon: SVF < 0.3

---

## 5. NbS Decision Logic

### 5.1 Decision Tree

The NbS assignment follows a hierarchical decision tree:

```
IF density ≥ 0.7:
    → Green Roof (limited ground space)

ELSE IF density ≥ 0.6 AND roughness ≥ 1.0:
    → Green Roof (dense + poor ventilation)

ELSE IF 0.3 < density < 0.6 AND roughness ≥ 0.5:
    → Ventilation Corridor (clear obstacles)

ELSE IF 0.3 < density < 0.6:
    → Urban Forest (street trees)

ELSE IF density ≤ 0.3 AND roughness < 0.5:
    → Permeable Pavement (likely paved)

ELSE IF density ≤ 0.3:
    → Rain Garden (some buildings present)

ELSE:
    → None (already green or unsuitable)
```

### 5.2 G20 NbS Principles

All recommendations align with the 8 G20 principles:

1. **Evidence-based and Transparent**: Uses real data and documented methods
2. **Inclusive and Participatory**: Designed for stakeholder engagement
3. **Achieves Net Gains to Biodiversity**: Prioritizes biodiversity benefits
4. **Economically Viable**: Includes cost estimates
5. **Supported by Adaptive Management**: Allows iterative refinement
6. **Sustainable and Resilient**: Long-term viability
7. **Context-Specific**: Tailored to Hyderabad's climate
8. **Integrates with Other Solutions**: Complements grey infrastructure

### 5.3 Multi-benefit Assessment

Each intervention is scored (0-5 scale) on:
- Climate Adaptation
- Biodiversity
- Air Quality
- Water Management
- Social Well-being
- Economic Value

**Overall Score**:
```
Overall = Mean(all_benefit_scores) × 20 (scaled to 100)
```

---

## 6. Benefit Quantification

### 6.1 Cooling Effect

**Green Roofs**: 3.5°C surface temperature reduction
**Urban Forests**: 2.0°C ambient temperature reduction (shaded areas)
**Permeable Pavement**: 1.5°C surface temperature reduction

*Source: Meta-analysis of NbS cooling studies*

### 6.2 Air Quality (PM2.5 Removal)

**Trees**: 15 g/year per mature tree
**Green Roofs**: 2.5 g/m²/year

**Formula**:
```
Total PM2.5 Removal = (Num_Trees × 15) + (Green_Roof_Area_m² × 2.5) grams/year
```

### 6.3 Carbon Sequestration

**Trees**: 22 kg CO₂/year per mature tree
**Green Roofs**: 1.5 kg CO₂/m²/year

**Formula**:
```
Total Carbon = (Num_Trees × 22) + (Green_Roof_Area_m² × 1.5) kg CO₂/year
```

### 6.4 Stormwater Management

**Runoff Reduction**:
- Green Roofs: 60% retention
- Permeable Pavement: 80% infiltration
- Rain Gardens: 90% retention
- Urban Forests: 30% canopy interception

**Formula**:
```
Runoff_Reduced = Area_m² × Annual_Rainfall_mm × Reduction_Factor
```

### 6.5 Tree Density

**Urban Forests**: 100 trees per hectare (standard density)
**Ventilation Corridors**: 50 trees per hectare (lower density for airflow)

**Calculation**:
```
Num_Trees = (Area_m² / 10,000) × Trees_per_Hectare
```

---

## 7. Cost Estimation

### 7.1 Unit Costs (INR)

| NbS Type | Unit | Cost | Notes |
|----------|------|------|-------|
| Green Roof | per m² | ₹150 | Extensive system, 10-15cm substrate |
| Urban Forest | per tree | ₹5,000 | Planting + 3 years maintenance |
| Ventilation Corridor | per m² | ₹100 | Clearing + landscaping |
| Permeable Pavement | per m² | ₹80 | Materials + installation |
| Rain Garden | per m² | ₹70 | Excavation + plants |
| Wetland Restoration | per m² | ₹60 | Site preparation + plants |

### 7.2 Total Cost Calculation

```
Total_Cost = Σ(Area_m² × Unit_Cost) for all NbS types
```

**Currency Conversions**:
- 1 Lakh = ₹100,000
- 1 Crore = ₹10,000,000 = 100 Lakhs

---

## 8. Prioritization Algorithm

### 8.1 Priority Scoring

```
Priority_Score = (10 - Base_Priority) + Benefit_Priority + Cost_Priority + Population_Priority
```

**Components**:
1. **Base Priority**: From NbS type (1-7, lower = more urgent)
2. **Benefit Priority**: Overall benefit score / 10 (0-10)
3. **Cost Priority**: (1 - Normalized_Cost) × 5 (0-5, cheaper = higher)
4. **Population Priority**: Normalized_Population × 5 (0-5, optional)

### 8.2 Budget Constraints

When budget is specified:
1. Sort interventions by Priority_Score (descending)
2. Calculate cumulative cost
3. Mark interventions within budget

---

## 9. Validation & Limitations

### 9.1 Data Quality

**OSM Completeness**:
- Hyderabad: ~70-80% building coverage
- Height data: Often missing or estimated
- Regular updates via community mapping

**Recommendations**:
- Field validation for critical areas
- Supplement with government datasets
- Use MS Building Footprints for better accuracy

### 9.2 Model Limitations

1. **Roughness Length**: Simplified formula (doesn't account for building arrangement)
2. **SVF**: Approximation (true SVF requires 3D ray-tracing)
3. **Benefits**: Based on literature estimates (vary by location and implementation)
4. **Costs**: Approximate (actual costs vary by contractor and materials)

### 9.3 Uncertainty Ranges

- Morphology metrics: ±10-15%
- Cost estimates: ±20-30%
- Benefit quantification: ±25-40%

---

## 10. References

### Academic Literature

1. **Macdonald, R. W., Griffiths, R. F., & Hall, D. J. (1998).** *An improved method for the estimation of surface roughness of obstacle arrays.* Atmospheric Environment, 32(11), 1857-1864.

2. **Grimmond, C. S. B., & Oke, T. R. (1999).** *Aerodynamic properties of urban areas derived from analysis of surface form.* Journal of Applied Meteorology, 38(9), 1262-1292.

3. **IUCN (2020).** *Global Standard for Nature-based Solutions: A user-friendly framework for the verification, design and scaling up of NbS.* First Edition. Gland, Switzerland: IUCN.

### Policy Documents

4. **UNEP (2021).** *Smart, Sustainable and Resilient Cities: The Power of Nature-based Solutions.* G20 Working Paper for the Italian Presidency.

5. **WHO (2021).** *WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide.* Geneva: World Health Organization.

### Data Sources

6. **OpenStreetMap Contributors.** *OpenStreetMap.* Retrieved from https://www.openstreetmap.org (ODbL License)

7. **Microsoft AI for Earth.** *Global ML Building Footprints.* Retrieved from https://github.com/microsoft/GlobalMLBuildingFootprints (ODbL License)

8. **Open-Meteo.** *Historical Weather API.* Retrieved from https://open-meteo.com (CC BY 4.0)

---

## 11. Code Repository

Full implementation available at:
[Project Repository URL]

**Key Modules**:
- `src/morphology.py`: Urban morphology calculations
- `src/nbs_logic.py`: Decision engine and benefit assessment
- `src/data_loader.py`: API integrations and caching

---

*Document Version: 1.0*  
*Last Updated: 2024-12-01*  
*Contact: [Project maintainer email]*

