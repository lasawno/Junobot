import React, { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { PortfolioPanel } from './components/PortfolioPanel';
import { TradePanel } from './components/TradePanel';
import { StrategiesPanel } from './components/StrategiesPanel';
import { MarketPanel } from './components/MarketPanel';
import './App.css';

export function App() {
  const [activeTab, setActiveTab] = useState('portfolio');
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [marketData, setMarketData] = useState({});

  const ws = useWebSocket('ws://localhost:5000');

  useEffect(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'SUBSCRIBE_PORTFOLIO' }));
      ws.send(JSON.stringify({ type: 'SUBSCRIBE_TRADES' }));
      ws.send(JSON.stringify({ type: 'SUBSCRIBE_MARKET', payload: { symbol: 'EURUSD' } }));
    }
  }, [ws]);

  useEffect(() => {
    if (!ws) return;

    const handleMessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWebSocketMessage(message);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.addEventListener('message', handleMessage);
    return () => ws.removeEventListener('message', handleMessage);
  }, [ws]);

  const handleWebSocketMessage = useCallback((message) => {
    const { type, data } = message;

    switch (type) {
      case 'PORTFOLIO_UPDATE':
        setPortfolio(data);
        break;
      case 'TRADES_UPDATE':
        setTrades(data);
        break;
      case 'STRATEGIES_UPDATE':
        setStrategies(data);
        break;
      case 'MARKET_DATA':
        setMarketData(prev => ({ ...prev, [data.symbol]: data }));
        break;
      default:
        console.log('Unhandled message type:', type);
    }
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'portfolio':
        return <PortfolioPanel data={portfolio} />;
      case 'trades':
        return <TradePanel trades={trades} />;
      case 'strategies':
        return <StrategiesPanel strategies={strategies} />;
      case 'market':
        return <MarketPanel data={marketData} />;
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Junobot Trading Dashboard</h1>
        <div className="connection-status">
          <span className={`status-indicator ${ws?.readyState === WebSocket.OPEN ? 'connected' : 'disconnected'}`}></span>
          {ws?.readyState === WebSocket.OPEN ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-button ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => setActiveTab('portfolio')}
        >
          Portfolio
        </button>
        <button
          className={`nav-button ${activeTab === 'trades' ? 'active' : ''}`}
          onClick={() => setActiveTab('trades')}
        >
          Trades
        </button>
        <button
          className={`nav-button ${activeTab === 'strategies' ? 'active' : ''}`}
          onClick={() => setActiveTab('strategies')}
        >
          Strategies
        </button>
        <button
          className={`nav-button ${activeTab === 'market' ? 'active' : ''}`}
          onClick={() => setActiveTab('market')}
        >
          Market
        </button>
      </nav>

      <main className="app-content">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
