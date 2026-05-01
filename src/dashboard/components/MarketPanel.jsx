import React, { useState } from 'react';

const POPULAR_SYMBOLS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'];

export function MarketPanel({ data }) {
  const [selectedSymbol, setSelectedSymbol] = useState('EURUSD');

  const currentData = data[selectedSymbol];

  return (
    <div className="panel market-panel">
      <h2>Market Data</h2>

      <div className="symbols-menu">
        {POPULAR_SYMBOLS.map(symbol => (
          <button
            key={symbol}
            className={`symbol-button ${selectedSymbol === symbol ? 'active' : ''}`}
            onClick={() => setSelectedSymbol(symbol)}
          >
            {symbol}
          </button>
        ))}
      </div>

      {currentData ? (
        <div className="market-data">
          <div className="price-display">
            <h3>{selectedSymbol}</h3>
            <div className="price-info">
              <div className="price-row">
                <span>Bid:</span>
                <span className="price">${currentData.bid?.toFixed(4)}</span>
              </div>
              <div className="price-row">
                <span>Ask:</span>
                <span className="price">${currentData.ask?.toFixed(4)}</span>
              </div>
              <div className="price-row">
                <span>Spread:</span>
                <span className="spread">{((currentData.ask - currentData.bid) * 10000).toFixed(1)} pips</span>
              </div>
            </div>
          </div>

          <div className="chart-placeholder">
            <p>Chart rendering - {currentData.timeframe}</p>
            {/* TODO: Integrate charting library (Chart.js, TradingView Lightweight Charts, etc.) */}
          </div>

          <div className="indicators">
            <h4>Technical Indicators</h4>
            <table className="indicators-table">
              <thead>
                <tr>
                  <th>Indicator</th>
                  <th>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>RSI (14)</td><td>N/A</td></tr>
                <tr><td>MACD</td><td>N/A</td></tr>
                <tr><td>MA (20)</td><td>N/A</td></tr>
                <tr><td>MA (50)</td><td>N/A</td></tr>
                <tr><td>Bollinger Bands</td><td>N/A</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <p>Loading market data for {selectedSymbol}...</p>
      )}
    </div>
  );
}
