from functools import cached_property
from typing import TYPE_CHECKING, Any

import openai
import requests

from hubs_bot.config import Config

if TYPE_CHECKING:  # pragma: no cover
    from praw import Reddit

    from hubs_bot.categorizer import Categorizer


class Context:
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config

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

    @cached_property
    def reddit(self) -> "Reddit":
        from praw import Reddit

        return Reddit(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            password=self.config.password,
            username=self.config.username,
            user_agent=self.config.username,
            check_for_updates=False,
        )
