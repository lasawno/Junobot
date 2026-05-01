import React, { useState } from 'react';

export function StrategiesPanel({ strategies }) {
  const [showNewStrategy, setShowNewStrategy] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'TIME_BASED',
    enabled: true
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleCreateStrategy = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/strategies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      setShowNewStrategy(false);
      setFormData({ name: '', type: 'TIME_BASED', enabled: true });
    } catch (err) {
      console.error('Failed to create strategy:', err);
    }
  };

  return (
    <div className="panel strategies-panel">
      <div className="panel-header">
        <h2>Kronos Strategies</h2>
        <button onClick={() => setShowNewStrategy(!showNewStrategy)} className="btn-primary">
          {showNewStrategy ? 'Cancel' : 'New Strategy'}
        </button>
      </div>

      {showNewStrategy && (
        <form className="strategy-form" onSubmit={handleCreateStrategy}>
          <div className="form-group">
            <label>Strategy Name</label>
            <input type="text" name="name" value={formData.name} onChange={handleInputChange} required />
          </div>

          <div className="form-group">
            <label>Strategy Type</label>
            <select name="type" value={formData.type} onChange={handleInputChange}>
              <option value="TIME_BASED">Time Based</option>
              <option value="SIGNAL_BASED">Signal Based</option>
              <option value="GRID_TRADING">Grid Trading</option>
              <option value="DCA">DCA (Dollar Cost Averaging)</option>
            </select>
          </div>

          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                name="enabled"
                checked={formData.enabled}
                onChange={handleInputChange}
              />
              Enabled
            </label>
          </div>

          <button type="submit" className="btn-primary">Create Strategy</button>
        </form>
      )}

      <h3>Active Strategies</h3>
      <div className="strategies-grid">
        {strategies && strategies.length > 0 ? (
          strategies.map(strategy => (
            <div key={strategy.id} className="strategy-card">
              <div className="strategy-header">
                <h4>{strategy.name}</h4>
                <span className={`status ${strategy.enabled ? 'enabled' : 'disabled'}`}>
                  {strategy.enabled ? 'Enabled' : 'Disabled'}
                </span>
              </div>
              <p className="strategy-type">{strategy.type}</p>
              <p className="strategy-info">ID: {strategy.id}</p>
              <div className="strategy-actions">
                <button className="btn-small">Edit</button>
                <button className="btn-small">Run Now</button>
                <button className="btn-small btn-danger">Delete</button>
              </div>
            </div>
          ))
        ) : (
          <p className="empty">No strategies configured</p>
        )}
      </div>
    </div>
  );
}
