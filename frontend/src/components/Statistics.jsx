import React from 'react';
import './Statistics.css';

function Statistics({ buildings, nbsInterventions, scenarioStage }) {
  const avgHeight = buildings.length > 0
    ? buildings.reduce((sum, b) => sum + (b.height || 0), 0) / buildings.length
    : 0;
  
  const totalArea = buildings.length > 0
    ? buildings.reduce((sum, b) => sum + (b.area || 0), 0)
    : 0;

  const visibleInterventions = Math.floor((nbsInterventions.length * scenarioStage) / 100);
  const tempReduction = scenarioStage * 0.02;
  const co2Seq = scenarioStage * 1.2;
  const greenCoverage = scenarioStage * 0.5;

  return (
    <div className="statistics-panel">
      <div className="stat-card">
        <div className="stat-label">Buildings</div>
        <div className="stat-value">{buildings.length.toLocaleString()}</div>
        <div className="stat-sub">Avg Height: {avgHeight.toFixed(1)}m</div>
      </div>
      
      {nbsInterventions.length > 0 && (
        <>
          <div className="stat-card">
            <div className="stat-label">NbS Zones</div>
            <div className="stat-value">{nbsInterventions.length.toLocaleString()}</div>
            <div className="stat-sub">Active: {visibleInterventions}</div>
          </div>
          
          <div className="stat-card highlight">
            <div className="stat-label">Temp Reduction</div>
            <div className="stat-value">-{tempReduction.toFixed(2)}°C</div>
            <div className="stat-sub">Heat Island Effect</div>
          </div>
          
          <div className="stat-card highlight">
            <div className="stat-label">CO₂ Sequestration</div>
            <div className="stat-value">{co2Seq.toFixed(1)} t/yr</div>
            <div className="stat-sub">Carbon Capture</div>
          </div>
        </>
      )}
    </div>
  );
}

export default Statistics;

