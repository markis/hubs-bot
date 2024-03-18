"""This module contains the Context class, which is a container for the bot's dependencies."""
from functools import cached_property
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import TYPE_CHECKING

import requests
import requests.cookies
import requests.utils
from openai import OpenAI

from hubs_bot.config import Config

if TYPE_CHECKING:
    from praw import Reddit

    from hubs_bot.categorizer import Categorizer
    from hubs_bot.summarizer import Summarizer


class Context:
    """A container for the bot's dependencies."""

    config: Config

    def __init__(self, config: Config) -> None:
        """Initialize the context."""
        self.config = config

    def http_get(self, url: str) -> str:
        """Make an HTTP GET request to the given URL and return the response."""
        cookie_path = Path(self.config.cookies_file)
        cookie_jar = requests.cookies.RequestsCookieJar()
        if cookie_path.exists():
            moz_jar = MozillaCookieJar(cookie_path)
            moz_jar.load()
            cookie_jar.update(moz_jar)

        resp = requests.get(url, cookies=cookie_jar, timeout=10)
        return resp.text

    @cached_property
    def openai(self) -> OpenAI:
        """Return an instance of the OpenAI API."""
        return OpenAI(api_key=self.config.openai_key)

    @cached_property
    def categorizer(self) -> "Categorizer":
        """Return an instance of the Categorizer."""
        from hubs_bot.categorizer import Categorizer

        return Categorizer(self, self.config)

    @cached_property
    def summarizer(self) -> "Summarizer":
        """Return an instance of the Summarizer."""
        from hubs_bot.summarizer import Summarizer

        return Summarizer(self, self.config)

    @cached_property
    def reddit(self) -> "Reddit":
        """Return an instance of the Reddit API."""
        from praw import Reddit

        return Reddit(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            password=self.config.password,
            username=self.config.username,
            user_agent=self.config.username,
            check_for_updates=False,
        )
