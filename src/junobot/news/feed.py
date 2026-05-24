import logging
import time
from dataclasses import dataclass

import feedparser

log = logging.getLogger("junobot.news")

# Per-ticker Yahoo Finance RSS — substitute {symbol} per query.
DEFAULT_TICKER_FEED_TEMPLATE = (
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
)

# General market feeds — same content for every symbol, used as context.
DEFAULT_MARKET_FEEDS = [
    "https://feeds.content.dowjones.io/public/rss/RSSMarketsMain",
    "https://www.marketwatch.com/rss/topstories",
]

feedparser.USER_AGENT = "Mozilla/5.0 (compatible; junobot/0.1)"


@dataclass(frozen=True)
class Article:
    title: str
    summary: str
    link: str
    source: str  # feed URL the article came from
    ticker_specific: bool  # True if from a per-symbol feed


class NewsFeed:
    def __init__(
        self,
        market_feeds: list[str] | None = None,
        ticker_feed_template: str | None = DEFAULT_TICKER_FEED_TEMPLATE,
        cache_seconds: int = 60,
    ):
        self.market_feeds = market_feeds if market_feeds is not None else DEFAULT_MARKET_FEEDS
        self.ticker_feed_template = ticker_feed_template
        self.cache_seconds = cache_seconds
        self._cache: dict[str, tuple[float, list[Article]]] = {}

    def _fetch_url(self, url: str, ticker_specific: bool) -> list[Article]:
        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            log.warning("feed parse failed: %s status=%s", url, parsed.get("status"))
            return []
        return [
            Article(
                title=e.get("title", ""),
                summary=e.get("summary", ""),
                link=e.get("link", ""),
                source=url,
                ticker_specific=ticker_specific,
            )
            for e in parsed.entries
        ]

    def fetch(self, symbol: str | None = None) -> list[Article]:
        """Market headlines + (if symbol given) ticker-specific Yahoo headlines.
        Cached per symbol for `cache_seconds`."""
        cache_key = symbol or "__market__"
        now = time.time()
        cached = self._cache.get(cache_key)
        if cached and (now - cached[0]) < self.cache_seconds:
            return cached[1]

        articles: list[Article] = []
        for url in self.market_feeds:
            articles.extend(self._fetch_url(url, ticker_specific=False))

        if symbol and self.ticker_feed_template:
            url = self.ticker_feed_template.format(symbol=symbol)
            articles.extend(self._fetch_url(url, ticker_specific=True))

        self._cache[cache_key] = (now, articles)
        return articles
