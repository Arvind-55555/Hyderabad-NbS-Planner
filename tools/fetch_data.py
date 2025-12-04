import geopandas as gpd
from shapely.geometry import Point, box
import pandas as pd
import requests
import os

# --- CONFIGURATION ---
# Import project config for consistency
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.config import CITY_LAT, CITY_LON, ANALYSIS_RADIUS_METERS
    LAT, LON = CITY_LAT, CITY_LON
    # Convert radius to degrees (approximate)
    radius_degrees = ANALYSIS_RADIUS_METERS / 111000
except:
    # Fallback to default Hyderabad coordinates
    LAT, LON = 17.3850, 78.4867
    radius_degrees = 0.05

# Define a buffer to clip the massive dataset later
ROI_BOX = box(LON - radius_degrees, LAT - radius_degrees, LON + radius_degrees, LAT + radius_degrees)
DATA_DIR = "data"

os.makedirs(DATA_DIR, exist_ok=True)

def get_hyderabad_data():
    print("1. Fetching Google Open Buildings Data for Hyderabad...")
    
    # Google Open Buildings V3 - Direct S2 tile for Hyderabad region
    # The tiles.geojson endpoint is no longer available, so we use direct tile access
    # Hyderabad is in S2 cell: 31c (Level 4)
    # Direct download URL pattern: https://storage.googleapis.com/open-buildings-data/v3/polygons_s2_level_4_gzip/TILE.csv.gz
    
    # For Hyderabad region (17.3850, 78.4867), the S2 tile is approximately "31c" or "324"
    # Let's try the most likely S2 tiles for this region
    possible_tiles = [
        "324",  # Most likely tile for Hyderabad
        "31c", 
        "325",
        "326"
    ]
    
    tile_url = None
    tile_name = None
    
    print("2. Identifying correct S2 tile for Hyderabad...")
    for tile_id in possible_tiles:
        test_url = f"https://storage.googleapis.com/open-buildings-data/v3/polygons_s2_level_4_gzip/{tile_id}.csv.gz"
        print(f"   Trying tile: {tile_id}...")
        
        try:
            # Test if URL exists with a HEAD request
            response = requests.head(test_url, timeout=10)
            if response.status_code == 200:
                tile_url = test_url
                tile_name = tile_id
                print(f"   ✓ Found tile: {tile_id}")
                break
        except:
            continue
    
    if not tile_url:
        print("\n❌ Error: Could not automatically find the correct tile.")
        print("\nAlternative approaches:")
        print("\n1. MANUAL DOWNLOAD:")
        print("   • Visit: https://sites.research.google/open-buildings/")
        print("   • Download data for India (Telangana region)")
        print("   • Extract and place CSV at: data/india_buildings.csv.gz")
        print("   • Re-run this script")
        print("\n2. USE SYNTHETIC DATA (for testing):")
        print("   • Run: python tools/fetch_data.py --synthetic")
        print("   • This generates ~5000 mock buildings for demonstration")
        print("\n3. FIND CORRECT TILE:")
        print(f"   • Visit: https://s2.sidewalklabs.com/regioncoverer/?center={LAT},{LON}")
        print("   • Note the S2 cell ID and update this script")
        return None
    
    print(f"\n2. Using S2 Tile: {tile_name}")
    print(f"   URL: {tile_url}")
    print(f"   Note: This tile covers a large region including Hyderabad")

    # --- DOWNLOAD SECTION ---
    # The file is a gzipped CSV. 
    filename = os.path.join(DATA_DIR, f"tile_{tile_name}.csv.gz")
    
    if not os.path.exists(filename):
        print(f"3. Downloading tile (this may take time)...")
        response = requests.get(tile_url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        print("   Download Complete.")
    else:
        print("   File already exists. Skipping download.")

    # --- PROCESSING SECTION ---
    print("4. Processing & Clipping Data (This is memory intensive)...")
    
    # We use chunks because the CSV is massive (can be 2GB+)
    # We only want buildings inside our Hyderabad ROI Box
    chunksize = 100000
    filtered_rows = []
    
    # Columns in V3: latitude, longitude, area_in_meters, confidence, geometry, full_plus_code, height_m (if using V3+ height)
    # Note: V3 Standard includes geometry/lat/lon. 
    # If specific height data isn't in standard CSV, we estimate or use 2.5D dataset.
    # Standard V3 usually has: latitude, longitude, area_in_meters, confidence, geometry
    
    for chunk in pd.read_csv(filename, compression='gzip', chunksize=chunksize):
        # Rough filter by lat/lon first (fast)
        mask = (
            (chunk['latitude'] > ROI_BOX.bounds[1]) & 
            (chunk['latitude'] < ROI_BOX.bounds[3]) & 
            (chunk['longitude'] > ROI_BOX.bounds[0]) & 
            (chunk['longitude'] < ROI_BOX.bounds[2])
        )
        subset = chunk[mask]
        
        if not subset.empty:
            filtered_rows.append(subset)
            print(f"   Found {len(subset)} buildings in chunk...")

    if filtered_rows:
        hyd_df = pd.concat(filtered_rows)
        
        # Add random height if not present (Open Buildings V3 standard is 2D polygons, V3-2.5D is raster)
        # For the 4D engine, we need height.
        if 'height' not in hyd_df.columns:
            import numpy as np
            print("   Note: Standard V3 CSV is 2D. Generating synthetic heights based on area...")
            # Heuristic: Larger area = Taller building (roughly) + random variation
            hyd_df['height'] = np.sqrt(hyd_df['area_in_meters']) * 0.8 + np.random.randint(3, 15, size=len(hyd_df))
        
        # Add 'lon' and 'lat' columns for compatibility with nbs_engine.py
        hyd_df['lon'] = hyd_df['longitude']
        hyd_df['lat'] = hyd_df['latitude']
        
        output_file = os.path.join(DATA_DIR, "hyderabad_clipped.csv")
        hyd_df.to_csv(output_file, index=False)
        print(f"5. Success! Saved {len(hyd_df)} buildings to {output_file}")
        print(f"   Columns: {list(hyd_df.columns)}")
        print(f"   Building heights range: {hyd_df['height'].min():.1f}m - {hyd_df['height'].max():.1f}m")
        print("\n✓ Data ready! You can now run: streamlit run tools/nbs_engine.py")
        return True
    else:
        print("   No buildings found in the ROI.")
        return False

def generate_synthetic_data():
    """
    Generate synthetic building data for testing when real data is unavailable
    """
    print("\n" + "="*80)
    print("GENERATING SYNTHETIC BUILDING DATA FOR TESTING")
    print("="*80)
    print("\nNote: This creates mock data for demonstration purposes.")
    print("For real analysis, please download actual Google Open Buildings data.\n")
    
    import numpy as np
    np.random.seed(42)
    
    # Generate ~5000 synthetic buildings in Hyderabad region
    n_buildings = 5000
    
    # Scatter buildings around Hyderabad center
    lat_spread = 0.04  # ~4.4 km
    lon_spread = 0.04
    
    lats = np.random.normal(LAT, lat_spread/3, n_buildings)
    lons = np.random.normal(LON, lon_spread/3, n_buildings)
    
    # Clip to ROI
    mask = (lats > ROI_BOX.bounds[1]) & (lats < ROI_BOX.bounds[3]) & \
           (lons > ROI_BOX.bounds[0]) & (lons < ROI_BOX.bounds[2])
    
    lats = lats[mask]
    lons = lons[mask]
    n_buildings = len(lats)
    
    # Generate building properties
    areas = np.random.lognormal(3.5, 0.8, n_buildings)  # Log-normal distribution for areas
    areas = np.clip(areas, 20, 2000)  # Clip to reasonable range
    
    # Heights based on area (taller buildings tend to be larger)
    heights = np.sqrt(areas) * 0.8 + np.random.randint(3, 15, size=n_buildings)
    heights = np.clip(heights, 3, 50)
    
    confidences = np.random.uniform(0.7, 1.0, n_buildings)
    
    # Create DataFrame
    df = pd.DataFrame({
        'latitude': lats,
        'longitude': lons,
        'lat': lats,
        'lon': lons,
        'area_in_meters': areas,
        'height': heights,
        'confidence': confidences,
        'geometry': ['POLYGON' for _ in range(n_buildings)],  # Placeholder
        'source': ['synthetic' for _ in range(n_buildings)]
    })
    
    # Save
    output_file = os.path.join(DATA_DIR, "hyderabad_clipped.csv")
    df.to_csv(output_file, index=False)
    
    print(f"✓ Generated {n_buildings} synthetic buildings")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Area range: {areas.min():.1f} - {areas.max():.1f} m²")
    print(f"✓ Height range: {heights.min():.1f} - {heights.max():.1f} m")
    print("\nYou can now run: streamlit run tools/nbs_engine.py")
    print("\nTo get real data:")
    print("1. Visit: https://sites.research.google/open-buildings/")
    print("2. Download India/Telangana region data")
    print("3. Replace the synthetic data file")
    

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--synthetic":
        # Generate synthetic data for testing
        generate_synthetic_data()
    else:
        # Try to fetch real data
        result = get_hyderabad_data()
        
        # If real data fetch failed, offer synthetic option
        if result is None:
            print("\n" + "="*80)
            print("FAILED TO FETCH REAL DATA")
            print("="*80)
            response = input("\nWould you like to generate synthetic data for testing? (y/N): ")
            if response.lower() in ['y', 'yes']:
                generate_synthetic_data()
            else:
                print("\nExiting. Please resolve the data access issue and try again.")
                print("See documentation for manual download instructions.")