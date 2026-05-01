import cron from 'node-cron';
import { logger } from '../utils/logger.js';
import { StrategyExecutor } from './executor.js';

export class KronosScheduler {
  constructor() {
    this.strategies = new Map();
    this.tasks = new Map();
    this.executor = new StrategyExecutor();
  }

  registerStrategy(strategyId, strategy) {
    if (this.strategies.has(strategyId)) {
      logger.warn(`Strategy ${strategyId} already registered, updating...`);
    }
    this.strategies.set(strategyId, strategy);
    logger.info(`Strategy registered: ${strategyId}`);
  }

  unregisterStrategy(strategyId) {
    if (this.tasks.has(strategyId)) {
      this.tasks.get(strategyId).stop();
      this.tasks.delete(strategyId);
    }
    this.strategies.delete(strategyId);
    logger.info(`Strategy unregistered: ${strategyId}`);
  }

  scheduleStrategy(strategyId, cronExpression) {
    const strategy = this.strategies.get(strategyId);

    if (!strategy) {
      logger.error(`Strategy not found: ${strategyId}`);
      return false;
    }

    // Stop existing task if any
    if (this.tasks.has(strategyId)) {
      this.tasks.get(strategyId).stop();
    }

    try {
      const task = cron.schedule(cronExpression, async () => {
        logger.info(`Executing strategy: ${strategyId}`);
        await this.executor.execute(strategy);
      });

      this.tasks.set(strategyId, task);
      logger.info(`Strategy scheduled: ${strategyId} (${cronExpression})`);
      return true;
    } catch (err) {
      logger.error(`Failed to schedule strategy ${strategyId}:`, err);
      return false;
    }
  }

  enableStrategy(strategyId) {
    const strategy = this.strategies.get(strategyId);
    if (!strategy) {
      logger.error(`Strategy not found: ${strategyId}`);
      return false;
    }

    strategy.enabled = true;
    logger.info(`Strategy enabled: ${strategyId}`);
    return true;
  }

  disableStrategy(strategyId) {
    const strategy = this.strategies.get(strategyId);
    if (!strategy) {
      logger.error(`Strategy not found: ${strategyId}`);
      return false;
    }

    strategy.enabled = false;

    // Stop the scheduled task
    if (this.tasks.has(strategyId)) {
      this.tasks.get(strategyId).stop();
      this.tasks.delete(strategyId);
    }

    logger.info(`Strategy disabled: ${strategyId}`);
    return true;
  }

  getStrategy(strategyId) {
    return this.strategies.get(strategyId);
  }

  getStrategies() {
    return Array.from(this.strategies.entries()).map(([id, strategy]) => ({
      id,
      ...strategy,
      isScheduled: this.tasks.has(id)
    }));
  }

  stopAll() {
    for (const task of this.tasks.values()) {
      task.stop();
    }
    this.tasks.clear();
    logger.info('All scheduled strategies stopped');
  }
}

// Singleton instance
let scheduler = null;

export function getScheduler() {
  if (!scheduler) {
    scheduler = new KronosScheduler();
  }
  return scheduler;
}

// Initialize scheduler on import
const kronosScheduler = getScheduler();

// Handle graceful shutdown
process.on('SIGINT', () => {
  logger.info('Shutting down Kronos scheduler...');
  kronosScheduler.stopAll();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Shutting down Kronos scheduler (SIGTERM)...');
  kronosScheduler.stopAll();
  process.exit(0);
});

export default kronosScheduler;
