// Default view state for Hyderabad
export const INITIAL_VIEW_STATE = {
  latitude: 17.3616,
  longitude: 78.4747,
  zoom: 14,
  pitch: 60,
  bearing: 30
};

// Mapbox token - replace with your own
// Get one at: https://account.mapbox.com/access-tokens/
export const MAPBOX_TOKEN = process.env.VITE_MAPBOX_TOKEN || '';

// Camera presets
export const CAMERA_PRESETS = {
  'Default 3D': {
    pitch: 60,
    bearing: 30,
    zoom: 14
  },
  'Top Down': {
    pitch: 0,
    bearing: 0,
    zoom: 14
  },
  'Oblique View': {
    pitch: 75,
    bearing: 45,
    zoom: 14
  },
  'Street Level': {
    pitch: 80,
    bearing: 0,
    zoom: 16
  }
};

// NbS color mapping
export const NBS_COLORS = {
  'Green Roof': [46, 204, 113, 180],
  'Urban Forest': [39, 174, 96, 200],
  'Ventilation Corridor': [52, 152, 219, 160],
  'Permeable Pavement': [149, 165, 166, 150],
  'Rain Garden': [22, 160, 133, 170],
  'Wetland Restoration': [26, 188, 156, 180]
};

