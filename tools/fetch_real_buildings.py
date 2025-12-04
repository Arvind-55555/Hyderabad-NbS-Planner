#!/usr/bin/env python3
"""
Fetch Real Building Data for Hyderabad from Multiple Public Sources

This script tries multiple data sources in order of preference:
1. GOBS (Geospatial Open Building Stack) - India-specific, includes heights
2. OpenStreetMap - Community-maintained, always available
3. Microsoft Building Footprints - High quality when available

All sources are free and publicly available.
"""

import os
import sys
import requests
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, box, shape
import json
import logging
from pathlib import Path

# Setup
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.config import CITY_LAT, CITY_LON, ANALYSIS_RADIUS_METERS
    LAT, LON = CITY_LAT, CITY_LON
    radius_degrees = ANALYSIS_RADIUS_METERS / 111000
except:
    LAT, LON = 17.3850, 78.4867
    radius_degrees = 0.05

ROI_BOX = box(LON - radius_degrees, LAT - radius_degrees, LON + radius_degrees, LAT + radius_degrees)
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def print_banner(text):
    """Print formatted banner"""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80 + "\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 1: GOBS (Geospatial Open Building Stack)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_from_gobs():
    """
    Fetch from GOBS - India-specific building dataset with heights
    Source: https://gobs.aeee.in/
    
    GOBS provides:
    - Building footprints
    - Building heights (estimated)
    - Floor count estimates
    - Functional land use predictions
    """
    print_banner("SOURCE 1: GOBS (Geospatial Open Building Stack)")
    
    logger.info("GOBS is a comprehensive India-specific dataset")
    logger.info("Website: https://gobs.aeee.in/")
    
    # GOBS data is typically accessed via their API or bulk download
    # For now, provide manual download instructions as their API requires registration
    
    print("📋 MANUAL DOWNLOAD REQUIRED:")
    print("\n1. Visit: https://gobs.aeee.in/")
    print("2. Navigate to 'Data Download' section")
    print("3. Select: Telangana → Hyderabad")
    print("4. Download the CSV file")
    print("5. Save as: data/gobs_hyderabad.csv")
    print("6. Re-run this script with: --process-gobs")
    
    # Check if user already downloaded
    gobs_file = os.path.join(DATA_DIR, "gobs_hyderabad.csv")
    if os.path.exists(gobs_file):
        logger.info(f"✓ Found GOBS file: {gobs_file}")
        return process_gobs_data(gobs_file)
    
    return None


def process_gobs_data(filepath):
    """Process GOBS data if already downloaded"""
    try:
        logger.info(f"Processing GOBS data from {filepath}")
        
        # Read GOBS CSV
        df = pd.read_csv(filepath)
        
        # GOBS columns (typical): latitude, longitude, area, height, floors, land_use
        # Ensure we have required columns
        required = ['latitude', 'longitude']
        if not all(col in df.columns for col in required):
            logger.error("GOBS file missing required columns")
            return None
        
        # Filter to ROI
        mask = (df['latitude'] > ROI_BOX.bounds[1]) & \
               (df['latitude'] < ROI_BOX.bounds[3]) & \
               (df['longitude'] > ROI_BOX.bounds[0]) & \
               (df['longitude'] < ROI_BOX.bounds[2])
        
        df_filtered = df[mask].copy()
        
        # Add lat/lon aliases
        df_filtered['lat'] = df_filtered['latitude']
        df_filtered['lon'] = df_filtered['longitude']
        
        # Ensure height column
        if 'height' not in df_filtered.columns:
            if 'building_height' in df_filtered.columns:
                df_filtered['height'] = df_filtered['building_height']
            elif 'floors' in df_filtered.columns:
                df_filtered['height'] = df_filtered['floors'] * 3.0  # Estimate
            else:
                df_filtered['height'] = 10.0  # Default
        
        # Ensure area column
        if 'area_in_meters' not in df_filtered.columns:
            if 'footprint_area' in df_filtered.columns:
                df_filtered['area_in_meters'] = df_filtered['footprint_area']
            else:
                df_filtered['area_in_meters'] = 100.0  # Default
        
        # Save processed data
        output_file = os.path.join(DATA_DIR, "hyderabad_clipped.csv")
        df_filtered.to_csv(output_file, index=False)
        
        logger.info(f"✓ Processed {len(df_filtered)} buildings from GOBS")
        logger.info(f"✓ Saved to: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing GOBS data: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 2: OpenStreetMap (OSM)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_from_osm():
    """
    Fetch from OpenStreetMap using Overpass API
    Source: https://www.openstreetmap.org/
    
    This is free, always available, and provides good coverage for Hyderabad
    """
    print_banner("SOURCE 2: OpenStreetMap (Overpass API)")
    
    logger.info("Querying OSM for buildings in Hyderabad region...")
    logger.info("This may take 1-2 minutes for the region...")
    
    # Overpass API query for buildings
    overpass_url = "http://overpass-api.de/api/interpreter"
    
    # Bounding box: south, west, north, east
    bbox = f"{ROI_BOX.bounds[1]},{ROI_BOX.bounds[0]},{ROI_BOX.bounds[3]},{ROI_BOX.bounds[2]}"
    
    overpass_query = f"""
    [out:json][timeout:180];
    (
      way["building"]({bbox});
      relation["building"]({bbox});
    );
    out geom;
    """
    
    try:
        logger.info("Sending request to Overpass API...")
        response = requests.post(
            overpass_url,
            data={'data': overpass_query},
            timeout=180
        )
        
        if response.status_code != 200:
            logger.error(f"Overpass API returned status {response.status_code}")
            return None
        
        data = response.json()
        
        if 'elements' not in data or len(data['elements']) == 0:
            logger.warning("No buildings found in OSM for this region")
            return None
        
        logger.info(f"✓ Retrieved {len(data['elements'])} buildings from OSM")
        
        # Process OSM data
        buildings = []
        
        for element in data['elements']:
            try:
                # Get geometry
                if element['type'] == 'way' and 'geometry' in element:
                    coords = [(node['lon'], node['lat']) for node in element['geometry']]
                    
                    if len(coords) < 3:
                        continue
                    
                    # Calculate centroid
                    lon_avg = sum(c[0] for c in coords) / len(coords)
                    lat_avg = sum(c[1] for c in coords) / len(coords)
                    
                    # Get height from tags
                    tags = element.get('tags', {})
                    height = None
                    
                    if 'height' in tags:
                        try:
                            height = float(tags['height'].replace('m', ''))
                        except:
                            pass
                    elif 'building:levels' in tags:
                        try:
                            levels = int(tags['building:levels'])
                            height = levels * 3.0  # Estimate 3m per floor
                        except:
                            pass
                    
                    if height is None:
                        # Estimate based on building type
                        building_type = tags.get('building', 'yes')
                        if building_type in ['apartments', 'commercial', 'office']:
                            height = 15.0
                        elif building_type in ['house', 'residential']:
                            height = 6.0
                        else:
                            height = 10.0
                    
                    # Estimate area (rough approximation)
                    area = estimate_area_from_coords(coords)
                    
                    buildings.append({
                        'latitude': lat_avg,
                        'longitude': lon_avg,
                        'lat': lat_avg,
                        'lon': lon_avg,
                        'height': height,
                        'area_in_meters': area,
                        'building_type': tags.get('building', 'yes'),
                        'source': 'osm',
                        'osm_id': element.get('id')
                    })
                    
            except Exception as e:
                logger.debug(f"Skipping element: {e}")
                continue
        
        if not buildings:
            logger.warning("Could not process any buildings from OSM data")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(buildings)
        
        # Save
        output_file = os.path.join(DATA_DIR, "hyderabad_clipped.csv")
        df.to_csv(output_file, index=False)
        
        logger.info(f"✓ Processed {len(df)} buildings from OSM")
        logger.info(f"✓ Height range: {df['height'].min():.1f}m - {df['height'].max():.1f}m")
        logger.info(f"✓ Saved to: {output_file}")
        
        return True
        
    except requests.Timeout:
        logger.error("Request timed out. Try reducing the search area.")
        return None
    except Exception as e:
        logger.error(f"Error fetching from OSM: {e}")
        return None


def estimate_area_from_coords(coords):
    """Estimate building area from coordinates (rough approximation)"""
    try:
        # Use shoelace formula for polygon area
        n = len(coords)
        if n < 3:
            return 100.0
        
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]
        
        area = abs(area) / 2.0
        
        # Convert from degrees² to m² (rough approximation at Hyderabad latitude)
        # 1 degree ≈ 111km at equator, ~110km at Hyderabad's latitude
        meters_per_deg_lat = 111000
        meters_per_deg_lon = 111000 * 0.952  # cos(17.4°)
        
        area_m2 = area * meters_per_deg_lat * meters_per_deg_lon
        
        # Clamp to reasonable range
        return max(20.0, min(area_m2, 5000.0))
        
    except:
        return 100.0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOURCE 3: Google Earth Engine (requires authentication)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_from_earth_engine():
    """
    Fetch from Google Earth Engine
    Requires: ee library and authentication
    """
    print_banner("SOURCE 3: Google Earth Engine")
    
    try:
        import ee
        logger.info("Attempting to use Google Earth Engine...")
        
        # Try to initialize
        try:
            ee.Initialize()
        except:
            logger.warning("Earth Engine not authenticated")
            print("\n📋 TO USE EARTH ENGINE:")
            print("1. Install: pip install earthengine-api")
            print("2. Authenticate: earthengine authenticate")
            print("3. Re-run this script")
            return None
        
        # Load Google Open Buildings dataset
        buildings = ee.FeatureCollection('GOOGLE/Research/open-buildings/v3/polygons')
        
        # Filter to ROI
        roi = ee.Geometry.Rectangle([
            ROI_BOX.bounds[0], ROI_BOX.bounds[1],
            ROI_BOX.bounds[2], ROI_BOX.bounds[3]
        ])
        
        buildings_filtered = buildings.filterBounds(roi)
        
        # Get feature count
        count = buildings_filtered.size().getInfo()
        logger.info(f"Found {count} buildings in Earth Engine")
        
        if count == 0:
            logger.warning("No buildings found in this region")
            return None
        
        # Export (this requires more complex setup)
        logger.info("Earth Engine data export requires additional setup")
        logger.info("See: https://developers.google.com/earth-engine/guides/exporting")
        
        return None
        
    except ImportError:
        logger.info("Earth Engine library not installed")
        logger.info("Install with: pip install earthengine-api")
        return None
    except Exception as e:
        logger.error(f"Error with Earth Engine: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN EXECUTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + "  REAL BUILDING DATA FETCHER - Multiple Public Sources".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\n📍 Target Location: Hyderabad, India")
    print(f"   Coordinates: {LAT:.4f}°N, {LON:.4f}°E")
    print(f"   Search Radius: ~{ANALYSIS_RADIUS_METERS/1000:.1f} km")
    
    # Check if data already exists
    output_file = os.path.join(DATA_DIR, "hyderabad_clipped.csv")
    if os.path.exists(output_file):
        print(f"\n⚠️  File already exists: {output_file}")
        response = input("   Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("   Keeping existing file. Exiting.")
            return
        os.remove(output_file)
    
    # Try sources in order
    sources = [
        ("OpenStreetMap (OSM)", fetch_from_osm),
        ("GOBS (if already downloaded)", fetch_from_gobs),
        ("Google Earth Engine", fetch_from_earth_engine),
    ]
    
    for source_name, fetch_func in sources:
        try:
            result = fetch_func()
            if result:
                print("\n" + "="*80)
                print(f"✅ SUCCESS! Downloaded real building data from {source_name}")
                print("="*80)
                print(f"\n✓ Data saved to: {output_file}")
                print(f"\n🚀 Next step: streamlit run tools/nbs_engine.py")
                return
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to fetch from {source_name}: {e}")
            continue
    
    # All sources failed
    print("\n" + "="*80)
    print("⚠️  Could not automatically fetch data from any source")
    print("="*80)
    print("\n📋 MANUAL OPTIONS:")
    print("\n1. GOBS (Recommended for India):")
    print("   • Visit: https://gobs.aeee.in/")
    print("   • Download Hyderabad/Telangana data")
    print("   • Save as: data/gobs_hyderabad.csv")
    print("   • Run: python tools/fetch_real_buildings.py --process-gobs")
    print("\n2. Use synthetic data (for testing):")
    print("   • Run: python tools/fetch_data.py --synthetic")
    print("\n3. Try OSM with smaller area:")
    print("   • Edit src/config.py: ANALYSIS_RADIUS_METERS = 3000")
    print("   • Re-run this script")


if __name__ == "__main__":
    import sys
    
    if "--process-gobs" in sys.argv:
        gobs_file = os.path.join(DATA_DIR, "gobs_hyderabad.csv")
        if os.path.exists(gobs_file):
            process_gobs_data(gobs_file)
        else:
            print(f"Error: {gobs_file} not found")
            print("Please download from https://gobs.aeee.in/ first")
    else:
        main()

