"""Categorizes articles using OpenAI's GPT-3."""

import logging
from typing import TYPE_CHECKING, Any, NotRequired, TypedDict, TypeGuard

from openai import OpenAI
from praw.reddit import Submission

from hubs_bot.config import Config
from hubs_bot.context import Context

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from praw.models.reddit.submission import SubmissionFlair


class Flair(TypedDict):
    """Represents a flair on a subreddit."""

    flair_template_id: str
    flair_text: str
    flair_css_class: NotRequired[str]
    flair_text_editable: NotRequired[bool]
    flair_position: NotRequired[str]


def is_flair(value: Any) -> TypeGuard[Flair]:
    """Type guard for the Flair type."""
    return isinstance(value, dict) and all(key in value for key in Flair.__required_keys__)


class Categorizer:
    """Categorizes articles."""

    config: Config
    openai: OpenAI

    def __init__(self, context: Context, config: Config) -> None:
        """Initialize the categorizer."""
        self.config = config
        self.openai = context.openai

    def flair_submission(self, submission: Submission, article: str) -> None:
        """
        Flair the submission using only the flair available on the subreddit.

        Args:
            submission: The submission to flair
            article: The text of the article to categorize
        """
        flair: SubmissionFlair = submission.flair
        choices = {
            choice["flair_text"].lower(): choice["flair_template_id"]
            for choice in flair.choices()
            if is_flair(choice)
        }

        flair_id = self._ask_openai(article, choices)
        submission.flair.select(flair_id)

    def _ask_openai(self, content_text: str, choices: dict[str, str]) -> str:
        result = self.config.subreddit_flair
        prompt = (
            "Using one of the following categories ("
            + ", ".join(choices.keys())
            + "), categorize this article and respond with just the category:"
            + content_text
        )
        resp = self.openai.completions.create(model=self.config.openai_model, prompt=prompt)

        if resp and resp.choices and len(resp.choices) > 0 and (text := resp.choices[0].text):
            result = choices.get(text.strip().lower(), result)

        return result
