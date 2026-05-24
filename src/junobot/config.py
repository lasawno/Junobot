import os

from dotenv import load_dotenv

from junobot.brokers import Broker
from junobot.brokers.alpaca import AlpacaBroker
from junobot.brokers.robinhood import RobinhoodBroker

load_dotenv()


class ConfigError(Exception):
    pass


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"Missing required env var: {name}. See .env.example.")
    return value


def load_broker() -> Broker:
    broker_name = os.environ.get("JUNOBOT_BROKER", "alpaca").lower()

    if broker_name == "alpaca":
        return AlpacaBroker(
            api_key=_require("ALPACA_API_KEY"),
            api_secret=_require("ALPACA_API_SECRET"),
            paper=os.environ.get("ALPACA_PAPER", "true").lower() == "true",
        )

    if broker_name == "robinhood":
        return RobinhoodBroker(
            username=_require("ROBINHOOD_USERNAME"),
            password=_require("ROBINHOOD_PASSWORD"),
            mfa_secret=os.environ.get("ROBINHOOD_MFA_SECRET"),
        )

    raise ConfigError(f"Unknown JUNOBOT_BROKER: {broker_name!r}. Use 'alpaca' or 'robinhood'.")
