import blessed from 'blessed';
import contrib from 'blessed-contrib';
import { logger } from '../utils/logger.js';

export class CLIDashboard {
  constructor() {
    this.screen = blessed.screen({
      smartCSR: true,
      mouse: true,
      title: 'Junobot CLI Dashboard'
    });

    this.grid = new contrib.grid({ rows: 12, cols: 12, screen: this.screen });

    this.setupComponents();
    this.setupKeyBindings();
  }

  setupComponents() {
    // Portfolio Summary (Top Left)
    this.portfolioBox = this.grid.set(0, 0, 3, 4, blessed.box, {
      parent: this.screen,
      label: 'Portfolio',
      content: 'Loading...',
      tags: true,
      style: {
        border: { fg: 'green' },
        label: { fg: 'white', bold: true }
      }
    });

    // Account Info (Top Center)
    this.accountBox = this.grid.set(0, 4, 3, 4, blessed.box, {
      parent: this.screen,
      label: 'Account',
      content: 'Loading...',
      tags: true,
      style: {
        border: { fg: 'cyan' },
        label: { fg: 'white', bold: true }
      }
    });

    // Status (Top Right)
    this.statusBox = this.grid.set(0, 8, 3, 4, blessed.box, {
      parent: this.screen,
      label: 'Status',
      content: '{green-fg}Connected{/}\nAPI: Ready\nKronos: Active',
      tags: true,
      style: {
        border: { fg: 'yellow' },
        label: { fg: 'white', bold: true }
      }
    });

    // Market Prices (Middle Left)
    this.pricesBox = this.grid.set(3, 0, 3, 4, blessed.box, {
      parent: this.screen,
      label: 'Market Prices',
      content: 'EURUSD: 1.0950\nGBPUSD: 1.2650\nUSDJPY: 110.50',
      tags: true,
      style: {
        border: { fg: 'magenta' },
        label: { fg: 'white', bold: true }
      },
      keys: true,
      vi: true,
      scrollable: true,
      alwaysScroll: true
    });

    // Recent Trades (Middle Center)
    this.tradesBox = this.grid.set(3, 4, 3, 4, blessed.box, {
      parent: this.screen,
      label: 'Recent Trades',
      content: 'No trades yet',
      tags: true,
      style: {
        border: { fg: 'blue' },
        label: { fg: 'white', bold: true }
      },
      keys: true,
      vi: true,
      scrollable: true,
      alwaysScroll: true
    });

    // P&L Chart (Middle Right)
    this.pnlChart = this.grid.set(3, 8, 3, 4, contrib.line, {
      style: {
        line: 'yellow',
        text: 'green',
        baseline: 'black'
      },
      xLabelPadding: 3,
      xPadding: 5,
      label: 'P&L (24h)',
      showLegend: true,
      wholeNumbersOnly: false,
      xLabelFormat: ((x) => {
        const hours = Math.floor(x / 4);
        return `${hours}h`;
      })
    });

    this.pnlChart.setData([{
      title: 'P&L',
      x: Array.from({ length: 24 }, (_, i) => i),
      y: Array.from({ length: 24 }, () => Math.random() * 1000 - 500)
    }]);

    // Strategies Status (Bottom Left)
    this.strategiesBox = this.grid.set(6, 0, 3, 6, blessed.box, {
      parent: this.screen,
      label: 'Kronos Strategies',
      content: '- Strategy 1: TIME_BASED (Enabled)\n- Strategy 2: DCA (Enabled)\n- Strategy 3: GRID (Disabled)',
      tags: true,
      style: {
        border: { fg: 'cyan' },
        label: { fg: 'white', bold: true }
      },
      keys: true,
      vi: true,
      scrollable: true,
      alwaysScroll: true
    });

    // Activity Log (Bottom Right)
    this.logBox = this.grid.set(6, 6, 3, 6, blessed.box, {
      parent: this.screen,
      label: 'Activity Log',
      content: '[12:00:00] System started\n[12:00:05] Connected to API\n[12:00:10] Loaded 3 strategies',
      tags: true,
      style: {
        border: { fg: 'magenta' },
        label: { fg: 'white', bold: true }
      },
      keys: true,
      vi: true,
      scrollable: true,
      mouse: true,
      alwaysScroll: true
    });

    // Help Text (Bottom)
    this.helpBox = blessed.box({
      parent: this.screen,
      top: 12,
      left: 0,
      width: '100%',
      height: 1,
      content: '{cyan-fg}q{/}:quit | {cyan-fg}r{/}:refresh | {cyan-fg}s{/}:strategies | {cyan-fg}t{/}:trades | {cyan-fg}m{/}:market',
      tags: true,
      style: {
        bg: 'blue',
        fg: 'white'
      }
    });
  }

  setupKeyBindings() {
    this.screen.key(['q', 'C-c'], () => {
      logger.info('Exiting CLI dashboard...');
      return process.exit(0);
    });

    this.screen.key(['r'], () => {
      this.refresh();
    });

    this.screen.key(['s'], () => {
      this.showStrategiesDetail();
    });

    this.screen.key(['t'], () => {
      this.showTradesDetail();
    });

    this.screen.key(['m'], () => {
      this.showMarketDetail();
    });
  }

  updatePortfolio(data) {
    const content = [
      `{bold}Total: ${data.totalBalance.toFixed(2)} USD{/}`,
      `{green-fg}Equity: ${data.equity.toFixed(2)}{/}`,
      `{blue-fg}Cash: ${data.cash.toFixed(2)}{/}`,
      `{yellow-fg}Unrealized P&L: ${data.unrealizedPnL.toFixed(2)}{/}`,
      `{magenta-fg}Realized P&L: ${data.realizedPnL.toFixed(2)}{/}`
    ].join('\n');

    this.portfolioBox.setContent(content);
    this.screen.render();
  }

  updateAccount(data) {
    const content = [
      `{bold}Account ID:{/} ${data.accountId}`,
      `{bold}Type:{/} ${data.accountType}`,
      `{bold}Leverage:{/} 1:${data.leverage}`,
      `{bold}Currency:{/} ${data.currency}`
    ].join('\n');

    this.accountBox.setContent(content);
    this.screen.render();
  }

  updateStatus(status) {
    const apiStatus = status.api === 'connected' ? '{green-fg}Connected{/}' : '{red-fg}Disconnected{/}';
    const kronosStatus = status.kronos === 'active' ? '{green-fg}Active{/}' : '{yellow-fg}Standby{/}';

    const content = [
      apiStatus,
      `API: {bold}Ready{/}`,
      `Kronos: ${kronosStatus}`
    ].join('\n');

    this.statusBox.setContent(content);
    this.screen.render();
  }

  addLog(message) {
    const time = new Date().toLocaleTimeString();
    const logEntry = `[${time}] ${message}`;

    const current = this.logBox.content || '';
    const lines = current.split('\n');
    lines.push(logEntry);

    if (lines.length > 20) {
      lines.shift();
    }

    this.logBox.setContent(lines.join('\n'));
    this.screen.render();
  }

  updatePnLChart(data) {
    this.pnlChart.setData([{
      title: 'P&L',
      x: data.x,
      y: data.y
    }]);
    this.screen.render();
  }

  refresh() {
    this.addLog('Dashboard refreshed');
    this.screen.render();
  }

  showStrategiesDetail() {
    this.addLog('Showing strategies detail (s)');
  }

  showTradesDetail() {
    this.addLog('Showing trades detail (t)');
  }

  showMarketDetail() {
    this.addLog('Showing market detail (m)');
  }

  render() {
    this.screen.render();
  }

  destroy() {
    this.screen.destroy();
  }
}

export default CLIDashboard;
