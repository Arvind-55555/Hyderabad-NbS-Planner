"""
Data Loader Module
Handles fetching data from OpenStreetMap, weather APIs, and air quality sources
Implements caching to avoid repeated API calls
"""

import osmnx as ox
import geopandas as gpd
import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from shapely.geometry import Point
import logging

from .config import (
    CITY_LAT, CITY_LON, ANALYSIS_RADIUS_METERS,
    OPEN_METEO_URL, OPEN_METEO_PARAMS, WAQI_URL,
    CRS_WGS84, CRS_UTM, OSM_TIMEOUT,
    CACHE_ENABLED, CACHE_DIR, CACHE_EXPIRY_DAYS,
    WIND_SPEED_THRESHOLD, MS_BUILDINGS_PATH, USE_MS_BUILDINGS
)

# Setup logging
logger = logging.getLogger(__name__)


class DataCache:
    """Simple file-based cache for OSM data"""
    
    def __init__(self, cache_dir=CACHE_DIR, expiry_days=CACHE_EXPIRY_DAYS):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.expiry_days = expiry_days
    
    def _get_cache_path(self, key):
        """Generate cache file path for a given key"""
        return self.cache_dir / f"{key}.geojson"
    
    def _get_metadata_path(self, key):
        """Generate metadata file path"""
        return self.cache_dir / f"{key}_meta.json"
    
    def is_valid(self, key):
        """Check if cached data exists and is not expired"""
        meta_path = self._get_metadata_path(key)
        
        if not meta_path.exists():
            return False
        
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        
        cached_date = datetime.fromisoformat(metadata['timestamp'])
        expiry_date = cached_date + timedelta(days=self.expiry_days)
        
        return datetime.now() < expiry_date
    
    def save(self, key, gdf):
        """Save GeoDataFrame to cache"""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_metadata_path(key)
        
        # Save data
        if not gdf.empty:
            gdf.to_file(cache_path, driver='GeoJSON')
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'num_features': len(gdf)
        }
        with open(meta_path, 'w') as f:
            json.dump(metadata, f)
        
        logger.debug(f"Saved {len(gdf)} features to cache: {key}")
    
    def load(self, key):
        """Load GeoDataFrame from cache"""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        gdf = gpd.read_file(cache_path)
        logger.debug(f"Loaded {len(gdf)} features from cache: {key}")
        return gdf


def fetch_live_infrastructure(lat=CITY_LAT, lon=CITY_LON, dist=ANALYSIS_RADIUS_METERS, use_cache=CACHE_ENABLED):
    """
    Fetches real-time building footprints, street networks, and green/blue spaces from OpenStreetMap.
    
    Args:
        lat (float): Latitude of center point
        lon (float): Longitude of center point
        dist (int): Radius in meters
        use_cache (bool): Whether to use cached data
    
    Returns:
        tuple: (buildings_gdf, streets_gdf, green_blue_gdf)
    """
    logger.info(f"Fetching OSM data for coordinates ({lat}, {lon}) radius {dist}m...")
    
    cache = DataCache() if use_cache else None
    cache_key = f"osm_{lat}_{lon}_{dist}"
    
    # Initialize empty GeoDataFrames
    buildings = gpd.GeoDataFrame()
    edges = gpd.GeoDataFrame()
    green_blue = gpd.GeoDataFrame()
    
    # 1. Fetch Buildings
    logger.info("Fetching building footprints...")
    
    if USE_MS_BUILDINGS and os.path.exists(MS_BUILDINGS_PATH):
        logger.info("Loading Microsoft Building Footprints...")
        buildings = load_ms_buildings(lat, lon, dist)
    else:
        buildings_cache_key = f"{cache_key}_buildings"
        
        if use_cache and cache.is_valid(buildings_cache_key):
            logger.info("Loading buildings from cache...")
            buildings = cache.load(buildings_cache_key)
        else:
            tags = {'building': True}
            try:
                buildings = ox.features_from_point(
                    (lat, lon), 
                    tags=tags, 
                    dist=dist
                )
                
                if not buildings.empty:
                    # Convert to UTM for metric calculations
                    buildings = buildings.to_crs(CRS_UTM)
                    
                    if use_cache:
                        cache.save(buildings_cache_key, buildings)
                    
                    logger.info(f"Retrieved {len(buildings)} building footprints.")
                else:
                    logger.warning("No buildings found in the specified area.")
                    
            except Exception as e:
                logger.error(f"Error fetching buildings: {e}")
                buildings = gpd.GeoDataFrame(crs=CRS_UTM)
    
    # 2. Fetch Street Network
    logger.info("Fetching street network...")
    streets_cache_key = f"{cache_key}_streets"
    
    if use_cache and cache.is_valid(streets_cache_key):
        logger.info("Loading streets from cache...")
        edges = cache.load(streets_cache_key)
    else:
        try:
            G = ox.graph_from_point(
                (lat, lon), 
                dist=dist, 
                network_type='drive',
                simplify=True
            )
            edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
            
            if not edges.empty:
                edges = edges.to_crs(CRS_UTM)
                
                if use_cache:
                    cache.save(streets_cache_key, edges)
                
                logger.info(f"Retrieved {len(edges)} street segments.")
            else:
                logger.warning("No streets found in the specified area.")
                
        except Exception as e:
            logger.error(f"Error fetching streets: {e}")
            edges = gpd.GeoDataFrame(crs=CRS_UTM)
    
    # 3. Fetch Green/Blue Spaces
    logger.info("Fetching green and blue spaces...")
    green_cache_key = f"{cache_key}_green_blue"
    
    if use_cache and cache.is_valid(green_cache_key):
        logger.info("Loading green/blue spaces from cache...")
        green_blue = cache.load(green_cache_key)
    else:
        try:
            env_tags = {
                'leisure': ['park', 'garden', 'playground'],
                'landuse': ['grass', 'forest', 'meadow', 'recreation_ground'],
                'natural': ['water', 'wetland', 'wood', 'scrub']
            }
            green_blue = ox.features_from_point(
                (lat, lon), 
                tags=env_tags, 
                dist=dist
            )
            
            if not green_blue.empty:
                green_blue = green_blue.to_crs(CRS_UTM)
                
                if use_cache:
                    cache.save(green_cache_key, green_blue)
                
                logger.info(f"Retrieved {len(green_blue)} green/blue features.")
            else:
                logger.warning("No green/blue spaces found in the specified area.")
                
        except Exception as e:
            logger.warning(f"Green/Blue fetch warning: {e}")
            green_blue = gpd.GeoDataFrame(crs=CRS_UTM)
    
    return buildings, edges, green_blue


def load_ms_buildings(lat, lon, dist):
    """
    Load Microsoft Building Footprints for the specified area
    
    Args:
        lat, lon: Center coordinates
        dist: Radius in meters
    
    Returns:
        GeoDataFrame: Buildings within the specified area
    """
    logger.info("Loading Microsoft Building Footprints from file...")
    
    try:
        # Load full dataset
        buildings = gpd.read_file(MS_BUILDINGS_PATH)
        
        # Create buffer around center point
        from shapely.geometry import Point
        center = gpd.GeoDataFrame(
            geometry=[Point(lon, lat)],
            crs=CRS_WGS84
        ).to_crs(CRS_UTM)
        
        buffer = center.buffer(dist)
        buffer_gdf = gpd.GeoDataFrame(geometry=buffer, crs=CRS_UTM)
        
        # Spatial filter
        buildings_utm = buildings.to_crs(CRS_UTM)
        filtered = gpd.sjoin(
            buildings_utm, 
            buffer_gdf, 
            how='inner', 
            predicate='intersects'
        )
        
        logger.info(f"Loaded {len(filtered)} buildings from MS dataset.")
        return filtered
        
    except Exception as e:
        logger.error(f"Error loading MS Buildings: {e}")
        return gpd.GeoDataFrame(crs=CRS_UTM)


def fetch_prevailing_wind_direction(lat=CITY_LAT, lon=CITY_LON, 
                                     start_date="2023-01-01", 
                                     end_date="2023-12-31"):
    """
    Fetches historical wind data from Open-Meteo to determine
    the dominant wind direction for ventilation planning.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        start_date (str): Start date for historical data (YYYY-MM-DD)
        end_date (str): End date for historical data (YYYY-MM-DD)
    
    Returns:
        float: Dominant wind direction in degrees (0-360)
    """
    logger.info("Fetching historical wind data from Open-Meteo...")
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "wind_direction_10m,wind_speed_10m"
    }
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame({
            'dir': data['hourly']['wind_direction_10m'],
            'speed': data['hourly']['wind_speed_10m']
        })
        
        # Filter for significant winds (> threshold m/s)
        significant_winds = df[df['speed'] > WIND_SPEED_THRESHOLD]
        
        if len(significant_winds) == 0:
            logger.warning("No significant winds found. Using default (270° West).")
            return 270.0
        
        # Calculate most frequent direction (mode)
        # For better accuracy, could use vector averaging
        dominant_dir = float(significant_winds['dir'].mode()[0])
        
        logger.info(f"Dominant Wind Direction: {dominant_dir}°")
        logger.info(f"Based on {len(significant_winds)} significant wind observations")
        
        return dominant_dir
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}. Defaulting to 270° (West).")
        return 270.0
    except Exception as e:
        logger.error(f"Unexpected error in wind data processing: {e}. Defaulting to 270° (West).")
        return 270.0


def fetch_wind_statistics(lat=CITY_LAT, lon=CITY_LON, 
                          start_date="2023-01-01", 
                          end_date="2023-12-31"):
    """
    Fetch comprehensive wind statistics including speed and direction distributions
    
    Returns:
        dict: Wind statistics including speed, direction, and seasonal variations
    """
    logger.info("Fetching comprehensive wind statistics...")
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "wind_direction_10m,wind_speed_10m,temperature_2m"
    }
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame({
            'timestamp': pd.to_datetime(data['hourly']['time']),
            'wind_dir': data['hourly']['wind_direction_10m'],
            'wind_speed': data['hourly']['wind_speed_10m'],
            'temperature': data['hourly']['temperature_2m']
        })
        
        # Filter significant winds
        significant = df[df['wind_speed'] > WIND_SPEED_THRESHOLD]
        
        stats = {
            'mean_speed': float(significant['wind_speed'].mean()),
            'max_speed': float(significant['wind_speed'].max()),
            'dominant_direction': float(significant['wind_dir'].mode()[0]),
            'mean_temperature': float(df['temperature'].mean()),
            'max_temperature': float(df['temperature'].max()),
            'total_observations': len(df),
            'significant_wind_hours': len(significant)
        }
        
        logger.info("Wind statistics calculated successfully.")
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching wind statistics: {e}")
        return {
            'mean_speed': 3.0,
            'max_speed': 15.0,
            'dominant_direction': 270.0,
            'mean_temperature': 28.0,
            'max_temperature': 42.0
        }


def fetch_air_quality(lat=CITY_LAT, lon=CITY_LON):
    """
    Fetches current air quality index from World Air Quality Index API
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        dict: Air quality data including AQI, PM2.5, and pollutants
    """
    logger.info("Fetching air quality data from WAQI...")
    
    try:
        url = WAQI_URL.format(lat, lon)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'ok':
            aqi_data = {
                'aqi': data['data'].get('aqi', 'N/A'),
                'pm25': data['data']['iaqi'].get('pm25', {}).get('v', 'N/A'),
                'pm10': data['data']['iaqi'].get('pm10', {}).get('v', 'N/A'),
                'station': data['data'].get('city', {}).get('name', 'Unknown'),
                'timestamp': data['data'].get('time', {}).get('s', 'N/A')
            }
            logger.info(f"Current AQI: {aqi_data['aqi']} (Station: {aqi_data['station']})")
            return aqi_data
        else:
            logger.warning("Invalid response from WAQI API.")
            return {'aqi': 'N/A', 'pm25': 'N/A'}
            
    except Exception as e:
        logger.warning(f"Error fetching air quality: {e}. Data unavailable.")
        return {'aqi': 'N/A', 'pm25': 'N/A'}


def get_study_area_bounds(lat=CITY_LAT, lon=CITY_LON, dist=ANALYSIS_RADIUS_METERS):
    """
    Get bounding box of study area
    
    Returns:
        tuple: (minx, miny, maxx, maxy) in UTM coordinates
    """
    from shapely.geometry import Point
    
    center = gpd.GeoDataFrame(
        geometry=[Point(lon, lat)],
        crs=CRS_WGS84
    ).to_crs(CRS_UTM)
    
    buffer = center.buffer(dist)
    bounds = buffer.total_bounds  # (minx, miny, maxx, maxy)
    
    return bounds


def export_to_geojson(gdf, filename, output_dir):
    """
    Export GeoDataFrame to GeoJSON file
    
    Args:
        gdf: GeoDataFrame to export
        filename: Output filename
        output_dir: Output directory path
    """
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to WGS84 for GeoJSON standard
    gdf_wgs84 = gdf.to_crs(CRS_WGS84)
    gdf_wgs84.to_file(output_path, driver='GeoJSON')
    
    logger.info(f"Exported to: {output_path}")


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Data Loader Module...")
    buildings, streets, green = fetch_live_infrastructure()
    print(f"Buildings: {len(buildings)}")
    print(f"Streets: {len(streets)}")
    print(f"Green/Blue: {len(green)}")
    
    wind_dir = fetch_prevailing_wind_direction()
    print(f"Prevailing wind: {wind_dir}°")
    
    aqi = fetch_air_quality()
    print(f"Air Quality: {aqi}")

