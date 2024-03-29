"""Bot that submits articles from the Hub Times to Reddit."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from praw import Reddit
from praw.models.reddit.redditor import Redditor

from hubs_bot.categorizer import Categorizer
from hubs_bot.config import Config
from hubs_bot.context import Context

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from praw.reddit import Submission, Subreddit


@dataclass
class HubTimesArticle:
    """Represents an article from the Hub Times."""

    url: str
    headline: str
    article: str


class HubTimesBot:
    """Bot that submits articles from the Hub Times to Reddit."""

    config: Config
    reddit: Reddit
    http_get: Callable[[str], str]
    categorizer: Categorizer

    def __init__(self, context: Context, config: Config) -> None:
        """Initialize the bot."""
        self.config = config
        self.reddit = context.reddit
        self.http_get = context.http_get
        self.categorizer = context.categorizer
        self.summarizer = context.summarizer

    def run(self) -> None:
        """This is the starting point of this bot."""
        logger.info("running")

        try:
            link = self.get_hub_times_article()
            logger.info("link found: %s", link)
            self.submit_link(link)
        except AssertionError:
            logger.exception("no link found")

    def get_hub_times_article(self) -> HubTimesArticle:
        """Get the latest article from the Hub Times."""
        html = self.http_get(self.config.hubtimes_url)
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find(self.is_hub_times_link)
        assert isinstance(link, Tag), "No article on front page"

        article_url = self.get_url(link)
        article_html = self.http_get(article_url)
        soup = BeautifulSoup(article_html, "html.parser")
        article_tag = soup.find("article")

        assert article_tag, "Article page is missing an <article> tag"
        article = article_tag.get_text(" ", strip=True)
        headline_tag = article_tag.find("h1")

        assert headline_tag, "Article page is missing an <h1> tag"
        assert not isinstance(headline_tag, int), "Article page has numeric h1"
        article_headline = headline_tag.text

        return HubTimesArticle(url=article_url, headline=article_headline, article=article)

    def is_hub_times_link(self, tag: Tag | NavigableString) -> bool:
        """
        Check if tag is a link to a hub times article.

        Args:
            tag: tag to check
        """
        return bool(
            isinstance(tag, Tag)
            and tag.name == "a"
            and tag.has_attr("href")
            and tag.find_all(attrs={"data-c-ms": True})
        )

    def get_headline(self, tag: Tag) -> str:
        """
        Get Headline from tag.

        Args:
            tag: tag that contains the headline text
        """
        text = tag.get_text() or ""
        return text.strip()

    def get_url(self, tag: Tag) -> str:
        """
        Get URL from tag.

        Args:
            tag: tag that contains the URL
        """
        return urljoin(self.config.base_url, tag.attrs["href"])

    def submit_link(self, link: HubTimesArticle) -> bool:
        """Submit the link to Reddit."""
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
        self.categorizer.flair_submission(submission, link.article)
        logger.info("submitted link %s", submission.id)

        summary = self.summarizer.generate(link.article)
        if summary:
            summary_comment = f"Generated Article Summary:\n\n> {summary}"
            submission.reply(summary_comment)

        return True
