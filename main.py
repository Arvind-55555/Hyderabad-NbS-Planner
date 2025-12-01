#!/usr/bin/env python3
"""
Hyderabad Nature-based Solutions (NbS) Planner
Main execution script

This script orchestrates the complete NbS analysis workflow:
1. Data fetching from live sources
2. Urban morphology analysis
3. NbS decision logic application
4. Visualization generation
5. Report creation
"""

import sys
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src import config
from src import data_loader
from src import morphology
from src import nbs_logic
from src import visualization
from src import reporting
from src import utils


def main(lat=None, lon=None, radius=None, grid_size=None, output_dir=None, 
         no_cache=False, quick_mode=False):
    """
    Main execution function
    
    Args:
        lat: Latitude (default from config)
        lon: Longitude (default from config)
        radius: Analysis radius in meters (default from config)
        grid_size: Grid cell size in meters (default from config)
        output_dir: Output directory (default from config)
        no_cache: Disable caching
        quick_mode: Skip detailed visualizations and reports
    """
    # Setup
    utils.print_banner()
    utils.setup_logging()
    utils.ensure_directories()
    
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("="*70)
    logger.info("HYDERABAD NATURE-BASED SOLUTIONS PLANNER - ANALYSIS STARTED")
    logger.info("="*70)
    
    # Use config defaults if not provided
    lat = lat or config.CITY_LAT
    lon = lon or config.CITY_LON
    radius = radius or config.ANALYSIS_RADIUS_METERS
    grid_size = grid_size or config.GRID_SIZE_METERS
    output_dir = Path(output_dir) if output_dir else Path(config.OUTPUT_DIR)
    
    # Validate coordinates
    is_valid, message = utils.validate_coordinates(lat, lon)
    if not is_valid:
        logger.error(message)
        return False
    
    logger.info(f"Analysis Location: ({lat}, {lon})")
    logger.info(f"Analysis Radius: {radius}m")
    logger.info(f"Grid Cell Size: {grid_size}m")
    logger.info(f"Output Directory: {output_dir}")
    logger.info("="*70)
    
    try:
        # ================================================================
        # STEP 1: DATA COLLECTION
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 1/6: FETCHING LIVE DATA")
        logger.info("="*70)
        
        with utils.Timer("Data fetching"):
            buildings, streets, green_blue = data_loader.fetch_live_infrastructure(
                lat=lat,
                lon=lon,
                dist=radius,
                use_cache=not no_cache
            )
            
            if buildings.empty:
                logger.error("CRITICAL: No building data retrieved. Cannot proceed.")
                logger.error("Try increasing the analysis radius or check your internet connection.")
                return False
            
            wind_dir = data_loader.fetch_prevailing_wind_direction(lat=lat, lon=lon)
            
            # Optional: Fetch air quality
            try:
                aqi_data = data_loader.fetch_air_quality(lat=lat, lon=lon)
                logger.info(f"Current AQI: {aqi_data.get('aqi', 'N/A')}")
            except Exception as e:
                logger.warning(f"Could not fetch AQI data: {e}")
        
        # ================================================================
        # STEP 2: URBAN MORPHOLOGY ANALYSIS
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 2/6: URBAN MORPHOLOGY ANALYSIS")
        logger.info("="*70)
        
        with utils.Timer("Morphology analysis"):
            # Create analysis grid
            grid = morphology.create_analysis_grid(buildings, grid_size=grid_size)
            logger.info(f"Created analysis grid: {len(grid)} cells")
            
            # Calculate morphology metrics
            analyzed_grid = morphology.calculate_roughness_and_density(grid, buildings)
            
            # Print statistics
            building_stats = morphology.calculate_building_statistics(buildings)
            logger.info(f"Building Statistics: {building_stats['total_buildings']} buildings")
            logger.info(f"Mean Building Height: {building_stats['mean_height']:.1f}m")
        
        # ================================================================
        # STEP 3: NbS PLANNING
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 3/6: APPLYING NbS DECISION LOGIC")
        logger.info("="*70)
        
        with utils.Timer("NbS planning"):
            nbs_plan = nbs_logic.run_nbs_planning(
                analyzed_grid,
                wind_dir,
                green_blue_gdf=green_blue,
                calculate_benefits=True,
                calculate_costs=True
            )
            
            # Generate summary
            summary_df = nbs_logic.generate_intervention_summary(nbs_plan)
            
            logger.info(f"\nIntervention Summary:")
            for _, row in summary_df.iterrows():
                logger.info(f"  {row['NbS_Type']:25s}: "
                           f"{row['Total_Area_hectares']:8.2f} ha, "
                           f"₹{row['Total_Cost_Crores']:.2f} Cr")
        
        # ================================================================
        # STEP 4: VISUALIZATION
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 4/6: GENERATING VISUALIZATIONS")
        logger.info("="*70)
        
        maps_dir = output_dir / 'maps'
        maps_dir.mkdir(parents=True, exist_ok=True)
        
        with utils.Timer("Visualization generation"):
            # Main NbS map
            timestamp = utils.get_timestamp()
            main_map_path = maps_dir / f'nbs_plan_{timestamp}.png'
            
            visualization.plot_nbs_map(
                nbs_plan,
                streets,
                green_blue,
                wind_dir,
                output_path=main_map_path,
                title=f"Nature-based Solutions Plan - {config.CITY_NAME}"
            )
            
            if not quick_mode:
                # Morphology maps
                morph_map_path = maps_dir / f'morphology_{timestamp}.png'
                visualization.plot_morphology_maps(
                    nbs_plan,
                    streets,
                    output_dir=maps_dir
                )
                
                # Statistics charts
                stats_chart_path = maps_dir / f'statistics_{timestamp}.png'
                visualization.plot_intervention_statistics(
                    summary_df,
                    output_path=stats_chart_path
                )
                
                # Cost-benefit analysis
                costbenefit_path = maps_dir / f'cost_benefit_{timestamp}.png'
                visualization.plot_cost_benefit_analysis(
                    summary_df,
                    output_path=costbenefit_path
                )
                
                # Dashboard
                dashboard_path = maps_dir / f'dashboard_{timestamp}.png'
                visualization.create_dashboard(
                    nbs_plan,
                    streets,
                    green_blue,
                    summary_df,
                    wind_dir,
                    output_path=dashboard_path
                )
                
                logger.info("All visualizations generated successfully.")
        
        # ================================================================
        # STEP 5: REPORT GENERATION
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 5/6: GENERATING REPORTS")
        logger.info("="*70)
        
        reports_dir = output_dir / 'reports'
        
        with utils.Timer("Report generation"):
            report_files, stats = reporting.generate_full_report(
                nbs_plan,
                summary_df,
                buildings,
                streets,
                green_blue,
                wind_dir,
                output_dir=reports_dir
            )
            
            logger.info("\nGenerated Reports:")
            for report_type, filepath in report_files.items():
                if report_type != 'timestamp':
                    logger.info(f"  {report_type:20s}: {filepath}")
        
        # ================================================================
        # STEP 6: SUMMARY
        # ================================================================
        logger.info("\n" + "="*70)
        logger.info("STEP 6/6: ANALYSIS COMPLETE")
        logger.info("="*70)
        
        # Print summary to console
        utils.print_summary(stats)
        
        logger.info("\n" + "="*70)
        logger.info("ALL OUTPUTS SAVED TO:")
        logger.info(f"  {output_dir.absolute()}")
        logger.info("="*70)
        
        logger.info("\n✓ Analysis completed successfully!")
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("\n\nAnalysis interrupted by user.")
        return False
        
    except Exception as e:
        logger.error(f"\n\nERROR during analysis: {e}", exc_info=True)
        return False


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Hyderabad Nature-based Solutions Planner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (Charminar)
  python main.py
  
  # Analyze Hitech City
  python main.py --lat 17.4435 --lon 78.3772
  
  # Larger radius and finer grid
  python main.py --radius 2000 --grid-size 100
  
  # Quick mode (skip detailed visualizations)
  python main.py --quick
  
  # Disable caching
  python main.py --no-cache
        """
    )
    
    parser.add_argument('--lat', type=float, default=None,
                       help=f'Latitude (default: {config.CITY_LAT})')
    
    parser.add_argument('--lon', type=float, default=None,
                       help=f'Longitude (default: {config.CITY_LON})')
    
    parser.add_argument('--radius', type=int, default=None,
                       help=f'Analysis radius in meters (default: {config.ANALYSIS_RADIUS_METERS})')
    
    parser.add_argument('--grid-size', type=int, default=None,
                       help=f'Grid cell size in meters (default: {config.GRID_SIZE_METERS})')
    
    parser.add_argument('--output-dir', type=str, default=None,
                       help=f'Output directory (default: {config.OUTPUT_DIR})')
    
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable caching (fetch fresh data)')
    
    parser.add_argument('--quick', action='store_true',
                       help='Quick mode (skip detailed visualizations)')
    
    parser.add_argument('--check-deps', action='store_true',
                       help='Check dependencies and exit')
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    # Check dependencies if requested
    if args.check_deps:
        utils.print_banner()
        print("\nChecking dependencies...\n")
        deps = utils.check_dependencies()
        for package, status in deps.items():
            print(f"  {package:15s}: {status}")
        sys.exit(0)
    
    # Run main analysis
    success = main(
        lat=args.lat,
        lon=args.lon,
        radius=args.radius,
        grid_size=args.grid_size,
        output_dir=args.output_dir,
        no_cache=args.no_cache,
        quick_mode=args.quick
    )
    
    sys.exit(0 if success else 1)
