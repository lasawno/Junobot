import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger.js';

export class StrategyExecutor {
  constructor() {
    this.trades = new Map();
    this.executionHistory = [];
  }

  async execute(strategy) {
    const executionId = uuidv4();
    const startTime = Date.now();

    logger.info(`[${executionId}] Starting execution of strategy: ${strategy.id}`);

    try {
      if (!strategy.enabled) {
        logger.warn(`[${executionId}] Strategy is disabled: ${strategy.id}`);
        return {
          success: false,
          reason: 'Strategy disabled',
          executionId
        };
      }

      // Execute strategy logic
      const result = await this.executeStrategy(strategy, executionId);

      const duration = Date.now() - startTime;
      logger.info(`[${executionId}] Execution completed in ${duration}ms`);

      this.recordExecution(executionId, strategy.id, true, result, duration);
      return result;
    } catch (err) {
      const duration = Date.now() - startTime;
      logger.error(`[${executionId}] Execution failed:`, err);

      this.recordExecution(executionId, strategy.id, false, { error: err.message }, duration);
      return {
        success: false,
        error: err.message,
        executionId
      };
    }
  }

  async executeStrategy(strategy, executionId) {
    const { type, config } = strategy;

    switch (type) {
      case 'TIME_BASED':
        return await this.executeTimeBased(strategy, executionId);
      case 'SIGNAL_BASED':
        return await this.executeSignalBased(strategy, executionId);
      case 'GRID_TRADING':
        return await this.executeGridTrading(strategy, executionId);
      case 'DCA':
        return await this.executeDCA(strategy, executionId);
      default:
        throw new Error(`Unknown strategy type: ${type}`);
    }
  }

  async executeTimeBased(strategy, executionId) {
    logger.info(`[${executionId}] Executing time-based strategy`);

    // Time-based trading at specific intervals
    const { symbol, quantity, buyTime, sellTime } = strategy.config;

    return {
      success: true,
      executionId,
      type: 'TIME_BASED',
      actions: [
        { action: 'buy', symbol, quantity, timestamp: new Date() }
      ]
    };
  }

  async executeSignalBased(strategy, executionId) {
    logger.info(`[${executionId}] Executing signal-based strategy`);

    // Buy/sell based on technical signals
    const { symbol, indicators } = strategy.config;

    return {
      success: true,
      executionId,
      type: 'SIGNAL_BASED',
      signal: 'BUY',
      actions: []
    };
  }

  async executeGridTrading(strategy, executionId) {
    logger.info(`[${executionId}] Executing grid trading strategy`);

    // Grid trading placing orders at intervals
    const { symbol, gridSize, minPrice, maxPrice } = strategy.config;

    return {
      success: true,
      executionId,
      type: 'GRID_TRADING',
      gridLevels: [],
      actions: []
    };
  }

  async executeDCA(strategy, executionId) {
    logger.info(`[${executionId}] Executing DCA (Dollar Cost Averaging) strategy`);

    // DCA - buy fixed amount at regular intervals
    const { symbol, amount, frequency } = strategy.config;

    return {
      success: true,
      executionId,
      type: 'DCA',
      amount,
      symbol,
      actions: [
        { action: 'buy', symbol, amount, timestamp: new Date() }
      ]
    };
  }

  recordExecution(executionId, strategyId, success, result, duration) {
    this.executionHistory.push({
      executionId,
      strategyId,
      success,
      result,
      duration,
      timestamp: new Date()
    });

    // Keep only last 1000 executions
    if (this.executionHistory.length > 1000) {
      this.executionHistory.shift();
    }
  }

  getExecutionHistory(strategyId, limit = 50) {
    return this.executionHistory
      .filter(e => e.strategyId === strategyId)
      .slice(-limit)
      .reverse();
  }

  getAllExecutions(limit = 100) {
    return this.executionHistory.slice(-limit).reverse();
  }

  getTrade(tradeId) {
    return this.trades.get(tradeId);
  }

  recordTrade(trade) {
    const tradeId = uuidv4();
    this.trades.set(tradeId, {
      id: tradeId,
      ...trade,
      timestamp: new Date()
    });
    return tradeId;
  }
}

export const strategyExecutor = new StrategyExecutor();
