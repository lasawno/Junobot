from junobot.strategies.base import Action, MarketContext, Signal, Strategy
from junobot.strategies.composite import AndStrategy
from junobot.strategies.news_sentiment import NewsSentimentStrategy
from junobot.strategies.sma_crossover import SmaCrossover

__all__ = [
    "Action",
    "MarketContext",
    "Signal",
    "Strategy",
    "SmaCrossover",
    "NewsSentimentStrategy",
    "AndStrategy",
]


_SMA_KEYS = {"short", "long"}
_NEWS_KEYS = {
    "market_feeds",
    "ticker_feed_template",
    "buy_threshold",
    "sell_threshold",
    "min_articles",
    "cache_seconds",
}


def get_strategy(name: str, **kwargs) -> Strategy:
    if name == "sma_crossover":
        return SmaCrossover(**{k: v for k, v in kwargs.items() if k in _SMA_KEYS})
    if name == "news_sentiment":
        return NewsSentimentStrategy(**{k: v for k, v in kwargs.items() if k in _NEWS_KEYS})
    if name == "sma_and_news":
        # Conservative composite: only act when both agree.
        sma = SmaCrossover(**{k: v for k, v in kwargs.items() if k in _SMA_KEYS})
        news = NewsSentimentStrategy(**{k: v for k, v in kwargs.items() if k in _NEWS_KEYS})
        return AndStrategy(sma, news)
    raise ValueError(
        f"Unknown strategy: {name!r}. Available: 'sma_crossover', 'news_sentiment', 'sma_and_news'"
    )
