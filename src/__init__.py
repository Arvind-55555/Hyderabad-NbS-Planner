"""
Hyderabad Nature-based Solutions (NbS) Planner
A comprehensive tool for urban climate resilience planning

Modules:
    - config: Configuration and constants
    - data_loader: Data fetching from OSM, weather APIs
    - morphology: Urban morphology calculations
    - nbs_logic: NbS decision engine
    - visualization: Map and plot generation
    - reporting: Statistics and report generation
    - utils: Helper functions and utilities
"""

__version__ = "1.0.0"
__author__ = "Hyderabad NbS Project"

from . import config
from . import data_loader
from . import morphology
from . import nbs_logic
from . import visualization
from . import reporting
from . import utils

__all__ = [
    'config',
    'data_loader',
    'morphology',
    'nbs_logic',
    'visualization',
    'reporting',
    'utils'
]

