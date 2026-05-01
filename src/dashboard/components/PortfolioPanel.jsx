import React from 'react';

export function PortfolioPanel({ data }) {
  if (!data) {
    return <div className="panel"><p>Loading portfolio data...</p></div>;
  }

  return (
    <div className="panel portfolio-panel">
      <h2>Portfolio Overview</h2>

      <div className="portfolio-summary">
        <div className="summary-card">
          <h3>Total Balance</h3>
          <p className="amount">${data.totalBalance?.toFixed(2) || '0.00'}</p>
        </div>

        <div className="summary-card">
          <h3>Equity</h3>
          <p className="amount">${data.equity?.toFixed(2) || '0.00'}</p>
        </div>

        <div className="summary-card">
          <h3>Cash</h3>
          <p className="amount">${data.cash?.toFixed(2) || '0.00'}</p>
        </div>

        <div className="summary-card">
          <h3>Unrealized P&L</h3>
          <p className={`amount ${data.unrealizedPnL >= 0 ? 'positive' : 'negative'}`}>
            ${data.unrealizedPnL?.toFixed(2) || '0.00'}
          </p>
        </div>

        <div className="summary-card">
          <h3>Realized P&L</h3>
          <p className={`amount ${data.realizedPnL >= 0 ? 'positive' : 'negative'}`}>
            ${data.realizedPnL?.toFixed(2) || '0.00'}
          </p>
        </div>
      </div>

      <h3>Open Positions</h3>
      <table className="positions-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Quantity</th>
            <th>Entry Price</th>
            <th>Current Price</th>
            <th>Unrealized P&L</th>
            <th>%</th>
          </tr>
        </thead>
        <tbody>
          {data.positions && data.positions.length > 0 ? (
            data.positions.map(pos => (
              <tr key={pos.id}>
                <td>{pos.symbol}</td>
                <td>{pos.quantity}</td>
                <td>${pos.entryPrice?.toFixed(2)}</td>
                <td>${pos.currentPrice?.toFixed(2)}</td>
                <td className={pos.unrealizedPnL >= 0 ? 'positive' : 'negative'}>
                  ${pos.unrealizedPnL?.toFixed(2)}
                </td>
                <td className={pos.unrealizedPnLPercent >= 0 ? 'positive' : 'negative'}>
                  {pos.unrealizedPnLPercent?.toFixed(2)}%
                </td>
              </tr>
            ))
          ) : (
            <tr><td colSpan="6" className="empty">No open positions</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
