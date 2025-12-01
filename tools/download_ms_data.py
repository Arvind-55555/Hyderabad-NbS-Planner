#!/usr/bin/env python3
"""
Microsoft Building Footprints Downloader Helper
Provides instructions and utilities for downloading MS Buildings data
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_instructions():
    """Print detailed download instructions"""
    instructions = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║           MICROSOFT BUILDING FOOTPRINTS DOWNLOAD GUIDE                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

The Microsoft Global Building Footprints dataset provides high-precision
building polygons with inferred heights from satellite imagery.

═══════════════════════════════════════════════════════════════════════════

STEP 1: VISIT THE REPOSITORY

Go to: https://github.com/microsoft/GlobalMLBuildingFootprints

═══════════════════════════════════════════════════════════════════════════

STEP 2: DOWNLOAD INDIA DATASET

1. Navigate to the "Releases" section
2. Find the latest release
3. Look for "India" in the dataset list
4. Download the GeoJSONL file (~1.5 GB compressed)

Direct link format (check for latest version):
https://github.com/microsoft/GlobalMLBuildingFootprints/releases/download/v3/India.geojsonl.zip

═══════════════════════════════════════════════════════════════════════════

STEP 3: EXTRACT HYDERABAD SUBSET

Once downloaded, extract the Hyderabad area using Python:

```python
import geopandas as gpd
from pathlib import Path

# Load the full India dataset (this may take a few minutes)
print("Loading India building footprints...")
gdf = gpd.read_file('India.geojsonl')

# Extract Hyderabad bounding box
# Coordinates: [78.3°E, 17.3°N] to [78.6°E, 17.5°N]
print("Extracting Hyderabad subset...")
hyderabad = gdf.cx[78.3:78.6, 17.3:17.5]

print(f"Found {len(hyderabad)} buildings in Hyderabad area")

# Save to project directory
output_path = Path('data/references/hyderabad_buildings_ms.geojson')
output_path.parent.mkdir(parents=True, exist_ok=True)

print(f"Saving to {output_path}...")
hyderabad.to_file(output_path, driver='GeoJSON')

print("✓ Done! Hyderabad building footprints saved.")
```

═══════════════════════════════════════════════════════════════════════════

STEP 4: ENABLE IN PROJECT

Edit `src/config.py` and set:

```python
USE_MS_BUILDINGS = True
```

The data_loader module will automatically use the MS Buildings data
instead of OSM for better accuracy.

═══════════════════════════════════════════════════════════════════════════

ALTERNATIVE: QUADKEY-BASED DOWNLOAD

Microsoft also provides data by QuadKeys for more efficient downloading.
Hyderabad falls under QuadKeys starting with: 123130323*

Use the provided download links in the repository to get specific quadkeys.

═══════════════════════════════════════════════════════════════════════════

DATASET INFORMATION

- **Total Buildings (India)**: ~500 million
- **Hyderabad Buildings**: ~800,000 (estimated)
- **Format**: GeoJSON / GeoJSONL
- **License**: ODbL (Open Database License)
- **Attributes**:
  - geometry: Building polygon
  - height: Inferred height in meters (if available)
  - confidence: Prediction confidence score

═══════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING

Q: The file is too large to process
A: Use dask-geopandas for parallel processing, or download by quadkey

Q: Memory error when loading
A: Process in chunks:
   ```python
   for chunk in pd.read_json('India.geojsonl', lines=True, chunksize=10000):
       # Process each chunk
   ```

Q: How do I find the right QuadKey?
A: Use online tools like https://www.maptiler.com/google-maps-coordinates-tile-bounds-projection/

═══════════════════════════════════════════════════════════════════════════

For more information, visit:
- GitHub: https://github.com/microsoft/GlobalMLBuildingFootprints
- Blog: https://www.microsoft.com/en-us/maps/building-footprints

═══════════════════════════════════════════════════════════════════════════
    """
    
    print(instructions)


def extract_hyderabad(input_file, output_file=None):
    """
    Extract Hyderabad subset from India dataset
    
    Args:
        input_file: Path to India GeoJSONL file
        output_file: Path to save Hyderabad subset
    """
    try:
        import geopandas as gpd
        from pathlib import Path
        
        print(f"\nLoading building footprints from: {input_file}")
        print("This may take several minutes for the full India dataset...")
        
        # Load data
        gdf = gpd.read_file(input_file)
        print(f"Loaded {len(gdf)} buildings from India dataset")
        
        # Extract Hyderabad
        print("\nExtracting Hyderabad bounding box [78.3°E, 17.3°N] to [78.6°E, 17.5°N]...")
        hyderabad = gdf.cx[78.3:78.6, 17.3:17.5]
        print(f"Found {len(hyderabad)} buildings in Hyderabad area")
        
        if len(hyderabad) == 0:
            print("WARNING: No buildings found in the specified area.")
            print("Check if the input file covers Hyderabad region.")
            return False
        
        # Determine output path
        if output_file is None:
            output_file = Path('data/references/hyderabad_buildings_ms.geojson')
        else:
            output_file = Path(output_file)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save
        print(f"\nSaving to: {output_file}")
        hyderabad.to_file(output_file, driver='GeoJSON')
        
        print(f"✓ Successfully saved {len(hyderabad)} buildings")
        print(f"\nFile size: {output_file.stat().st_size / 1024**2:.2f} MB")
        
        # Print statistics
        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        print(f"Total buildings extracted: {len(hyderabad)}")
        print(f"Total footprint area: {hyderabad.geometry.area.sum() / 10000:.2f} hectares")
        print(f"Output file: {output_file}")
        print("="*70)
        
        print("\nNext steps:")
        print(f"1. Set USE_MS_BUILDINGS = True in src/config.py")
        print(f"2. Verify MS_BUILDINGS_PATH points to: {output_file}")
        print(f"3. Run main.py to use the MS Buildings data")
        
        return True
        
    except ImportError:
        print("ERROR: geopandas is not installed.")
        print("Install with: pip install geopandas")
        return False
        
    except Exception as e:
        print(f"ERROR during extraction: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Microsoft Building Footprints Helper',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--extract',
        type=str,
        metavar='INPUT_FILE',
        help='Extract Hyderabad subset from India GeoJSONL file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        metavar='OUTPUT_FILE',
        help='Output file path (default: data/references/hyderabad_buildings_ms.geojson)'
    )
    
    args = parser.parse_args()
    
    if args.extract:
        success = extract_hyderabad(args.extract, args.output)
        sys.exit(0 if success else 1)
    else:
        print_instructions()
        sys.exit(0)


if __name__ == "__main__":
    main()

