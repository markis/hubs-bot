import dataclasses
import os

from typing import Optional

import requests

from bs4 import BeautifulSoup
from bs4.element import Tag
from praw import Reddit
from praw.reddit import Subreddit


BASE_URL = "https://www.beaconjournal.com"
HUBTIMES_URL = f"{BASE_URL}/communities/hudsonhubtimes/"
SUBREDDIT = os.environ.get("SUBREDDIT", "hudsonohtest")


@dataclasses.dataclass
class HubTimesLink:
    headline: str
    url: str


def get_hub_times_link() -> Optional[HubTimesLink]:
    req = requests.get(HUBTIMES_URL)
    soup = BeautifulSoup(req.text, "html.parser")
    link = soup.find(is_hub_times_link)
    if not link:
        return None

    return HubTimesLink(url=get_url(link), headline=get_headline(link))


def is_hub_times_link(tag: Tag) -> bool:
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
    reddit = Reddit(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        password=os.environ["PASSWORD"],
        username="hubs-bot",
        user_agent="hubs-bot",
    )
    reddit.validate_on_submit = True
    sr: Subreddit = reddit.subreddit(SUBREDDIT)
    for submission in sr.new():
        if submission.url == link.url:
            print("link already exists, don't submit")
            return

    sr.submit(title=link.headline, url=link.url)
    print(f"submitted link, {link.url}")


if __name__ == "__main__":
    link = get_hub_times_link()
    if link:
        submit_link(link)
