import React from 'react';
import './Sidebar.css';

function Sidebar({ scenarioStage, setScenarioStage, cameraPreset, setCameraPreset, buildings, nbsInterventions }) {
  const visibleInterventions = Math.floor((nbsInterventions.length * scenarioStage) / 100);
  const tempReduction = scenarioStage * 0.02;
  const co2Seq = scenarioStage * 1.2;
  const greenCoverage = scenarioStage * 0.5;
  
  const stateLabel = scenarioStage === 0 ? 'BEFORE' : scenarioStage === 100 ? 'AFTER' : 'TRANSITION';
  const progressColor = scenarioStage === 100 ? '🟢' : scenarioStage > 0 ? '🟡' : '🔴';

  const nbsCounts = nbsInterventions.reduce((acc, int) => {
    const type = int.properties?.nbs_type || 'Unknown';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1>🏗️ NbS 4D Engine</h1>
        <p>Hyderabad Spatial Planner</p>
        <p className="subtitle">Real OSM Buildings + G20 NbS Framework</p>
      </div>

      <div className="sidebar-section">
        <h3>📷 View Presets</h3>
        <select
          value={cameraPreset}
          onChange={(e) => setCameraPreset(e.target.value)}
          className="preset-select"
        >
          <option value="Default 3D">Default 3D</option>
          <option value="Top Down">Top Down</option>
          <option value="Oblique View">Oblique View</option>
          <option value="Street Level">Street Level</option>
        </select>
      </div>

      <div className="sidebar-section">
        <h3>🕒 Temporal Control</h3>
        <input
          type="range"
          min="0"
          max="100"
          value={scenarioStage}
          onChange={(e) => setScenarioStage(Number(e.target.value))}
          className="slider"
        />
        <div className="slider-info">
          <span className="status-indicator">{progressColor} {scenarioStage}% Complete</span>
        </div>
        <div className="state-label">
          <strong>State:</strong> {stateLabel}
        </div>
      </div>

      <div className="sidebar-section">
        <h3>📊 Current Metrics</h3>
        <div className="metrics-grid">
          <div className="metric">
            <div className="metric-label">Phase</div>
            <div className="metric-value">{scenarioStage}%</div>
          </div>
          <div className="metric">
            <div className="metric-label">State</div>
            <div className="metric-value">{stateLabel}</div>
          </div>
        </div>
      </div>

      {nbsInterventions.length > 0 && (
        <>
          <div className="sidebar-section">
            <h3>🌳 NbS Implementation</h3>
            <div className="metric">
              <div className="metric-label">NbS Zones</div>
              <div className="metric-value">{nbsInterventions.length.toLocaleString()}</div>
              <div className="metric-delta">+{visibleInterventions} active</div>
            </div>
            <div className="metric">
              <div className="metric-label">Heat Reduction</div>
              <div className="metric-value">-{tempReduction.toFixed(2)}°C</div>
              <div className="metric-delta">-{Math.floor(tempReduction * 50)}%</div>
            </div>
            <div className="metric">
              <div className="metric-label">CO₂ Sequestration</div>
              <div className="metric-value">{co2Seq.toFixed(1)} t/yr</div>
              <div className="metric-delta">+{Math.floor(co2Seq)}%</div>
            </div>
            <div className="metric">
              <div className="metric-label">Green Coverage</div>
              <div className="metric-value">{greenCoverage.toFixed(1)}%</div>
              <div className="metric-delta">+{greenCoverage.toFixed(1)}%</div>
            </div>
          </div>

          <div className="sidebar-section">
            <h3>🌳 NbS Breakdown</h3>
            {Object.entries(nbsCounts).map(([type, count]) => {
              const activeCount = Math.floor(count * (scenarioStage / 100));
              const progress = count > 0 ? activeCount / count : 0;
              
              return (
                <div key={type} className="nbs-item">
                  <div className="nbs-header">
                    <strong>{type}</strong>
                    <span>{activeCount}/{count}</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${progress * 100}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {buildings.length > 0 && (
        <div className="sidebar-section">
          <div className="metric">
            <div className="metric-label">Buildings</div>
            <div className="metric-value">{buildings.length.toLocaleString()}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sidebar;

