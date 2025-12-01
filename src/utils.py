"""
Utilities Module
Helper functions for logging, caching, file operations, and common tasks
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import pickle

from .config import LOG_LEVEL, LOG_FORMAT, LOG_FILE, PROJECT_ROOT


def setup_logging(log_file=LOG_FILE, log_level=LOG_LEVEL):
    """
    Setup logging configuration for the application
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Level: {log_level}, File: {log_file}")
    
    return logger


def ensure_directories():
    """
    Ensure all required directories exist
    """
    from .config import (
        CACHE_DIR, OUTPUT_DIR, MAPS_DIR, 
        REPORTS_DIR, EXPORTS_DIR, REFERENCE_DIR
    )
    
    directories = [
        CACHE_DIR,
        OUTPUT_DIR,
        MAPS_DIR,
        REPORTS_DIR,
        EXPORTS_DIR,
        REFERENCE_DIR
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(__name__)
    logger.debug("All required directories verified/created.")


def format_area(area_sqm):
    """
    Format area in human-readable units
    
    Args:
        area_sqm: Area in square meters
    
    Returns:
        str: Formatted area string
    """
    if area_sqm < 10000:
        return f"{area_sqm:.2f} m²"
    else:
        return f"{area_sqm / 10000:.2f} ha"


def format_cost(cost_inr):
    """
    Format cost in Indian Rupee notation
    
    Args:
        cost_inr: Cost in INR
    
    Returns:
        str: Formatted cost string
    """
    if cost_inr < 100000:  # Less than 1 lakh
        return f"₹{cost_inr:,.2f}"
    elif cost_inr < 10000000:  # Less than 1 crore
        lakhs = cost_inr / 100000
        return f"₹{lakhs:.2f} Lakhs"
    else:
        crores = cost_inr / 10000000
        return f"₹{crores:.2f} Crores"


def format_percentage(value, decimals=1):
    """
    Format value as percentage
    
    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places
    
    Returns:
        str: Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_number(number, decimals=2):
    """
    Format number with thousand separators
    
    Args:
        number: Number to format
        decimals: Number of decimal places
    
    Returns:
        str: Formatted number string
    """
    return f"{number:,.{decimals}f}"


def get_timestamp():
    """
    Get current timestamp string
    
    Returns:
        str: Timestamp in YYYYMMDD_HHMMSS format
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def get_date_string():
    """
    Get current date string
    
    Returns:
        str: Date in YYYY-MM-DD format
    """
    return datetime.now().strftime('%Y-%m-%d')


def save_pickle(obj, filepath):
    """
    Save object to pickle file
    
    Args:
        obj: Object to save
        filepath: Path to save file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)
    
    logger = logging.getLogger(__name__)
    logger.debug(f"Object saved to pickle: {filepath}")


def load_pickle(filepath):
    """
    Load object from pickle file
    
    Args:
        filepath: Path to pickle file
    
    Returns:
        Loaded object or None if file doesn't exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return None
    
    with open(filepath, 'rb') as f:
        obj = pickle.load(f)
    
    logger = logging.getLogger(__name__)
    logger.debug(f"Object loaded from pickle: {filepath}")
    
    return obj


def save_json(data, filepath, indent=2):
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
        indent: JSON indentation
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    
    logger = logging.getLogger(__name__)
    logger.debug(f"JSON saved to: {filepath}")


def load_json(filepath):
    """
    Load dictionary from JSON file
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Loaded dictionary or None if file doesn't exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger = logging.getLogger(__name__)
    logger.debug(f"JSON loaded from: {filepath}")
    
    return data


def get_file_size(filepath):
    """
    Get human-readable file size
    
    Args:
        filepath: Path to file
    
    Returns:
        str: Formatted file size
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return "File not found"
    
    size_bytes = filepath.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} TB"


def print_progress(current, total, prefix='Progress:', suffix='Complete', length=50):
    """
    Print progress bar to console
    
    Args:
        current: Current iteration
        total: Total iterations
        prefix: Prefix string
        suffix: Suffix string
        length: Length of progress bar
    """
    percent = 100 * (current / float(total))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    
    print(f'\r{prefix} |{bar}| {percent:.1f}% {suffix}', end='', flush=True)
    
    if current == total:
        print()  # New line on completion


def validate_coordinates(lat, lon):
    """
    Validate latitude and longitude values
    
    Args:
        lat: Latitude value
        lon: Longitude value
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not (-90 <= lat <= 90):
        return False, f"Invalid latitude: {lat}. Must be between -90 and 90."
    
    if not (-180 <= lon <= 180):
        return False, f"Invalid longitude: {lon}. Must be between -180 and 180."
    
    return True, "Coordinates are valid."


def calculate_bounds_area(bounds):
    """
    Calculate area of bounding box in square meters
    
    Args:
        bounds: Tuple of (minx, miny, maxx, maxy) in UTM coordinates
    
    Returns:
        float: Area in square meters
    """
    minx, miny, maxx, maxy = bounds
    width = maxx - minx
    height = maxy - miny
    return width * height


def summarize_dataframe(df, name="DataFrame"):
    """
    Print summary of DataFrame
    
    Args:
        df: pandas DataFrame or GeoDataFrame
        name: Name of the DataFrame
    """
    logger = logging.getLogger(__name__)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"{name} Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    logger.info(f"Columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    if hasattr(df, 'crs'):
        logger.info(f"CRS: {df.crs}")
    
    logger.info(f"{'='*60}\n")


def check_dependencies():
    """
    Check if all required dependencies are installed
    
    Returns:
        dict: Dictionary of {package: version or error}
    """
    packages = [
        'osmnx',
        'geopandas',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'requests',
        'shapely',
        'rasterio',
        'sklearn'
    ]
    
    results = {}
    
    for package in packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown version')
            results[package] = f"✓ {version}"
        except ImportError:
            results[package] = "✗ Not installed"
    
    return results


def print_banner():
    """
    Print application banner
    """
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           HYDERABAD NATURE-BASED SOLUTIONS PLANNER           ║
    ║                                                               ║
    ║           Urban Climate Resilience & Green Infrastructure    ║
    ║                                                               ║
    ║           Based on G20 NbS Working Paper Framework           ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(stats):
    """
    Print summary statistics to console
    
    Args:
        stats: Summary statistics dictionary
    """
    print("\n" + "="*70)
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    if 'analysis_metadata' in stats:
        meta = stats['analysis_metadata']
        print(f"\nCity: {meta['city']}")
        print(f"Date: {meta['analysis_date']}")
        print(f"Total Grid Cells: {meta['total_grid_cells']}")
        print(f"Intervention Cells: {meta['cells_with_interventions']}")
        print(f"Coverage: {meta['intervention_coverage_pct']:.1f}%")
    
    if 'area_statistics' in stats:
        area = stats['area_statistics']
        print(f"\nTotal Study Area: {area['total_study_area_hectares']:.2f} ha")
        print(f"Intervention Area: {area['total_intervention_area_hectares']:.2f} ha")
    
    if 'financial' in stats:
        fin = stats['financial']
        print(f"\nTotal Cost: {format_cost(fin['total_cost_inr'])}")
        print(f"Cost per Hectare: {format_cost(fin['average_cost_per_hectare'])}")
    
    if 'interventions_by_type' in stats:
        print("\nInterventions by Type:")
        print("-" * 70)
        for nbs_type, data in stats['interventions_by_type'].items():
            print(f"  {nbs_type:25s} | {data['area_hectares']:8.2f} ha | "
                  f"{format_cost(data['cost_crores'] * 10000000):15s}")
    
    print("="*70 + "\n")


class Timer:
    """Context manager for timing code blocks"""
    
    def __init__(self, name="Operation"):
        self.name = name
        self.logger = logging.getLogger(__name__)
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting: {self.name}")
        return self
    
    def __exit__(self, *args):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        self.logger.info(f"Completed: {self.name} in {duration:.2f} seconds")


if __name__ == "__main__":
    # Test utilities
    setup_logging()
    print_banner()
    
    print("\nChecking dependencies...")
    deps = check_dependencies()
    for package, status in deps.items():
        print(f"  {package:15s}: {status}")
    
    print("\nUtilities module loaded successfully.")

