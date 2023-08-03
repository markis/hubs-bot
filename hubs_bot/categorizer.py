import logging
from textwrap import dedent
from typing import Any, TypedDict, TypeGuard

import openai
from praw.models.reddit.submission import SubmissionFlair
from praw.reddit import Submission

from hubs_bot.config import Config
from hubs_bot.context import Context

logger = logging.getLogger(__name__)


class Flair(TypedDict):
    flair_css_class: str
    flair_template_id: str
    flair_text_editable: bool
    flair_position: str
    flair_text: str


def is_flair(value: Any) -> TypeGuard[Flair]:
    return isinstance(value, dict)


class Categorizer:
    config: Config
    openai_completion: openai.Completion

    def __init__(self, context: Context, config: Config) -> None:
        self.config = config
        self.openai_completion = context.openai_completion

    def flair_submission(self, submission: Submission) -> None:
        """
        Flair the submission using only the flair available on the subreddit
        """
        flair: SubmissionFlair = submission.flair
        choices = {
            choice["flair_text"]: choice["flair_template_id"]
            for choice in flair.choices()
            if is_flair(choice)
        }

        flair_id = self._ask_openai(submission.title, choices)
        submission.flair.select(flair_id)

    def _ask_openai(self, content_text: str, choices: dict[str, str]) -> str:
        result = self.config.subreddit_flair
        prompt = dedent(
            f"""
            Using only one of the following categories:
            {", ".join(choices.keys())}

            How would you categorize the following news article:

            {content_text}
            """
        )

        resp: Any = self.openai_completion.create(  # type: ignore[no-untyped-call]
            model="text-davinci-003",
            prompt=prompt,
        )

        if resp and len(resp.choices) > 0:
            text: str = resp.choices[0].text
            result = choices.get(text.strip(), result)

        return result
