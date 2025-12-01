"""
Nature-based Solutions (NbS) Decision Engine
Implements the G20 NbS Working Paper framework
Assigns appropriate interventions based on urban morphology and context
"""

import numpy as np
import pandas as pd
import logging

from .config import (
    DENSITY_VERY_HIGH, DENSITY_HIGH, DENSITY_MEDIUM, DENSITY_LOW,
    ROUGHNESS_VERY_HIGH, ROUGHNESS_HIGH, ROUGHNESS_MEDIUM,
    SVF_OPEN, SVF_MODERATE, SVF_ENCLOSED,
    WIND_ALIGNMENT_TOLERANCE,
    G20_NBS_PRINCIPLES,
    MULTI_BENEFIT_CATEGORIES,
    NBS_TYPES
)

logger = logging.getLogger(__name__)


def assign_nbs_intervention(row, wind_dir, green_blue_gdf=None):
    """
    Assigns a Nature-based Solution based on morphology, wind alignment, and context.
    
    Decision logic based on G20 NbS Working Paper principles:
    1. Dense urban cores → Green Roofs (limited ground space)
    2. Medium density + high roughness → Ventilation Corridors
    3. Medium density + good flow → Urban Forests
    4. Low density → Permeable Pavement
    5. Near water → Wetland Restoration
    6. Low-lying areas → Rain Gardens / Sponge City elements
    
    Args:
        row: Grid cell row with morphology metrics
        wind_dir: Prevailing wind direction (degrees)
        green_blue_gdf: Existing green/blue spaces (optional)
    
    Returns:
        str: Recommended NbS intervention type
    """
    density = row['density']
    roughness = row['roughness']
    svf = row.get('svf', 0.5)
    avg_height = row.get('avg_height', 0)
    
    # Check if already green space
    if density < 0.05:
        # Very low density - might already be green space or water
        return "None"
    
    # Priority 1: Very High Density Areas (>70% built)
    # Solution: Green Roofs (no ground space available)
    if density >= DENSITY_VERY_HIGH:
        return "Green Roof"
    
    # Priority 2: High Density with High Roughness (60-70% built, rough)
    # Problem: Heat island + poor ventilation
    if density >= DENSITY_HIGH and roughness >= ROUGHNESS_HIGH:
        # Check if this could be a ventilation corridor
        # (Simplified: we don't check actual alignment here, but could be enhanced)
        return "Green Roof"  # Still too dense for corridors
    
    # Priority 3: Medium-High Density with High Roughness
    # Solution: Ventilation Corridor (clear obstacles, align trees)
    if (DENSITY_MEDIUM < density < DENSITY_HIGH) and (roughness >= ROUGHNESS_MEDIUM):
        return "Ventilation Corridor"
    
    # Priority 4: Medium Density with Lower Roughness
    # Solution: Urban Forests (street trees without blocking flow)
    if (DENSITY_MEDIUM < density < DENSITY_HIGH):
        # Good flow potential, add trees for shade and air quality
        return "Urban Forest"
    
    # Priority 5: Low-Medium Density with Low SVF (enclosed spaces)
    # Solution: Urban Forests for shade and cooling
    if (DENSITY_LOW < density <= DENSITY_MEDIUM) and (svf < SVF_MODERATE):
        return "Urban Forest"
    
    # Priority 6: Low Density Areas
    # Solution: Permeable Pavement (parking lots, roads)
    if density <= DENSITY_MEDIUM:
        # Check if it's likely paved (can add heuristics)
        if roughness < ROUGHNESS_MEDIUM:
            return "Permeable Pavement"
        else:
            # Some buildings present
            return "Rain Garden"
    
    # Default: No specific intervention
    return "None"


def assess_multi_benefits(nbs_type, area_sqm, density, roughness):
    """
    Assess multiple benefits of an NbS intervention.
    
    Based on G20 NbS Working Paper multi-benefit framework:
    - Climate Adaptation
    - Biodiversity
    - Air Quality
    - Water Management
    - Social Well-being
    - Economic Value
    
    Args:
        nbs_type (str): Type of NbS intervention
        area_sqm (float): Area of intervention in square meters
        density (float): Local building density
        roughness (float): Local roughness length
    
    Returns:
        dict: Multi-benefit scores and estimates
    """
    from .config import (
        COOLING_GREEN_ROOF, COOLING_URBAN_FOREST, COOLING_PAVEMENT,
        PM25_REMOVAL_TREE, PM25_REMOVAL_GREEN_ROOF,
        CARBON_SEQUESTRATION_TREE, CARBON_SEQUESTRATION_GREEN_ROOF,
        RUNOFF_REDUCTION_GREEN_ROOF, RUNOFF_REDUCTION_PERMEABLE,
        RUNOFF_REDUCTION_RAIN_GARDEN,
        TREES_PER_HECTARE
    )
    
    benefits = {
        'climate_adaptation': 0,  # Score 0-5
        'biodiversity': 0,
        'air_quality': 0,
        'water_management': 0,
        'social_wellbeing': 0,
        'economic_value': 0,
        'cooling_effect_celsius': 0,
        'pm25_removal_kg_yr': 0,
        'carbon_sequestration_kg_yr': 0,
        'runoff_reduction_percent': 0,
        'estimated_trees': 0
    }
    
    area_hectares = area_sqm / 10000.0
    
    if nbs_type == "Green Roof":
        benefits['climate_adaptation'] = 5  # Excellent for heat reduction
        benefits['biodiversity'] = 3  # Moderate
        benefits['air_quality'] = 3
        benefits['water_management'] = 5  # Excellent stormwater retention
        benefits['social_wellbeing'] = 2
        benefits['economic_value'] = 4
        benefits['cooling_effect_celsius'] = COOLING_GREEN_ROOF
        benefits['pm25_removal_kg_yr'] = area_sqm * PM25_REMOVAL_GREEN_ROOF / 1000
        benefits['carbon_sequestration_kg_yr'] = area_sqm * CARBON_SEQUESTRATION_GREEN_ROOF
        benefits['runoff_reduction_percent'] = RUNOFF_REDUCTION_GREEN_ROOF * 100
    
    elif nbs_type == "Urban Forest":
        estimated_trees = int(area_hectares * TREES_PER_HECTARE)
        benefits['climate_adaptation'] = 4
        benefits['biodiversity'] = 5  # Excellent for wildlife
        benefits['air_quality'] = 5  # Excellent air purification
        benefits['water_management'] = 3
        benefits['social_wellbeing'] = 5  # Recreation, aesthetics
        benefits['economic_value'] = 4
        benefits['cooling_effect_celsius'] = COOLING_URBAN_FOREST
        benefits['pm25_removal_kg_yr'] = estimated_trees * PM25_REMOVAL_TREE / 1000
        benefits['carbon_sequestration_kg_yr'] = estimated_trees * CARBON_SEQUESTRATION_TREE
        benefits['runoff_reduction_percent'] = 30  # Tree canopy interception
        benefits['estimated_trees'] = estimated_trees
    
    elif nbs_type == "Ventilation Corridor":
        benefits['climate_adaptation'] = 5  # Critical for heat dissipation
        benefits['biodiversity'] = 3
        benefits['air_quality'] = 5  # Excellent for pollutant dispersion
        benefits['water_management'] = 2
        benefits['social_wellbeing'] = 4
        benefits['economic_value'] = 3
        benefits['cooling_effect_celsius'] = 2.5
        # Corridors combine trees + open space
        estimated_trees = int(area_hectares * 50)  # Lower density than urban forest
        benefits['pm25_removal_kg_yr'] = estimated_trees * PM25_REMOVAL_TREE / 1000
        benefits['carbon_sequestration_kg_yr'] = estimated_trees * CARBON_SEQUESTRATION_TREE
        benefits['estimated_trees'] = estimated_trees
    
    elif nbs_type == "Permeable Pavement":
        benefits['climate_adaptation'] = 3
        benefits['biodiversity'] = 1  # Limited
        benefits['air_quality'] = 2
        benefits['water_management'] = 5  # Excellent for groundwater recharge
        benefits['social_wellbeing'] = 2
        benefits['economic_value'] = 4
        benefits['cooling_effect_celsius'] = COOLING_PAVEMENT
        benefits['runoff_reduction_percent'] = RUNOFF_REDUCTION_PERMEABLE * 100
    
    elif nbs_type == "Wetland Restoration":
        benefits['climate_adaptation'] = 4
        benefits['biodiversity'] = 5  # Excellent habitat
        benefits['air_quality'] = 3
        benefits['water_management'] = 5  # Natural water treatment
        benefits['social_wellbeing'] = 4
        benefits['economic_value'] = 3
        benefits['cooling_effect_celsius'] = 3.0
        benefits['runoff_reduction_percent'] = 95
    
    elif nbs_type == "Rain Garden":
        benefits['climate_adaptation'] = 4
        benefits['biodiversity'] = 4
        benefits['air_quality'] = 3
        benefits['water_management'] = 5
        benefits['social_wellbeing'] = 4
        benefits['economic_value'] = 4
        benefits['cooling_effect_celsius'] = 1.5
        benefits['runoff_reduction_percent'] = RUNOFF_REDUCTION_RAIN_GARDEN * 100
    
    # Calculate overall multi-benefit score (0-100)
    benefit_scores = [
        benefits['climate_adaptation'],
        benefits['biodiversity'],
        benefits['air_quality'],
        benefits['water_management'],
        benefits['social_wellbeing'],
        benefits['economic_value']
    ]
    benefits['overall_score'] = sum(benefit_scores) / len(benefit_scores) * 20  # Scale to 100
    
    return benefits


def calculate_implementation_cost(nbs_type, area_sqm, num_trees=0):
    """
    Estimate implementation cost for NbS intervention
    
    Args:
        nbs_type (str): Type of intervention
        area_sqm (float): Area in square meters
        num_trees (int): Number of trees (for Urban Forest)
    
    Returns:
        float: Estimated cost in INR
    """
    costs = NBS_TYPES.get(nbs_type, {})
    
    if nbs_type == "Urban Forest":
        cost_per_tree = costs.get('cost_per_tree', 5000)
        return num_trees * cost_per_tree
    else:
        cost_per_sqm = costs.get('cost_per_sqm', 100)
        return area_sqm * cost_per_sqm


def run_nbs_planning(analysis_gdf, prevailing_wind, green_blue_gdf=None, 
                     calculate_benefits=True, calculate_costs=True):
    """
    Main NbS planning function. Applies decision logic to each grid cell.
    
    Args:
        analysis_gdf (GeoDataFrame): Grid with morphology metrics
        prevailing_wind (float): Prevailing wind direction in degrees
        green_blue_gdf (GeoDataFrame): Existing green/blue spaces (optional)
        calculate_benefits (bool): Whether to calculate multi-benefits
        calculate_costs (bool): Whether to calculate implementation costs
    
    Returns:
        GeoDataFrame: Grid with NbS recommendations and assessments
    """
    logger.info(f"Applying NbS decision logic (prevailing wind: {prevailing_wind}°)...")
    
    # Apply NbS assignment
    analysis_gdf['Proposed_NbS'] = analysis_gdf.apply(
        lambda row: assign_nbs_intervention(row, prevailing_wind, green_blue_gdf),
        axis=1
    )
    
    # Count interventions by type
    nbs_counts = analysis_gdf['Proposed_NbS'].value_counts()
    logger.info("NbS Interventions Assigned:")
    for nbs_type, count in nbs_counts.items():
        logger.info(f"  {nbs_type}: {count} cells")
    
    # Calculate benefits if requested
    if calculate_benefits:
        logger.info("Calculating multi-benefits for each intervention...")
        
        benefits_list = []
        for idx, row in analysis_gdf.iterrows():
            cell_area = row.get('cell_area', 22500)  # Default 150x150m
            benefits = assess_multi_benefits(
                row['Proposed_NbS'],
                cell_area,
                row['density'],
                row['roughness']
            )
            benefits_list.append(benefits)
        
        # Add benefit columns
        benefits_df = pd.DataFrame(benefits_list, index=analysis_gdf.index)
        for col in benefits_df.columns:
            analysis_gdf[f'benefit_{col}'] = benefits_df[col]
    
    # Calculate costs if requested
    if calculate_costs:
        logger.info("Calculating implementation costs...")
        
        costs = []
        for idx, row in analysis_gdf.iterrows():
            cell_area = row.get('cell_area', 22500)
            num_trees = row.get('benefit_estimated_trees', 0) if calculate_benefits else 0
            cost = calculate_implementation_cost(row['Proposed_NbS'], cell_area, num_trees)
            costs.append(cost)
        
        analysis_gdf['cost_inr'] = costs
    
    # Add priority ranking
    analysis_gdf['priority'] = analysis_gdf['Proposed_NbS'].map(
        lambda x: NBS_TYPES.get(x, {}).get('priority', 999)
    )
    
    logger.info("NbS planning complete.")
    
    return analysis_gdf


def generate_intervention_summary(nbs_gdf):
    """
    Generate summary statistics for NbS interventions
    
    Args:
        nbs_gdf (GeoDataFrame): Grid with NbS recommendations
    
    Returns:
        DataFrame: Summary statistics by intervention type
    """
    logger.info("Generating intervention summary...")
    
    summary_data = []
    
    for nbs_type in nbs_gdf['Proposed_NbS'].unique():
        if nbs_type == "None":
            continue
        
        subset = nbs_gdf[nbs_gdf['Proposed_NbS'] == nbs_type]
        
        total_area = subset.get('cell_area', pd.Series([22500] * len(subset))).sum()
        total_cost = subset['cost_inr'].sum() if 'cost_inr' in subset.columns else 0
        
        # Aggregate benefits
        benefits = {}
        for col in subset.columns:
            if col.startswith('benefit_'):
                benefit_name = col.replace('benefit_', '')
                benefits[benefit_name] = subset[col].sum()
        
        summary_data.append({
            'NbS_Type': nbs_type,
            'Num_Cells': len(subset),
            'Total_Area_sqm': total_area,
            'Total_Area_hectares': total_area / 10000,
            'Total_Cost_INR': total_cost,
            'Total_Cost_Crores': total_cost / 10000000,  # Convert to crores
            **benefits
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Sort by priority
    if not summary_df.empty and 'priority' in nbs_gdf.columns:
        # Create priority map from the NbS GeoDataFrame
        priority_map = {}
        for nbs_type in summary_df['NbS_Type'].unique():
            # Get priority from first occurrence of this NbS type
            matching_rows = nbs_gdf[nbs_gdf['Proposed_NbS'] == nbs_type]
            if not matching_rows.empty:
                priority_map[nbs_type] = matching_rows['priority'].iloc[0]
        
        summary_df['Priority'] = summary_df['NbS_Type'].map(priority_map)
        summary_df = summary_df.sort_values('Priority')
    
    logger.info(f"Summary generated for {len(summary_df)} intervention types.")
    
    return summary_df


def prioritize_interventions(nbs_gdf, budget_inr=None, population_density=None):
    """
    Prioritize interventions based on budget constraints and population benefit
    
    Args:
        nbs_gdf (GeoDataFrame): Grid with NbS recommendations
        budget_inr (float): Available budget in INR (optional)
        population_density (array): Population density per cell (optional)
    
    Returns:
        GeoDataFrame: Grid with implementation priority scores
    """
    logger.info("Prioritizing interventions...")
    
    # Base priority from NbS type
    nbs_gdf['base_priority'] = nbs_gdf['priority']
    
    # Adjust priority based on multi-benefit score
    if 'benefit_overall_score' in nbs_gdf.columns:
        # Higher benefit score = higher priority
        nbs_gdf['benefit_priority'] = nbs_gdf['benefit_overall_score'] / 100 * 10
    else:
        nbs_gdf['benefit_priority'] = 0
    
    # Adjust priority based on cost-effectiveness
    if 'cost_inr' in nbs_gdf.columns:
        # Lower cost = higher priority (inverse)
        max_cost = nbs_gdf['cost_inr'].max()
        nbs_gdf['cost_priority'] = (1 - nbs_gdf['cost_inr'] / max_cost) * 5
    else:
        nbs_gdf['cost_priority'] = 0
    
    # Adjust for population (if available)
    if population_density is not None:
        nbs_gdf['pop_priority'] = population_density / max(population_density) * 5
    else:
        nbs_gdf['pop_priority'] = 0
    
    # Calculate final priority score (higher = more urgent)
    nbs_gdf['final_priority_score'] = (
        (10 - nbs_gdf['base_priority']) +  # Lower priority number = higher urgency
        nbs_gdf['benefit_priority'] +
        nbs_gdf['cost_priority'] +
        nbs_gdf['pop_priority']
    )
    
    # Rank interventions
    nbs_gdf['implementation_rank'] = nbs_gdf['final_priority_score'].rank(
        ascending=False, method='dense'
    )
    
    # If budget constraint, mark affordable interventions
    if budget_inr is not None and 'cost_inr' in nbs_gdf.columns:
        sorted_by_priority = nbs_gdf.sort_values('final_priority_score', ascending=False)
        cumulative_cost = sorted_by_priority['cost_inr'].cumsum()
        affordable = cumulative_cost <= budget_inr
        nbs_gdf['within_budget'] = False
        nbs_gdf.loc[sorted_by_priority[affordable].index, 'within_budget'] = True
        
        total_affordable = affordable.sum()
        logger.info(f"Budget constraint: {total_affordable} interventions affordable "
                    f"out of {len(nbs_gdf[nbs_gdf['Proposed_NbS'] != 'None'])}")
    
    logger.info("Prioritization complete.")
    
    return nbs_gdf


if __name__ == "__main__":
    # Test module
    logging.basicConfig(level=logging.INFO)
    
    print("NbS Logic module loaded successfully.")
    print(f"Implementing {len(NBS_TYPES)} types of Nature-based Solutions.")
    print(f"Based on {len(G20_NBS_PRINCIPLES)} G20 NbS Principles.")

