import CLIDashboard from './dashboard.js';
import { logger } from '../utils/logger.js';

export async function startCLIDashboard(apiUrl = 'http://localhost:5000') {
  try {
    const dashboard = new CLIDashboard();

    // Simulate data updates for demo
    setInterval(async () => {
      try {
        const response = await fetch(`${apiUrl}/api/portfolio`);
        const data = await response.json();
        dashboard.updatePortfolio(data);
      } catch (err) {
        logger.error('Failed to fetch portfolio:', err);
      }
    }, 5000);

    // Sample data update
    dashboard.updatePortfolio({
      totalBalance: 50000,
      equity: 52000,
      cash: 2000,
      unrealizedPnL: 2000,
      realizedPnL: 500
    });

    dashboard.updateAccount({
      accountId: 'ACC-001',
      accountType: 'LIVE',
      leverage: 1,
      currency: 'USD'
    });

    dashboard.updateStatus({
      api: 'connected',
      kronos: 'active'
    });

    dashboard.addLog('CLI Dashboard started');
    dashboard.render();

    return dashboard;
  } catch (err) {
    logger.error('Failed to start CLI dashboard:', err);
    throw err;
  }
}

export { CLIDashboard };
