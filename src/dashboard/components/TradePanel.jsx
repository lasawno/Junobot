import React, { useState } from 'react';

export function TradePanel({ trades }) {
  const [showNewTrade, setShowNewTrade] = useState(false);
  const [formData, setFormData] = useState({
    symbol: 'EURUSD',
    side: 'BUY',
    quantity: 1,
    price: '',
    stopLoss: '',
    takeProfit: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePlaceTrade = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/trades', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const result = await response.json();
      setShowNewTrade(false);
      setFormData({ symbol: 'EURUSD', side: 'BUY', quantity: 1, price: '', stopLoss: '', takeProfit: '' });
    } catch (err) {
      console.error('Failed to place trade:', err);
    }
  };

  return (
    <div className="panel trade-panel">
      <div className="panel-header">
        <h2>Trades</h2>
        <button onClick={() => setShowNewTrade(!showNewTrade)} className="btn-primary">
          {showNewTrade ? 'Cancel' : 'New Trade'}
        </button>
      </div>

      {showNewTrade && (
        <form className="trade-form" onSubmit={handlePlaceTrade}>
          <div className="form-group">
            <label>Symbol</label>
            <input type="text" name="symbol" value={formData.symbol} onChange={handleInputChange} required />
          </div>

          <div className="form-group">
            <label>Side</label>
            <select name="side" value={formData.side} onChange={handleInputChange}>
              <option>BUY</option>
              <option>SELL</option>
            </select>
          </div>

          <div className="form-group">
            <label>Quantity</label>
            <input type="number" name="quantity" value={formData.quantity} onChange={handleInputChange} required />
          </div>

          <div className="form-group">
            <label>Price</label>
            <input type="number" name="price" value={formData.price} onChange={handleInputChange} step="0.0001" />
          </div>

          <div className="form-group">
            <label>Stop Loss</label>
            <input type="number" name="stopLoss" value={formData.stopLoss} onChange={handleInputChange} step="0.0001" />
          </div>

          <div className="form-group">
            <label>Take Profit</label>
            <input type="number" name="takeProfit" value={formData.takeProfit} onChange={handleInputChange} step="0.0001" />
          </div>

          <button type="submit" className="btn-primary">Place Trade</button>
        </form>
      )}

      <h3>Recent Trades</h3>
      <table className="trades-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Side</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Status</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {trades && trades.length > 0 ? (
            trades.map(trade => (
              <tr key={trade.id}>
                <td>{trade.symbol}</td>
                <td className={trade.side === 'BUY' ? 'buy' : 'sell'}>{trade.side}</td>
                <td>{trade.quantity}</td>
                <td>${trade.price?.toFixed(4)}</td>
                <td><span className={`status ${trade.status?.toLowerCase()}`}>{trade.status}</span></td>
                <td>{new Date(trade.timestamp).toLocaleString()}</td>
              </tr>
            ))
          ) : (
            <tr><td colSpan="6" className="empty">No trades yet</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
