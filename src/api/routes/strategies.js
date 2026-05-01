import express from 'express';

export const strategiesRouter = express.Router();

// Get all strategies
strategiesRouter.get('/', (req, res) => {
  // TODO: Fetch from database
  res.json({ strategies: [] });
});

// Get strategy details
strategiesRouter.get('/:strategyId', (req, res) => {
  // TODO: Fetch strategy
  res.json({ strategy: {} });
});

// Create new strategy
strategiesRouter.post('/', (req, res) => {
  const { name, type, config } = req.body;
  // TODO: Validate and save strategy
  res.status(201).json({ strategyId: '', status: 'created' });
});

// Update strategy
strategiesRouter.put('/:strategyId', (req, res) => {
  // TODO: Update strategy
  res.json({ success: true });
});

// Enable/disable strategy
strategiesRouter.patch('/:strategyId/toggle', (req, res) => {
  const { enabled } = req.body;
  // TODO: Toggle strategy
  res.json({ success: true });
});

// Delete strategy
strategiesRouter.delete('/:strategyId', (req, res) => {
  // TODO: Delete strategy
  res.json({ success: true });
});
