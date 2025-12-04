import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(
    layout="wide", 
    page_title="Hyderabad NbS 4D Engine",
    page_icon="🌍",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    /* Slider container */
    .slider-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin: 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(46, 204, 113, 0.1);
        border-left: 4px solid #2ecc71;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    /* Styled metric labels */
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 0.5rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Import project config for consistency
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.config import CITY_LAT, CITY_LON
    DEFAULT_LAT, DEFAULT_LON = CITY_LAT, CITY_LON
except:
    DEFAULT_LAT, DEFAULT_LON = 17.3850, 78.4867

# Enhanced Map Styles
MAPBOX_STYLE = "mapbox://styles/mapbox/dark-v11"

# Camera presets
CAMERA_PRESETS = {
    "Default 3D": pdk.ViewState(
        latitude=DEFAULT_LAT, 
        longitude=DEFAULT_LON, 
        zoom=14, 
        pitch=60,
        bearing=30
    ),
    "Top Down": pdk.ViewState(
        latitude=DEFAULT_LAT,
        longitude=DEFAULT_LON,
        zoom=14,
        pitch=0,
        bearing=0
    ),
    "Oblique View": pdk.ViewState(
        latitude=DEFAULT_LAT,
        longitude=DEFAULT_LON,
        zoom=14,
        pitch=75,
        bearing=45
    ),
    "Street Level": pdk.ViewState(
        latitude=DEFAULT_LAT,
        longitude=DEFAULT_LON,
        zoom=16,
        pitch=80,
        bearing=0
    )
}

INITIAL_VIEW_STATE = CAMERA_PRESETS["Default 3D"]

# --- 2. LOAD REAL DATA (Google Buildings + NbS Interventions) ---
@st.cache_data
def load_buildings_data():
    """Load Google Open Buildings data"""
    try:
        df = pd.read_csv("data/hyderabad_clipped.csv")
        
        # Ensure columns exist
        if 'lon' not in df.columns and 'longitude' in df.columns:
            df['lon'] = df['longitude']
        if 'lat' not in df.columns and 'latitude' in df.columns:
            df['lat'] = df['latitude']
        
        st.sidebar.success(f"✓ Loaded {len(df):,} buildings from Google Open Buildings")
        return df
    except FileNotFoundError:
        st.error("⚠️ Building data not found at: data/hyderabad_clipped.csv")
        st.info("Run: `python tools/fetch_data.py` first")
        return pd.DataFrame()

@st.cache_data
def load_nbs_interventions():
    """Load NbS interventions from existing analysis"""
    import geopandas as gpd
    from pathlib import Path
    
    try:
        # Find latest NbS GeoJSON
        geojson_files = list(Path('outputs/reports').glob('nbs_interventions_*.geojson'))
        if not geojson_files:
            st.warning("⚠️ No NbS interventions found. Run: `python main.py` first")
            return None
        
        latest = sorted(geojson_files, key=lambda x: x.stat().st_mtime)[-1]
        gdf = gpd.read_file(latest)
        
        # Filter out 'None' interventions
        gdf = gdf[gdf['Proposed_NbS'] != 'None'].copy()
        
        st.sidebar.success(f"✓ Loaded {len(gdf):,} NbS intervention zones")
        return gdf
    except Exception as e:
        st.warning(f"Could not load NbS data: {e}")
        return None

df = load_buildings_data()
nbs_gdf = load_nbs_interventions()

# --- 3. UI DASHBOARD CONTROLS ---
st.sidebar.title("🏗️ NbS 4D Engine")
st.sidebar.markdown("**Hyderabad Spatial Planner**")
st.sidebar.markdown("*Real OSM Buildings + G20 NbS Framework*")

st.sidebar.markdown("---")

# Camera preset selector
st.sidebar.markdown("### 📷 View Presets")
camera_preset = st.sidebar.selectbox(
    "Camera Angle",
    options=list(CAMERA_PRESETS.keys()),
    index=0,
    help="Choose a preset camera angle for the 3D view"
)

current_view_state = CAMERA_PRESETS[camera_preset]

st.sidebar.markdown("---")

# The "4th Dimension" - Time/Intervention Slider
st.sidebar.markdown("### 🕒 Temporal Control")
scenario_stage = st.sidebar.slider(
    "Implementation Phase", 
    min_value=0, 
    max_value=100, 
    value=0,
    step=1,
    help="0% = BEFORE (Current State). 100% = AFTER (Full NbS Implementation)"
)

# Visual progress indicator
progress_color = "🟢" if scenario_stage == 100 else "🟡" if scenario_stage > 0 else "🔴"
st.sidebar.markdown(f"**Status:** {progress_color} {scenario_stage}% Complete")

st.sidebar.markdown("---")

# Statistics with enhanced metrics
st.sidebar.markdown("### 📊 Current Metrics")

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Phase", f"{scenario_stage}%", delta=None)
with col2:
    state_label = "BEFORE" if scenario_stage < 50 else "AFTER" if scenario_stage == 100 else "TRANSITION"
    st.metric("State", state_label)

if nbs_gdf is not None:
    st.sidebar.markdown("---")
    
    # Enhanced NbS metrics
    visible_interventions = int(len(nbs_gdf) * (scenario_stage / 100))
    temp_reduction = scenario_stage * 0.02
    co2_seq = scenario_stage * 1.2
    green_coverage = scenario_stage * 0.5
    
    st.sidebar.metric("NbS Zones", f"{len(nbs_gdf):,}", delta=f"{visible_interventions} active")
    st.sidebar.metric("Heat Reduction", f"-{temp_reduction:.2f}°C", delta=f"-{temp_reduction*50:.0f}%")
    st.sidebar.metric("CO₂ Sequestration", f"{co2_seq:.1f} t/yr", delta=f"+{scenario_stage*1.2:.0f}%")
    st.sidebar.metric("Green Coverage", f"{green_coverage:.1f}%", delta=f"+{scenario_stage*0.5:.1f}%")
    
    # NbS breakdown with visual indicators
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌳 NbS Breakdown")
    
    nbs_counts = nbs_gdf['Proposed_NbS'].value_counts()
    for nbs_type, count in nbs_counts.items():
        # Calculate active count based on stage
        active_count = int(count * (scenario_stage / 100))
        st.sidebar.markdown(f"**{nbs_type}**")
        st.sidebar.progress(active_count / count if count > 0 else 0)
        st.sidebar.caption(f"{active_count}/{count} active")

# --- 4. ENGINE LOGIC (ENHANCED COLOR SYSTEM) ---
# Color Format: [R, G, B, A]

def get_building_color(row, stage, height_col='height'):
    """
    Enhanced building colors based on height and stage
    Taller buildings are lighter, shorter are darker
    """
    height = row.get(height_col, 10.0)
    
    # Base concrete color varies by height
    # Taller buildings = lighter gray (more urban)
    # Shorter buildings = darker gray (residential)
    
    if height > 15:
        # Tall buildings (commercial/high-rise)
        base_r, base_g, base_b = 140, 140, 150
    elif height > 10:
        # Medium buildings
        base_r, base_g, base_b = 120, 120, 130
    else:
        # Short buildings (residential)
        base_r, base_g, base_b = 100, 100, 110
    
    # Slight green tint as NbS is implemented (subtle)
    if stage > 50:
        green_factor = (stage - 50) / 50.0 * 0.2  # Max 20% green tint
        base_g = int(base_g * (1 + green_factor))
    
    return [base_r, base_g, base_b, 220]

# Performance optimization: Sample if too many buildings
MAX_BUILDINGS_DISPLAY = 10000
if not df.empty and len(df) > MAX_BUILDINGS_DISPLAY:
    st.info(f"⚠️ Large dataset ({len(df):,} buildings). Displaying sample of {MAX_BUILDINGS_DISPLAY:,} for performance.")
    df = df.sample(n=MAX_BUILDINGS_DISPLAY, random_state=42)

# Apply enhanced colors
if not df.empty:
    df['color'] = df.apply(lambda row: get_building_color(row, scenario_stage), axis=1)
    
    # Add height category for tooltips
    df['height_category'] = pd.cut(
        df['height'],
        bins=[0, 6, 12, 20, 100],
        labels=['Low (1-2 floors)', 'Medium (3-4 floors)', 'High (5-7 floors)', 'Very High (8+ floors)']
    )

# --- 4B. NbS LAYER PREPARATION ---
def prepare_nbs_layer_data(nbs_gdf, stage):
    """
    Prepare NbS interventions data for visualization
    
    Args:
        nbs_gdf: GeoDataFrame with NbS interventions
        stage: Implementation stage (0-100)
    
    Returns:
        list: Data for PyDeck PolygonLayer
    """
    if nbs_gdf is None or stage == 0:
        return []
    
    # Enhanced color mapping for NbS types with gradients
    nbs_colors = {
        'Green Roof': [46, 204, 113, 180],       # Bright green with transparency
        'Urban Forest': [39, 174, 96, 200],      # Dark green
        'Ventilation Corridor': [52, 152, 219, 160],  # Blue
        'Permeable Pavement': [149, 165, 166, 150],   # Gray
        'Rain Garden': [22, 160, 133, 170],      # Teal
        'Wetland Restoration': [26, 188, 156, 180]    # Light teal
    }
    
    # Enhanced colors with glow effect for active interventions
    nbs_colors_glow = {
        'Green Roof': [76, 224, 133],       # Brighter for glow
        'Urban Forest': [59, 194, 116],
        'Ventilation Corridor': [72, 172, 239],
        'Permeable Pavement': [169, 185, 186],
        'Rain Garden': [42, 180, 153],
        'Wetland Restoration': [46, 208, 176]
    }
    
    nbs_data = []
    opacity = int(255 * (stage / 100.0))  # Fade in with slider
    
    for idx, row in nbs_gdf.iterrows():
        nbs_type = row['Proposed_NbS']
        base_color = list(nbs_colors.get(nbs_type, [100, 200, 100, 180]))
        
        # Get polygon coordinates
        coords = list(row.geometry.exterior.coords)
        polygon_coords = [[lon, lat] for lon, lat in coords]
        
        # Determine elevation based on NbS type (more realistic)
        if nbs_type == 'Green Roof':
            elevation = row.get('avg_height', 6.0) + 0.3  # On top of buildings
        elif nbs_type == 'Urban Forest':
            elevation = 8.0  # Tree height
        elif nbs_type == 'Rain Garden':
            elevation = 0.2  # Slightly elevated
        else:
            elevation = 0.1  # Ground level
        
        # Enhanced color with stage-based opacity
        final_opacity = int(base_color[3] * (opacity / 255.0))
        final_color = base_color[:3] + [final_opacity]
        
        # Calculate area for tooltip
        try:
            area = row.geometry.area * 111000 * 111000 * 0.952  # Rough m² conversion
        except:
            area = 0
        
        nbs_data.append({
            'polygon': polygon_coords,
            'color': final_color,
            'elevation': elevation,
            'nbs_type': nbs_type,
            'priority': row.get('priority', 999),
            'area_m2': area,
            'zone_id': idx
        })
    
    return nbs_data

nbs_layer_data = prepare_nbs_layer_data(nbs_gdf, scenario_stage)

# --- 5. LAYERS CONFIGURATION ---

layers = []

# A. Heat Map Layer (Visualizing Impact - BEFORE state)
# This layer fades OUT as NbS Implementation increases (Simulating heat reduction)
heat_opacity = max(0, 1.0 - (scenario_stage / 120.0))

if not df.empty:
    heat_layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=["lon", "lat"],
        get_weight="height",
        opacity=heat_opacity,
        threshold=0.3,
        radius_pixels=40,
    )
    layers.append(heat_layer)

# B. 3D Buildings Layer (Enhanced with better styling)
if not df.empty:
    building_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="height",
        elevation_scale=1.0,
        radius=12,  # Slightly smaller for better detail
        get_fill_color="color",
        get_line_color=[80, 80, 80, 100],  # Subtle outline
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
        highlight_color=[255, 255, 255, 100],  # White highlight on hover
        material={
            "ambient": 0.4,
            "diffuse": 0.6,
            "shininess": 32,
            "specularColor": [60, 60, 60]
        },
        extruded=True,
        coverage=1.0,
        wireframe=False,
    )
    layers.append(building_layer)

# C. NbS Interventions Layer (Enhanced with glow effect)
if nbs_layer_data:
    # Main NbS layer
    nbs_layer = pdk.Layer(
        "PolygonLayer",
        data=nbs_layer_data,
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 150],  # Brighter outline
        line_width_min_pixels=2,  # Thicker outline for visibility
        get_elevation="elevation",
        elevation_scale=1.0,
        pickable=True,
        auto_highlight=True,
        highlight_color=[255, 255, 255, 200],  # Bright highlight
        extruded=True,
        wireframe=False,
        material={
            "ambient": 0.5,
            "diffuse": 0.7,
            "shininess": 64,
            "specularColor": [100, 100, 100]
        },
        opacity=0.85,
    )
    layers.append(nbs_layer)
    
    # Optional: Add a subtle glow layer for active interventions
    if scenario_stage > 50:
        glow_data = []
        for item in nbs_layer_data:
            if item.get('priority', 999) <= 3:  # High priority only
                glow_item = item.copy()
                glow_color = list(glow_item['color'])
                glow_color[3] = min(100, glow_color[3] // 3)  # Very transparent
                glow_item['color'] = glow_color
                glow_item['elevation'] = glow_item.get('elevation', 0) + 0.1
                glow_data.append(glow_item)
        
        if glow_data:
            glow_layer = pdk.Layer(
                "PolygonLayer",
                data=glow_data,
                get_polygon="polygon",
                get_fill_color="color",
                get_elevation="elevation",
                elevation_scale=1.0,
                extruded=True,
                wireframe=False,
                opacity=0.3,
            )
            layers.append(glow_layer)

# --- 6. RENDER THE ENGINE ---
# Enhanced header with gradient
st.markdown("""
<div class="main-header">
    🌍 Hyderabad NbS 4D Visualization Engine
</div>
""", unsafe_allow_html=True)

# Status banner based on current state
if scenario_stage == 0:
    st.info("🏙️ **BEFORE State**: Current urban heat island. Buildings in gray, heat map visible (red glow).")
elif scenario_stage == 100:
    st.success("🌳 **AFTER State**: Full NbS implementation complete! Green roofs, rain gardens, and urban forests active. Heat island eliminated.")
else:
    st.warning(f"🔄 **TRANSITION State**: {scenario_stage}% implementation in progress. NbS interventions appearing, heat dissipating.")

# Quick stats row
if not df.empty and nbs_gdf is not None:
    quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
    with quick_col1:
        st.metric("Buildings", f"{len(df):,}")
    with quick_col2:
        st.metric("NbS Zones", f"{len(nbs_gdf):,}")
    with quick_col3:
        st.metric("Active", f"{int(len(nbs_gdf) * (scenario_stage / 100)):,}")
    with quick_col4:
        st.metric("Temp ↓", f"-{scenario_stage * 0.02:.2f}°C")

st.markdown("---")

# Enhanced tooltips with better formatting
def create_tooltip_html():
    """Create tooltip HTML based on available data"""
    if nbs_layer_data:
        return {
            "html": """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 12px; border-radius: 8px; font-family: Arial;">
                <b style="font-size: 14px;">🏢 Building Info</b><br/>
                <hr style="margin: 5px 0; border-color: rgba(255,255,255,0.3);"/>
                <b>Height:</b> {height}m<br/>
                <b>Area:</b> {area_in_meters:.0f}m²<br/>
                <b>Type:</b> {building_type}<br/>
            </div>
            """,
            "style": {
                "backgroundColor": "transparent",
                "border": "none"
            }
        }
    else:
        return {
            "html": """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 12px; border-radius: 8px; font-family: Arial;">
                <b style="font-size: 14px;">🏢 Building Details</b><br/>
                <hr style="margin: 5px 0; border-color: rgba(255,255,255,0.3);"/>
                <b>Height:</b> {height}m<br/>
                <b>Area:</b> {area_in_meters:.0f}m²<br/>
                <b>Type:</b> {building_type}<br/>
                <b>Source:</b> {source}
            </div>
            """,
            "style": {
                "backgroundColor": "transparent",
                "border": "none"
            }
        }

tooltip = create_tooltip_html()

deck = pdk.Deck(
    map_style=MAPBOX_STYLE,
    initial_view_state=current_view_state,
    layers=layers,
    tooltip=tooltip,
    # Enhanced lighting for better 3D effect
    parameters={
        "depthTest": True,
        "blend": True,
        "lightSettings": {
            "lightsPosition": [-122.4, 37.8, 8000, -122.4, 37.8, 8000],
            "ambientRatio": 0.4,
            "diffuseRatio": 0.6,
            "specularRatio": 0.2,
        }
    }
)

# Render with enhanced container
st.pydeck_chart(deck, use_container_width=True, height=750)

# --- 7. ENHANCED STATISTICS & CHARTS ---
st.markdown("---")

# Main statistics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 📊 Urban Morphology")
    if not df.empty:
        st.metric("Buildings", f"{len(df):,}", help="Total buildings in view")
        st.metric("Avg Height", f"{df['height'].mean():.1f}m", 
                 delta=f"{df['height'].max():.1f}m max")
        st.metric("Total Area", f"{df['area_in_meters'].sum()/10000:.1f} ha")

with col2:
    st.markdown("### 🌳 NbS Implementation")
    if nbs_gdf is not None:
        visible_interventions = int(len(nbs_gdf) * (scenario_stage / 100))
        st.metric("Zones Total", f"{len(nbs_gdf):,}")
        st.metric("Active Now", f"{visible_interventions:,}", 
                 delta=f"+{visible_interventions}" if scenario_stage > 0 else None)
        st.metric("Coverage", f"{scenario_stage * 0.5:.1f}%",
                 delta=f"+{scenario_stage * 0.5:.1f}%" if scenario_stage > 0 else None)
    else:
        st.info("No NbS data")

with col3:
    st.markdown("### 🌡️ Climate Impact")
    if scenario_stage > 0:
        temp_reduction = scenario_stage * 0.02
        co2_seq = scenario_stage * 1.2
        air_quality = 100 - (scenario_stage * 0.3)  # AQI improvement
        
        st.metric("Temp Reduction", f"-{temp_reduction:.2f}°C",
                 delta=f"-{temp_reduction*50:.0f}% heat")
        st.metric("CO₂ Sequestration", f"{co2_seq:.1f} t/yr",
                 delta=f"+{co2_seq:.1f}t")
        st.metric("Air Quality", f"{air_quality:.0f} AQI",
                 delta=f"+{scenario_stage*0.3:.0f}%")
    else:
        st.info("Baseline metrics")

with col4:
    st.markdown("### 💧 Ecosystem Services")
    if scenario_stage > 0:
        water_retention = scenario_stage * 0.8  # mm/year
        biodiversity = scenario_stage * 0.15  # index
        recreation = scenario_stage * 0.6  # score
        
        st.metric("Water Retention", f"{water_retention:.1f} mm/yr")
        st.metric("Biodiversity", f"{biodiversity:.2f} index",
                 delta=f"+{biodiversity*100:.0f}%")
        st.metric("Recreation Value", f"{recreation:.1f}/10")

st.markdown("---")

# Enhanced charts section
if scenario_stage > 0 and nbs_gdf is not None:
    st.markdown("### 📈 Impact Trends")
    
    # Create trend data
    stages = list(range(0, 101, 10))
    temp_data = [s * 0.02 for s in stages]
    co2_data = [s * 1.2 for s in stages]
    coverage_data = [s * 0.5 for s in stages]
    
    # Temperature reduction chart
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=stages,
        y=temp_data,
        mode='lines+markers',
        name='Temperature Reduction',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8)
    ))
    fig_temp.add_vline(x=scenario_stage, line_dash="dash", 
                      line_color="white", annotation_text="Current")
    fig_temp.update_layout(
        title="Temperature Reduction Over Time",
        xaxis_title="Implementation Phase (%)",
        yaxis_title="Temperature Reduction (°C)",
        template="plotly_dark",
        height=250
    )
    
    # CO2 sequestration chart
    fig_co2 = go.Figure()
    fig_co2.add_trace(go.Scatter(
        x=stages,
        y=co2_data,
        mode='lines+markers',
        name='CO₂ Sequestration',
        line=dict(color='#2ecc71', width=3),
        marker=dict(size=8),
        fill='tozeroy'
    ))
    fig_co2.add_vline(x=scenario_stage, line_dash="dash",
                     line_color="white", annotation_text="Current")
    fig_co2.update_layout(
        title="CO₂ Sequestration Over Time",
        xaxis_title="Implementation Phase (%)",
        yaxis_title="CO₂ Sequestration (t/yr)",
        template="plotly_dark",
        height=250
    )
    
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(fig_temp, use_container_width=True)
    with chart_col2:
        st.plotly_chart(fig_co2, use_container_width=True)
    
    st.markdown("---")

st.markdown("---")

# Explanation
st.markdown("""
### 🎬 4D Visualization Logic

**Temporal Dimension (4D):**
- **0% (BEFORE)**: Current state - Buildings in gray, heat map shows urban heat island effect
- **1-99% (TRANSITION)**: Progressive NbS implementation - Interventions fade in gradually
- **100% (AFTER)**: Full implementation - All NbS visible, heat dissipates

**Data Sources:**
- **Buildings**: Google Open Buildings (real footprints with estimated heights)
- **NbS Interventions**: Automated planning based on G20 framework
- **Analysis**: Urban morphology + climate data

**Interactive Controls:**
- 🖱️ **Left-click + drag**: Rotate view
- 🖱️ **Right-click + drag**: Pan
- 🎡 **Scroll**: Zoom in/out
- 🎚️ **Slider**: Change temporal state (BEFORE → AFTER)
""")

# Legend
with st.expander("🎨 NbS Color Legend"):
    st.markdown("""
    - 🟢 **Green**: Green Roofs, Urban Forests
    - 🔵 **Blue**: Ventilation Corridors
    - ⚫ **Gray**: Permeable Pavement
    - 🔷 **Teal**: Rain Gardens, Wetlands
    - 🔴 **Red Glow**: Urban heat island effect (fades out with NbS)
    """)

# Data sources
with st.expander("📚 Data Sources & Methodology"):
    st.markdown("""
    **Google Open Buildings V3**
    - Source: https://sites.research.google/open-buildings/
    - Coverage: Global building footprints with confidence scores
    - Processing: Clipped to Hyderabad region, heights estimated from area
    
    **NbS Planning Framework**
    - Based on: G20 Smart Cities Working Paper on Nature-based Solutions
    - Methodology: Urban morphology analysis (density, roughness, SVF)
    - Decision Logic: Multi-criteria NbS selection
    - Analysis: See `python main.py` output
    
    **Visualization Technology**
    - Engine: PyDeck (Deck.gl) - WebGL 3D rendering
    - Theme: SpatialBound aesthetic (dark theme, glossy materials)
    - Temporal: Smooth transitions with slider control
    """)
