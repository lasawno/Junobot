import express from 'express';

export const tradesRouter = express.Router();

// Get trade history
tradesRouter.get('/', (req, res) => {
  const { limit = 50, offset = 0 } = req.query;
  // TODO: Fetch from database
  res.json({
    trades: [],
    total: 0,
    limit: parseInt(limit),
    offset: parseInt(offset)
  });
});

// Get trade details
tradesRouter.get('/:tradeId', (req, res) => {
  // TODO: Fetch trade from database
  res.json({ trade: {} });
});

// Place new trade
tradesRouter.post('/', (req, res) => {
  const { symbol, side, quantity, price, stopLoss, takeProfit } = req.body;
  // TODO: Validate and execute trade
  res.status(201).json({ tradeId: '', status: 'pending' });
});

// Modify trade
tradesRouter.put('/:tradeId', (req, res) => {
  // TODO: Modify trade parameters
  res.json({ success: true });
});

// Close trade
tradesRouter.delete('/:tradeId', (req, res) => {
  // TODO: Close position
  res.json({ success: true });
});
