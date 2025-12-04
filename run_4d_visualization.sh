#!/bin/bash
# Complete 4D Visualization Workflow Runner
# This script runs the complete pipeline: fetch data → analyze → visualize in 4D

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║              HYDERABAD NbS 4D VISUALIZATION - COMPLETE WORKFLOW              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 1: Check Dependencies
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}STEP 1: Checking Dependencies${NC}"
echo "────────────────────────────────────────────────────────────────────────────"

if ! python -c "import pydeck" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PyDeck not found. Installing...${NC}"
    pip install pydeck
else
    echo -e "${GREEN}✓ PyDeck installed${NC}"
fi

if ! python -c "import geopandas" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  GeoPandas not found. Installing...${NC}"
    pip install geopandas
else
    echo -e "${GREEN}✓ GeoPandas installed${NC}"
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 2: Fetch Google Buildings Data (if not exists)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}STEP 2: Fetching Google Buildings Data${NC}"
echo "────────────────────────────────────────────────────────────────────────────"

if [ -f "data/hyderabad_clipped.csv" ]; then
    echo -e "${GREEN}✓ Building data already exists${NC}"
    
    # Show file info
    num_buildings=$(wc -l < data/hyderabad_clipped.csv)
    file_size=$(du -h data/hyderabad_clipped.csv | cut -f1)
    echo "  Buildings: $((num_buildings - 1))"  # Subtract header
    echo "  File size: $file_size"
    
    read -p "Re-fetch data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Fetching fresh data..."
        python tools/fetch_data.py
    fi
else
    echo "Fetching Google Buildings data..."
    python tools/fetch_data.py
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 3: Run NbS Analysis (if not exists)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}STEP 3: Running NbS Analysis${NC}"
echo "────────────────────────────────────────────────────────────────────────────"

if ls outputs/reports/nbs_interventions_*.geojson 1> /dev/null 2>&1; then
    echo -e "${GREEN}✓ NbS analysis results already exist${NC}"
    
    latest_geojson=$(ls -t outputs/reports/nbs_interventions_*.geojson | head -1)
    num_features=$(python -c "import geopandas as gpd; print(len(gpd.read_file('$latest_geojson')))")
    echo "  NbS zones: $num_features"
    echo "  File: $(basename $latest_geojson)"
    
    read -p "Re-run analysis? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Running analysis..."
        python main.py
    fi
else
    echo "Running NbS analysis (this may take 1-2 minutes)..."
    python main.py
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 4: Validate Data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}STEP 4: Validating Data${NC}"
echo "────────────────────────────────────────────────────────────────────────────"

# Validate buildings CSV
if python -c "
import pandas as pd
import sys
try:
    df = pd.read_csv('data/hyderabad_clipped.csv')
    required_cols = ['lat', 'lon', 'height']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        print(f'❌ Missing columns: {missing}')
        sys.exit(1)
    print(f'✓ Buildings CSV valid: {len(df)} rows')
    print(f'  Columns: {list(df.columns)}')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ Buildings data validated${NC}"
else
    echo -e "${YELLOW}⚠️  Buildings data validation failed${NC}"
    echo "Check data/hyderabad_clipped.csv"
    exit 1
fi

# Validate NbS GeoJSON
if python -c "
import geopandas as gpd
import sys
from pathlib import Path
try:
    geojson_files = list(Path('outputs/reports').glob('nbs_interventions_*.geojson'))
    if not geojson_files:
        print('❌ No NbS GeoJSON found')
        sys.exit(1)
    latest = sorted(geojson_files, key=lambda x: x.stat().st_mtime)[-1]
    gdf = gpd.read_file(latest)
    nbs_zones = gdf[gdf['Proposed_NbS'] != 'None']
    print(f'✓ NbS GeoJSON valid: {len(nbs_zones)} intervention zones')
    print(f'  Types: {list(nbs_zones[\"Proposed_NbS\"].unique())}')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ NbS data validated${NC}"
else
    echo -e "${YELLOW}⚠️  NbS data validation failed${NC}"
    echo "Run: python main.py"
    exit 1
fi

echo ""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STEP 5: Launch 4D Visualization Engine
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo -e "${BLUE}STEP 5: Launching 4D Visualization Engine${NC}"
echo "────────────────────────────────────────────────────────────────────────────"
echo ""
echo -e "${GREEN}✓ All data validated and ready!${NC}"
echo ""
echo "Starting Streamlit 4D engine..."
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                     4D VISUALIZATION ENGINE LAUNCHING                         ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║  The browser will open automatically at: http://localhost:8501               ║"
echo "║                                                                               ║"
echo "║  CONTROLS:                                                                    ║"
echo "║  • Use the slider to move between BEFORE (0%) and AFTER (100%)               ║"
echo "║  • Rotate: Left-click + drag                                                 ║"
echo "║  • Pan: Right-click + drag                                                   ║"
echo "║  • Zoom: Scroll wheel                                                        ║"
echo "║                                                                               ║"
echo "║  Press Ctrl+C to stop the server                                             ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

sleep 2

# Launch Streamlit
streamlit run tools/nbs_engine.py

echo ""
echo -e "${GREEN}✓ Visualization session ended${NC}"

