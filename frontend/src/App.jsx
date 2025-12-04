import React, { useState, useEffect, useMemo } from 'react';
import DeckGL from '@deck.gl/react';
import { Map } from 'react-map-gl';
import { ColumnLayer, HeatmapLayer, PolygonLayer } from '@deck.gl/layers';
import Papa from 'papaparse';
import './App.css';
import Sidebar from './components/Sidebar';
import Statistics from './components/Statistics';
import { INITIAL_VIEW_STATE, MAPBOX_TOKEN } from './utils/constants';

// Mapbox token - replace with your own or use public token
const MAPBOX_ACCESS_TOKEN = MAPBOX_TOKEN || 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXV4NTFmZ2Y5M2M2YzBmN2RkM2YifQ.rJcFIG214AriISLbB6B5aw';

function App() {
  const [buildings, setBuildings] = useState([]);
  const [nbsInterventions, setNbsInterventions] = useState([]);
  const [scenarioStage, setScenarioStage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cameraPreset, setCameraPreset] = useState('Default 3D');
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  // Load buildings data
  useEffect(() => {
    async function loadBuildings() {
      try {
        // Try multiple paths for different deployment platforms
        const basePath = window.location.pathname.includes('/Hyderabad-NbS-Planner/') 
          ? '/Hyderabad-NbS-Planner' 
          : '';
        const paths = [
          `${basePath}/data/hyderabad_clipped.csv`,
          '/data/hyderabad_clipped.csv',
          './data/hyderabad_clipped.csv'
        ];
        
        let response;
        for (const path of paths) {
          try {
            response = await fetch(path);
            if (response.ok) break;
          } catch (e) {
            continue;
          }
        }
        
        if (!response || !response.ok) {
          throw new Error('Failed to load buildings data');
        }
        if (!response.ok) {
          throw new Error('Failed to load buildings data');
        }
        const text = await response.text();
        
        Papa.parse(text, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            const data = results.data.map(row => ({
              lat: parseFloat(row.lat || row.latitude),
              lon: parseFloat(row.lon || row.longitude),
              height: parseFloat(row.height || 10),
              area: parseFloat(row.area_in_meters || 100),
              building_type: row.building_type || 'yes',
              source: row.source || 'osm'
            })).filter(b => !isNaN(b.lat) && !isNaN(b.lon));
            
            setBuildings(data);
            setLoading(false);
          },
          error: (err) => {
            setError('Failed to parse buildings data');
            setLoading(false);
          }
        });
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    loadBuildings();
  }, []);

  // Load NbS interventions
  useEffect(() => {
    async function loadNbsData() {
      try {
        // Try multiple paths for different deployment platforms
        const basePath = window.location.pathname.includes('/Hyderabad-NbS-Planner/') 
          ? '/Hyderabad-NbS-Planner' 
          : '';
        const paths = [
          `${basePath}/outputs/reports/nbs_interventions_20251201_124521.geojson`,
          '/outputs/reports/nbs_interventions_20251201_124521.geojson',
          './outputs/reports/nbs_interventions_20251201_124521.geojson'
        ];
        
        let response;
        for (const path of paths) {
          try {
            response = await fetch(path);
            if (response.ok) break;
          } catch (e) {
            continue;
          }
        }
        
        if (!response || !response.ok) {
        if (!response.ok) {
          console.warn('NbS data not found, continuing without it');
          return;
        }
        const geojson = await response.json();
        
        const interventions = geojson.features
          .filter(f => f.properties.Proposed_NbS !== 'None')
          .map(feature => ({
            ...feature,
            properties: {
              ...feature.properties,
              nbs_type: feature.properties.Proposed_NbS
            }
          }));
        
        setNbsInterventions(interventions);
      } catch (err) {
        console.warn('Could not load NbS data:', err);
      }
    }

    loadNbsData();
  }, []);

  // Prepare building colors based on height and stage
  const buildingData = useMemo(() => {
    return buildings.map(building => {
      let r = 100, g = 100, b = 110;
      
      // Height-based coloring
      if (building.height > 15) {
        r = 140; g = 140; b = 150;
      } else if (building.height > 10) {
        r = 120; g = 120; b = 130;
      }
      
      // Subtle green tint as NbS is implemented
      if (scenarioStage > 50) {
        const greenFactor = (scenarioStage - 50) / 50.0 * 0.2;
        g = Math.min(255, Math.floor(g * (1 + greenFactor)));
      }
      
      return {
        ...building,
        color: [r, g, b, 220]
      };
    });
  }, [buildings, scenarioStage]);

  // Prepare NbS layer data
  const nbsLayerData = useMemo(() => {
    if (scenarioStage === 0 || nbsInterventions.length === 0) {
      return [];
    }

    const nbsColors = {
      'Green Roof': [46, 204, 113, 180],
      'Urban Forest': [39, 174, 96, 200],
      'Ventilation Corridor': [52, 152, 219, 160],
      'Permeable Pavement': [149, 165, 166, 150],
      'Rain Garden': [22, 160, 133, 170],
      'Wetland Restoration': [26, 188, 156, 180]
    };

    const opacity = scenarioStage / 100.0;

    return nbsInterventions.map(feature => {
      const nbsType = feature.properties.nbs_type;
      const baseColor = nbsColors[nbsType] || [100, 200, 100, 180];
      
      // Get polygon coordinates
      const coords = feature.geometry.coordinates[0];
      const polygon = coords.map(([lon, lat]) => [lon, lat]);
      
      // Determine elevation
      let elevation = 0.1;
      if (nbsType === 'Green Roof') {
        elevation = (feature.properties.avg_height || 6.0) + 0.3;
      } else if (nbsType === 'Urban Forest') {
        elevation = 8.0;
      } else if (nbsType === 'Rain Garden') {
        elevation = 0.2;
      }
      
      return {
        polygon,
        color: [baseColor[0], baseColor[1], baseColor[2], Math.floor(baseColor[3] * opacity)],
        elevation,
        nbs_type: nbsType,
        priority: feature.properties.priority || 999
      };
    });
  }, [nbsInterventions, scenarioStage]);

  // Create layers
  const layers = useMemo(() => {
    const layerList = [];
    
    // Heat map layer (fades out with NbS)
    const heatOpacity = Math.max(0, 1.0 - (scenarioStage / 120.0));
    if (buildingData.length > 0 && heatOpacity > 0) {
      layerList.push(
        new HeatmapLayer({
          id: 'heatmap',
          data: buildingData,
          getPosition: d => [d.lon, d.lat],
          getWeight: d => d.height,
          radiusPixels: 40,
          intensity: 1,
          threshold: 0.3,
          opacity: heatOpacity
        })
      );
    }
    
    // Buildings layer
    if (buildingData.length > 0) {
      layerList.push(
        new ColumnLayer({
          id: 'buildings',
          data: buildingData,
          getPosition: d => [d.lon, d.lat],
          getElevation: d => d.height,
          elevationScale: 1,
          radius: 12,
          getFillColor: d => d.color,
          getLineColor: [80, 80, 80, 100],
          lineWidthMinPixels: 0.5,
          pickable: true,
          autoHighlight: true,
          highlightColor: [255, 255, 255, 100],
          extruded: true,
          material: {
            ambient: 0.4,
            diffuse: 0.6,
            shininess: 32,
            specularColor: [60, 60, 60]
          }
        })
      );
    }
    
    // NbS interventions layer
    if (nbsLayerData.length > 0) {
      layerList.push(
        new PolygonLayer({
          id: 'nbs-interventions',
          data: nbsLayerData,
          getPolygon: d => d.polygon,
          getFillColor: d => d.color,
          getLineColor: [255, 255, 255, 150],
          lineWidthMinPixels: 2,
          getElevation: d => d.elevation,
          elevationScale: 1,
          pickable: true,
          autoHighlight: true,
          highlightColor: [255, 255, 255, 200],
          extruded: true,
          wireframe: false,
          material: {
            ambient: 0.5,
            diffuse: 0.7,
            shininess: 64,
            specularColor: [100, 100, 100]
          }
        })
      );
    }
    
    return layerList;
  }, [buildingData, nbsLayerData, scenarioStage]);

  // Update view state based on camera preset
  useEffect(() => {
    const presets = {
      'Default 3D': { pitch: 60, bearing: 30, zoom: 14 },
      'Top Down': { pitch: 0, bearing: 0, zoom: 14 },
      'Oblique View': { pitch: 75, bearing: 45, zoom: 14 },
      'Street Level': { pitch: 80, bearing: 0, zoom: 16 }
    };
    
    const preset = presets[cameraPreset] || presets['Default 3D'];
    setViewState(prev => ({
      ...prev,
      ...preset
    }));
  }, [cameraPreset]);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading 4D Visualization Engine...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-screen">
        <h2>⚠️ Error Loading Data</h2>
        <p>{error}</p>
        <p>Please ensure data files are available in the repository.</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Sidebar
        scenarioStage={scenarioStage}
        setScenarioStage={setScenarioStage}
        cameraPreset={cameraPreset}
        setCameraPreset={setCameraPreset}
        buildings={buildings}
        nbsInterventions={nbsInterventions}
      />
      
      <div className="map-container">
        <DeckGL
          initialViewState={viewState}
          viewState={viewState}
          onViewStateChange={({ viewState }) => setViewState(viewState)}
          controller={true}
          layers={layers}
          getTooltip={({ object }) => {
            if (object) {
              if (object.height) {
                return `Building\nHeight: ${object.height}m\nArea: ${object.area}m²`;
              } else if (object.nbs_type) {
                return `NbS Zone\nType: ${object.nbs_type}\nPriority: ${object.priority}`;
              }
            }
            return null;
          }}
        >
          <Map
            mapStyle="mapbox://styles/mapbox/dark-v11"
            mapboxAccessToken={MAPBOX_ACCESS_TOKEN}
            reuseMaps
          />
        </DeckGL>
        
        <Statistics
          buildings={buildings}
          nbsInterventions={nbsInterventions}
          scenarioStage={scenarioStage}
        />
      </div>
    </div>
  );
}

export default App;

