import logging
from collections.abc import Callable
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from praw import Reddit
from praw.models.reddit.redditor import Redditor
from praw.reddit import Submission, Subreddit

from hubs_bot.categorizer import Categorizer
from hubs_bot.config import Config
from hubs_bot.context import Context

logger = logging.getLogger(__name__)


@dataclass
class HubTimesLink:
    headline: str
    url: str


class HubTimesBot:
    config: Config
    reddit: Reddit
    http_get: Callable[[str], str]

    def __init__(self, context: Context, config: Config) -> None:
        self.config = config
        self.reddit = context.reddit
        self.http_get = context.http_get
        self.categorizer = Categorizer(context, config)

    def run(self) -> None:
        """
        Hubs-bot main

        This is the starting point of this script.
        """
        logger.info("running")

        link = self.get_hub_times_link()
        if not link:
            logger.info("no link found")
        else:
            logger.info(f"link found: {link}")
            self.submit_link(link)

    def get_hub_times_link(self) -> HubTimesLink | None:
        """
        Get the latest article from the hub times front page
        """
        html = self.http_get(self.config.hubtimes_url)
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find(self.is_hub_times_link)
        if not isinstance(link, Tag):
            return None

        return HubTimesLink(url=self.get_url(link), headline=self.get_headline(link))

    def is_hub_times_link(self, tag: Tag | NavigableString) -> bool:
        """
        Look for links with specific tags
        """
        if isinstance(tag, Tag) and tag.name == "a" and tag.has_attr("href"):
            for news_tag in self.config.news_tags:
                if tag.find(attrs={"data-c-ms": news_tag}):
                    return True
        return False

    def get_headline(self, tag: Tag) -> str:
        text = tag.get_text() or ""
        return text.strip()

    def get_url(self, tag: Tag) -> str:
        return str(self.config.base_url + tag.attrs["href"])

    def submit_link(self, link: HubTimesLink) -> bool:
        """
        Submit the link to Reddit
        """
        reddit = self.reddit
        reddit.validate_on_submit = True
        sr: Subreddit = reddit.subreddit(self.config.subreddit)
        submission: Submission
        me = reddit.user.me()
        if me and isinstance(me, Redditor):
            for submission in me.submissions.new(limit=10):
                if submission.url == link.url:
                    logger.info("link already exists, don't submit")
                    return False

        for submission in sr.new(limit=10):
            if submission.url == link.url:
                logger.info("link already exists, don't submit")
                return False

        submission = sr.submit(
            title=link.headline, url=link.url, flair_id=self.config.subreddit_flair
        )
        submission.mod.approve()
        self.categorizer.flair_submission(submission)
        logger.info(f"submitted link, {submission.id}")
        return True
