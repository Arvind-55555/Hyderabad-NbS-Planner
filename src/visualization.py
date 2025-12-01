"""
Visualization Module
Creates maps, charts, and visualizations for NbS analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Patch
import seaborn as sns
import numpy as np
import logging
from pathlib import Path

from .config import (
    NBS_COLORS, DENSITY_CMAP, ROUGHNESS_CMAP, SVF_CMAP,
    MAP_DPI, MAP_FIGSIZE, MAPS_DIR
)

logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']


def plot_nbs_map(nbs_gdf, streets_gdf, green_blue_gdf, wind_dir, 
                 output_path=None, title=None):
    """
    Create comprehensive NbS intervention map
    
    Args:
        nbs_gdf: GeoDataFrame with NbS recommendations
        streets_gdf: Street network
        green_blue_gdf: Existing green/blue spaces
        wind_dir: Prevailing wind direction
        output_path: Path to save the map
        title: Custom title (optional)
    
    Returns:
        Figure: Matplotlib figure object
    """
    logger.info("Creating NbS intervention map...")
    
    fig, ax = plt.subplots(1, 1, figsize=MAP_FIGSIZE)
    
    # Plot streets as background
    if not streets_gdf.empty:
        streets_gdf.plot(ax=ax, linewidth=0.5, color='gray', alpha=0.4, zorder=1)
    
    # Plot NbS interventions (colored grid)
    nbs_gdf['color'] = nbs_gdf['Proposed_NbS'].map(NBS_COLORS)
    
    nbs_gdf.plot(
        ax=ax,
        color=nbs_gdf['color'],
        alpha=0.7,
        edgecolor='white',
        linewidth=0.3,
        zorder=2
    )
    
    # Plot existing green/blue spaces on top
    if not green_blue_gdf.empty:
        green_blue_gdf.plot(
            ax=ax, 
            color='#1e8449',  # Dark green
            alpha=0.8, 
            edgecolor='darkgreen',
            linewidth=0.5,
            zorder=3, 
            label='Existing Green/Blue Space'
        )
    
    # Add wind direction indicator
    add_wind_arrow(ax, wind_dir, nbs_gdf)
    
    # Create legend
    legend_elements = [
        Patch(facecolor=color, label=nbs_type, edgecolor='white')
        for nbs_type, color in NBS_COLORS.items()
        if nbs_type in nbs_gdf['Proposed_NbS'].values
    ]
    
    # Add existing green space to legend if present
    if not green_blue_gdf.empty:
        legend_elements.append(
            Patch(facecolor='#1e8449', label='Existing Green/Blue', edgecolor='darkgreen')
        )
    
    ax.legend(
        handles=legend_elements,
        loc='upper right',
        title="Nature-based Solutions",
        fontsize=10,
        title_fontsize=11,
        framealpha=0.95
    )
    
    # Title
    if title is None:
        title = f"Nature-based Solutions Plan\nPrevailing Wind: {wind_dir:.0f}°"
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Remove axes
    ax.set_axis_off()
    
    # Tight layout
    plt.tight_layout()
    
    # Save if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight')
        logger.info(f"Map saved to: {output_path}")
    
    return fig


def add_wind_arrow(ax, wind_dir, gdf):
    """Add wind direction arrow to map"""
    # Get map bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Arrow origin (top-left corner)
    arrow_x = minx + (maxx - minx) * 0.1
    arrow_y = maxy - (maxy - miny) * 0.1
    
    # Arrow direction (convert meteorological to cartesian)
    # Meteorological: 0° = North, 90° = East
    # Cartesian: 0° = East, 90° = North
    angle_rad = np.radians(270 - wind_dir)
    arrow_length = (maxx - minx) * 0.08
    
    dx = arrow_length * np.cos(angle_rad)
    dy = arrow_length * np.sin(angle_rad)
    
    ax.arrow(
        arrow_x, arrow_y, dx, dy,
        head_width=arrow_length * 0.3,
        head_length=arrow_length * 0.25,
        fc='#3498db',
        ec='black',
        linewidth=2,
        alpha=0.8,
        zorder=10
    )
    
    # Add label
    ax.text(
        arrow_x, arrow_y - (maxy - miny) * 0.05,
        f'Wind: {wind_dir:.0f}°',
        fontsize=10,
        fontweight='bold',
        ha='center',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )


def plot_morphology_maps(analysis_gdf, streets_gdf, output_dir=None):
    """
    Create multiple maps showing different morphology metrics
    
    Args:
        analysis_gdf: GeoDataFrame with morphology data
        streets_gdf: Street network
        output_dir: Directory to save maps
    
    Returns:
        Figure: Matplotlib figure with subplots
    """
    logger.info("Creating morphology maps...")
    
    fig, axes = plt.subplots(2, 2, figsize=(18, 16))
    axes = axes.flatten()
    
    metrics = [
        ('density', 'Plan Area Density', DENSITY_CMAP, 0, 1),
        ('roughness', 'Roughness Length (z₀) [m]', ROUGHNESS_CMAP, 0, analysis_gdf['roughness'].quantile(0.95)),
        ('avg_height', 'Average Building Height [m]', 'viridis', 0, analysis_gdf['avg_height'].quantile(0.95)),
        ('svf', 'Sky View Factor', SVF_CMAP, 0, 1)
    ]
    
    for idx, (metric, title, cmap, vmin, vmax) in enumerate(metrics):
        ax = axes[idx]
        
        # Plot streets
        if not streets_gdf.empty:
            streets_gdf.plot(ax=ax, linewidth=0.3, color='gray', alpha=0.3)
        
        # Plot metric
        analysis_gdf.plot(
            column=metric,
            ax=ax,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            alpha=0.8,
            edgecolor='white',
            linewidth=0.2,
            legend=True,
            legend_kwds={
                'label': title,
                'orientation': 'horizontal',
                'shrink': 0.8,
                'pad': 0.05
            }
        )
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_axis_off()
    
    plt.suptitle('Urban Morphology Analysis', fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    if output_dir:
        output_path = Path(output_dir) / 'morphology_maps.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight')
        logger.info(f"Morphology maps saved to: {output_path}")
    
    return fig


def plot_intervention_statistics(summary_df, output_path=None):
    """
    Create bar charts showing intervention statistics
    
    Args:
        summary_df: DataFrame with intervention summary
        output_path: Path to save the chart
    
    Returns:
        Figure: Matplotlib figure
    """
    logger.info("Creating intervention statistics charts...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Area by NbS Type
    ax1 = axes[0, 0]
    summary_df.plot(
        x='NbS_Type',
        y='Total_Area_hectares',
        kind='bar',
        ax=ax1,
        color='#27ae60',
        legend=False
    )
    ax1.set_title('Total Area by NbS Type', fontsize=14, fontweight='bold')
    ax1.set_xlabel('NbS Intervention', fontsize=12)
    ax1.set_ylabel('Area (hectares)', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Cost by NbS Type
    ax2 = axes[0, 1]
    if 'Total_Cost_Crores' in summary_df.columns:
        summary_df.plot(
            x='NbS_Type',
            y='Total_Cost_Crores',
            kind='bar',
            ax=ax2,
            color='#e74c3c',
            legend=False
        )
        ax2.set_title('Implementation Cost by NbS Type', fontsize=14, fontweight='bold')
        ax2.set_xlabel('NbS Intervention', fontsize=12)
        ax2.set_ylabel('Cost (Crores INR)', fontsize=12)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(axis='y', alpha=0.3)
    
    # 3. Multi-benefit Radar (if available)
    ax3 = axes[1, 0]
    if all(col in summary_df.columns for col in ['benefit_climate_adaptation', 'benefit_biodiversity']):
        plot_benefits_radar(summary_df, ax3)
    else:
        ax3.text(0.5, 0.5, 'Benefits data not available', 
                ha='center', va='center', fontsize=14)
        ax3.set_axis_off()
    
    # 4. Number of Cells by NbS Type
    ax4 = axes[1, 1]
    summary_df.plot(
        x='NbS_Type',
        y='Num_Cells',
        kind='bar',
        ax=ax4,
        color='#3498db',
        legend=False
    )
    ax4.set_title('Number of Grid Cells by NbS Type', fontsize=14, fontweight='bold')
    ax4.set_xlabel('NbS Intervention', fontsize=12)
    ax4.set_ylabel('Number of Cells', fontsize=12)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y', alpha=0.3)
    
    plt.suptitle('NbS Implementation Statistics', fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight')
        logger.info(f"Statistics chart saved to: {output_path}")
    
    return fig


def plot_benefits_radar(summary_df, ax):
    """Create radar chart for multi-benefit assessment"""
    benefit_cols = [
        'benefit_climate_adaptation',
        'benefit_biodiversity',
        'benefit_air_quality',
        'benefit_water_management',
        'benefit_social_wellbeing',
        'benefit_economic_value'
    ]
    
    # Check if columns exist
    available_cols = [col for col in benefit_cols if col in summary_df.columns]
    
    if len(available_cols) < 3:
        ax.text(0.5, 0.5, 'Insufficient benefit data', ha='center', va='center')
        ax.set_axis_off()
        return
    
    # Select top 3 NbS types by area
    top_nbs = summary_df.nlargest(3, 'Total_Area_hectares')
    
    categories = [col.replace('benefit_', '').replace('_', ' ').title() 
                  for col in available_cols]
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, size=10)
    ax.set_ylim(0, 5)
    
    colors = ['#27ae60', '#3498db', '#e74c3c']
    
    for idx, (_, row) in enumerate(top_nbs.iterrows()):
        values = [row[col] for col in available_cols]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=row['NbS_Type'], color=colors[idx])
        ax.fill(angles, values, alpha=0.25, color=colors[idx])
    
    ax.set_title('Multi-benefit Assessment (Top 3 NbS)', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))


def plot_cost_benefit_analysis(summary_df, output_path=None):
    """
    Create cost-benefit scatter plot
    
    Args:
        summary_df: DataFrame with costs and benefits
        output_path: Path to save chart
    
    Returns:
        Figure: Matplotlib figure
    """
    logger.info("Creating cost-benefit analysis chart...")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    if 'Total_Cost_Crores' in summary_df.columns and 'benefit_overall_score' in summary_df.columns:
        colors_map = {row['NbS_Type']: NBS_COLORS.get(row['NbS_Type'], '#95a5a6') 
                      for _, row in summary_df.iterrows()}
        
        for _, row in summary_df.iterrows():
            ax.scatter(
                row['Total_Cost_Crores'],
                row['benefit_overall_score'],
                s=row['Total_Area_hectares'] * 20,
                c=colors_map[row['NbS_Type']],
                alpha=0.7,
                edgecolors='black',
                linewidth=1.5,
                label=row['NbS_Type']
            )
            
            # Add labels
            ax.annotate(
                row['NbS_Type'],
                (row['Total_Cost_Crores'], row['benefit_overall_score']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=10,
                fontweight='bold'
            )
        
        ax.set_xlabel('Total Cost (Crores INR)', fontsize=14, fontweight='bold')
        ax.set_ylabel('Overall Benefit Score', fontsize=14, fontweight='bold')
        ax.set_title('Cost-Benefit Analysis of NbS Interventions', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        # Add reference line (diagonal)
        ax.axline((0, 0), slope=10, color='gray', linestyle='--', alpha=0.5, 
                  label='Reference Line')
        
        # Remove duplicate legend entries
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='best', fontsize=10)
        
        plt.tight_layout()
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight')
            logger.info(f"Cost-benefit chart saved to: {output_path}")
    else:
        logger.warning("Cost or benefit data not available for cost-benefit analysis.")
        ax.text(0.5, 0.5, 'Data not available', ha='center', va='center', 
                transform=ax.transAxes, fontsize=14)
    
    return fig


def create_dashboard(nbs_gdf, streets_gdf, green_blue_gdf, summary_df, wind_dir, 
                     output_path=None):
    """
    Create comprehensive dashboard with multiple visualizations
    
    Args:
        nbs_gdf: GeoDataFrame with NbS recommendations
        streets_gdf: Street network
        green_blue_gdf: Existing green/blue spaces
        summary_df: Summary statistics
        wind_dir: Prevailing wind direction
        output_path: Path to save dashboard
    
    Returns:
        Figure: Matplotlib figure
    """
    logger.info("Creating comprehensive dashboard...")
    
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # Main map (large, top-left)
    ax_map = fig.add_subplot(gs[0:2, 0:2])
    
    # Plot main NbS map
    if not streets_gdf.empty:
        streets_gdf.plot(ax=ax_map, linewidth=0.5, color='gray', alpha=0.4)
    
    nbs_gdf['color'] = nbs_gdf['Proposed_NbS'].map(NBS_COLORS)
    nbs_gdf.plot(ax=ax_map, color=nbs_gdf['color'], alpha=0.7, edgecolor='white', linewidth=0.3)
    
    if not green_blue_gdf.empty:
        green_blue_gdf.plot(ax=ax_map, color='#1e8449', alpha=0.8)
    
    add_wind_arrow(ax_map, wind_dir, nbs_gdf)
    ax_map.set_title('NbS Intervention Map', fontsize=16, fontweight='bold')
    ax_map.set_axis_off()
    
    # Area chart (top-right)
    ax_area = fig.add_subplot(gs[0, 2])
    if not summary_df.empty:
        summary_df.plot(x='NbS_Type', y='Total_Area_hectares', kind='barh', 
                        ax=ax_area, legend=False, color='#27ae60')
        ax_area.set_title('Area by Type', fontsize=12, fontweight='bold')
        ax_area.set_xlabel('Hectares', fontsize=10)
        ax_area.tick_params(axis='y', labelsize=9)
    
    # Cost chart (middle-right)
    ax_cost = fig.add_subplot(gs[1, 2])
    if 'Total_Cost_Crores' in summary_df.columns:
        summary_df.plot(x='NbS_Type', y='Total_Cost_Crores', kind='barh', 
                        ax=ax_cost, legend=False, color='#e74c3c')
        ax_cost.set_title('Cost by Type', fontsize=12, fontweight='bold')
        ax_cost.set_xlabel('Crores INR', fontsize=10)
        ax_cost.tick_params(axis='y', labelsize=9)
    
    # Statistics table (bottom row)
    ax_table = fig.add_subplot(gs[2, :])
    ax_table.axis('tight')
    ax_table.axis('off')
    
    if not summary_df.empty:
        # Select key columns for table
        table_cols = ['NbS_Type', 'Num_Cells', 'Total_Area_hectares', 
                      'Total_Cost_Crores', 'benefit_overall_score']
        table_cols = [col for col in table_cols if col in summary_df.columns]
        
        table_data = summary_df[table_cols].round(2)
        table = ax_table.table(cellText=table_data.values,
                              colLabels=table_data.columns,
                              cellLoc='center',
                              loc='center',
                              bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header
        for i in range(len(table_data.columns)):
            table[(0, i)].set_facecolor('#3498db')
            table[(0, i)].set_text_props(weight='bold', color='white')
    
    plt.suptitle('Hyderabad NbS Analysis Dashboard', fontsize=20, fontweight='bold', y=0.98)
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=MAP_DPI, bbox_inches='tight')
        logger.info(f"Dashboard saved to: {output_path}")
    
    return fig


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Visualization module loaded successfully.")

