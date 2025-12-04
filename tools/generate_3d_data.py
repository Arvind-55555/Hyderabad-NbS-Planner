#!/usr/bin/env python3
"""
Generate and Upload 3D Data to SpatialBound
This script generates 3D data from NbS analysis results and uploads to SpatialBound for 4D visualization
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_3d_generator import Data3DGenerator, generate_3d_data_for_project
from src.spatialbound_integration import SpatialBoundClient
import geopandas as gpd
import pandas as pd
import json


def load_analysis_results(output_dir: Path) -> dict:
    """
    Load NbS analysis results from output directory
    
    Args:
        output_dir: Output directory containing analysis results
    
    Returns:
        dict: Dictionary containing loaded data
    """
    logger = logging.getLogger(__name__)
    logger.info("Loading analysis results...")
    
    data = {}
    
    # Load GeoJSON with NbS interventions
    geojson_files = list((output_dir / 'reports').glob('nbs_interventions_*.geojson'))
    if not geojson_files:
        logger.error("No NbS interventions GeoJSON found!")
        return None
    
    latest_geojson = sorted(geojson_files, key=lambda x: x.stat().st_mtime)[-1]
    logger.info(f"Loading: {latest_geojson}")
    data['nbs_gdf'] = gpd.read_file(latest_geojson)
    
    # Load CSV files
    summary_csv = output_dir / 'reports' / 'csv' / 'nbs_summary.csv'
    if summary_csv.exists():
        data['summary_df'] = pd.read_csv(summary_csv)
    
    grid_csv = output_dir / 'reports' / 'csv' / 'nbs_grid_data.csv'
    if grid_csv.exists():
        data['grid_df'] = pd.read_csv(grid_csv)
    
    # Load statistics JSON
    json_files = list((output_dir / 'reports').glob('nbs_statistics_*.json'))
    if json_files:
        latest_json = sorted(json_files, key=lambda x: x.stat().st_mtime)[-1]
        with open(latest_json, 'r') as f:
            data['stats'] = json.load(f)
    
    logger.info(f"✓ Loaded {len(data['nbs_gdf'])} NbS intervention cells")
    
    return data


def load_infrastructure_from_cache(cache_dir: Path) -> dict:
    """
    Load infrastructure data (buildings, streets, green spaces) from cache
    
    Args:
        cache_dir: Cache directory
    
    Returns:
        dict: Dictionary with infrastructure GeoDataFrames
    """
    logger = logging.getLogger(__name__)
    logger.info("Loading infrastructure data from cache...")
    
    cache_files = list(Path(cache_dir).glob('*.json'))
    
    if not cache_files:
        logger.error("No cache files found!")
        return None
    
    # Get the most recent cache file
    latest_cache = sorted(cache_files, key=lambda x: x.stat().st_mtime)[-1]
    logger.info(f"Loading from cache: {latest_cache.name}")
    
    with open(latest_cache, 'r') as f:
        cache_data = json.load(f)
    
    data = {}
    
    # Load buildings
    if 'buildings' in cache_data and cache_data['buildings']:
        data['buildings_gdf'] = gpd.GeoDataFrame.from_features(
            cache_data['buildings']['features'],
            crs='EPSG:4326'
        )
        logger.info(f"✓ Loaded {len(data['buildings_gdf'])} buildings")
    
    # Load green/blue spaces
    if 'green_blue' in cache_data and cache_data['green_blue']:
        data['green_blue_gdf'] = gpd.GeoDataFrame.from_features(
            cache_data['green_blue']['features'],
            crs='EPSG:4326'
        )
        logger.info(f"✓ Loaded {len(data['green_blue_gdf'])} green/blue spaces")
    
    return data


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate 3D data and upload to SpatialBound for 4D visualization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate 3D data only (no upload)
  python tools/generate_3d_data.py --no-upload
  
  # Generate and upload to SpatialBound
  python tools/generate_3d_data.py --project-name "Charminar NbS Plan"
  
  # Specify custom output directory
  python tools/generate_3d_data.py --output-dir outputs --data-dir outputs/3d_data
  
  # Use specific API key
  python tools/generate_3d_data.py --api-key "your-api-key-here"
        """
    )
    
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Output directory containing analysis results')
    
    parser.add_argument('--data-dir', type=str, default='outputs/3d_data',
                       help='Directory to save generated 3D data files')
    
    parser.add_argument('--cache-dir', type=str, default='cache',
                       help='Cache directory containing infrastructure data')
    
    parser.add_argument('--project-name', type=str, default='Hyderabad_NbS',
                       help='Project name for SpatialBound')
    
    parser.add_argument('--api-key', type=str, default=None,
                       help='SpatialBound API key (defaults to SPATIALBOUND_API_KEY env var)')
    
    parser.add_argument('--no-upload', action='store_true',
                       help='Generate 3D data only, skip upload to SpatialBound')
    
    parser.add_argument('--location', type=str, default='17.3616,78.4747',
                       help='Location as "latitude,longitude" for project metadata')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("="*80)
    logger.info("SPATIALBOUND 4D DATA GENERATION AND UPLOAD")
    logger.info("="*80)
    
    # Parse location
    try:
        lat, lon = map(float, args.location.split(','))
    except:
        logger.error("Invalid location format. Use: latitude,longitude")
        return 1
    
    # Load analysis results
    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        logger.error("Please run the analysis first: python main.py")
        return 1
    
    analysis_data = load_analysis_results(output_dir)
    if not analysis_data:
        logger.error("Failed to load analysis results")
        return 1
    
    # Load infrastructure data
    cache_dir = Path(args.cache_dir)
    infrastructure_data = load_infrastructure_from_cache(cache_dir)
    if not infrastructure_data:
        logger.error("Failed to load infrastructure data from cache")
        return 1
    
    # Merge data
    nbs_gdf = analysis_data['nbs_gdf']
    buildings_gdf = infrastructure_data.get('buildings_gdf', gpd.GeoDataFrame())
    green_blue_gdf = infrastructure_data.get('green_blue_gdf', gpd.GeoDataFrame())
    
    # Add height information to buildings if not present
    if 'avg_height' not in buildings_gdf.columns:
        logger.warning("No height data in buildings, using defaults")
        buildings_gdf['avg_height'] = 6.0  # Default 2-story building
    
    # Generate 3D data
    logger.info("\n" + "="*80)
    logger.info("STEP 1: GENERATING 3D DATA")
    logger.info("="*80)
    
    data_dir = Path(args.data_dir)
    
    try:
        generated_files = generate_3d_data_for_project(
            buildings_gdf=buildings_gdf,
            nbs_gdf=nbs_gdf,
            green_blue_gdf=green_blue_gdf,
            output_dir=data_dir,
            project_name=args.project_name
        )
        
        logger.info("\n✓ 3D data generation complete!")
        
    except Exception as e:
        logger.error(f"Failed to generate 3D data: {e}", exc_info=True)
        return 1
    
    # Upload to SpatialBound (if not disabled)
    if not args.no_upload:
        logger.info("\n" + "="*80)
        logger.info("STEP 2: UPLOADING TO SPATIALBOUND")
        logger.info("="*80)
        
        try:
            # Initialize SpatialBound client
            client = SpatialBoundClient(api_key=args.api_key)
            
            # Test connection
            if not client.test_connection():
                logger.error("Failed to connect to SpatialBound API")
                logger.error("Please check your API key and network connection")
                return 1
            
            # Create project
            logger.info(f"\nCreating project: {args.project_name}")
            project_id = client.create_project(
                project_name=args.project_name,
                location=(lat, lon),
                description=f"Nature-based Solutions planning for {args.project_name}"
            )
            
            if not project_id:
                logger.error("Failed to create project")
                return 1
            
            logger.info(f"✓ Project created with ID: {project_id}")
            
            # Upload BEFORE state
            logger.info("\nUploading BEFORE state...")
            before_success = client.upload_buildings_before(
                project_id=project_id,
                buildings_file=generated_files['before_cityjson']
            )
            
            if not before_success:
                logger.error("Failed to upload BEFORE state")
                return 1
            
            # Upload AFTER state
            logger.info("\nUploading AFTER state...")
            after_success = client.upload_nbs_after(
                project_id=project_id,
                nbs_file=generated_files['after_cityjson']
            )
            
            if not after_success:
                logger.error("Failed to upload AFTER state")
                return 1
            
            # Generate 4D visualization
            logger.info("\nGenerating 4D visualization...")
            viz_url = client.generate_4d_visualization(
                project_id=project_id,
                config={
                    "transition_duration": 3.0,
                    "show_labels": True,
                    "color_scheme": "nbs_standard"
                }
            )
            
            if viz_url:
                logger.info("\n" + "="*80)
                logger.info("✓ 4D VISUALIZATION READY!")
                logger.info("="*80)
                logger.info(f"\nViewer URL: {viz_url}")
                logger.info(f"Project ID: {project_id}")
                
                # Get embed code
                embed_code = client.get_embed_code(project_id)
                
                # Save project info
                project_info_path = data_dir / 'spatialbound_project_info.json'
                project_info = {
                    "project_id": project_id,
                    "project_name": args.project_name,
                    "viewer_url": viz_url,
                    "embed_code": embed_code,
                    "location": {"latitude": lat, "longitude": lon}
                }
                
                with open(project_info_path, 'w') as f:
                    json.dump(project_info, f, indent=2)
                
                logger.info(f"\nProject info saved to: {project_info_path}")
                logger.info("\nEmbed code:")
                logger.info(embed_code)
                
            else:
                logger.error("Failed to generate 4D visualization")
                return 1
            
        except Exception as e:
            logger.error(f"Failed to upload to SpatialBound: {e}", exc_info=True)
            return 1
    
    else:
        logger.info("\n✓ 3D data generated successfully (upload skipped)")
        logger.info("\nTo upload to SpatialBound, run:")
        logger.info(f"  python tools/generate_3d_data.py --project-name \"{args.project_name}\"")
    
    logger.info("\n" + "="*80)
    logger.info("COMPLETE!")
    logger.info("="*80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

