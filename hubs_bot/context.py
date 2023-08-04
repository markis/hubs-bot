from functools import cached_property
from typing import TYPE_CHECKING, Any

import openai
import requests
from praw import Reddit

from hubs_bot.config import Config

if TYPE_CHECKING:  # pragma: no cover
    from hubs_bot.categorizer import Categorizer


class Context:
    reddit: Reddit

    def __init__(self, config: Config) -> None:
        self.reddit = Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            password=config.password,
            username=config.username,
            user_agent=config.username,
        )
        openai.api_key = config.openai_key

    def http_get(self, url: str) -> str:
        resp = requests.get(url, timeout=10)
        return resp.text

    @cached_property
    def openai_completion(self) -> Any:
        return openai.Completion

    @cached_property
    def categorizer(self) -> "Categorizer":
        from hubs_bot.categorizer import Categorizer

        return Categorizer(self, Config())
