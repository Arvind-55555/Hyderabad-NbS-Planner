"""
Urban Morphology Analysis Module
Calculates urban morphology metrics including:
- Plan Area Density (λp)
- Roughness Length (z0)
- Sky View Factor (SVF)
- Building Height Distribution
"""

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box
import logging

from .config import (
    GRID_SIZE_METERS, CRS_UTM,
    DEFAULT_BUILDING_HEIGHT, FLOOR_HEIGHT,
    DENSITY_VERY_HIGH, DENSITY_HIGH, DENSITY_MEDIUM, DENSITY_LOW,
    ROUGHNESS_VERY_HIGH, ROUGHNESS_HIGH, ROUGHNESS_MEDIUM, ROUGHNESS_LOW
)

logger = logging.getLogger(__name__)


def filter_polygon_geometries(gdf):
    """
    Filter GeoDataFrame to only include Polygon and MultiPolygon geometries.
    This is necessary because OSM data can contain mixed geometry types.
    
    Args:
        gdf (GeoDataFrame): Input GeoDataFrame with potentially mixed geometries
    
    Returns:
        GeoDataFrame: Filtered GeoDataFrame with only polygon geometries
    """
    from shapely.geometry import Polygon, MultiPolygon
    
    if gdf.empty:
        return gdf
    
    # Filter to only Polygon and MultiPolygon
    mask = gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])
    filtered = gdf[mask].copy()
    
    if len(filtered) < len(gdf):
        removed = len(gdf) - len(filtered)
        logger.warning(f"Removed {removed} non-polygon geometries from dataset")
    
    return filtered


def create_analysis_grid(buildings, grid_size=GRID_SIZE_METERS):
    """
    Creates a regular grid over the study area for localized analysis.
    
    Args:
        buildings (GeoDataFrame): Building footprints
        grid_size (float): Size of grid cells in meters
    
    Returns:
        GeoDataFrame: Grid cells with unique IDs
    """
    logger.info(f"Creating analysis grid with {grid_size}m cells...")
    
    if buildings.empty:
        logger.error("Cannot create grid: buildings GeoDataFrame is empty")
        return gpd.GeoDataFrame(crs=CRS_UTM)
    
    minx, miny, maxx, maxy = buildings.total_bounds
    
    # Create grid
    cols = list(np.arange(minx, maxx, grid_size))
    rows = list(np.arange(miny, maxy, grid_size))
    
    polygons = []
    for x in cols:
        for y in rows:
            polygons.append(box(x, y, x + grid_size, y + grid_size))
    
    grid = gpd.GeoDataFrame({'geometry': polygons}, crs=buildings.crs)
    grid['grid_id'] = range(len(grid))
    grid['cell_area'] = grid_size * grid_size  # m²
    
    logger.info(f"Created grid with {len(grid)} cells.")
    
    return grid


def estimate_building_heights(buildings):
    """
    Estimate building heights from OSM tags or use defaults.
    
    Priority:
    1. 'height' tag (if available)
    2. 'building:levels' tag * FLOOR_HEIGHT
    3. DEFAULT_BUILDING_HEIGHT
    
    Args:
        buildings (GeoDataFrame): Building footprints
    
    Returns:
        Series: Estimated heights in meters
    """
    heights = pd.Series([DEFAULT_BUILDING_HEIGHT] * len(buildings), index=buildings.index)
    
    # Method 1: Direct height tag
    if 'height' in buildings.columns:
        height_vals = pd.to_numeric(buildings['height'], errors='coerce')
        heights = heights.where(height_vals.isna(), height_vals)
    
    # Method 2: Building levels
    if 'building:levels' in buildings.columns:
        levels = pd.to_numeric(buildings['building:levels'], errors='coerce')
        estimated_from_levels = levels * FLOOR_HEIGHT
        heights = heights.where(estimated_from_levels.isna(), estimated_from_levels)
    
    # Method 3: Building type heuristics
    if 'building' in buildings.columns:
        # Assign typical heights based on building type
        type_heights = {
            'apartments': 18.0,  # ~6 floors
            'commercial': 15.0,  # ~5 floors
            'retail': 9.0,  # ~3 floors
            'industrial': 12.0,  # ~4 floors
            'house': 6.0,  # ~2 floors
            'residential': 9.0,  # ~3 floors
            'detached': 6.0,  # ~2 floors
        }
        
        for btype, height in type_heights.items():
            mask = buildings['building'] == btype
            heights[mask] = height
    
    return heights


def calculate_plan_area_density(grid, buildings):
    """
    Calculate Plan Area Density (λp) for each grid cell.
    λp = (Built-up Area) / (Total Cell Area)
    
    Args:
        grid (GeoDataFrame): Analysis grid
        buildings (GeoDataFrame): Building footprints
    
    Returns:
        Series: Density values for each grid cell
    """
    logger.info("Calculating plan area density...")
    
    # Filter to only polygon geometries (OSM can have mixed types)
    buildings_clean = filter_polygon_geometries(buildings)
    
    if buildings_clean.empty:
        logger.warning("No polygon geometries found in buildings. Returning zero density.")
        return pd.Series({grid_id: 0.0 for grid_id in grid['grid_id']})
    
    # Spatial join to find buildings in each cell
    joined = gpd.sjoin(buildings_clean, grid, how='inner', predicate='intersects')
    
    densities = {}
    
    for grid_id in grid['grid_id']:
        cell_buildings = joined[joined['grid_id'] == grid_id]
        cell_geom = grid[grid['grid_id'] == grid_id].geometry.iloc[0]
        cell_area = cell_geom.area
        
        if len(cell_buildings) == 0:
            densities[grid_id] = 0.0
        else:
            # Calculate intersection area (more accurate than raw building area)
            try:
                intersection = gpd.overlay(
                    cell_buildings,
                    gpd.GeoDataFrame(geometry=[cell_geom], crs=grid.crs),
                    how='intersection'
                )
                
                built_area = intersection.geometry.area.sum()
                densities[grid_id] = min(built_area / cell_area, 1.0)  # Cap at 1.0
            except Exception as e:
                logger.warning(f"Error calculating density for grid {grid_id}: {e}. Using fallback method.")
                # Fallback: use simple area sum
                built_area = cell_buildings.geometry.area.sum()
                densities[grid_id] = min(built_area / cell_area, 1.0)
    
    density_series = pd.Series(densities)
    logger.info(f"Density calculation complete. Mean: {density_series.mean():.3f}")
    
    return density_series


def calculate_roughness_length(grid, buildings):
    """
    Calculate Roughness Length (z0) for each grid cell.
    
    Uses simplified Macdonald et al. (1998) formula:
    z0 ≈ 0.5 * mean_height * density
    
    More sophisticated methods consider:
    - Building spacing
    - Frontal area index
    - Height variability
    
    Args:
        grid (GeoDataFrame): Analysis grid
        buildings (GeoDataFrame): Building footprints with heights
    
    Returns:
        tuple: (roughness_series, height_series)
    """
    logger.info("Calculating roughness length...")
    
    # Filter to only polygon geometries
    buildings_clean = filter_polygon_geometries(buildings)
    
    if buildings_clean.empty:
        logger.warning("No polygon geometries found. Returning zero roughness.")
        zero_series = pd.Series({grid_id: 0.0 for grid_id in grid['grid_id']})
        return zero_series, zero_series
    
    # Ensure buildings have height estimates
    buildings_clean['height_m'] = estimate_building_heights(buildings_clean)
    
    # Spatial join
    joined = gpd.sjoin(buildings_clean, grid, how='inner', predicate='intersects')
    
    roughness_values = {}
    height_values = {}
    
    for grid_id in grid['grid_id']:
        cell_buildings = joined[joined['grid_id'] == grid_id]
        cell_geom = grid[grid['grid_id'] == grid_id].geometry.iloc[0]
        cell_area = cell_geom.area
        
        if len(cell_buildings) == 0:
            roughness_values[grid_id] = 0.0
            height_values[grid_id] = 0.0
        else:
            # Calculate density for this cell
            try:
                intersection = gpd.overlay(
                    cell_buildings,
                    gpd.GeoDataFrame(geometry=[cell_geom], crs=grid.crs),
                    how='intersection'
                )
                
                built_area = intersection.geometry.area.sum()
                density = min(built_area / cell_area, 1.0)
            except Exception as e:
                logger.debug(f"Overlay failed for grid {grid_id}, using fallback: {e}")
                # Fallback: use simple area sum
                built_area = cell_buildings.geometry.area.sum()
                density = min(built_area / cell_area, 1.0)
            
            # Calculate mean height
            mean_height = cell_buildings['height_m'].mean()
            
            # Roughness formula (simplified)
            roughness = 0.5 * mean_height * density
            
            roughness_values[grid_id] = roughness
            height_values[grid_id] = mean_height
    
    roughness_series = pd.Series(roughness_values)
    height_series = pd.Series(height_values)
    
    logger.info(f"Roughness calculation complete. Mean: {roughness_series.mean():.3f}m")
    
    return roughness_series, height_series


def calculate_sky_view_factor_simple(grid, buildings):
    """
    Simplified Sky View Factor (SVF) calculation.
    
    SVF ranges from 0 (completely obstructed) to 1 (open sky).
    
    This simplified version uses:
    SVF ≈ 1 - (building_coverage * height_factor)
    
    For accurate SVF, ray-tracing or fisheye analysis is needed.
    
    Args:
        grid (GeoDataFrame): Analysis grid
        buildings (GeoDataFrame): Building footprints with heights
    
    Returns:
        Series: SVF values for each grid cell
    """
    logger.info("Calculating simplified Sky View Factor...")
    
    # Filter to only polygon geometries
    buildings_clean = filter_polygon_geometries(buildings)
    
    if buildings_clean.empty:
        logger.warning("No polygon geometries found. Returning SVF = 1.0 (open sky).")
        return pd.Series({grid_id: 1.0 for grid_id in grid['grid_id']})
    
    buildings_clean['height_m'] = estimate_building_heights(buildings_clean)
    
    joined = gpd.sjoin(buildings_clean, grid, how='inner', predicate='intersects')
    
    svf_values = {}
    
    for grid_id in grid['grid_id']:
        cell_buildings = joined[joined['grid_id'] == grid_id]
        cell_geom = grid[grid['grid_id'] == grid_id].geometry.iloc[0]
        cell_area = cell_geom.area
        
        if len(cell_buildings) == 0:
            svf_values[grid_id] = 1.0  # Completely open
        else:
            # Calculate coverage and height
            try:
                intersection = gpd.overlay(
                    cell_buildings,
                    gpd.GeoDataFrame(geometry=[cell_geom], crs=grid.crs),
                    how='intersection'
                )
                
                built_area = intersection.geometry.area.sum()
                coverage = min(built_area / cell_area, 1.0)
            except Exception as e:
                logger.debug(f"Overlay failed for SVF calculation, using fallback: {e}")
                # Fallback: use simple area sum
                built_area = cell_buildings.geometry.area.sum()
                coverage = min(built_area / cell_area, 1.0)
            
            mean_height = cell_buildings['height_m'].mean()
            
            # Height factor (normalized by typical building height)
            height_factor = min(mean_height / 20.0, 1.0)  # 20m = typical reference
            
            # SVF approximation
            svf = 1.0 - (coverage * height_factor)
            svf_values[grid_id] = max(svf, 0.0)  # Ensure non-negative
    
    svf_series = pd.Series(svf_values)
    logger.info(f"SVF calculation complete. Mean: {svf_series.mean():.3f}")
    
    return svf_series


def classify_density(density):
    """
    Classify density into categories
    
    Args:
        density (float): Plan area density (0-1)
    
    Returns:
        str: Density classification
    """
    if density >= DENSITY_VERY_HIGH:
        return 'Very High'
    elif density >= DENSITY_HIGH:
        return 'High'
    elif density >= DENSITY_MEDIUM:
        return 'Medium'
    elif density >= DENSITY_LOW:
        return 'Low'
    else:
        return 'Very Low'


def classify_roughness(roughness):
    """
    Classify roughness into categories
    
    Args:
        roughness (float): Roughness length in meters
    
    Returns:
        str: Roughness classification
    """
    if roughness >= ROUGHNESS_VERY_HIGH:
        return 'Very High'
    elif roughness >= ROUGHNESS_HIGH:
        return 'High'
    elif roughness >= ROUGHNESS_MEDIUM:
        return 'Medium'
    elif roughness >= ROUGHNESS_LOW:
        return 'Low'
    else:
        return 'Very Low'


def calculate_roughness_and_density(grid, buildings):
    """
    Main function to calculate all morphology metrics for each grid cell.
    
    Args:
        grid (GeoDataFrame): Analysis grid
        buildings (GeoDataFrame): Building footprints
    
    Returns:
        GeoDataFrame: Grid with morphology metrics added
    """
    logger.info("Computing urban morphology metrics...")
    
    if buildings.empty:
        logger.warning("No buildings data. Returning empty grid.")
        grid['density'] = 0.0
        grid['roughness'] = 0.0
        grid['avg_height'] = 0.0
        grid['svf'] = 1.0
        grid['density_class'] = 'Very Low'
        grid['roughness_class'] = 'Very Low'
        return grid
    
    # Calculate metrics
    density = calculate_plan_area_density(grid, buildings)
    roughness, avg_height = calculate_roughness_length(grid, buildings)
    svf = calculate_sky_view_factor_simple(grid, buildings)
    
    # Merge into grid
    grid['density'] = grid['grid_id'].map(density).fillna(0.0)
    grid['roughness'] = grid['grid_id'].map(roughness).fillna(0.0)
    grid['avg_height'] = grid['grid_id'].map(avg_height).fillna(0.0)
    grid['svf'] = grid['grid_id'].map(svf).fillna(1.0)
    
    # Classifications
    grid['density_class'] = grid['density'].apply(classify_density)
    grid['roughness_class'] = grid['roughness'].apply(classify_roughness)
    
    logger.info("Morphology analysis complete.")
    logger.info(f"  Mean Density: {grid['density'].mean():.3f}")
    logger.info(f"  Mean Roughness: {grid['roughness'].mean():.3f}m")
    logger.info(f"  Mean Height: {grid['avg_height'].mean():.3f}m")
    logger.info(f"  Mean SVF: {grid['svf'].mean():.3f}")
    
    return grid


def calculate_building_statistics(buildings):
    """
    Calculate comprehensive building statistics
    
    Args:
        buildings (GeoDataFrame): Building footprints
    
    Returns:
        dict: Building statistics
    """
    if buildings.empty:
        return {
            'total_buildings': 0,
            'total_footprint_area': 0,
            'mean_footprint_area': 0,
            'mean_height': 0
        }
    
    # Filter to only polygon geometries
    buildings_clean = filter_polygon_geometries(buildings)
    
    if buildings_clean.empty:
        logger.warning("No polygon geometries found in buildings.")
        return {
            'total_buildings': 0,
            'total_footprint_area': 0,
            'mean_footprint_area': 0,
            'mean_height': 0
        }
    
    buildings_clean['height_m'] = estimate_building_heights(buildings_clean)
    buildings_clean['footprint_area'] = buildings_clean.geometry.area
    
    stats = {
        'total_buildings': len(buildings_clean),
        'total_footprint_area': buildings_clean['footprint_area'].sum(),
        'mean_footprint_area': buildings_clean['footprint_area'].mean(),
        'median_footprint_area': buildings_clean['footprint_area'].median(),
        'mean_height': buildings_clean['height_m'].mean(),
        'median_height': buildings_clean['height_m'].median(),
        'max_height': buildings_clean['height_m'].max()
    }
    
    logger.info(f"Building statistics: {stats['total_buildings']} buildings, "
                f"mean height {stats['mean_height']:.1f}m")
    
    return stats


if __name__ == "__main__":
    # Test module
    logging.basicConfig(level=logging.INFO)
    
    print("Morphology module loaded successfully.")
    print("Use in conjunction with data_loader for full analysis.")

