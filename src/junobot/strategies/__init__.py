from junobot.strategies.base import Action, MarketContext, Signal, Strategy
from junobot.strategies.sma_crossover import SmaCrossover

__all__ = ["Action", "MarketContext", "Signal", "Strategy", "SmaCrossover"]


def get_strategy(name: str, **kwargs) -> Strategy:
    if name == "sma_crossover":
        return SmaCrossover(**kwargs)
    raise ValueError(f"Unknown strategy: {name!r}. Available: 'sma_crossover'")
