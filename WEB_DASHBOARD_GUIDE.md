# 🌐 Web Dashboard Guide

## Hyderabad NbS Interactive Web Dashboard

### Overview

The web dashboard provides an interactive, user-friendly interface to explore your Hyderabad Nature-based Solutions analysis results. Built with Streamlit, it offers real-time data exploration, interactive charts, and downloadable reports.

---

## 🚀 Quick Start

### 1. Install Additional Dependencies

```bash
pip install streamlit streamlit-folium plotly folium scipy
```

Or install all at once:

```bash
pip install -r requirements.txt
```

### 2. Launch the Dashboard

```bash
streamlit run web_app.py
```

The dashboard will automatically open in your web browser at `http://localhost:8501`

### 3. Alternative Launch Methods

```bash
# Specify port
streamlit run web_app.py --server.port 8502

# Run in headless mode (for servers)
streamlit run web_app.py --server.headless true

# With custom theme
streamlit run web_app.py --theme.base dark
```

---

## 🎯 Dashboard Features

### 📊 Main Components

#### **Header Section**
- Project title and branding
- Quick summary metrics (4 key KPIs)
- Visual cards showing:
  - Total grid cells
  - Study area coverage
  - Implementation costs
  - CO₂ sequestration

#### **Sidebar**
- Analysis information
- Date and location
- Coverage statistics
- Download buttons for:
  - Markdown reports
  - CSV data exports
  - JSON statistics

---

### 📑 Six Interactive Tabs

#### 1. 🗺️ **Interactive Map**

**Features:**
- Full interactive Folium map
- Click on grid cells for details
- Color-coded by NbS type
- Zoom, pan, and explore
- Popup information showing:
  - NbS recommendation
  - Density metrics
  - Roughness values
  - Building heights
  - Sky View Factor

**Controls:**
- Zoom in/out
- Pan across study area
- Click cells for detailed info
- Legend showing all NbS types

**Use Cases:**
- Spatial planning
- Identifying intervention locations
- Communicating with stakeholders
- Field work planning

---

#### 2. 📊 **Interventions**

**Features:**
- Summary statistics table
- Cost effectiveness horizontal bar chart
- 4-panel analysis:
  - Area by type (bar chart)
  - Cost by type (bar chart)
  - Area distribution (pie chart)
  - Cost distribution (pie chart)
- All charts are interactive (hover for details)

**Interactive Elements:**
- Hover over bars for exact values
- Click legend items to toggle visibility
- Zoom into specific sections
- Download charts as PNG

**Insights Provided:**
- Which interventions cover most area
- Where budget is allocated
- Cost-effectiveness comparison
- Relative proportions

---

#### 3. 🌿 **Benefits**

**Features:**
- Multi-benefit radar chart
  - Compares all NbS types
  - 6 benefit categories
  - Interactive hover details
  
- Benefit scores heatmap
  - Color-coded matrix
  - Easy comparison
  - Green gradient (higher = better)

- Environmental benefits (4 panels):
  - CO₂ sequestration
  - PM2.5 removal
  - Temperature reduction
  - Trees to plant

**Interactive Elements:**
- Hover for exact benefit scores
- Toggle NbS types on/off
- Zoom into specific metrics
- Export charts

**Use Cases:**
- Multi-criteria decision making
- Environmental impact reporting
- Grant applications
- Stakeholder presentations

---

#### 4. 🏙️ **Morphology**

**Features:**
- Four key metrics displayed:
  - Mean density (plan area fraction)
  - Mean roughness (z₀)
  - Mean building height
  - Mean Sky View Factor

- Distribution histograms (4 panels):
  - Interactive histograms
  - Mean value indicators (red lines)
  - Hover for bin details

- Correlation matrix:
  - Shows metric relationships
  - Color-coded (-1 to +1)
  - Interactive heatmap

**Interactive Elements:**
- Hover over histograms for frequencies
- Click bins for details
- Zoom into distributions
- Export correlation matrix

**Insights:**
- Understand urban fabric
- Identify patterns
- Validate calculations
- Research and analysis

---

#### 5. 📋 **Data Tables**

**Features:**
- **Intervention Summary Table**
  - All NbS types
  - Formatted numbers
  - Sortable columns
  - Full precision view

- **Grid Cell Data Table**
  - 441 detailed rows
  - Multiple filters:
    - Filter by NbS type (multi-select)
    - Filter by density range (slider)
  - Shows first 100 rows
  - Download capability

**Interactive Filters:**
```
NbS Type Filter:
☐ Green Roof
☐ Ventilation Corridor
☐ Permeable Pavement
☐ Rain Garden

Density Range: [0.0 ─────●─────●───── 1.0]
```

**Use Cases:**
- Detailed data exploration
- Finding specific cells
- Data validation
- Exporting filtered subsets

---

#### 6. 🖼️ **Static Reports**

**Features:**
- View all generated visualizations
- Dropdown selector for different charts
- Full-size image display
- Download individual images

**Available Visualizations:**
1. Intervention Analysis (4 panels)
2. Cost Effectiveness
3. Benefits Heatmap
4. Benefits Radar
5. Environmental Benefits (4 panels)
6. Morphology Distributions (4 histograms)
7. Morphology Correlation
8. Comprehensive Dashboard

**Use Cases:**
- Presentations
- Reports
- Publications
- Social media

---

## 🎨 Interactive Features

### Plotly Charts
All charts are powered by Plotly, providing:

**Hover Information:**
- Exact values on mouse hover
- Context-aware tooltips
- Multi-variable display

**Zoom & Pan:**
- Box zoom (drag to select area)
- Scroll zoom
- Double-click to reset
- Pan mode (click and drag)

**Export:**
- PNG download
- SVG export
- Interactive HTML

**Toggle:**
- Click legend items to show/hide
- Select/deselect categories
- Isolate specific data

### Filtering & Sorting
- Dynamic data filtering
- Real-time updates
- Multiple filter combinations
- Sort any column

### Responsive Design
- Adapts to screen size
- Mobile-friendly layouts
- Tablet optimized
- Full-screen support

---

## 💾 Download Capabilities

### From Sidebar:
1. **📄 Markdown Report**
   - Complete analysis report
   - Formatted text
   - Methodology included

2. **📊 Summary CSV**
   - Intervention summary
   - All metrics
   - Excel-ready

### From Tabs:
3. **🖼️ Individual Charts**
   - PNG format
   - High resolution
   - Publication quality

4. **📋 Filtered Data**
   - Custom selections
   - CSV export
   - Analysis-ready

---

## 🎯 Use Cases

### 1. **Stakeholder Presentations**
- Launch dashboard during meeting
- Navigate between tabs
- Show interactive map
- Drill down into specific metrics
- Answer questions in real-time

### 2. **Budget Planning**
- Review Interventions tab
- Analyze cost effectiveness
- Compare alternatives
- Export data for spreadsheets

### 3. **Environmental Reporting**
- Navigate to Benefits tab
- Show quantified impacts
- Export environmental charts
- Include in reports

### 4. **Urban Planning**
- Use interactive map
- Identify intervention zones
- Review morphology patterns
- Export spatial data

### 5. **Research & Analysis**
- Explore Data Tables tab
- Apply filters
- Export subsets
- Validate calculations

---

## 🔧 Customization

### Theme Options

**Light Theme (default):**
```bash
streamlit run web_app.py
```

**Dark Theme:**
```bash
streamlit run web_app.py --theme.base dark
```

**Custom Theme:**
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#2ecc71"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

### Port Configuration

```bash
# Default (8501)
streamlit run web_app.py

# Custom port
streamlit run web_app.py --server.port 8080

# Multiple instances
streamlit run web_app.py --server.port 8502
```

### Performance Tuning

```bash
# Increase memory
streamlit run web_app.py --server.maxUploadSize 200

# Enable caching
streamlit run web_app.py --server.enableCORS false

# Headless mode (servers)
streamlit run web_app.py --server.headless true
```

---

## 📱 Access Options

### Local Access
```
http://localhost:8501
```

### Network Access
```
http://<your-ip>:8501
```

Find your IP:
```bash
# Linux/Mac
hostname -I

# Windows
ipconfig
```

### Cloud Deployment

**Streamlit Cloud (Free):**
1. Push to GitHub
2. Visit streamlit.io/cloud
3. Connect repository
4. Deploy automatically

**Heroku:**
```bash
# Create Procfile
web: streamlit run web_app.py --server.port $PORT

# Deploy
heroku create
git push heroku main
```

---

## 🐛 Troubleshooting

### Dashboard Won't Start

**Error:** `ModuleNotFoundError: No module named 'streamlit'`

**Solution:**
```bash
pip install streamlit streamlit-folium plotly
```

### No Data Displayed

**Error:** "No data found"

**Solution:**
```bash
# Run analysis first
python main.py

# Then launch dashboard
streamlit run web_app.py
```

### Map Not Loading

**Error:** Spatial data not found

**Solution:**
```bash
# Re-run analysis with GeoJSON export
python main.py
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Use different port
streamlit run web_app.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9
```

### Charts Not Interactive

**Issue:** Charts appear as static images

**Solution:**
- Ensure plotly is installed
- Clear browser cache
- Try different browser

---

## 🚀 Performance Tips

### For Large Datasets
1. **Enable Caching:**
   - Data automatically cached
   - Fast reload on navigation

2. **Filter Data:**
   - Use filters in Data Tables
   - Reduce displayed rows

3. **Close Unused Tabs:**
   - Each tab consumes resources
   - Navigate only as needed

### For Presentations
1. **Pre-load All Tabs:**
   - Click through once before demo
   - Ensures smooth navigation

2. **Use Full Screen:**
   - F11 in most browsers
   - Hide browser toolbars

3. **Clear Cache if Needed:**
   - Press 'C' in dashboard
   - Then 'Clear Cache'

---

## 🎓 Learning Resources

### Streamlit Documentation
- https://docs.streamlit.io
- Component gallery
- Tutorial videos

### Plotly Documentation
- https://plotly.com/python/
- Chart types
- Customization options

### Folium Documentation
- https://python-visualization.github.io/folium/
- Map features
- Markers and layers

---

## 🔄 Updates & Maintenance

### After New Analysis
```bash
# Run new analysis
python main.py --lat <new_lat> --lon <new_lon>

# Refresh dashboard (automatic)
# Or press 'R' in dashboard to reload
```

### Update Visualizations
```bash
# Regenerate charts
python tools/visualize_results.py

# Refresh browser to see new images
```

### Clear Cache
```bash
# In dashboard: Press 'C' then 'Clear Cache'
# Or delete cache directory
rm -rf ~/.streamlit/cache
```

---

## 📊 Dashboard Metrics

**Loading Performance:**
- Initial load: ~2-3 seconds
- Tab switching: <1 second
- Chart interactions: Real-time

**Data Handling:**
- Grid cells: 441 (fast)
- Charts: 8 interactive
- Maps: Full-featured Folium

**Browser Support:**
- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ IE11 (limited support)

---

## 🎯 Best Practices

### For Presentations:
1. Test dashboard before meeting
2. Pre-load all tabs
3. Use full-screen mode
4. Prepare talking points per tab
5. Have backup static images ready

### For Analysis:
1. Start with Summary metrics
2. Use Interactive Map first
3. Drill down to specific tabs
4. Export data as needed
5. Save filtered views

### For Reporting:
1. Capture screenshots
2. Export key charts
3. Download data tables
4. Include in documents
5. Reference interactive version

---

## 📞 Support & Help

### Quick Help
- Press '?' in dashboard for shortcuts
- Hover over elements for tooltips
- Check browser console for errors

### Common Shortcuts
- **R**: Reload data
- **C**: Clear cache
- **?**: Show help
- **ESC**: Close menus

### Getting Help
1. Check error messages in terminal
2. Review this guide
3. Check Streamlit documentation
4. Verify data files exist

---

## 🎉 Summary

The web dashboard provides:

✅ **Interactive Exploration**
- Click, zoom, filter, explore

✅ **Real-time Updates**
- Data refreshes automatically

✅ **Professional Visualizations**
- Publication-quality charts

✅ **Easy Sharing**
- Share URL with colleagues

✅ **Multi-device Support**
- Works on desktop, tablet, mobile

✅ **Download Capabilities**
- Export reports and data

✅ **No Coding Required**
- User-friendly interface

---

**Ready to explore your NbS analysis interactively!** 🚀

```bash
streamlit run web_app.py
```

Then open: http://localhost:8501

---

*Last Updated: December 1, 2025*  
*Dashboard Version: 1.0*  
*Powered by Streamlit + Plotly + Folium*

