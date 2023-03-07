import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

BASE_URL = "https://www.beaconjournal.com"
NEWS_TAGS = {"LOCAL", "HUDSON HUB TIMES"}


def create_set_factory(
    env_name: str, default: set[str], env: Mapping[str, str | set[str]]
) -> Callable[[], set[str]]:
    def _get_set() -> set[str]:
        value = env.get(env_name, default)
        if isinstance(value, str):
            return set(value.split(","))
        elif isinstance(value, set):
            return value
        else:
            raise ValueError(f"${env_name} is not set correctly")

    return _get_set


@dataclass
class Config:
    base_url: str = os.environ.get("BASE_URL", BASE_URL)
    hubtimes_url: str = os.environ.get("HUBTIMES_URL", f"{BASE_URL}/communities/hudsonhubtimes/")
    subreddit: str = os.environ.get("SUBREDDIT", "hudsonohtest")
    subreddit_flair: str = os.environ.get("SUBREDDIT_FLAIR", "93312688-b815-11ea-917e-0e65e9cea44f")
    news_tags: set[str] = field(
        default_factory=create_set_factory("NEWS_TAGS", NEWS_TAGS, os.environ)
    )
    username: str = os.environ.get("USERNAME", "hubs-bot")
    password: str = os.environ.get("PASSWORD", "password")
    client_id: str = os.environ.get("CLIENT_ID", "client_id")
    client_secret: str = os.environ.get("CLIENT_SECRET", "client_secret")
