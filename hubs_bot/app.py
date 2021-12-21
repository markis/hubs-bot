import dataclasses
import logging
import os
import time

from typing import Optional

import requests

from bs4 import BeautifulSoup
from bs4.element import Tag
from praw import Reddit
from praw.reddit import Submission
from praw.reddit import Subreddit
from schedule import every
from schedule import repeat
from schedule import run_pending


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hubs-bot")

BASE_URL = "https://www.beaconjournal.com"
HUBTIMES_URL = f"{BASE_URL}/communities/hudsonhubtimes/"
SUBREDDIT = os.environ.get("SUBREDDIT", "hudsonohtest")
SUBREDDIT_FLAIR = os.environ.get("SUBREDDIT_FLAIR")


@dataclasses.dataclass
class HubTimesLink:
    headline: str
    url: str


@repeat(every(5).minutes)
def main() -> None:
    """
    Hubs-bot main

    This is the starting point of this script.
    """
    link = get_hub_times_link()
    if link:
        submit_link(link)


def get_hub_times_link() -> Optional[HubTimesLink]:
    """
    Get the latest article from the hub times front page
    """
    req = requests.get(HUBTIMES_URL)
    soup = BeautifulSoup(req.text, "html.parser")
    link = soup.find(is_hub_times_link)
    if not link:
        return None

    return HubTimesLink(url=get_url(link), headline=get_headline(link))


def is_hub_times_link(tag: Tag) -> bool:
    """
    Look for a link that specifies that's tagged as "Hudson Hub Times"
    """
    if tag.name == "a" and tag.has_attr("href"):
        if tag.find(attrs={"data-c-ms": "HUDSON HUB TIMES"}):
            return True
    return False


def get_headline(tag: Tag) -> str:
    text = tag.get_text() or ""
    return text.strip()


def get_url(tag: Tag) -> str:
    return str(BASE_URL + tag.attrs["href"])


def submit_link(link: HubTimesLink) -> None:
    """
    Submit the link to Reddit
    """
    reddit = Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        password=os.environ["PASSWORD"],
        username="hubs-bot",
        user_agent="hubs-bot",
    )
    reddit.validate_on_submit = True
    sr: Subreddit = reddit.subreddit(SUBREDDIT)
    submission: Submission
    for submission in sr.new():
        if submission.url == link.url:
            logger.debug("link already exists, don't submit")
            return

    submission = sr.submit(title=link.headline, url=link.url, flair_id=SUBREDDIT_FLAIR)
    submission.mod.approve()
    logger.info(f"submitted link, {submission.id} {link.url}")


if __name__ == "__main__":
    logger.info("starting")
    main()
    while True:
        run_pending()
        time.sleep(1)
