#!/usr/bin/env python3
"""
Batch Processing Tool for Multiple Locations
Allows running NbS analysis for multiple locations from a CSV file
"""

import sys
import csv
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import utils


def process_locations_from_csv(csv_file, output_base_dir=None, grid_size=150, 
                               radius=1500, no_cache=False):
    """
    Process multiple locations from CSV file
    
    CSV Format:
    name,latitude,longitude,radius(optional),grid_size(optional)
    
    Args:
        csv_file: Path to CSV file with locations
        output_base_dir: Base directory for outputs
        grid_size: Default grid size
        radius: Default analysis radius
        no_cache: Disable caching
    """
    # Import main here to avoid circular imports
    from main import main as run_analysis
    
    csv_path = Path(csv_file)
    
    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_file}")
        return False
    
    if output_base_dir is None:
        output_base_dir = Path('outputs/batch_analysis')
    else:
        output_base_dir = Path(output_base_dir)
    
    # Read locations
    locations = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append(row)
    
    if len(locations) == 0:
        print("ERROR: No locations found in CSV file.")
        return False
    
    print(f"\n{'='*70}")
    print(f"BATCH PROCESSING: {len(locations)} LOCATIONS")
    print(f"{'='*70}\n")
    
    results = []
    
    for idx, location in enumerate(locations, 1):
        name = location.get('name', f'Location_{idx}')
        lat = float(location['latitude'])
        lon = float(location['longitude'])
        loc_radius = int(location.get('radius', radius))
        loc_grid = int(location.get('grid_size', grid_size))
        
        print(f"\n{'='*70}")
        print(f"PROCESSING {idx}/{len(locations)}: {name}")
        print(f"Coordinates: ({lat}, {lon})")
        print(f"{'='*70}\n")
        
        # Create location-specific output directory
        location_dir = output_base_dir / name.replace(' ', '_').replace(',', '')
        
        try:
            success = run_analysis(
                lat=lat,
                lon=lon,
                radius=loc_radius,
                grid_size=loc_grid,
                output_dir=location_dir,
                no_cache=no_cache,
                quick_mode=False
            )
            
            results.append({
                'name': name,
                'latitude': lat,
                'longitude': lon,
                'status': 'SUCCESS' if success else 'FAILED',
                'output_dir': str(location_dir)
            })
            
        except Exception as e:
            print(f"\nERROR processing {name}: {e}")
            results.append({
                'name': name,
                'latitude': lat,
                'longitude': lon,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Save summary
    summary_path = output_base_dir / 'batch_summary.csv'
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_path, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
    
    # Print summary
    print(f"\n{'='*70}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*70}")
    
    successful = sum(1 for r in results if r['status'] == 'SUCCESS')
    failed = len(results) - successful
    
    print(f"\nTotal Locations: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"\nSummary saved to: {summary_path}")
    print(f"Outputs saved to: {output_base_dir}")
    print(f"{'='*70}\n")
    
    return failed == 0


def create_sample_csv(output_file='locations_sample.csv'):
    """Create a sample CSV file with example locations"""
    
    sample_locations = [
        {
            'name': 'Charminar - Old City',
            'latitude': 17.3616,
            'longitude': 78.4747,
            'radius': 1500,
            'grid_size': 150
        },
        {
            'name': 'Hitech City',
            'latitude': 17.4435,
            'longitude': 78.3772,
            'radius': 1500,
            'grid_size': 150
        },
        {
            'name': 'Gachibowli',
            'latitude': 17.4399,
            'longitude': 78.3489,
            'radius': 1500,
            'grid_size': 150
        },
        {
            'name': 'Secunderabad',
            'latitude': 17.4399,
            'longitude': 78.4983,
            'radius': 1500,
            'grid_size': 150
        },
        {
            'name': 'Banjara Hills',
            'latitude': 17.4239,
            'longitude': 78.4738,
            'radius': 1000,
            'grid_size': 100
        }
    ]
    
    output_path = Path(output_file)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'latitude', 'longitude', 'radius', 'grid_size'])
        writer.writeheader()
        writer.writerows(sample_locations)
    
    print(f"Sample CSV created: {output_path}")
    print(f"\nContents ({len(sample_locations)} locations):")
    for loc in sample_locations:
        print(f"  - {loc['name']}: ({loc['latitude']}, {loc['longitude']})")
    
    print(f"\nEdit this file and run:")
    print(f"  python tools/batch_process.py --csv {output_file}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Batch Process Multiple Locations for NbS Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a sample CSV template
  python tools/batch_process.py --create-sample
  
  # Process locations from CSV
  python tools/batch_process.py --csv locations.csv
  
  # Process with custom settings
  python tools/batch_process.py --csv locations.csv --radius 2000 --grid-size 100
  
  # Process without caching
  python tools/batch_process.py --csv locations.csv --no-cache

CSV Format:
  name,latitude,longitude,radius,grid_size
  Charminar,17.3616,78.4747,1500,150
  Hitech City,17.4435,78.3772,1500,150
        """
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        help='Path to CSV file with locations'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='Create a sample CSV file with Hyderabad locations'
    )
    
    parser.add_argument(
        '--sample-output',
        type=str,
        default='locations_sample.csv',
        help='Output path for sample CSV (default: locations_sample.csv)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Base output directory (default: outputs/batch_analysis)'
    )
    
    parser.add_argument(
        '--radius',
        type=int,
        default=1500,
        help='Default analysis radius in meters (default: 1500)'
    )
    
    parser.add_argument(
        '--grid-size',
        type=int,
        default=150,
        help='Default grid cell size in meters (default: 150)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching (fetch fresh data)'
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_csv(args.sample_output)
        return 0
    
    if not args.csv:
        parser.print_help()
        print("\nERROR: Please provide --csv file or use --create-sample")
        return 1
    
    # Setup logging
    utils.setup_logging()
    
    # Run batch processing
    success = process_locations_from_csv(
        args.csv,
        output_base_dir=args.output_dir,
        grid_size=args.grid_size,
        radius=args.radius,
        no_cache=args.no_cache
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

