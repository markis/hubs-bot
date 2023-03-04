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
        )

    def http_get(self, url: str) -> str:
        resp = requests.get(url)
        return resp.text
