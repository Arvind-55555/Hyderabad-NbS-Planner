# Visualization Guide

## Overview of Generated Charts

This document explains all the visualizations created from your Hyderabad NbS analysis.

---

## 📊 1. Intervention Analysis (`intervention_analysis.png`)

**Four-panel comprehensive analysis of interventions:**

### Panel A: Area by Type (Bar Chart)
- Shows total area (hectares) for each NbS intervention
- **Largest**: Permeable Pavement (240.75 ha)
- **Smallest**: Green Roof (4.5 ha)
- Values labeled on each bar

### Panel B: Cost by Type (Bar Chart)
- Implementation costs in Crores INR
- **Most Expensive**: Permeable Pavement (₹19.26 Cr)
- **Least Expensive**: Green Roof (₹0.68 Cr)
- Total project cost: ₹38.56 Crores

### Panel C: Area Distribution (Pie Chart)
- Percentage breakdown of total intervention area
- Visualizes relative proportion of each NbS type
- Permeable Pavement dominates at ~49%

### Panel D: Cost Distribution (Pie Chart)
- Percentage breakdown of total costs
- Shows where budget allocation goes
- Helps identify cost-intensive interventions

**Use This For:**
- Budget planning
- Area allocation decisions
- Stakeholder presentations
- Comparing intervention scales

---

## 💰 2. Cost Effectiveness (`cost_effectiveness.png`)

**Horizontal bar chart showing cost per square meter for each NbS type**

### Key Insights:
- **Most Cost-Effective**: Rain Garden (₹70/m²)
- **Least Cost-Effective**: Green Roof (₹150/m²)
- Lower values = better cost-effectiveness
- Helps prioritize interventions for budget-constrained projects

**Formula**: Cost per m² = (Total Cost / Total Area)

**Use This For:**
- Budget optimization
- ROI analysis
- Choosing interventions for pilot projects
- Justifying intervention selection

---

## 🌿 3. Benefits Heatmap (`benefits_heatmap.png`)

**Matrix showing multi-benefit scores (0-5 scale) for each NbS type**

### Benefit Categories Assessed:
1. **Climate Adaptation**: Temperature reduction, UHI mitigation
2. **Biodiversity**: Habitat creation, species support
3. **Air Quality**: PM2.5 removal, pollutant filtration
4. **Water Management**: Stormwater retention, groundwater recharge
5. **Social Well-being**: Recreation, aesthetics, mental health
6. **Economic Value**: Property values, energy savings, job creation

### Color Code:
- **Dark Green**: High benefit (score 5)
- **Light Green**: Moderate benefit (score 2-4)
- **Yellow**: Low benefit (score 0-1)

### Key Findings:
- **Rain Garden**: Excellent for water management (5) and biodiversity (4)
- **Permeable Pavement**: Best for water management (5)
- **Green Roof**: Balanced across multiple benefits

**Use This For:**
- Multi-criteria decision making
- Identifying intervention strengths
- Communicating co-benefits to stakeholders
- Aligning with SDG goals

---

## 🕸️ 4. Benefits Radar Chart (`benefits_radar.png`)

**Spider/Radar plot comparing top 4 NbS types across 6 benefit categories**

### How to Read:
- Each colored line represents one NbS type
- Larger area = more benefits overall
- Shape shows benefit profile (balanced vs. specialized)

### Patterns:
- **Green Roof**: Balanced pentagonal shape (good all-around)
- **Permeable Pavement**: Elongated toward water management
- **Rain Garden**: Strong in biodiversity and water
- **Ventilation Corridor**: Specialized for climate and air quality

**Use This For:**
- Quick visual comparison
- Identifying complementary interventions
- Portfolio optimization (mix interventions for full coverage)
- Scientific presentations

---

## 🌳 5. Environmental Benefits (`environmental_benefits.png`)

**Four-panel quantification of specific environmental impacts**

### Panel A: Temperature Reduction (°C)
- Cooling effect per NbS type
- **Best**: Green Roof (7°C reduction)
- Cumulative effect across all interventions

### Panel B: PM2.5 Removal (kg/year)
- Air quality improvement
- **Best**: Ventilation Corridor (40.3 kg/yr)
- Total removal: 152.8 kg/year
- Equivalent to removing X vehicles from roads

### Panel C: CO₂ Sequestration (kg/year)
- Carbon offset potential
- **Best**: Green Roof (67.5 tonnes/yr)
- Total sequestration: 126.6 tonnes/year
- Equivalent to offsetting X flights

### Panel D: Trees to be Planted
- Physical implementation scale
- **Most**: Ventilation Corridor (2,688 trees)
- Total trees: 2,688 across all interventions

**Use This For:**
- Climate action reporting (NDCs, city climate plans)
- Quantifying environmental ROI
- Grant applications
- Public awareness campaigns

---

## 🏙️ 6. Morphology Distributions (`morphology_distributions.png`)

**Four histograms showing distribution of urban morphology metrics across the study area**

### Panel A: Plan Area Density
- Distribution of building coverage (0-1)
- Mean: 0.096 (9.6% built)
- Shows mostly low-density area

### Panel B: Roughness Length (m)
- Measure of airflow resistance
- Mean: 0.288m (low-medium roughness)
- Higher values = more stagnant air

### Panel C: Building Height (m)
- Distribution of average building heights per cell
- Mean: 4.67m (~1.5 floors)
- Indicates low-rise development pattern

### Panel D: Sky View Factor (SVF)
- Openness to sky (0-1)
- Mean: 0.971 (very open)
- High SVF = good natural ventilation

### Statistical Features:
- **Histogram**: Frequency distribution
- **KDE Line**: Smoothed trend (black line)
- **Red Dashed**: Mean value
- **Blue Dashed**: Median value

**Use This For:**
- Understanding urban fabric
- Identifying urban typologies
- Baseline for monitoring changes
- Academic research

---

## 🔗 7. Morphology Correlation (`morphology_correlation.png`)

**Correlation matrix showing relationships between morphology metrics**

### How to Read:
- **+1.0 (Dark Red)**: Perfect positive correlation
- **0.0 (White)**: No correlation
- **-1.0 (Dark Blue)**: Perfect negative correlation

### Key Relationships:
- **Density ↔ Roughness**: Strong positive (0.8+)
  - More buildings → more airflow resistance
- **Density ↔ SVF**: Strong negative (-0.7+)
  - More buildings → less open sky
- **Height ↔ Roughness**: Positive correlation
  - Taller buildings increase roughness

**Use This For:**
- Understanding urban physics
- Validating morphology calculations
- Identifying interdependencies
- Planning interventions that address multiple issues

---

## 📈 8. Comprehensive Dashboard (`comprehensive_dashboard.png`)

**All-in-one summary with 10 panels**

### Top Row (Panels 1-3):
1. **Area by Type**: Bar chart of intervention areas
2. **Cost by Type**: Bar chart of costs
3. **Area Distribution**: Pie chart

### Second Row (Panels 4-6):
4. **Grid Cells**: Number of cells per intervention
5. **Cost per Hectare**: Cost efficiency
6. **Statistics Table**: Key metrics summary

### Third Row (Panels 7-9):
7. **CO₂ Sequestration**: Environmental benefit
8. **PM2.5 Removal**: Air quality benefit
9. **Trees Planted**: Implementation scale

### Bottom Row (Panel 10):
10. **Multi-benefit Comparison**: Grouped bar chart showing all 6 benefit categories for all NbS types

**Use This For:**
- Executive presentations
- Project overview
- Stakeholder meetings
- Quick reference

---

## 📁 File Sizes & Details

| Visualization | File Size | Panels | Resolution |
|--------------|-----------|--------|------------|
| Intervention Analysis | 511 KB | 4 | 300 DPI |
| Cost Effectiveness | 155 KB | 1 | 300 DPI |
| Benefits Heatmap | 272 KB | 1 | 300 DPI |
| Benefits Radar | 414 KB | 1 | 300 DPI |
| Environmental Benefits | 398 KB | 4 | 300 DPI |
| Morphology Distributions | 394 KB | 4 | 300 DPI |
| Morphology Correlation | 170 KB | 1 | 300 DPI |
| Comprehensive Dashboard | 758 KB | 10 | 300 DPI |

**Total**: 3.1 MB for all 8 visualizations

---

## 🎯 How to Use These Visualizations

### For Budget Planning:
1. Start with **Cost Effectiveness** chart
2. Reference **Intervention Analysis** (cost panels)
3. Use **Dashboard** for executive summary

### For Environmental Reporting:
1. Focus on **Environmental Benefits** chart
2. Use **Benefits Heatmap** for multi-benefit assessment
3. Include **Dashboard** bottom panels for totals

### For Urban Planning:
1. Study **Morphology Distributions**
2. Review **Morphology Correlation** for relationships
3. Use insights to refine intervention placement

### For Presentations:
1. **Dashboard**: Overview slide
2. **Intervention Analysis**: Budget and area details
3. **Benefits Radar**: Quick comparison
4. **Environmental Benefits**: Impact quantification

### For Reports:
- Include all visualizations in appendix
- Use Dashboard as executive summary
- Reference specific charts in methodology section

---

## 🔧 Customization

To regenerate with different settings:

```bash
# All visualizations
python tools/visualize_results.py

# Only specific types
python tools/visualize_results.py --charts interventions benefits

# From different output directory
python tools/visualize_results.py --output-dir path/to/outputs
```

---

## 📊 Data Sources

All visualizations are generated from:
- `outputs/reports/csv/nbs_summary.csv` - Intervention summary
- `outputs/reports/csv/nbs_grid_data.csv` - Detailed grid analysis
- `outputs/reports/nbs_statistics_*.json` - Aggregated statistics
- `outputs/reports/nbs_interventions_*.geojson` - Spatial data

---

## 🎨 Color Scheme

**NbS Type Colors** (consistent across all charts):
- 🟢 **Green Roof**: #2ecc71 (Green)
- 🔵 **Ventilation Corridor**: #3498db (Blue)
- 🟢 **Urban Forest**: #27ae60 (Dark Green)
- ⚫ **Permeable Pavement**: #95a5a6 (Grey)
- 🔷 **Rain Garden**: #16a085 (Turquoise)
- 🔵 **Wetland Restoration**: #1abc9c (Teal)

**Analysis Colors**:
- Cost: Red (#e74c3c)
- Area: Green (#2ecc71)
- Benefits: Green gradient (YlGn)
- Morphology: Viridis/Plasma

---

## 💡 Tips for Interpretation

### When Area & Cost Don't Match:
- Indicates differences in cost per unit area
- High cost, low area → expensive intervention (Green Roof)
- Low cost, high area → cost-effective intervention (Rain Garden)

### Multi-benefit Scores:
- Score 5: Excellent performance
- Score 3-4: Good performance
- Score 1-2: Moderate performance
- Score 0: Minimal benefit

### Morphology Metrics:
- **High Density + High Roughness** → Poor ventilation, heat island
- **Low SVF** → Urban canyons, limited sky visibility
- **Low Density + High SVF** → Open, well-ventilated areas

---

## 📱 Sharing & Exporting

**For Reports**: All images are 300 DPI (publication quality)

**For Presentations**: Resize to fit slides (16:9 or 4:3)

**For Social Media**: Crop to 1080x1080 for Instagram/LinkedIn

**For Web**: Convert to WebP for smaller file sizes

---

## 🆘 Troubleshooting

**Charts look empty?**
- Check that analysis completed successfully
- Verify CSV files contain data
- Re-run main.py if needed

**Colors don't match map?**
- Colors are consistent with NBS_COLORS in config.py
- Check if NbS types match between runs

**Need more detail?**
- Increase grid resolution in main analysis
- Run with larger study area
- Generate custom charts using pandas/matplotlib

---

## 📚 References

**Visualization Best Practices:**
- Tufte, E. (2001). *The Visual Display of Quantitative Information*
- Few, S. (2012). *Show Me the Numbers*

**Color Schemes:**
- ColorBrewer 2.0 (colorbrewer2.org)
- Material Design Colors

**Urban Morphology:**
- Grimmond & Oke (1999) - Morphology metrics
- Stewart & Oke (2012) - Local Climate Zones

---

**Generated**: December 1, 2025  
**Analysis**: Charminar, Hyderabad (1.5km radius)  
**Tool**: Hyderabad NbS Planner v1.0

---

*For questions or custom visualizations, refer to tools/visualize_results.py*

