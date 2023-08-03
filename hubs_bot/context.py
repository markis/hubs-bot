from functools import cached_property
from typing import Any

import openai
import requests
from praw import Reddit

from hubs_bot.config import Config


class Context:
    reddit: Reddit

    def __init__(self, config: Config) -> None:
        self.reddit = Reddit(
            client_id=config.client_id,
            client_secret=config.client_secret,
            password=config.password,
            username=config.username,
            user_agent=config.username,
            check_for_updates=False,
        )
        openai.api_key = config.openai_key

    def http_get(self, url: str) -> str:
        resp = requests.get(url, timeout=10)
        return resp.text

    @cached_property
    def openai_completion(self) -> Any:
        return openai.Completion
