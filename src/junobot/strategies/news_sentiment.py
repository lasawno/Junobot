from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from junobot.news import NewsFeed
from junobot.strategies.base import Action, MarketContext, Signal, Strategy


class NewsSentimentStrategy(Strategy):
    """Scores headlines with VADER and maps aggregate sentiment to BUY/SELL/HOLD.

    Pulls per-ticker Yahoo Finance headlines (always relevant) plus general
    market headlines (context). Ticker-specific articles are weighted 2x.
    """

    name = "news_sentiment"

    def __init__(
        self,
        market_feeds: list[str] | None = None,
        ticker_feed_template: str | None = None,
        buy_threshold: float = 0.25,
        sell_threshold: float = -0.25,
        min_articles: int = 3,
        cache_seconds: int = 60,
    ):
        if buy_threshold <= sell_threshold:
            raise ValueError("buy_threshold must be greater than sell_threshold")
        kwargs = {"market_feeds": market_feeds, "cache_seconds": cache_seconds}
        if ticker_feed_template is not None:
            kwargs["ticker_feed_template"] = ticker_feed_template
        self.feed = NewsFeed(**kwargs)
        self.analyzer = SentimentIntensityAnalyzer()
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.min_articles = min_articles

    def evaluate(self, ctx: MarketContext) -> Signal:
        articles = self.feed.fetch(symbol=ctx.symbol)
        if len(articles) < self.min_articles:
            return Signal(
                ctx.symbol,
                Action.HOLD,
                reason=f"insufficient articles ({len(articles)} < {self.min_articles})",
            )

        weighted_sum = 0.0
        weight_total = 0.0
        ticker_count = 0
        for a in articles:
            score = self.analyzer.polarity_scores(a.title)["compound"]
            w = 2.0 if a.ticker_specific else 1.0
            weighted_sum += score * w
            weight_total += w
            if a.ticker_specific:
                ticker_count += 1
        avg = weighted_sum / weight_total

        sample = f"n={len(articles)} ticker={ticker_count} avg={avg:+.2f}"
        if avg >= self.buy_threshold:
            return Signal(ctx.symbol, Action.BUY, reason=f"news bullish [{sample}]")
        if avg <= self.sell_threshold:
            return Signal(ctx.symbol, Action.SELL, reason=f"news bearish [{sample}]")
        return Signal(ctx.symbol, Action.HOLD, reason=f"news neutral [{sample}]")
