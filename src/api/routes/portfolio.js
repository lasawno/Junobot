import express from 'express';

export const portfolioRouter = express.Router();

// Get portfolio summary
portfolioRouter.get('/', (req, res) => {
  // TODO: Fetch from database
  res.json({
    totalBalance: 0,
    equity: 0,
    cash: 0,
    positions: [],
    unrealizedPnL: 0,
    realizedPnL: 0
  });
});

// Get position details
portfolioRouter.get('/positions', (req, res) => {
  // TODO: Fetch positions from database
  res.json({ positions: [] });
});

// Get account details
portfolioRouter.get('/account', (req, res) => {
  // TODO: Fetch account info
  res.json({
    accountId: '',
    accountType: 'LIVE',
    leverage: 1,
    currency: 'USD'
  });
});
