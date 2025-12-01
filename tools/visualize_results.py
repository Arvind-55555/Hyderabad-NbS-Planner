#!/usr/bin/env python3
"""
Enhanced Visualization Tool for NbS Analysis Results
Creates comprehensive charts and visualizations from generated output data
"""

import sys
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from datetime import datetime

from src.config import NBS_COLORS

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.figsize'] = (14, 10)


def load_data(output_dir):
    """
    Load all generated output files
    
    Args:
        output_dir: Path to outputs directory
    
    Returns:
        dict: Dictionary containing all loaded data
    """
    output_path = Path(output_dir)
    reports_path = output_path / 'reports'
    
    data = {}
    
    # Find latest files
    csv_files = list((reports_path / 'csv').glob('nbs_*.csv'))
    geojson_files = list(reports_path.glob('nbs_interventions_*.geojson'))
    json_files = list(reports_path.glob('nbs_statistics_*.json'))
    
    if not csv_files:
        print(f"ERROR: No CSV files found in {reports_path / 'csv'}")
        return None
    
    # Load CSV files
    summary_file = [f for f in csv_files if 'summary' in f.name][0]
    grid_file = [f for f in csv_files if 'grid_data' in f.name][0]
    
    print(f"Loading data from: {reports_path}")
    data['summary'] = pd.read_csv(summary_file)
    data['grid'] = pd.read_csv(grid_file)
    print(f"  ✓ Loaded summary: {len(data['summary'])} NbS types")
    print(f"  ✓ Loaded grid data: {len(data['grid'])} cells")
    
    # Load GeoJSON if available
    if geojson_files:
        latest_geojson = sorted(geojson_files, key=lambda x: x.stat().st_mtime)[-1]
        data['spatial'] = gpd.read_file(latest_geojson)
        print(f"  ✓ Loaded spatial data: {len(data['spatial'])} features")
    
    # Load JSON if available
    if json_files:
        import json
        latest_json = sorted(json_files, key=lambda x: x.stat().st_mtime)[-1]
        with open(latest_json, 'r') as f:
            data['stats'] = json.load(f)
        print(f"  ✓ Loaded statistics")
    
    return data


def create_intervention_charts(summary_df, output_dir):
    """
    Create comprehensive intervention analysis charts
    """
    print("\n📊 Creating intervention analysis charts...")
    
    output_path = Path(output_dir) / 'visualizations'
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. AREA AND COST COMPARISON
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Area by type (bar chart)
    ax1 = axes[0, 0]
    colors_list = [NBS_COLORS.get(nbs, '#95a5a6') for nbs in summary_df['NbS_Type']]
    summary_df.plot(x='NbS_Type', y='Total_Area_hectares', kind='bar', 
                    ax=ax1, color=colors_list, legend=False)
    ax1.set_title('Intervention Area by Type', fontsize=14, fontweight='bold')
    ax1.set_xlabel('NbS Type', fontsize=12)
    ax1.set_ylabel('Area (hectares)', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for container in ax1.containers:
        ax1.bar_label(container, fmt='%.1f ha', padding=3)
    
    # Cost by type (bar chart)
    ax2 = axes[0, 1]
    summary_df.plot(x='NbS_Type', y='Total_Cost_Crores', kind='bar', 
                    ax=ax2, color=colors_list, legend=False)
    ax2.set_title('Implementation Cost by Type', fontsize=14, fontweight='bold')
    ax2.set_xlabel('NbS Type', fontsize=12)
    ax2.set_ylabel('Cost (Crores INR)', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(axis='y', alpha=0.3)
    
    for container in ax2.containers:
        ax2.bar_label(container, fmt='₹%.2f Cr', padding=3)
    
    # Area distribution (pie chart)
    ax3 = axes[1, 0]
    wedges, texts, autotexts = ax3.pie(
        summary_df['Total_Area_hectares'],
        labels=summary_df['NbS_Type'],
        colors=colors_list,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10}
    )
    ax3.set_title('Area Distribution', fontsize=14, fontweight='bold')
    
    # Cost distribution (pie chart)
    ax4 = axes[1, 1]
    wedges, texts, autotexts = ax4.pie(
        summary_df['Total_Cost_Crores'],
        labels=summary_df['NbS_Type'],
        colors=colors_list,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10}
    )
    ax4.set_title('Cost Distribution', fontsize=14, fontweight='bold')
    
    plt.suptitle('Nature-based Solutions - Area & Cost Analysis', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_file = output_path / 'intervention_analysis.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()
    
    # 2. COST-EFFECTIVENESS ANALYSIS
    fig, ax = plt.subplots(figsize=(12, 8))
    
    summary_df['cost_per_hectare'] = (summary_df['Total_Cost_Crores'] * 1e7) / (summary_df['Total_Area_hectares'] * 10000)
    
    bars = ax.barh(summary_df['NbS_Type'], summary_df['cost_per_hectare'], 
                   color=colors_list)
    ax.set_xlabel('Cost per Square Meter (INR)', fontsize=12, fontweight='bold')
    ax.set_ylabel('NbS Type', fontsize=12, fontweight='bold')
    ax.set_title('Cost Effectiveness Comparison\n(Lower is more cost-effective)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, summary_df['cost_per_hectare'])):
        ax.text(value + 2, bar.get_y() + bar.get_height()/2, 
                f'₹{value:.0f}/m²', 
                va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_path / 'cost_effectiveness.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()


def create_benefits_analysis(summary_df, output_dir):
    """
    Create multi-benefit analysis visualizations
    """
    print("\n🌿 Creating benefits analysis...")
    
    output_path = Path(output_dir) / 'visualizations'
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Check if benefit columns exist
    benefit_cols = [col for col in summary_df.columns if col in [
        'climate_adaptation', 'biodiversity', 'air_quality', 
        'water_management', 'social_wellbeing', 'economic_value'
    ]]
    
    if len(benefit_cols) < 3:
        print("  ⚠ Insufficient benefit data for visualization")
        return
    
    # 1. MULTI-BENEFIT HEATMAP
    fig, ax = plt.subplots(figsize=(12, 8))
    
    benefit_data = summary_df[['NbS_Type'] + benefit_cols].set_index('NbS_Type')
    
    sns.heatmap(benefit_data, annot=True, fmt='.0f', cmap='YlGn', 
                cbar_kws={'label': 'Benefit Score'}, ax=ax, 
                linewidths=0.5, linecolor='white')
    
    ax.set_title('Multi-benefit Assessment Matrix\n(Scores: 0-5 scale)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Benefit Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('NbS Type', fontsize=12, fontweight='bold')
    
    # Improve label readability
    ax.set_xticklabels([col.replace('_', ' ').title() for col in benefit_cols], 
                       rotation=45, ha='right')
    
    plt.tight_layout()
    output_file = output_path / 'benefits_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()
    
    # 2. RADAR CHART FOR TOP NbS TYPES
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    categories = [col.replace('_', ' ').title() for col in benefit_cols]
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, max(summary_df[benefit_cols].max().max(), 5))
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.grid(True, linestyle='--', alpha=0.7)
    
    colors_radar = ['#27ae60', '#3498db', '#e74c3c', '#f39c12']
    
    for idx, (_, row) in enumerate(summary_df.head(4).iterrows()):
        values = [row[col] for col in benefit_cols]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, 
                label=row['NbS_Type'], color=colors_radar[idx])
        ax.fill(angles, values, alpha=0.15, color=colors_radar[idx])
    
    ax.set_title('Multi-benefit Radar Chart\n(Comparing NbS Types)', 
                 fontsize=14, fontweight='bold', pad=30, y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=10)
    
    plt.tight_layout()
    output_file = output_path / 'benefits_radar.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()
    
    # 3. ENVIRONMENTAL BENEFITS BAR CHART
    env_cols = ['cooling_effect_celsius', 'pm25_removal_kg_yr', 
                'carbon_sequestration_kg_yr', 'estimated_trees']
    available_env_cols = [col for col in env_cols if col in summary_df.columns]
    
    if available_env_cols:
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        colors_list = [NBS_COLORS.get(nbs, '#95a5a6') for nbs in summary_df['NbS_Type']]
        
        titles = {
            'cooling_effect_celsius': 'Temperature Reduction (°C)',
            'pm25_removal_kg_yr': 'PM2.5 Removal (kg/year)',
            'carbon_sequestration_kg_yr': 'CO₂ Sequestration (kg/year)',
            'estimated_trees': 'Trees to be Planted',
            'runoff_reduction_percent': 'Stormwater Retention (%)'
        }
        
        for idx, col in enumerate(available_env_cols[:4]):
            ax = axes[idx]
            summary_df.plot(x='NbS_Type', y=col, kind='bar', 
                           ax=ax, color=colors_list, legend=False)
            ax.set_title(titles.get(col, col), fontsize=12, fontweight='bold')
            ax.set_xlabel('NbS Type', fontsize=10)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for container in ax.containers:
                ax.bar_label(container, fmt='%.1f', padding=3, fontsize=9)
        
        plt.suptitle('Environmental Benefits Quantification', 
                     fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        output_file = output_path / 'environmental_benefits.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        plt.close()


def create_morphology_visualizations(grid_df, output_dir):
    """
    Create morphology analysis visualizations
    """
    print("\n🏙️ Creating morphology visualizations...")
    
    output_path = Path(output_dir) / 'visualizations'
    output_path.mkdir(parents=True, exist_ok=True)
    
    morph_cols = ['density', 'roughness', 'avg_height', 'svf']
    available_morph = [col for col in morph_cols if col in grid_df.columns]
    
    if len(available_morph) < 2:
        print("  ⚠ Insufficient morphology data")
        return
    
    # 1. MORPHOLOGY DISTRIBUTIONS
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    
    titles = {
        'density': 'Plan Area Density Distribution',
        'roughness': 'Roughness Length Distribution (m)',
        'avg_height': 'Building Height Distribution (m)',
        'svf': 'Sky View Factor Distribution'
    }
    
    colors_hist = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
    
    for idx, col in enumerate(available_morph[:4]):
        ax = axes[idx]
        data = grid_df[col].dropna()
        
        # Histogram with KDE
        ax.hist(data, bins=30, alpha=0.7, color=colors_hist[idx], 
                edgecolor='black', density=True)
        
        # Add KDE line
        from scipy import stats
        kde = stats.gaussian_kde(data)
        x_range = np.linspace(data.min(), data.max(), 100)
        ax.plot(x_range, kde(x_range), color='black', linewidth=2, 
                label='KDE')
        
        # Statistics
        mean_val = data.mean()
        median_val = data.median()
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_val:.3f}')
        ax.axvline(median_val, color='blue', linestyle='--', linewidth=2, 
                   label=f'Median: {median_val:.3f}')
        
        ax.set_title(titles.get(col, col), fontsize=12, fontweight='bold')
        ax.set_xlabel(col.replace('_', ' ').title(), fontsize=10)
        ax.set_ylabel('Density', fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
    
    plt.suptitle('Urban Morphology Distribution Analysis', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    output_file = output_path / 'morphology_distributions.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()
    
    # 2. CORRELATION MATRIX
    if len(available_morph) >= 3:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        corr_data = grid_df[available_morph].corr()
        
        sns.heatmap(corr_data, annot=True, fmt='.2f', cmap='coolwarm', 
                    center=0, square=True, linewidths=1, cbar_kws={'label': 'Correlation'},
                    ax=ax, vmin=-1, vmax=1)
        
        ax.set_title('Morphology Metrics Correlation Matrix', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Improve labels
        labels = [col.replace('_', ' ').title() for col in available_morph]
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_yticklabels(labels, rotation=0)
        
        plt.tight_layout()
        output_file = output_path / 'morphology_correlation.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"  ✓ Saved: {output_file}")
        plt.close()


def create_summary_dashboard(data, output_dir):
    """
    Create comprehensive summary dashboard
    """
    print("\n📈 Creating summary dashboard...")
    
    output_path = Path(output_dir) / 'visualizations'
    output_path.mkdir(parents=True, exist_ok=True)
    
    summary_df = data['summary']
    stats = data.get('stats', {})
    
    fig = plt.figure(figsize=(20, 14))
    gs = fig.add_gridspec(4, 3, hspace=0.35, wspace=0.3)
    
    colors_list = [NBS_COLORS.get(nbs, '#95a5a6') for nbs in summary_df['NbS_Type']]
    
    # Title
    fig.suptitle('Hyderabad Nature-based Solutions - Comprehensive Dashboard', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # 1. Area by Type (top-left)
    ax1 = fig.add_subplot(gs[0, 0])
    summary_df.plot(x='NbS_Type', y='Total_Area_hectares', kind='bar', 
                    ax=ax1, color=colors_list, legend=False)
    ax1.set_title('Area by NbS Type', fontsize=12, fontweight='bold')
    ax1.set_xlabel('')
    ax1.set_ylabel('Hectares', fontsize=10)
    ax1.tick_params(axis='x', rotation=45, labelsize=9)
    ax1.grid(axis='y', alpha=0.3)
    
    # 2. Cost by Type (top-center)
    ax2 = fig.add_subplot(gs[0, 1])
    summary_df.plot(x='NbS_Type', y='Total_Cost_Crores', kind='bar', 
                    ax=ax2, color=colors_list, legend=False)
    ax2.set_title('Cost by NbS Type', fontsize=12, fontweight='bold')
    ax2.set_xlabel('')
    ax2.set_ylabel('Crores INR', fontsize=10)
    ax2.tick_params(axis='x', rotation=45, labelsize=9)
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. Area Distribution Pie (top-right)
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.pie(summary_df['Total_Area_hectares'], labels=summary_df['NbS_Type'],
            colors=colors_list, autopct='%1.1f%%', startangle=90,
            textprops={'fontsize': 9})
    ax3.set_title('Area Distribution', fontsize=12, fontweight='bold')
    
    # 4. Number of Cells (row 2, left)
    ax4 = fig.add_subplot(gs[1, 0])
    summary_df.plot(x='NbS_Type', y='Num_Cells', kind='barh', 
                    ax=ax4, color=colors_list, legend=False)
    ax4.set_title('Grid Cells by Type', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Number of Cells', fontsize=10)
    ax4.set_ylabel('')
    ax4.tick_params(axis='y', labelsize=9)
    ax4.grid(axis='x', alpha=0.3)
    
    # 5. Cost Effectiveness (row 2, center)
    ax5 = fig.add_subplot(gs[1, 1])
    cost_per_ha = summary_df['Total_Cost_Crores'] / summary_df['Total_Area_hectares']
    ax5.barh(summary_df['NbS_Type'], cost_per_ha, color=colors_list)
    ax5.set_title('Cost per Hectare', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Crores/Hectare', fontsize=10)
    ax5.set_ylabel('')
    ax5.tick_params(axis='y', labelsize=9)
    ax5.grid(axis='x', alpha=0.3)
    
    # 6. Statistics Table (row 2, right)
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis('off')
    
    if stats:
        meta = stats.get('analysis_metadata', {})
        area_stats = stats.get('area_statistics', {})
        financial = stats.get('financial', {})
        
        table_data = [
            ['Total Grid Cells', f"{meta.get('total_grid_cells', 'N/A')}"],
            ['Intervention Cells', f"{meta.get('cells_with_interventions', 'N/A')}"],
            ['Coverage', f"{meta.get('intervention_coverage_pct', 0):.1f}%"],
            ['Study Area', f"{area_stats.get('total_study_area_hectares', 0):.1f} ha"],
            ['Intervention Area', f"{area_stats.get('total_intervention_area_hectares', 0):.1f} ha"],
            ['Total Cost', f"₹{financial.get('total_cost_crores', 0):.2f} Cr"],
        ]
        
        table = ax6.table(cellText=table_data, cellLoc='left', loc='center',
                         bbox=[0, 0, 1, 1], colWidths=[0.6, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        for i in range(len(table_data)):
            table[(i, 0)].set_facecolor('#e8f5e9')
            table[(i, 1)].set_facecolor('#ffffff')
            table[(i, 0)].set_text_props(weight='bold')
    
    ax6.set_title('Analysis Summary', fontsize=12, fontweight='bold', pad=10)
    
    # 7-9. Environmental Benefits (row 3, all columns)
    benefit_metrics = [
        ('carbon_sequestration_kg_yr', 'CO₂ Sequestration\n(tonnes/year)', 1000),
        ('pm25_removal_kg_yr', 'PM2.5 Removal\n(kg/year)', 1),
        ('estimated_trees', 'Trees to be Planted', 1)
    ]
    
    for idx, (col, title, divisor) in enumerate(benefit_metrics):
        if col in summary_df.columns:
            ax = fig.add_subplot(gs[2, idx])
            values = summary_df[col] / divisor
            ax.bar(range(len(summary_df)), values, color=colors_list)
            ax.set_title(title, fontsize=11, fontweight='bold')
            ax.set_xticks(range(len(summary_df)))
            ax.set_xticklabels(summary_df['NbS_Type'], rotation=45, 
                              ha='right', fontsize=9)
            ax.grid(axis='y', alpha=0.3)
            
            # Add total
            total = values.sum()
            if col == 'carbon_sequestration_kg_yr':
                ax.text(0.95, 0.95, f'Total: {total:.1f}t', 
                       transform=ax.transAxes, ha='right', va='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                       fontsize=10, fontweight='bold')
            else:
                ax.text(0.95, 0.95, f'Total: {total:.0f}', 
                       transform=ax.transAxes, ha='right', va='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                       fontsize=10, fontweight='bold')
    
    # 10. Overall Benefit Score (row 4, full width)
    ax10 = fig.add_subplot(gs[3, :])
    
    benefit_cols = ['climate_adaptation', 'biodiversity', 'air_quality', 
                   'water_management', 'social_wellbeing', 'economic_value']
    available_benefits = [col for col in benefit_cols if col in summary_df.columns]
    
    if available_benefits:
        x = np.arange(len(summary_df))
        width = 0.15
        
        for idx, col in enumerate(available_benefits):
            offset = (idx - len(available_benefits)/2) * width
            ax10.bar(x + offset, summary_df[col], width, 
                    label=col.replace('_', ' ').title())
        
        ax10.set_title('Multi-benefit Assessment Comparison', 
                      fontsize=12, fontweight='bold')
        ax10.set_xlabel('NbS Type', fontsize=10)
        ax10.set_ylabel('Benefit Score (0-5)', fontsize=10)
        ax10.set_xticks(x)
        ax10.set_xticklabels(summary_df['NbS_Type'], rotation=45, ha='right')
        ax10.legend(loc='upper left', ncol=3, fontsize=9)
        ax10.grid(axis='y', alpha=0.3)
        ax10.set_ylim(0, 5.5)
    
    plt.tight_layout()
    output_file = output_path / 'comprehensive_dashboard.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_file}")
    plt.close()


def main():
    """Main visualization function"""
    parser = argparse.ArgumentParser(
        description='Create comprehensive visualizations from NbS analysis results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Visualize results from default output directory
  python tools/visualize_results.py
  
  # Visualize from specific directory
  python tools/visualize_results.py --output-dir outputs
  
  # Create only specific visualizations
  python tools/visualize_results.py --charts interventions benefits
        """
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Path to outputs directory (default: outputs)'
    )
    
    parser.add_argument(
        '--charts',
        nargs='+',
        choices=['interventions', 'benefits', 'morphology', 'dashboard', 'all'],
        default=['all'],
        help='Which charts to generate (default: all)'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("NATURE-BASED SOLUTIONS - ENHANCED VISUALIZATION TOOL")
    print("="*70)
    
    # Load data
    print("\n📂 Loading output data...")
    data = load_data(args.output_dir)
    
    if data is None:
        print("\n❌ ERROR: Could not load data. Please run main.py first.")
        return 1
    
    summary_df = data['summary']
    grid_df = data['grid']
    
    # Generate visualizations
    chart_types = args.charts
    if 'all' in chart_types:
        chart_types = ['interventions', 'benefits', 'morphology', 'dashboard']
    
    if 'interventions' in chart_types:
        create_intervention_charts(summary_df, args.output_dir)
    
    if 'benefits' in chart_types:
        create_benefits_analysis(summary_df, args.output_dir)
    
    if 'morphology' in chart_types:
        create_morphology_visualizations(grid_df, args.output_dir)
    
    if 'dashboard' in chart_types:
        create_summary_dashboard(data, args.output_dir)
    
    # Summary
    viz_path = Path(args.output_dir) / 'visualizations'
    viz_files = list(viz_path.glob('*.png'))
    
    print("\n" + "="*70)
    print("✅ VISUALIZATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Generated {len(viz_files)} visualization files:")
    for f in sorted(viz_files):
        print(f"  • {f.name}")
    
    print(f"\n📁 All visualizations saved to: {viz_path}")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

