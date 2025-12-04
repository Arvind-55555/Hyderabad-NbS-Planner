"""
Streamlit App Entry Point for Streamlit Cloud Deployment
This file serves as the main entry point for the 4D visualization engine
"""

# For Streamlit Cloud, we can directly run the nbs_engine.py
# This file exists for compatibility and can be used as an alternative entry point

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the main engine (it will run automatically)
# Note: For deployment, configure Streamlit Cloud to use tools/nbs_engine.py directly

