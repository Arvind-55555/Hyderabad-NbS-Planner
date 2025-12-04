# Hyderabad NbS 4D Visualization - React App

Standalone React application for 4D visualization of Nature-based Solutions in Hyderabad.

## Features

- 🌍 **Real-time 3D visualization** with 5,000+ buildings from OpenStreetMap
- 🎚️ **Temporal slider** for BEFORE/AFTER scenarios (0% → 100%)
- 📊 **Interactive charts** and statistics
- 🎥 **4 camera presets** (Default 3D, Top Down, Oblique, Street Level)
- 🌳 **217 NbS intervention zones** with enhanced visualization
- 📈 **Comprehensive metrics** dashboard
- ⚡ **Performance optimized** with React and Deck.gl

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

Opens at: http://localhost:3000

## Build for Production

```bash
npm run build
```

Output: `dist/` directory

## Deploy to GitHub Pages

```bash
npm run deploy
```

This will:
1. Build the app
2. Deploy to `gh-pages` branch
3. Make it available at: `https://arvind-55555.github.io/Hyderabad-NbS-Planner/`

## Configuration

### Mapbox Token

1. Get a free token at: https://account.mapbox.com/access-tokens/
2. Create `.env` file:
   ```
   VITE_MAPBOX_TOKEN=your_token_here
   ```

### Data Files

The app expects these files in the repository:
- `data/hyderabad_clipped.csv` - Building data
- `outputs/reports/nbs_interventions_*.geojson` - NbS interventions

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx      # Control panel
│   │   ├── Statistics.jsx   # Metrics display
│   │   └── *.css            # Component styles
│   ├── utils/
│   │   └── constants.js     # Configuration
│   ├── App.jsx              # Main app component
│   ├── App.css              # App styles
│   ├── main.jsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies
├── vite.config.js          # Vite configuration
└── index.html              # HTML template
```

## Technologies

- **React 18** - UI framework
- **Deck.gl** - 3D visualization (WebGL)
- **React Map GL** - Map integration
- **Mapbox GL** - Base maps
- **PapaParse** - CSV parsing
- **Vite** - Build tool

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires WebGL support.

