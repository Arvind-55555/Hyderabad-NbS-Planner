#!/usr/bin/env python3
"""
Hyderabad NbS Web Dashboard
Interactive web interface for exploring Nature-based Solutions analysis results
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import folium
from streamlit_folium import st_folium
import base64
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Hyderabad NbS Dashboard",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2ecc71;
        padding: 1rem;
        background: linear-gradient(90deg, #e8f5e9 0%, #c8e6c9 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2ecc71;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(output_dir='outputs'):
    """Load all analysis data"""
    output_path = Path(output_dir)
    reports_path = output_path / 'reports'
    
    data = {}
    
    try:
        # Load CSV files
        csv_path = reports_path / 'csv'
        data['summary'] = pd.read_csv(csv_path / 'nbs_summary.csv')
        data['grid'] = pd.read_csv(csv_path / 'nbs_grid_data.csv')
        
        # Load GeoJSON
        geojson_files = list(reports_path.glob('nbs_interventions_*.geojson'))
        if geojson_files:
            latest_geojson = sorted(geojson_files, key=lambda x: x.stat().st_mtime)[-1]
            data['spatial'] = gpd.read_file(latest_geojson)
        
        # Load JSON stats
        json_files = list(reports_path.glob('nbs_statistics_*.json'))
        if json_files:
            latest_json = sorted(json_files, key=lambda x: x.stat().st_mtime)[-1]
            with open(latest_json, 'r') as f:
                data['stats'] = json.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


def get_image_base64(image_path):
    """Convert image to base64 for display"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


def create_summary_metrics(stats):
    """Create summary metric cards"""
    if not stats:
        return
    
    meta = stats.get('analysis_metadata', {})
    area_stats = stats.get('area_statistics', {})
    financial = stats.get('financial', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Grid Cells",
            value=f"{meta.get('total_grid_cells', 0):,}",
            delta=f"{meta.get('intervention_coverage_pct', 0):.1f}% coverage"
        )
    
    with col2:
        st.metric(
            label="🏞️ Study Area",
            value=f"{area_stats.get('total_study_area_hectares', 0):.0f} ha",
            delta=f"{area_stats.get('total_intervention_area_hectares', 0):.0f} ha interventions"
        )
    
    with col3:
        st.metric(
            label="💰 Total Cost",
            value=f"₹{financial.get('total_cost_crores', 0):.2f} Cr",
            delta=f"₹{financial.get('average_cost_per_hectare', 0)/100000:.2f} L/ha"
        )
    
    with col4:
        env_benefits = stats.get('environmental_benefits', {})
        co2 = env_benefits.get('carbon_sequestration_kg_yr', 0) / 1000
        st.metric(
            label="🌱 CO₂ Sequestration",
            value=f"{co2:.1f} t/yr",
            delta="Environmental benefit"
        )


def create_intervention_charts(summary_df):
    """Create interactive intervention charts"""
    
    # Area and Cost comparison
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Area by NbS Type', 'Cost by NbS Type', 
                       'Area Distribution', 'Cost Distribution'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "pie"}]]
    )
    
    # Bar charts
    fig.add_trace(
        go.Bar(x=summary_df['NbS_Type'], y=summary_df['Total_Area_hectares'],
               marker_color='#2ecc71', name='Area',
               text=summary_df['Total_Area_hectares'].round(1),
               textposition='outside'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=summary_df['NbS_Type'], y=summary_df['Total_Cost_Crores'],
               marker_color='#e74c3c', name='Cost',
               text=summary_df['Total_Cost_Crores'].round(2),
               textposition='outside'),
        row=1, col=2
    )
    
    # Pie charts
    fig.add_trace(
        go.Pie(labels=summary_df['NbS_Type'], values=summary_df['Total_Area_hectares'],
               marker_colors=['#2ecc71', '#3498db', '#95a5a6', '#16a085'],
               textinfo='label+percent', name='Area'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Pie(labels=summary_df['NbS_Type'], values=summary_df['Total_Cost_Crores'],
               marker_colors=['#2ecc71', '#3498db', '#95a5a6', '#16a085'],
               textinfo='label+percent', name='Cost'),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="NbS Type", row=1, col=1)
    fig.update_yaxes(title_text="Hectares", row=1, col=1)
    fig.update_xaxes(title_text="NbS Type", row=1, col=2)
    fig.update_yaxes(title_text="Crores INR", row=1, col=2)
    
    fig.update_layout(height=700, showlegend=False, title_text="Intervention Analysis")
    
    return fig


def create_benefits_radar(summary_df):
    """Create interactive radar chart for benefits"""
    benefit_cols = ['climate_adaptation', 'biodiversity', 'air_quality', 
                   'water_management', 'social_wellbeing', 'economic_value']
    
    # Filter available columns
    available = [col for col in benefit_cols if col in summary_df.columns]
    
    if len(available) < 3:
        return None
    
    fig = go.Figure()
    
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
    
    for idx, (_, row) in enumerate(summary_df.head(4).iterrows()):
        fig.add_trace(go.Scatterpolar(
            r=[row[col] for col in available],
            theta=[col.replace('_', ' ').title() for col in available],
            fill='toself',
            name=row['NbS_Type'],
            marker_color=colors[idx]
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        title="Multi-benefit Assessment Radar"
    )
    
    return fig


def create_environmental_benefits(summary_df):
    """Create environmental benefits visualization"""
    env_metrics = {
        'carbon_sequestration_kg_yr': ('CO₂ Sequestration (tonnes/yr)', 1000),
        'pm25_removal_kg_yr': ('PM2.5 Removal (kg/yr)', 1),
        'cooling_effect_celsius': ('Temperature Reduction (°C)', 1),
        'estimated_trees': ('Trees to Plant', 1)
    }
    
    # Filter available metrics
    available = {k: v for k, v in env_metrics.items() if k in summary_df.columns}
    
    if not available:
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[v[0] for v in available.values()][:4]
    )
    
    positions = [(1,1), (1,2), (2,1), (2,2)]
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
    
    for idx, (col, (title, divisor)) in enumerate(list(available.items())[:4]):
        row, col_pos = positions[idx]
        values = summary_df[col] / divisor
        
        fig.add_trace(
            go.Bar(x=summary_df['NbS_Type'], y=values,
                   marker_color=colors[idx],
                   text=values.round(1), textposition='outside',
                   showlegend=False),
            row=row, col=col_pos
        )
    
    fig.update_layout(height=600, title_text="Environmental Benefits Quantification")
    
    return fig


def create_interactive_map(spatial_gdf):
    """Create interactive folium map"""
    if spatial_gdf is None or spatial_gdf.empty:
        return None
    
    # Convert to WGS84 if needed
    if spatial_gdf.crs != 'EPSG:4326':
        spatial_gdf = spatial_gdf.to_crs('EPSG:4326')
    
    # Calculate center
    center_lat = spatial_gdf.geometry.centroid.y.mean()
    center_lon = spatial_gdf.geometry.centroid.x.mean()
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Color mapping
    color_map = {
        'Green Roof': '#2ecc71',
        'Urban Forest': '#27ae60',
        'Ventilation Corridor': '#3498db',
        'Permeable Pavement': '#95a5a6',
        'Rain Garden': '#16a085',
        'Wetland Restoration': '#1abc9c',
        'None': '#ecf0f1'
    }
    
    # Add polygons
    for _, row in spatial_gdf.iterrows():
        nbs_type = row.get('Proposed_NbS', 'None')
        color = color_map.get(nbs_type, '#95a5a6')
        
        # Create popup content
        popup_html = f"""
        <div style='width: 200px'>
            <h4>{nbs_type}</h4>
            <b>Density:</b> {row.get('density', 0):.3f}<br>
            <b>Roughness:</b> {row.get('roughness', 0):.3f}m<br>
            <b>Height:</b> {row.get('avg_height', 0):.1f}m<br>
            <b>SVF:</b> {row.get('svf', 0):.3f}
        </div>
        """
        
        folium.GeoJson(
            row.geometry,
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': 'white',
                'weight': 1,
                'fillOpacity': 0.6
            },
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000;
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 5px; font-size: 14px;">
        <p style="margin: 0; font-weight: bold;">NbS Types</p>
    '''
    for nbs_type, color in color_map.items():
        if nbs_type != 'None':
            legend_html += f'<p style="margin: 5px 0;"><span style="background-color: {color}; width: 20px; height: 10px; display: inline-block;"></span> {nbs_type}</p>'
    legend_html += '</div>'
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m


def create_morphology_distributions(grid_df):
    """Create morphology distribution charts"""
    morph_cols = ['density', 'roughness', 'avg_height', 'svf']
    available = [col for col in morph_cols if col in grid_df.columns]
    
    if not available:
        return None
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[col.replace('_', ' ').title() for col in available[:4]]
    )
    
    positions = [(1,1), (1,2), (2,1), (2,2)]
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    
    for idx, col in enumerate(available[:4]):
        row, col_pos = positions[idx]
        data = grid_df[col].dropna()
        
        fig.add_trace(
            go.Histogram(x=data, marker_color=colors[idx],
                        nbinsx=30, showlegend=False, name=col),
            row=row, col=col_pos
        )
        
        # Add mean line
        mean_val = data.mean()
        fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                     annotation_text=f"Mean: {mean_val:.3f}",
                     row=row, col=col_pos)
    
    fig.update_layout(height=600, title_text="Urban Morphology Distributions")
    
    return fig


def main():
    """Main app function"""
    
    # Header
    st.markdown('<div class="main-header">🌳 Hyderabad Nature-based Solutions Dashboard 🌍</div>', 
                unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading analysis data...'):
        data = load_data()
    
    if data is None:
        st.error("⚠️ No data found. Please run the analysis first using `python main.py`")
        st.stop()
    
    summary_df = data['summary']
    grid_df = data['grid']
    spatial_gdf = data.get('spatial')
    stats = data.get('stats', {})
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/300x100/2ecc71/ffffff?text=NbS+Planner", 
                     use_container_width=True)
    st.sidebar.markdown("## 📊 Analysis Info")
    
    if stats:
        meta = stats.get('analysis_metadata', {})
        st.sidebar.info(f"""
        **City:** {meta.get('city', 'Hyderabad')}  
        **Date:** {meta.get('analysis_date', 'N/A')}  
        **Grid Cells:** {meta.get('total_grid_cells', 0)}  
        **Coverage:** {meta.get('intervention_coverage_pct', 0):.1f}%
        """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📥 Downloads")
    
    # Download buttons
    if st.sidebar.button("📄 Download Report (MD)"):
        report_files = list(Path('outputs/reports').glob('nbs_report_*.md'))
        if report_files:
            latest = sorted(report_files, key=lambda x: x.stat().st_mtime)[-1]
            with open(latest, 'r') as f:
                st.sidebar.download_button(
                    label="💾 Save Report",
                    data=f.read(),
                    file_name=latest.name,
                    mime='text/markdown'
                )
    
    if st.sidebar.button("📊 Download Summary CSV"):
        st.sidebar.download_button(
            label="💾 Save CSV",
            data=summary_df.to_csv(index=False),
            file_name='nbs_summary.csv',
            mime='text/csv'
        )
    
    # Summary metrics
    st.markdown("## 📈 Analysis Summary")
    create_summary_metrics(stats)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🗺️ Interactive Map",
        "📊 Interventions",
        "🌿 Benefits",
        "🏙️ Morphology",
        "📋 Data Tables",
        "🖼️ Static Reports"
    ])
    
    # TAB 1: Interactive Map
    with tab1:
        st.markdown("### 🗺️ NbS Intervention Map")
        st.markdown("Click on any grid cell to see details")
        
        if spatial_gdf is not None:
            m = create_interactive_map(spatial_gdf)
            if m:
                st_folium(m, width=1400, height=600)
            else:
                st.warning("Map data not available")
        else:
            st.warning("Spatial data not found. Please run analysis with GeoJSON export.")
    
    # TAB 2: Interventions
    with tab2:
        st.markdown("### 📊 Intervention Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Summary Statistics")
            st.dataframe(
                summary_df[['NbS_Type', 'Num_Cells', 'Total_Area_hectares', 'Total_Cost_Crores']].style.format({
                    'Total_Area_hectares': '{:.2f}',
                    'Total_Cost_Crores': '₹{:.2f}'
                }),
                use_container_width=True,
                height=250
            )
        
        with col2:
            st.markdown("#### Cost Effectiveness")
            summary_df['cost_per_hectare'] = summary_df['Total_Cost_Crores'] / summary_df['Total_Area_hectares']
            
            fig = px.bar(
                summary_df, 
                x='cost_per_hectare', 
                y='NbS_Type',
                orientation='h',
                color='NbS_Type',
                title='Cost per Hectare (Crores INR/ha)'
            )
            fig.update_layout(showlegend=False, height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Main intervention charts
        fig = create_intervention_charts(summary_df)
        st.plotly_chart(fig, use_container_width=True)
    
    # TAB 3: Benefits
    with tab3:
        st.markdown("### 🌿 Multi-benefit Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Radar Chart")
            radar_fig = create_benefits_radar(summary_df)
            if radar_fig:
                st.plotly_chart(radar_fig, use_container_width=True)
            else:
                st.warning("Benefit data not available")
        
        with col2:
            st.markdown("#### Benefit Scores Heatmap")
            benefit_cols = ['climate_adaptation', 'biodiversity', 'air_quality', 
                           'water_management', 'social_wellbeing', 'economic_value']
            available = [col for col in benefit_cols if col in summary_df.columns]
            
            if available:
                heatmap_data = summary_df[['NbS_Type'] + available].set_index('NbS_Type')
                fig = px.imshow(
                    heatmap_data.T,
                    labels=dict(x="NbS Type", y="Benefit Category", color="Score"),
                    color_continuous_scale='Greens',
                    aspect='auto'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Environmental benefits
        st.markdown("#### Environmental Benefits Quantification")
        env_fig = create_environmental_benefits(summary_df)
        if env_fig:
            st.plotly_chart(env_fig, use_container_width=True)
    
    # TAB 4: Morphology
    with tab4:
        st.markdown("### 🏙️ Urban Morphology Analysis")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            mean_density = grid_df['density'].mean() if 'density' in grid_df.columns else 0
            st.metric("Mean Density", f"{mean_density:.3f}", "Plan Area Fraction")
        
        with col2:
            mean_roughness = grid_df['roughness'].mean() if 'roughness' in grid_df.columns else 0
            st.metric("Mean Roughness", f"{mean_roughness:.3f}m", "z₀")
        
        with col3:
            mean_height = grid_df['avg_height'].mean() if 'avg_height' in grid_df.columns else 0
            st.metric("Mean Height", f"{mean_height:.1f}m", "Building Height")
        
        with col4:
            mean_svf = grid_df['svf'].mean() if 'svf' in grid_df.columns else 0
            st.metric("Mean SVF", f"{mean_svf:.3f}", "Sky View Factor")
        
        st.markdown("---")
        
        # Distributions
        morph_fig = create_morphology_distributions(grid_df)
        if morph_fig:
            st.plotly_chart(morph_fig, use_container_width=True)
        
        # Correlation
        st.markdown("#### Correlation Matrix")
        morph_cols = ['density', 'roughness', 'avg_height', 'svf']
        available = [col for col in morph_cols if col in grid_df.columns]
        
        if len(available) >= 2:
            corr = grid_df[available].corr()
            fig = px.imshow(
                corr,
                labels=dict(color="Correlation"),
                color_continuous_scale='RdBu',
                color_continuous_midpoint=0,
                aspect='auto'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 5: Data Tables
    with tab5:
        st.markdown("### 📋 Detailed Data Tables")
        
        # Summary table
        st.markdown("#### Intervention Summary")
        st.dataframe(
            summary_df.style.format({
                col: '{:.2f}' for col in summary_df.columns if summary_df[col].dtype in ['float64', 'float32']
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Grid data
        st.markdown("#### Grid Cell Data")
        st.markdown(f"Total cells: {len(grid_df)}")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            nbs_filter = st.multiselect(
                "Filter by NbS Type:",
                options=grid_df['Proposed_NbS'].unique() if 'Proposed_NbS' in grid_df.columns else [],
                default=None
            )
        
        with col2:
            density_range = st.slider(
                "Filter by Density:",
                0.0, 1.0, (0.0, 1.0),
                step=0.01
            ) if 'density' in grid_df.columns else (0, 1)
        
        # Apply filters
        filtered_grid = grid_df.copy()
        if nbs_filter:
            filtered_grid = filtered_grid[filtered_grid['Proposed_NbS'].isin(nbs_filter)]
        if 'density' in filtered_grid.columns:
            filtered_grid = filtered_grid[
                (filtered_grid['density'] >= density_range[0]) & 
                (filtered_grid['density'] <= density_range[1])
            ]
        
        st.dataframe(
            filtered_grid.head(100).style.format({
                col: '{:.3f}' for col in filtered_grid.columns if filtered_grid[col].dtype in ['float64', 'float32']
            }),
            use_container_width=True
        )
        
        if len(filtered_grid) > 100:
            st.info(f"Showing first 100 rows of {len(filtered_grid)} total")
    
    # TAB 6: Static Reports
    with tab6:
        st.markdown("### 🖼️ Generated Visualizations")
        
        viz_path = Path('outputs/visualizations')
        if viz_path.exists():
            viz_files = sorted(viz_path.glob('*.png'))
            
            if viz_files:
                selected_viz = st.selectbox(
                    "Select visualization:",
                    [f.name for f in viz_files]
                )
                
                selected_file = viz_path / selected_viz
                st.image(str(selected_file), use_container_width=True)
                
                # Download button
                with open(selected_file, 'rb') as f:
                    st.download_button(
                        label=f"📥 Download {selected_viz}",
                        data=f.read(),
                        file_name=selected_viz,
                        mime='image/png'
                    )
            else:
                st.warning("No visualizations found. Run `python tools/visualize_results.py` first.")
        else:
            st.warning("Visualizations directory not found.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p><b>Hyderabad Nature-based Solutions Planner v1.0</b></p>
        <p>Based on G20 NbS Working Paper Framework | Urban Climate Resilience Planning</p>
        <p>Generated: {}</p>
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)


if __name__ == "__main__":
    main()

