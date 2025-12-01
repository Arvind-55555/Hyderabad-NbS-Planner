"""
Reporting Module
Generates comprehensive reports, statistics, and exports for NbS analysis
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

from .config import (
    CITY_NAME, REPORTS_DIR, EXPORTS_DIR,
    G20_NBS_PRINCIPLES, MULTI_BENEFIT_CATEGORIES,
    REPORT_TITLE_TEMPLATE, REPORT_SUBTITLE
)

logger = logging.getLogger(__name__)


def generate_summary_statistics(nbs_gdf, summary_df, buildings_gdf=None):
    """
    Generate comprehensive summary statistics
    
    Args:
        nbs_gdf: GeoDataFrame with NbS recommendations
        summary_df: Intervention summary DataFrame
        buildings_gdf: Building footprints (optional)
    
    Returns:
        dict: Summary statistics
    """
    logger.info("Generating summary statistics...")
    
    total_cells = len(nbs_gdf)
    intervention_cells = len(nbs_gdf[nbs_gdf['Proposed_NbS'] != 'None'])
    
    stats = {
        'analysis_metadata': {
            'city': CITY_NAME,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_grid_cells': total_cells,
            'cells_with_interventions': intervention_cells,
            'intervention_coverage_pct': (intervention_cells / total_cells * 100) if total_cells > 0 else 0
        },
        'area_statistics': {
            'total_study_area_hectares': (nbs_gdf['cell_area'].sum() / 10000) if 'cell_area' in nbs_gdf.columns else 0,
            'total_intervention_area_hectares': summary_df['Total_Area_hectares'].sum() if not summary_df.empty else 0,
        },
        'financial': {
            'total_cost_inr': summary_df['Total_Cost_INR'].sum() if 'Total_Cost_INR' in summary_df.columns else 0,
            'total_cost_crores': summary_df['Total_Cost_Crores'].sum() if 'Total_Cost_Crores' in summary_df.columns else 0,
            'average_cost_per_hectare': 0
        },
        'environmental_benefits': {},
        'interventions_by_type': {}
    }
    
    # Calculate average cost per hectare
    if stats['area_statistics']['total_intervention_area_hectares'] > 0:
        stats['financial']['average_cost_per_hectare'] = (
            stats['financial']['total_cost_inr'] / 
            stats['area_statistics']['total_intervention_area_hectares']
        )
    
    # Environmental benefits (aggregate from summary_df)
    if not summary_df.empty:
        benefit_cols = [col for col in summary_df.columns if col.startswith('benefit_')]
        for col in benefit_cols:
            benefit_name = col.replace('benefit_', '')
            stats['environmental_benefits'][benefit_name] = summary_df[col].sum()
    
    # Interventions by type
    for _, row in summary_df.iterrows():
        stats['interventions_by_type'][row['NbS_Type']] = {
            'num_cells': row['Num_Cells'],
            'area_hectares': row['Total_Area_hectares'],
            'cost_crores': row.get('Total_Cost_Crores', 0),
            'percentage_of_total': (row['Total_Area_hectares'] / 
                                   stats['area_statistics']['total_intervention_area_hectares'] * 100)
            if stats['area_statistics']['total_intervention_area_hectares'] > 0 else 0
        }
    
    # Morphology statistics
    if 'density' in nbs_gdf.columns:
        stats['morphology'] = {
            'mean_density': float(nbs_gdf['density'].mean()),
            'mean_roughness': float(nbs_gdf['roughness'].mean()) if 'roughness' in nbs_gdf.columns else 0,
            'mean_height': float(nbs_gdf['avg_height'].mean()) if 'avg_height' in nbs_gdf.columns else 0,
            'mean_svf': float(nbs_gdf['svf'].mean()) if 'svf' in nbs_gdf.columns else 0
        }
    
    # Building statistics
    if buildings_gdf is not None and not buildings_gdf.empty:
        stats['buildings'] = {
            'total_buildings': len(buildings_gdf),
            'total_footprint_sqm': float(buildings_gdf.geometry.area.sum())
        }
    
    logger.info("Summary statistics generated successfully.")
    
    return stats


def generate_markdown_report(stats, summary_df, output_path=None):
    """
    Generate a comprehensive Markdown report
    
    Args:
        stats: Summary statistics dictionary
        summary_df: Intervention summary DataFrame
        output_path: Path to save the report
    
    Returns:
        str: Markdown report content
    """
    logger.info("Generating Markdown report...")
    
    md_content = []
    
    # Title
    date = datetime.now().strftime('%Y-%m-%d')
    title = REPORT_TITLE_TEMPLATE.format(city=CITY_NAME, date=date)
    md_content.append(f"# {title}\n")
    md_content.append(f"## {REPORT_SUBTITLE}\n")
    md_content.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    md_content.append("---\n")
    
    # Executive Summary
    md_content.append("## Executive Summary\n")
    meta = stats['analysis_metadata']
    area_stats = stats['area_statistics']
    financial = stats['financial']
    
    md_content.append(f"This report presents a comprehensive Nature-based Solutions (NbS) analysis for **{CITY_NAME}**, ")
    md_content.append(f"covering an area of **{area_stats['total_study_area_hectares']:.2f} hectares**. ")
    md_content.append(f"The analysis identified **{meta['cells_with_interventions']}** grid cells requiring NbS interventions, ")
    md_content.append(f"covering **{area_stats['total_intervention_area_hectares']:.2f} hectares** ")
    md_content.append(f"({meta['intervention_coverage_pct']:.1f}% of the study area).\n\n")
    
    md_content.append(f"The total estimated implementation cost is **₹{financial['total_cost_crores']:.2f} Crores** ")
    md_content.append(f"(₹{financial['total_cost_inr']/1e6:.2f} Million), ")
    md_content.append(f"with an average cost of **₹{financial['average_cost_per_hectare']/100000:.2f} Lakhs per hectare**.\n")
    md_content.append("---\n")
    
    # Interventions by Type
    md_content.append("## Proposed NbS Interventions\n")
    md_content.append("### Summary by Type\n")
    
    if not summary_df.empty:
        md_content.append("| NbS Type | Grid Cells | Area (ha) | Cost (Cr) | % of Total |\n")
        md_content.append("|----------|-----------|-----------|-----------|------------|\n")
        
        for nbs_type, data in stats['interventions_by_type'].items():
            md_content.append(f"| {nbs_type} | {data['num_cells']} | "
                            f"{data['area_hectares']:.2f} | "
                            f"{data['cost_crores']:.2f} | "
                            f"{data['percentage_of_total']:.1f}% |\n")
        
        md_content.append("\n")
        
        # Detailed descriptions
        md_content.append("### Intervention Details\n")
        for nbs_type, data in stats['interventions_by_type'].items():
            md_content.append(f"#### {nbs_type}\n")
            md_content.append(f"- **Area**: {data['area_hectares']:.2f} hectares\n")
            md_content.append(f"- **Number of sites**: {data['num_cells']} grid cells\n")
            md_content.append(f"- **Estimated cost**: ₹{data['cost_crores']:.2f} Crores\n")
            md_content.append(f"- **Percentage of total**: {data['percentage_of_total']:.1f}%\n\n")
    
    md_content.append("---\n")
    
    # Environmental Benefits
    md_content.append("## Environmental Benefits\n")
    
    if stats['environmental_benefits']:
        benefits = stats['environmental_benefits']
        
        md_content.append("### Climate & Air Quality\n")
        if 'carbon_sequestration_kg_yr' in benefits:
            carbon_tonnes = benefits['carbon_sequestration_kg_yr'] / 1000
            md_content.append(f"- **Carbon Sequestration**: {carbon_tonnes:.2f} tonnes CO₂/year\n")
        
        if 'pm25_removal_kg_yr' in benefits:
            md_content.append(f"- **PM2.5 Removal**: {benefits['pm25_removal_kg_yr']:.2f} kg/year\n")
        
        if 'cooling_effect_celsius' in benefits:
            md_content.append(f"- **Urban Cooling**: Up to {benefits['cooling_effect_celsius']:.1f}°C temperature reduction\n")
        
        md_content.append("\n### Water Management\n")
        if 'runoff_reduction_percent' in benefits:
            md_content.append(f"- **Stormwater Management**: {benefits['runoff_reduction_percent']:.1f}% runoff reduction potential\n")
        
        md_content.append("\n### Biodiversity\n")
        if 'estimated_trees' in benefits:
            md_content.append(f"- **Total Trees**: {int(benefits['estimated_trees'])} trees to be planted\n")
        
        md_content.append("\n### Multi-benefit Scores (0-5 scale)\n")
        for category in ['climate_adaptation', 'biodiversity', 'air_quality', 
                        'water_management', 'social_wellbeing', 'economic_value']:
            if category in benefits:
                score = benefits[category]
                md_content.append(f"- **{category.replace('_', ' ').title()}**: {score:.1f}/5\n")
    
    md_content.append("\n---\n")
    
    # Urban Morphology
    if 'morphology' in stats:
        md_content.append("## Urban Morphology Analysis\n")
        morph = stats['morphology']
        
        md_content.append("Key morphological metrics for the study area:\n\n")
        md_content.append(f"- **Mean Building Density**: {morph['mean_density']:.3f} (plan area fraction)\n")
        md_content.append(f"- **Mean Roughness Length (z₀)**: {morph['mean_roughness']:.3f} m\n")
        md_content.append(f"- **Mean Building Height**: {morph['mean_height']:.1f} m\n")
        md_content.append(f"- **Mean Sky View Factor**: {morph['mean_svf']:.3f}\n\n")
        
        md_content.append("**Interpretation:**\n")
        md_content.append(f"- {'High' if morph['mean_density'] > 0.5 else 'Moderate' if morph['mean_density'] > 0.3 else 'Low'} building density\n")
        md_content.append(f"- {'High' if morph['mean_roughness'] > 1.0 else 'Moderate' if morph['mean_roughness'] > 0.5 else 'Low'} airflow resistance\n")
        md_content.append(f"- {'Poor' if morph['mean_svf'] < 0.4 else 'Moderate' if morph['mean_svf'] < 0.7 else 'Good'} sky visibility\n")
        
        md_content.append("\n---\n")
    
    # G20 NbS Principles
    md_content.append("## Alignment with G20 NbS Principles\n")
    md_content.append("This analysis is guided by the 8 principles from the G20 Working Paper:\n\n")
    for num, principle in G20_NBS_PRINCIPLES.items():
        md_content.append(f"{num}. **{principle}**\n")
    
    md_content.append("\n---\n")
    
    # Implementation Recommendations
    md_content.append("## Implementation Recommendations\n")
    md_content.append("### Phased Approach\n")
    md_content.append("1. **Phase 1 (Year 1-2)**: High-priority interventions in dense urban cores\n")
    md_content.append("   - Green roofs on public buildings\n")
    md_content.append("   - Ventilation corridor clearance\n")
    md_content.append("2. **Phase 2 (Year 3-4)**: Medium-priority interventions\n")
    md_content.append("   - Urban forest development\n")
    md_content.append("   - Rain garden installations\n")
    md_content.append("3. **Phase 3 (Year 5+)**: Long-term sustainability\n")
    md_content.append("   - Permeable pavement retrofits\n")
    md_content.append("   - Wetland restoration projects\n\n")
    
    md_content.append("### Key Success Factors\n")
    md_content.append("- **Multi-stakeholder engagement**: Involve local communities, NGOs, and private sector\n")
    md_content.append("- **Adaptive management**: Monitor and adjust interventions based on performance\n")
    md_content.append("- **Capacity building**: Train municipal staff in NbS planning and maintenance\n")
    md_content.append("- **Financing mechanisms**: Explore green bonds, CSR funding, and international climate finance\n")
    md_content.append("- **Policy integration**: Mainstream NbS in city master plans and building codes\n")
    
    md_content.append("\n---\n")
    
    # Methodology
    md_content.append("## Methodology\n")
    md_content.append("### Data Sources\n")
    md_content.append("- **Building Footprints**: OpenStreetMap (live data)\n")
    md_content.append("- **Climate Data**: Open-Meteo historical weather API\n")
    md_content.append("- **Green/Blue Spaces**: OpenStreetMap land use data\n\n")
    
    md_content.append("### Analysis Steps\n")
    md_content.append("1. Fetched real-time infrastructure data from OpenStreetMap\n")
    md_content.append("2. Created 150m × 150m analysis grid over study area\n")
    md_content.append("3. Calculated urban morphology metrics (density, roughness, SVF)\n")
    md_content.append("4. Applied G20 NbS decision framework\n")
    md_content.append("5. Assessed multi-benefits and implementation costs\n")
    md_content.append("6. Generated recommendations and visualizations\n\n")
    
    md_content.append("### References\n")
    md_content.append("- UNEP (2021). *Smart, Sustainable and Resilient Cities: The Power of Nature-based Solutions*. G20 Working Paper.\n")
    md_content.append("- IUCN (2020). *Global Standard for Nature-based Solutions*.\n")
    md_content.append("- Macdonald et al. (1998). *Surface roughness estimation*. Atmospheric Environment.\n")
    
    md_content.append("\n---\n")
    md_content.append("*This report was generated using the Hyderabad NbS Planner automated analysis tool.*\n")
    
    report_content = ''.join(md_content)
    
    # Save to file if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info(f"Markdown report saved to: {output_path}")
    
    return report_content


def export_to_csv(summary_df, nbs_gdf, output_dir):
    """
    Export data to CSV files
    
    Args:
        summary_df: Summary statistics DataFrame
        nbs_gdf: Full NbS GeoDataFrame
        output_dir: Output directory
    """
    logger.info("Exporting data to CSV...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export summary
    summary_path = output_dir / 'nbs_summary.csv'
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"Summary exported to: {summary_path}")
    
    # Export full grid data (without geometry)
    grid_data = nbs_gdf.drop(columns=['geometry', 'color'], errors='ignore')
    grid_path = output_dir / 'nbs_grid_data.csv'
    grid_data.to_csv(grid_path, index=False)
    logger.info(f"Grid data exported to: {grid_path}")
    
    return summary_path, grid_path


def export_to_json(stats, output_path):
    """
    Export statistics to JSON
    
    Args:
        stats: Summary statistics dictionary
        output_path: Output file path
    """
    import numpy as np
    
    logger.info("Exporting statistics to JSON...")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Custom JSON encoder to handle numpy types
    def convert_types(obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(item) for item in obj]
        else:
            return obj
    
    # Convert all numpy types
    stats_converted = convert_types(stats)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stats_converted, f, indent=2, ensure_ascii=False)
    
    logger.info(f"JSON statistics exported to: {output_path}")
    
    return output_path


def generate_full_report(nbs_gdf, summary_df, buildings_gdf, streets_gdf, 
                         green_blue_gdf, wind_dir, output_dir=None):
    """
    Generate complete report with all outputs
    
    Args:
        nbs_gdf: GeoDataFrame with NbS recommendations
        summary_df: Summary statistics DataFrame
        buildings_gdf: Building footprints
        streets_gdf: Street network
        green_blue_gdf: Green/blue spaces
        wind_dir: Prevailing wind direction
        output_dir: Output directory (defaults to REPORTS_DIR)
    
    Returns:
        dict: Paths to all generated files
    """
    logger.info("Generating full report package...")
    
    if output_dir is None:
        output_dir = Path(REPORTS_DIR)
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. Summary statistics
    stats = generate_summary_statistics(nbs_gdf, summary_df, buildings_gdf)
    
    # 2. Markdown report
    md_path = output_dir / f'nbs_report_{timestamp}.md'
    generate_markdown_report(stats, summary_df, md_path)
    
    # 3. JSON export
    json_path = output_dir / f'nbs_statistics_{timestamp}.json'
    export_to_json(stats, json_path)
    
    # 4. CSV exports
    csv_dir = output_dir / 'csv'
    summary_csv, grid_csv = export_to_csv(summary_df, nbs_gdf, csv_dir)
    
    # 5. GeoJSON export (for GIS integration)
    geojson_path = output_dir / f'nbs_interventions_{timestamp}.geojson'
    nbs_export = nbs_gdf.copy()
    nbs_export = nbs_export.to_crs('EPSG:4326')  # WGS84 for GeoJSON
    
    # Select relevant columns for export
    export_cols = ['grid_id', 'Proposed_NbS', 'density', 'roughness', 'avg_height', 
                   'svf', 'priority', 'geometry']
    export_cols = [col for col in export_cols if col in nbs_export.columns]
    
    nbs_export[export_cols].to_file(geojson_path, driver='GeoJSON')
    logger.info(f"GeoJSON exported to: {geojson_path}")
    
    report_files = {
        'markdown_report': str(md_path),
        'json_statistics': str(json_path),
        'summary_csv': str(summary_csv),
        'grid_csv': str(grid_csv),
        'geojson': str(geojson_path),
        'timestamp': timestamp
    }
    
    logger.info(f"Full report package generated in: {output_dir}")
    
    return report_files, stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Reporting module loaded successfully.")

