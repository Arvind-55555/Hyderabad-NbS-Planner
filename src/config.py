"""
Configuration file for Hyderabad NbS Planner
Contains all constants, thresholds, and API configurations
"""

import os

# ============================================================================
# LOCATION SETTINGS
# ============================================================================

# Default Analysis Location - Charminar, Old City
CITY_LAT = 17.3616
CITY_LON = 78.4747
CITY_NAME = "Hyderabad"

# Alternative Locations (Uncomment to use)
# Hitech City: 17.4435, 78.3772
# Gachibowli: 17.4399, 78.3489
# Secunderabad: 17.4399, 78.4983

# Analysis Parameters
ANALYSIS_RADIUS_METERS = 1500  # 1.5km radius for analysis
GRID_SIZE_METERS = 150  # Grid cell size for morphology analysis

# Coordinate Reference System
CRS_WGS84 = "EPSG:4326"  # WGS84 for lat/lon
CRS_UTM = "EPSG:32644"  # UTM Zone 44N for Hyderabad (meters)

# ============================================================================
# API ENDPOINTS
# ============================================================================

# Open-Meteo Historical Weather API
OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_PARAMS = {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "hourly": "wind_direction_10m,wind_speed_10m,temperature_2m,relative_humidity_2m"
}

# World Air Quality Index API
WAQI_URL = "https://api.waqi.info/feed/geo:{};{}/"
WAQI_TOKEN = ""  # Add your token if available (optional for basic use)

# OpenStreetMap via osmnx
OSM_TIMEOUT = 180  # Timeout in seconds for OSM queries

# ============================================================================
# URBAN MORPHOLOGY THRESHOLDS
# ============================================================================

# Density Thresholds (Plan Area Fraction - λp)
DENSITY_VERY_HIGH = 0.7  # Very dense urban core (>70% built)
DENSITY_HIGH = 0.6  # Dense residential/commercial
DENSITY_MEDIUM = 0.3  # Suburban density
DENSITY_LOW = 0.15  # Low-density residential
# Below DENSITY_LOW = Open/undeveloped

# Roughness Length (z0) Thresholds in meters
# Based on Macdonald et al. (1998) and Grimmond & Oke (1999)
ROUGHNESS_VERY_HIGH = 1.5  # Dense high-rise urban core
ROUGHNESS_HIGH = 1.0  # Dense mid-rise buildings
ROUGHNESS_MEDIUM = 0.5  # Suburban, scattered buildings
ROUGHNESS_LOW = 0.1  # Open fields, grassland
# Below 0.1 = Water bodies, bare soil

# Building Height Defaults (when OSM data unavailable)
DEFAULT_BUILDING_HEIGHT = 6.0  # meters (approx 2 floors)
FLOOR_HEIGHT = 3.0  # meters per floor

# Sky View Factor (SVF) Thresholds
SVF_OPEN = 0.8  # Open sky, minimal obstruction
SVF_MODERATE = 0.5  # Moderate tree/building cover
SVF_ENCLOSED = 0.3  # Urban canyon effect
# Below 0.3 = Highly enclosed streets

# ============================================================================
# NATURE-BASED SOLUTIONS (NbS) PARAMETERS
# ============================================================================

# NbS Categories and Priorities
NBS_TYPES = {
    'Green Roof': {
        'priority': 1,
        'description': 'Vegetated rooftop systems',
        'applicable': 'Dense urban cores with limited ground space',
        'cost_per_sqm': 150,  # INR
    },
    'Urban Forest': {
        'priority': 2,
        'description': 'Street trees and park plantations',
        'applicable': 'Streets, parks, open spaces',
        'cost_per_tree': 5000,  # INR (planting + 3 years maintenance)
    },
    'Ventilation Corridor': {
        'priority': 3,
        'description': 'Wind-aligned green corridors',
        'applicable': 'Medium-density areas with poor airflow',
        'cost_per_sqm': 100,  # INR
    },
    'Permeable Pavement': {
        'priority': 4,
        'description': 'Porous surfaces for water infiltration',
        'applicable': 'Parking lots, sidewalks, low-traffic roads',
        'cost_per_sqm': 80,  # INR
    },
    'Wetland Restoration': {
        'priority': 5,
        'description': 'Natural water treatment systems',
        'applicable': 'Near water bodies, flood-prone areas',
        'cost_per_sqm': 60,  # INR
    },
    'Rain Garden': {
        'priority': 6,
        'description': 'Bioretention systems',
        'applicable': 'Low-lying areas, roadside drainage',
        'cost_per_sqm': 70,  # INR
    },
    'Sponge City Element': {
        'priority': 7,
        'description': 'Integrated water management',
        'applicable': 'Drainage systems, retention basins',
        'cost_per_sqm': 120,  # INR
    },
    'None': {
        'priority': 999,
        'description': 'No intervention needed',
        'applicable': 'Already green or unsuitable',
        'cost_per_sqm': 0,
    }
}

# Wind Parameters
WIND_SPEED_THRESHOLD = 2.0  # m/s - Minimum for significant ventilation
WIND_ALIGNMENT_TOLERANCE = 30  # degrees - Tolerance for corridor alignment

# Green Roof Parameters
GREEN_ROOF_MIN_BUILDING_HEIGHT = 2  # floors
GREEN_ROOF_SUBSTRATE_DEPTH = 0.15  # meters (extensive green roof)

# Tree Parameters for Urban Forests
TREE_CANOPY_DIAMETER = 8.0  # meters (mature tree)
TREE_SPACING = 10.0  # meters between trees
TREES_PER_HECTARE = 100  # Standard density for urban forestry

# ============================================================================
# BENEFITS ESTIMATION PARAMETERS (Based on research)
# ============================================================================

# Cooling Benefits
COOLING_GREEN_ROOF = 3.5  # °C temperature reduction
COOLING_URBAN_FOREST = 2.0  # °C in shaded areas
COOLING_PAVEMENT = 1.5  # °C surface temperature reduction

# Air Quality (PM2.5 removal)
PM25_REMOVAL_TREE = 15.0  # grams per year per tree
PM25_REMOVAL_GREEN_ROOF = 2.5  # grams per sqm per year

# Carbon Sequestration
CARBON_SEQUESTRATION_TREE = 22.0  # kg CO2 per year per tree
CARBON_SEQUESTRATION_GREEN_ROOF = 1.5  # kg CO2 per sqm per year

# Stormwater Management
RUNOFF_REDUCTION_GREEN_ROOF = 0.60  # 60% retention
RUNOFF_REDUCTION_PERMEABLE = 0.80  # 80% infiltration
RUNOFF_REDUCTION_RAIN_GARDEN = 0.90  # 90% retention

# Biodiversity
BIRD_SPECIES_URBAN_FOREST = 15  # Additional species attracted
POLLINATOR_SUPPORT_GREEN_ROOF = True

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

# Color Palette for NbS Types
NBS_COLORS = {
    'Green Roof': '#2ecc71',  # Green
    'Urban Forest': '#27ae60',  # Dark green
    'Ventilation Corridor': '#3498db',  # Blue
    'Permeable Pavement': '#95a5a6',  # Grey
    'Wetland Restoration': '#1abc9c',  # Turquoise
    'Rain Garden': '#16a085',  # Dark turquoise
    'Sponge City Element': '#2980b9',  # Dark blue
    'None': '#ecf0f1'  # Light grey
}

# Morphology Color Scales
DENSITY_CMAP = 'YlOrRd'  # Yellow-Orange-Red for density
ROUGHNESS_CMAP = 'viridis'  # Viridis for roughness
SVF_CMAP = 'plasma'  # Plasma for sky view factor

# Map Settings
MAP_DPI = 300  # High resolution for publication
MAP_FIGSIZE = (14, 12)  # inches
MAP_STYLE = 'seaborn-v0_8-darkgrid'

# ============================================================================
# DATA CACHING SETTINGS
# ============================================================================

# Project Root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cache Settings
CACHE_ENABLED = True
CACHE_DIR = os.path.join(PROJECT_ROOT, 'data', 'cache')
CACHE_EXPIRY_DAYS = 30  # Re-fetch data after 30 days

# Output Directories
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'outputs')
MAPS_DIR = os.path.join(OUTPUT_DIR, 'maps')
REPORTS_DIR = os.path.join(OUTPUT_DIR, 'reports')
EXPORTS_DIR = os.path.join(OUTPUT_DIR, 'exports')

# Reference Data
REFERENCE_DIR = os.path.join(PROJECT_ROOT, 'data', 'references')

# ============================================================================
# LOGGING SETTINGS
# ============================================================================

LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(PROJECT_ROOT, 'nbs_planner.log')

# ============================================================================
# G20 NBS PRINCIPLES (FROM WORKING PAPER)
# ============================================================================

G20_NBS_PRINCIPLES = {
    1: "Evidence-based and Transparent",
    2: "Inclusive and Participatory",
    3: "Achieves Net Gains to Biodiversity",
    4: "Economically Viable",
    5: "Supported by Adaptive Management",
    6: "Sustainable and Resilient",
    7: "Context-Specific",
    8: "Integrates with Other Solutions"
}

# Multi-benefit Assessment Categories
MULTI_BENEFIT_CATEGORIES = [
    'Climate Adaptation',
    'Biodiversity',
    'Air Quality',
    'Water Management',
    'Social Well-being',
    'Economic Value',
    'Health Benefits',
    'Carbon Sequestration'
]

# ============================================================================
# HYDERABAD-SPECIFIC PARAMETERS
# ============================================================================

# Climate Context
HYDERABAD_MONSOON_MONTHS = [6, 7, 8, 9]  # June to September
HYDERABAD_SUMMER_MONTHS = [3, 4, 5]  # March to May
HYDERABAD_ANNUAL_RAINFALL = 812  # mm average

# Native Species (Trees suitable for Hyderabad)
NATIVE_TREE_SPECIES = [
    'Neem (Azadirachta indica)',
    'Peepal (Ficus religiosa)',
    'Banyan (Ficus benghalensis)',
    'Jamun (Syzygium cumini)',
    'Tamarind (Tamarindus indica)',
    'Gulmohar (Delonix regia)',
    'Mango (Mangifera indica)',
    'Amla (Phyllanthus emblica)'
]

# Urban Heat Island Context
UHI_INTENSITY_HYDERABAD = 4.5  # °C difference between urban core and rural areas

# ============================================================================
# MICROSOFT BUILDING FOOTPRINTS INTEGRATION
# ============================================================================

MS_BUILDINGS_PATH = os.path.join(REFERENCE_DIR, 'hyderabad_buildings_ms.geojson')
USE_MS_BUILDINGS = False  # Set to True if MS Buildings data is available

# ============================================================================
# REPORT TEMPLATES
# ============================================================================

REPORT_TITLE_TEMPLATE = "Nature-based Solutions Analysis Report: {city} ({date})"
REPORT_SUBTITLE = "Urban Climate Resilience Planning"

