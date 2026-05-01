import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import dotenv from 'dotenv';
import { logger } from '../utils/logger.js';
import { portfolioRouter } from './routes/portfolio.js';
import { tradesRouter } from './routes/trades.js';
import { strategiesRouter } from './routes/strategies.js';
import { marketRouter } from './routes/market.js';

dotenv.config();

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || 'localhost';

// Middleware
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});
app.use(express.json());
app.use(express.static('public'));

// API Routes
app.use('/api/portfolio', portfolioRouter);
app.use('/api/trades', tradesRouter);
app.use('/api/strategies', strategiesRouter);
app.use('/api/market', marketRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// WebSocket connections for real-time updates
wss.on('connection', (ws) => {
  logger.info('WebSocket client connected');

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      handleWebSocketMessage(ws, message);
    } catch (err) {
      logger.error('WebSocket message error:', err);
      ws.send(JSON.stringify({ error: 'Invalid message format' }));
    }
  });

  ws.on('close', () => {
    logger.info('WebSocket client disconnected');
  });

  ws.on('error', (err) => {
    logger.error('WebSocket error:', err);
  });
});

function handleWebSocketMessage(ws, message) {
  const { type, payload } = message;

  switch (type) {
    case 'SUBSCRIBE_PORTFOLIO':
      subscribeToPortfolioUpdates(ws);
      break;
    case 'SUBSCRIBE_TRADES':
      subscribeToTradeUpdates(ws);
      break;
    case 'SUBSCRIBE_MARKET':
      subscribeToMarketData(ws, payload);
      break;
    default:
      logger.warn('Unknown message type:', type);
  }
}

function subscribeToPortfolioUpdates(ws) {
  // TODO: Implement portfolio update subscriptions
  ws.send(JSON.stringify({ type: 'PORTFOLIO_SUBSCRIBED' }));
}

function subscribeToTradeUpdates(ws) {
  // TODO: Implement trade update subscriptions
  ws.send(JSON.stringify({ type: 'TRADES_SUBSCRIBED' }));
}

function subscribeToMarketData(ws, payload) {
  // TODO: Implement market data subscriptions
  ws.send(JSON.stringify({ type: 'MARKET_SUBSCRIBED', symbol: payload?.symbol }));
}

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  res.status(err.status || 500).json({
    error: err.message || 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

server.listen(PORT, HOST, () => {
  logger.info(`Junobot API Server running on http://${HOST}:${PORT}`);
  logger.info(`WebSocket server ready for connections`);
});

export { app, server, wss };
