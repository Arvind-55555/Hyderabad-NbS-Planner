#!/usr/bin/env python3
"""
Validation script for 4D visualization setup
Checks all dependencies and data files before running the engine
"""

import sys
import os
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def check_dependency(module_name, package_name=None):
    """Check if a Python module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print_success(f"{package_name} installed")
        return True
    except ImportError:
        print_error(f"{package_name} NOT installed")
        print(f"   Install with: pip install {package_name}")
        return False

def check_file(filepath, description):
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        if size > 0:
            size_mb = size / (1024 * 1024)
            print_success(f"{description} exists ({size_mb:.2f} MB)")
            return True
        else:
            print_warning(f"{description} exists but is EMPTY")
            return False
    else:
        print_error(f"{description} NOT found")
        print(f"   Expected at: {path}")
        return False

def validate_buildings_csv():
    """Validate buildings CSV structure"""
    try:
        import pandas as pd
        
        csv_path = "data/hyderabad_clipped.csv"
        if not Path(csv_path).exists():
            return False
        
        df = pd.read_csv(csv_path, nrows=5)  # Read first 5 rows for validation
        
        required_columns = ['lat', 'lon', 'height']
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            print_error(f"Buildings CSV missing columns: {missing_cols}")
            print(f"   Available columns: {list(df.columns)}")
            return False
        
        print_success(f"Buildings CSV structure valid")
        print(f"   Columns: {list(df.columns)}")
        
        # Count total rows
        total_rows = sum(1 for _ in open(csv_path)) - 1  # Subtract header
        print(f"   Total buildings: {total_rows:,}")
        
        return True
    except Exception as e:
        print_error(f"Error validating CSV: {e}")
        return False

def validate_nbs_geojson():
    """Validate NbS GeoJSON structure"""
    try:
        import geopandas as gpd
        
        geojson_files = list(Path('outputs/reports').glob('nbs_interventions_*.geojson'))
        if not geojson_files:
            print_error("No NbS GeoJSON files found")
            print("   Run: python main.py")
            return False
        
        latest = sorted(geojson_files, key=lambda x: x.stat().st_mtime)[-1]
        gdf = gpd.read_file(latest)
        
        # Filter out 'None' interventions
        nbs_zones = gdf[gdf['Proposed_NbS'] != 'None']
        
        if len(nbs_zones) == 0:
            print_warning("NbS GeoJSON has no intervention zones")
            return False
        
        print_success(f"NbS GeoJSON valid")
        print(f"   File: {latest.name}")
        print(f"   Intervention zones: {len(nbs_zones):,}")
        print(f"   NbS types: {list(nbs_zones['Proposed_NbS'].unique())}")
        
        return True
    except Exception as e:
        print_error(f"Error validating GeoJSON: {e}")
        return False

def check_config():
    """Check project configuration"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.config import CITY_LAT, CITY_LON, CITY_NAME
        
        print_success(f"Project config loaded")
        print(f"   City: {CITY_NAME}")
        print(f"   Coordinates: ({CITY_LAT}, {CITY_LON})")
        
        return True
    except Exception as e:
        print_warning(f"Could not load project config: {e}")
        print("   Will use default Hyderabad coordinates")
        return True  # Non-critical

def main():
    print_header("4D VISUALIZATION SETUP VALIDATOR")
    
    all_checks_passed = True
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. CHECK PYTHON DEPENDENCIES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print(f"\n{Colors.BOLD}1. Python Dependencies{Colors.END}")
    print("─" * 80)
    
    dependencies = [
        ('streamlit', 'streamlit'),
        ('pydeck', 'pydeck'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('geopandas', 'geopandas'),
        ('shapely', 'shapely'),
        ('requests', 'requests'),
    ]
    
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_checks_passed = False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. CHECK PROJECT CONFIGURATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print(f"\n{Colors.BOLD}2. Project Configuration{Colors.END}")
    print("─" * 80)
    
    check_config()
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. CHECK DATA FILES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print(f"\n{Colors.BOLD}3. Data Files{Colors.END}")
    print("─" * 80)
    
    # Buildings data
    if not check_file('data/hyderabad_clipped.csv', 'Google Buildings CSV'):
        print("   Generate with: python tools/fetch_data.py")
        all_checks_passed = False
    else:
        if not validate_buildings_csv():
            all_checks_passed = False
    
    # NbS data
    if not validate_nbs_geojson():
        print("   Generate with: python main.py")
        all_checks_passed = False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. CHECK SCRIPT FILES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print(f"\n{Colors.BOLD}4. Script Files{Colors.END}")
    print("─" * 80)
    
    scripts = [
        ('tools/fetch_data.py', 'Data fetcher script'),
        ('tools/nbs_engine.py', '4D visualization engine'),
        ('run_4d_visualization.sh', 'Launcher script'),
    ]
    
    for script_path, description in scripts:
        if not check_file(script_path, description):
            all_checks_passed = False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5. FINAL SUMMARY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n" + "═" * 80)
    if all_checks_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.END}\n")
        print("Ready to launch 4D visualization:")
        print(f"  {Colors.BLUE}streamlit run tools/nbs_engine.py{Colors.END}")
        print("Or use the automated script:")
        print(f"  {Colors.BLUE}./run_4d_visualization.sh{Colors.END}")
        print()
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED{Colors.END}\n")
        print("Please resolve the issues above before running the 4D engine.")
        print("\nQuick fixes:")
        print(f"  1. Install dependencies: {Colors.BLUE}pip install -r requirements.txt{Colors.END}")
        print(f"  2. Fetch building data: {Colors.BLUE}python tools/fetch_data.py{Colors.END}")
        print(f"  3. Run NbS analysis: {Colors.BLUE}python main.py{Colors.END}")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())

