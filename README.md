# Junobot: AI-Powered Forex Trading Bot

An intelligent trading bot system for Forex and currency markets, featuring:

- **Kronos Time-Based Trading Engine**: Schedule and automate trading strategies
- **Web Dashboard**: Real-time portfolio monitoring and trade execution
- **CLI Dashboard**: Terminal-based trading interface
- **Camofox Anti-Detection Browser**: Automated web interaction without detection
- **Ruflo Integration**: Leverages Forex trading strategies and market analysis

## Features

### Core Components

#### 1. **Kronos Trading Engine**
- Time-based strategy execution with cron scheduling
- Multiple strategy types: DCA, Grid Trading, Signal-based, Time-based
- Real-time strategy monitoring and execution tracking
- Graceful error handling and recovery

#### 2. **Trading Dashboard (Web)**
- Portfolio overview with real-time P&L
- Trade execution interface
- Strategy management and configuration
- Market data visualization
- WebSocket real-time updates

#### 3. **CLI Dashboard**
- Terminal-based trading interface
- Real-time portfolio and performance charts
- Strategy status monitoring
- Activity logging
- Keyboard shortcuts for quick actions

#### 4. **Camofox Browser Integration**
- Anti-detection Firefox fork for automated trading
- Proxy support for distributed operations
- Anti-webdriver detection
- Fingerprint spoofing at C++ level
- Headless and headed modes

#### 5. **Ruflo Integration**
- Forex market analysis and strategies
- Technical indicators and signals
- Historical data and backtesting

## Installation

### Prerequisites
- Node.js 16+ and npm
- PostgreSQL (optional, for data persistence)
- Camoufox browser executable (for browser automation)

### Setup

1. Clone and navigate to repository:
```bash
cd /home/user/Junobot
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Configure your `.env` file with API keys and settings

## Usage

### Start API Server
```bash
npm start
```
Server will run on `http://localhost:5000`

### Start Development Mode
```bash
npm run dev
```
(Auto-reload on file changes)

### Start Kronos Scheduler
```bash
npm run kronos
```

### Access Web Dashboard
Open `http://localhost:5000` in your browser

### Start CLI Dashboard
```bash
node src/cli/main.js
```

## Project Structure

```
Junobot/
├── src/
│   ├── api/              # REST API server
│   │   ├── server.js
│   │   └── routes/
│   ├── kronos/           # Trading strategy engine
│   │   ├── scheduler.js
│   │   └── executor.js
│   ├── dashboard/        # Web UI (React)
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── hooks/
│   ├── cli/              # Terminal UI
│   │   ├── dashboard.js
│   │   └── main.js
│   ├── camofox/          # Browser automation
│   │   └── integration.js
│   └── utils/            # Shared utilities
├── config/               # Configuration files
├── public/               # Static assets
├── ruflo/                # External Forex library
├── package.json
└── README.md
```

## API Endpoints

### Portfolio
- `GET /api/portfolio` - Get portfolio summary
- `GET /api/portfolio/positions` - Get open positions
- `GET /api/portfolio/account` - Get account details

### Trades
- `GET /api/trades` - Get trade history
- `GET /api/trades/:tradeId` - Get trade details
- `POST /api/trades` - Place new trade
- `PUT /api/trades/:tradeId` - Modify trade
- `DELETE /api/trades/:tradeId` - Close trade

### Strategies
- `GET /api/strategies` - Get all strategies
- `GET /api/strategies/:strategyId` - Get strategy details
- `POST /api/strategies` - Create strategy
- `PUT /api/strategies/:strategyId` - Update strategy
- `PATCH /api/strategies/:strategyId/toggle` - Enable/disable
- `DELETE /api/strategies/:strategyId` - Delete strategy

### Market
- `GET /api/market` - Get supported symbols
- `GET /api/market/:symbol` - Get market data
- `GET /api/market/:symbol/indicators` - Get technical indicators

## Strategy Configuration

Configure strategies in `config/strategies.json`:

```json
{
  "id": "strategy-id",
  "name": "Strategy Name",
  "type": "TIME_BASED|SIGNAL_BASED|GRID_TRADING|DCA",
  "enabled": true,
  "config": {
    "symbol": "EURUSD",
    "frequency": "0 */4 * * *"
  },
  "riskManagement": {
    "stopLoss": 0.02,
    "takeProfit": 0.05
  }
}
```

### Strategy Types

- **TIME_BASED**: Execute trades at specific times
- **SIGNAL_BASED**: Trade based on technical indicators
- **GRID_TRADING**: Place orders in a grid pattern
- **DCA**: Dollar Cost Averaging with fixed intervals

## WebSocket Events

Real-time updates via WebSocket:

```javascript
// Subscribe to portfolio updates
ws.send(JSON.stringify({ type: 'SUBSCRIBE_PORTFOLIO' }));

// Subscribe to trades
ws.send(JSON.stringify({ type: 'SUBSCRIBE_TRADES' }));

// Subscribe to market data
ws.send(JSON.stringify({ 
  type: 'SUBSCRIBE_MARKET', 
  payload: { symbol: 'EURUSD' } 
}));
```

## CLI Dashboard Controls

- `q` - Quit
- `r` - Refresh
- `s` - Show strategies detail
- `t` - Show trades detail
- `m` - Show market detail

## Environment Variables

Key configuration variables in `.env`:

```
PORT=5000
DATABASE_URL=postgresql://...
CAMOUFOX_EXECUTABLE=/usr/bin/camoufox
TRADING_MODE=PAPER
LEVERAGE=1
KRONOS_ENABLED=true
```

See `.env.example` for all available options.

## Camofox Browser Usage

```javascript
import CamofoxBrowser from './src/camofox/integration.js';

const browser = new CamofoxBrowser({
  headless: true,
  antiDetection: true,
  proxy: 'http://proxy:8080'
});

await browser.launch();
const { pageId, page } = await browser.createPage('trading');
await browser.goto(pageId, 'https://example.com');
const data = await browser.scrapeData(pageId, '.price-data');
await browser.close();
```

## Development

### Running Tests
```bash
npm test
```

### Watch Mode
```bash
npm run test:watch
```

### Code Quality
```bash
npm run lint
```

## Performance Optimization

- WebSocket for real-time updates (vs polling)
- Strategy execution caching
- Database indexing on trade history
- Graceful shutdown and resource cleanup

## Security Considerations

- API key management via environment variables
- No sensitive data in logs
- CORS configuration for dashboard
- Input validation on all endpoints
- Anti-detection measures for browser automation

## Troubleshooting

### Camoufox Not Found
```bash
# Ensure Camoufox is installed and path is correct in .env
which camoufox
```

### WebSocket Connection Issues
```bash
# Check if server is running on correct port
netstat -an | grep 5000
```

### Database Connection
```bash
# Verify PostgreSQL is running and credentials are correct
psql -h localhost -U postgres
```

## Future Enhancements

- [ ] Machine learning strategy optimization
- [ ] Advanced backtesting engine
- [ ] Social trading features
- [ ] Multi-exchange support
- [ ] Risk analytics dashboard
- [ ] Automated portfolio rebalancing

## License

Apache 2.0 - See LICENSE file

## Support

For issues, questions, or contributions, please use the repository's issue tracker.

---

**Built with Camoufox anti-detection technology for reliable automated trading**